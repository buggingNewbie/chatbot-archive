import json

import httpx
from pydantic import BaseModel, ConfigDict, Field

class clientSingleton:
    API_URL = "http://127.0.0.1:12345"
    client : httpx.AsyncClient = None
   
    @staticmethod
    def getClient():
        if clientSingleton.client is None:
            clientSingleton.client = httpx.AsyncClient(base_url=clientSingleton.API_URL)
        return clientSingleton.client
    
    @staticmethod
    def closeClient():
        if clientSingleton.client is not None:
            clientSingleton.client.aclose()
            clientSingleton.client = None


#--------------------- Unused pydantic models --------------------------
class Headers(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=False)
    authorzation : str = Field(alias='Authorization', default="Bearer test")
    x_tenant_id : str = Field(alias='X-Tenant-Id', default="123")

class QueryParameters(BaseModel):
    model_config = ConfigDict(extra="forbid")
    page : int = Field(alias="page", default=None)
    page_size : int = Field(alias="pageSize", ge=1, le=100, default=None)
    search : str = Field(alias="search", default=None)

class ImageObject(BaseModel):
    model_config = ConfigDict(extra="forbid")
    url: str = Field(alias="url")
    is_primary: bool = Field(alias="isPrimary", default=None)

class ProductBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name : str = Field(alias="name", default=None)
    sku : str = Field(alias="sku", default=None)
    type : str = Field(alias="type", default=None)
    status : str = Field(alias="status", default=None)
    base_price : float = Field(alias="base_price", default=None)
    barcode : str = Field(alias="barcode", default=None)
    description: str = Field(alias="description", default=None)
    web_title: str = Field(alias="web_title", default=None)
    web_description: str = Field(alias="web_description", default=None)
    brand_id: str = Field(alias="brand_id", default=None)
    category_id: str = Field(alias="category_id", default=None)
    warranty_months: int = Field(alias="warranty_months", default=None)
    length_cm: float = Field(alias="length_cm", default=None)
    width_cm: float = Field(alias="width_cm", default=None)
    height_cm: float = Field(alias="height_cm", default=None)
    weight_g: float = Field(alias="weight_g", default=None)
    cost_price: float = Field(alias="cost_price", default=None)
    selling_price: float = Field(alias="selling_price", default=None)
    images: list[ImageObject] = Field(alias="images", default=None)
    tags: list[str] = Field(alias="tags", default=None)
    suppliers: list[str] = Field(alias="suppliers", default=None)

