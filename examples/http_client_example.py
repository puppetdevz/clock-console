"""
Example demonstrating httpx usage with FastAPI for making HTTP requests.

This module shows how to use httpx for both synchronous and asynchronous
HTTP requests within a FastAPI application.
"""

import httpx
from fastapi import FastAPI, HTTPException
from typing import Dict, Any, Optional

app = FastAPI(title="HTTP Client Example")

# Configuration for httpx clients
DEFAULT_TIMEOUT = httpx.Timeout(10.0, connect=5.0)
DEFAULT_LIMITS = httpx.Limits(max_keepalive_connections=5, max_connections=10)


@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "HTTP Client Example API", "client": "httpx"}


@app.get("/fetch-json-placeholder/{post_id}")
async def fetch_post(post_id: int) -> Dict[str, Any]:
    """
    Fetch a post from JSONPlaceholder API using async httpx.
    
    Args:
        post_id: The ID of the post to fetch
        
    Returns:
        The post data from JSONPlaceholder
    """
    url = f"https://jsonplaceholder.typicode.com/posts/{post_id}"
    
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Error fetching post: {e.response.text}"
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Error connecting to external API: {str(e)}"
            )


@app.get("/fetch-github-user/{username}")
async def fetch_github_user(username: str) -> Dict[str, Any]:
    """
    Fetch GitHub user information using async httpx.
    
    Args:
        username: GitHub username
        
    Returns:
        GitHub user data
    """
    url = f"https://api.github.com/users/{username}"
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "FastAPI-httpx-example"
    }
    
    async with httpx.AsyncClient(
        timeout=DEFAULT_TIMEOUT,
        limits=DEFAULT_LIMITS,
        headers=headers
    ) as client:
        try:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Return only essential information
            return {
                "login": data.get("login"),
                "name": data.get("name"),
                "bio": data.get("bio"),
                "public_repos": data.get("public_repos"),
                "followers": data.get("followers"),
                "following": data.get("following"),
                "created_at": data.get("created_at"),
                "avatar_url": data.get("avatar_url")
            }
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                raise HTTPException(status_code=404, detail="GitHub user not found")
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"GitHub API error: {e.response.text}"
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Error connecting to GitHub API: {str(e)}"
            )


@app.post("/proxy-request")
async def proxy_request(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    body: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Proxy a request to an external URL.
    
    Args:
        url: Target URL
        method: HTTP method (GET, POST, PUT, DELETE, etc.)
        headers: Optional headers to include
        body: Optional request body for POST/PUT requests
        
    Returns:
        Response from the external service
    """
    async with httpx.AsyncClient(timeout=DEFAULT_TIMEOUT) as client:
        try:
            request_kwargs = {
                "method": method.upper(),
                "url": url,
                "headers": headers or {}
            }
            
            if body and method.upper() in ["POST", "PUT", "PATCH"]:
                request_kwargs["json"] = body
            
            response = await client.request(**request_kwargs)
            response.raise_for_status()
            
            return {
                "status_code": response.status_code,
                "headers": dict(response.headers),
                "content": response.json() if response.headers.get("content-type", "").startswith("application/json") else response.text
            }
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"External service error: {e.response.text}"
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=503,
                detail=f"Error connecting to external service: {str(e)}"
            )


# Example of a shared client for better performance (connection pooling)
class HTTPClient:
    """Singleton HTTP client for reusing connections."""
    
    _client: Optional[httpx.AsyncClient] = None
    
    @classmethod
    async def get_client(cls) -> httpx.AsyncClient:
        """Get or create the shared async client."""
        if cls._client is None:
            cls._client = httpx.AsyncClient(
                timeout=DEFAULT_TIMEOUT,
                limits=DEFAULT_LIMITS,
                headers={"User-Agent": "FastAPI-httpx-app"}
            )
        return cls._client
    
    @classmethod
    async def close(cls):
        """Close the shared client."""
        if cls._client:
            await cls._client.aclose()
            cls._client = None


@app.on_event("shutdown")
async def shutdown_event():
    """Clean up HTTP client on shutdown."""
    await HTTPClient.close()


@app.get("/fetch-with-shared-client/{resource}")
async def fetch_with_shared_client(resource: str) -> Dict[str, Any]:
    """
    Example using a shared HTTP client for better performance.
    
    Args:
        resource: Resource to fetch (posts, users, comments)
        
    Returns:
        Data from JSONPlaceholder API
    """
    client = await HTTPClient.get_client()
    url = f"https://jsonplaceholder.typicode.com/{resource}"
    
    try:
        response = await client.get(url)
        response.raise_for_status()
        data = response.json()
        
        # Return first 5 items if it's a list
        if isinstance(data, list):
            return {"resource": resource, "count": len(data), "items": data[:5]}
        return {"resource": resource, "data": data}
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Error fetching resource: {e.response.text}"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Error connecting to API: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
