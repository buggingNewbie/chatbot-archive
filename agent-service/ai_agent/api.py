from dotenv import load_dotenv
load_dotenv()

import os
from uuid import uuid4
import json
from typing import Annotated
import time

from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from google.genai import types
from pydantic import BaseModel
import jwt
import httpx
from jwt.algorithms import RSAAlgorithm

from .agent import session_service, runner

app = FastAPI()

allowedOrigins = [
    os.getenv('FRONTEND_WEB_HOST', "http://localhost:5123"),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowedOrigins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

_jwks_cache = {
    'keys': None,
    'expires_at': 0
}
CACHE_TIME = int(os.getenv('JWKS_CACHE_TIME'))
JWKS_URL = os.getenv('JWKS_URL')
JWT_ISSUER = os.getenv('JWT_ISSUER')
AUDIENCE = os.getenv('STACK_PROJECT_ID')

# Helper for authorization with JWT
def authorize(auth_header: str):
    global _jwks_cache
    current_time = time.time()

    # Check auth header format
    if (not auth_header.lower().startswith("bearer ")):
        raise HTTPException(status_code=401, detail="Authorization header must be in Bearer format")
    token = auth_header[7:]
    if (token == ''):
        raise HTTPException(status_code=401, detail="Missing bearer token")


    # Fetch JWKS keys
    keys = None
    if (_jwks_cache["keys"] and current_time < _jwks_cache["expires_at"]):
        keys = _jwks_cache["keys"]
    else:
        with httpx.Client() as client:
            try:
                response = client.get(JWKS_URL)
                response.raise_for_status()
                jwks_data = response.json()
                _jwks_cache["keys"] = jwks_data.get("keys", [])
                _jwks_cache["expires_at"] = current_time + CACHE_TIME
                keys = _jwks_cache["keys"]
            except httpx.HTTPError as e:
                # If the network fails but we have stale cache, fallback to it
                if _jwks_cache["keys"]:
                    keys = _jwks_cache["keys"]
                raise HTTPException(status_code=500, detail=f"Failed to fetch JWKS: {e}")
            
    # Check valid token
    try:
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get('kid')

        key_data = next((key for key in keys if key['kid'] == kid), None)
        if not key_data:
            with httpx.Client() as client:
                try:
                    response = client.get(JWKS_URL)
                    response.raise_for_status()
                    jwks_data = response.json()
                    _jwks_cache["keys"] = jwks_data.get("keys", [])
                    _jwks_cache["expires_at"] = current_time + CACHE_TIME
                    keys = _jwks_cache["keys"]
                except httpx.HTTPError as e:
                    raise HTTPException(status_code=500, detail=f"Failed to connect to authorization service")
            key_data = next((key for key in keys if key['kid'] == kid), None)
            if not key_data:
                raise HTTPException(status_code=401, detail="Invalid Authorization JWT token")
            
        public_key = jwt.PyJWK(key_data).key

        return jwt.decode(
            token,
            public_key,
            algorithms=["ES256"],
            audience=AUDIENCE,
            issuer=JWT_ISSUER
        )
    except Exception as e:
        if isinstance(e, jwt.ExpiredSignatureError):
            raise HTTPException(status_code=401, detail="Authorization token expired")
        if isinstance(e, jwt.InvalidTokenError):
            raise HTTPException(status_code=401, detail="Invalid Authorization JWT token")
        if isinstance(e, HTTPException):
            raise e
            
        raise HTTPException(status_code=401, detail="Authentication error")
    
    
    

class ChatDto(BaseModel):
    message: str = None
    id: str = None
    confirmed: bool = None
    error: str = None

@app.post("/chat")
async def chat_route(request: ChatDto, authorization : Annotated[str, Header()] = "", x_tenant_id : Annotated[str, Header()] = "", x_session_id : Annotated[str | None, Header()] = None):
    try:
        decoded_jwt = authorize(authorization)

        session = None
        if x_session_id is None:
            newSessionId = str(uuid4())
            session = await session_service.create_session(
                app_name=runner.app_name, 
                user_id=decoded_jwt.get('sub'), 
                session_id=newSessionId
            )
        else:
            try:
                session = await session_service.get_session(
                    app_name=runner.app_name, 
                    user_id=decoded_jwt.get('sub'), 
                    session_id=x_session_id
                )
            except Exception as e:
                newSessionId = str(uuid4())
                session = await session_service.create_session(
                    app_name=runner.app_name, 
                    user_id=decoded_jwt.get('sub'), 
                    session_id=newSessionId)

        if (session is None):
            newSessionId = str(uuid4())
            session = await session_service.create_session(
                app_name=runner.app_name, 
                user_id=decoded_jwt.get('sub'), 
                session_id=newSessionId
            )
            if (session is None):
                raise HTTPException(status_code=500, detail="Cannot call AI API")

        headers = {}
        if (authorization != ""):
            headers["Authorization"] = authorization
        if (x_tenant_id != ""):
            headers["X-Tenant-Id"] = x_tenant_id

        message = {
            "headers": headers,
            "message": request.message if request.message is not None else "" 
        }

        if request.id is not None:
            message["id"] = request.id
        if request.confirmed is not None:
            message["confirmed"] = request.confirmed
        if request.error is not None:
            message["error"] = request.error

        response_parts = []
        async for event in runner.run_async(
            user_id=session.user_id,
            session_id=session.id,
            new_message=types.Content(parts=[types.Part(text=str(message))])
        ) :
            if event.author == 'user':
                continue

            try:
                text = event.content.parts[0].text
                if text is not None:
                    response_parts.append(text)
            except:
                continue
        
        agent_message = "".join(response_parts)

        try:
            response_json = json.loads(agent_message)
            response_json["sessionId"] = session.id

            return response_json
        except json.JSONDecodeError:
            raise HTTPException(status_code=500, detail="An error occured with the AI agent. Try sending the request again.")

    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        
        raise HTTPException(status_code=500, detail=str(e))
    