class BrandBody(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: str = Field(alias="name", default=None)
    description: str = Field(alias="description", default=None)
    logo_url: str = Field(alias="logoUrl", default=None)

class CategoryBody(BaseModel):
    name: str = Field(alias="name", default=None)
    slug: str = Field(alias="slug", default=None)
    description: str = Field(alias="description", default=None)
    parent_id: str = Field(alias="parentId", default=None)
    status: str = Field(alias="status", default=None)

#-----------------------------------------------------------------


async def get (route: str, headerAuth: str = "Bearer test", headerTenant: str = "123", page: int = 1, page_size: int = 20, search: str = "") -> dict:
    """Sends a GET request to the API server.
    """
    headers = {
        "Authorization": headerAuth,
        "X-Tenant-Id": headerTenant
    }
    params = {
        "page": page,
        "pageSize" : page_size
    }
    if search != "":
        params["search"] = search
    
    client = clientSingleton.getClient()
    response = await client.get(route, 
                                headers = headers, 
                                params = params)
    try:
        data = response.json()
        data["status_code"] = response.status_code
        return data
    except:
        return {
            "status_code": response.status_code,
            "error": "An unexpected error occured, could not parse response"
        }


async def post_product (route: str, headerAuth: str = "Bearer test", headerTenant: str = "123", name: str = None, sku: str = None, type: str = None, status: str = None, base_price: float = None, barcode: str = None, description: str = None, web_title: str = None, web_description: str = None, brand_id: str = None, category_id: str = None, warranty_months: int = None, length_cm: float = None, width_cm: float = None, height_cm: float = None, weight_g: float = None, cost_price: float = None, selling_price: float = None, images: list[str] = None, tags: list[str] = None, suppliers: list[str] = None) -> dict:
    """Sends a POST request with product data to the API server.
    """
    headers = {
        "Authorization": headerAuth,
        "X-Tenant-Id": headerTenant
    }
    body = {}
    if name is not None:
        body["name"] = name
    if sku is not None:
        body["sku"] = sku
    if type is not None:
        body["type"] = type
    if status is not None:
        body["status"] = status
    if base_price is not None:
        body["base_price"] = base_price
    if barcode is not None:
        body["barcode"] = barcode
    if description is not None:
        body["description"] = description
    if web_title is not None:
        body["web_title"] = web_title
    if web_description is not None:
        body["web_description"] = web_description
    if brand_id is not None:
        body["brand_id"] = brand_id
    if category_id is not None:
        body["category_id"] = category_id
    if warranty_months is not None:
        body["warranty_months"] = warranty_months
    if length_cm is not None:
        body["length_cm"] = length_cm
    if width_cm is not None:
        body["width_cm"] = width_cm
    if height_cm is not None:
        body["height_cm"] = height_cm
    if weight_g is not None:
        body["weight_g"] = weight_g
    if cost_price is not None:
        body["cost_price"] = cost_price
    if selling_price is not None:
        body["selling_price"] = selling_price
    if images is not None:
        body["images"] = []
        for item in images:
            body["images"].append(json.loads(item))
    if tags is not None:
        body["tags"] = tags
    if suppliers is not None:
        body["suppliers"] = suppliers
    
    client = clientSingleton.getClient()
    response = await client.post(route, headers=headers, json=body)
    try:
        data = response.json()
        data["status_code"] = response.status_code
        return data
    except:
        return {
            "status_code": response.status_code,
            "error": "An unexpected error occured, could not parse response"
        }


async def post_brand (route: str, headerAuth: str = "Bearer test", headerTenant: str = "123", name: str = None, description: str = None, logo_url: str = None) -> dict:
    """Sends a POST request with brand data to the API server.
    """
    headers = {
        "Authorization": headerAuth,
        "X-Tenant-Id": headerTenant
    }
    body = {}
    if name is not None:
        body["name"] = name
    if description is not None:
        body["description"] = description
    if logo_url is not None:
        body["logoUrl"] = logo_url
    
    client = clientSingleton.getClient()
    response = await client.post(route, headers=headers, json=body)
    try:
        data = response.json()
        data["status_code"] = response.status_code
        return data
    except:
        return {
            "status_code": response.status_code,
            "error": "An unexpected error occured, could not parse response"
        }


async def post_category (route: str, headerAuth: str = "Bearer test", headerTenant: str = "123", name: str = None, slug: str = None, description: str = None, parent_id: str = None, status: str = None) -> dict:
    """Sends a POST request with category data to the API server.
    """
    headers = {
        "Authorization": headerAuth,
        "X-Tenant-Id": headerTenant
    }
    body = {}
    if name is not None:
        body["name"] = name
    if slug is not None:
        body["slug"] = slug
    if description is not None:
        body["description"] = description
    if parent_id is not None:
        body["parentId"] = parent_id
    if status is not None:
        body["status"] = status
    
    client = clientSingleton.getClient()
    response = await client.post(route, headers=headers, json=body)
    try:
        data = response.json()
        data["status_code"] = response.status_code
        return data
    except:
        return {
            "status_code": response.status_code,
            "error": "An unexpected error occured, could not parse response"
        }

async def patch_product (route: str, headerAuth: str = "Bearer test", headerTenant: str = "123", name: str = None, sku: str = None, type: str = None, status: str = None, base_price: float = None, barcode: str = None, description: str = None, web_title: str = None, web_description: str = None, brand_id: str = None, category_id: str = None, warranty_months: int = None, length_cm: float = None, width_cm: float = None, height_cm: float = None, weight_g: float = None, cost_price: float = None, selling_price: float = None, images: list[str] = None, tags: list[str] = None, suppliers: list[str] = None) -> dict:
    """Sends a PATCH request with product data to the API server.
    """
    headers = {
        "Authorization": headerAuth,
        "X-Tenant-Id": headerTenant
    }
    body = {}
    if name is not None:
        body["name"] = name
    if sku is not None:
        body["sku"] = sku
    if type is not None:
        body["type"] = type
    if status is not None:
        body["status"] = status
    if base_price is not None:
        body["base_price"] = base_price
    if barcode is not None:
        body["barcode"] = barcode
    if description is not None:
        body["description"] = description
    if web_title is not None:
        body["web_title"] = web_title
    if web_description is not None:
        body["web_description"] = web_description
    if brand_id is not None:
        body["brand_id"] = brand_id
    if category_id is not None:
        body["category_id"] = category_id
    if warranty_months is not None:
        body["warranty_months"] = warranty_months
    if length_cm is not None:
        body["length_cm"] = length_cm
    if width_cm is not None:
        body["width_cm"] = width_cm
    if height_cm is not None:
        body["height_cm"] = height_cm
    if weight_g is not None:
        body["weight_g"] = weight_g
    if cost_price is not None:
        body["cost_price"] = cost_price
    if selling_price is not None:
        body["selling_price"] = selling_price
    if images is not None:
        body["images"] = images
    if tags is not None:
        body["tags"] = tags
    if suppliers is not None:
        body["suppliers"] = suppliers
    
    client = clientSingleton.getClient()
    response = await client.patch(route, headers=headers, json=body)
    try:
        data = response.json()
        data["status_code"] = response.status_code
        return data
    except:
        return {
            "status_code": response.status_code,
            "error": "An unexpected error occured, could not parse response"
        }


async def patch_brand (route: str, headerAuth: str = "Bearer test", headerTenant: str = "123", name: str = None, description: str = None, logo_url: str = None) -> dict:
    """Sends a PATCH request with brand data to the API server.
    """
    headers = {
        "Authorization": headerAuth,
        "X-Tenant-Id": headerTenant
    }
    body = {}
    if name is not None:
        body["name"] = name
    if description is not None:
        body["description"] = description
    if logo_url is not None:
        body["logoUrl"] = logo_url
    
    client = clientSingleton.getClient()
    response = await client.patch(route, headers=headers, json=body)
    try:
        data = response.json()
        data["status_code"] = response.status_code
        return data
    except:
        return {
            "status_code": response.status_code,
            "error": "An unexpected error occured, could not parse response"
        }


async def patch_category (route: str, headerAuth: str = "Bearer test", headerTenant: str = "123", name: str = None, slug: str = None, description: str = None, parent_id: str = None, status: str = None) -> dict:
    """Sends a PATCH request with category data to the API server.
    """
    headers = {
        "Authorization": headerAuth,
        "X-Tenant-Id": headerTenant
    }
    body = {}
    if name is not None:
        body["name"] = name
    if slug is not None:
        body["slug"] = slug
    if description is not None:
        body["description"] = description
    if parent_id is not None:
        body["parentId"] = parent_id
    if status is not None:
        body["status"] = status
    
    client = clientSingleton.getClient()
    response = await client.patch(route, headers=headers, json=body)
    try:
        data = response.json()
        data["status_code"] = response.status_code
        return data
    except:
        return {
            "status_code": response.status_code,
            "error": "An unexpected error occured, could not parse response"
        }

async def delete (route: str, headerAuth: str = "Bearer test", headerTenant: str = "123") -> dict:
    """Sends a DELETE request to the API server.
    """
    headers = {
        "Authorization": headerAuth,
        "X-Tenant-Id": headerTenant
    }
    client = clientSingleton.getClient()
    response = await client.delete(route, headers=headers)
    if response.status_code == 204:
        return {
            "status_code": 204
        }
    else:
        try:
            data = response.json()
            data["status_code"] = response.status_code
            return data
        except:
            return {
                "status_code": response.status_code,
                "error": "An unexpected error occured, could not parse response"
            }
