from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional, Any
from scrapling.fetchers import AsyncFetcher, AsyncDynamicSession, AsyncStealthySession
from urllib.parse import urlparse

app = FastAPI(
    title="Scrapling API Service",
    description="A high-performance scraping REST API powered by Scrapling",
    version="1.0.0"
)

class FetchRequest(BaseModel):
    url: str
    fetcher: Optional[str] = "stealthy" # Options: static, dynamic, stealthy
    timeout: Optional[int] = 30000
    proxy: Optional[str] = None
    cookies: Optional[Any] = None

class ExtractRequest(BaseModel):
    url: str
    fetcher: Optional[str] = "stealthy"
    selectors: Dict[str, str] # Key is name of field, value is CSS selector (e.g. "title": "h1::text")
    timeout: Optional[int] = 30000
    proxy: Optional[str] = None
    cookies: Optional[Any] = None

def parse_cookies(cookies_input: Any, target_url: str):
    """
    Parses cookies from various formats (string, dict, list)
    into a dictionary (for HTTP requests) and a list of SetCookieParam (for browser requests).
    """
    if not cookies_input:
        return None, None
        
    cookies_dict = {}
    
    # 1. Handle Cookie String format: "name1=val1; name2=val2"
    if isinstance(cookies_input, str):
        for item in cookies_input.split(';'):
            if '=' in item:
                k, v = item.split('=', 1)
                cookies_dict[k.strip()] = v.strip()
    # 2. Handle Dict format: {"name1": "val1"}
    elif isinstance(cookies_input, dict):
        cookies_dict = cookies_input
    # 3. Handle List of Dicts format: [{"name": "name1", "value": "val1"}]
    elif isinstance(cookies_input, list):
        for c in cookies_input:
            if isinstance(c, dict) and "name" in c and "value" in c:
                cookies_dict[c["name"]] = c["value"]
                
    # Prepare list of SetCookieParam for browser/playwright engines
    browser_cookies = []
    for k, v in cookies_dict.items():
        browser_cookies.append({
            "name": k,
            "value": v,
            "url": target_url # Telling Playwright exactly where to apply this cookie
        })
        
    return cookies_dict, browser_cookies

async def get_page(url: str, fetcher_type: str, timeout: int, proxy: Optional[str] = None, cookies_input: Optional[Any] = None):
    """Helper to fetch a page asynchronously based on selected fetcher type, optional proxy and optional cookies."""
    cookies_dict, browser_cookies = parse_cookies(cookies_input, url)
    
    try:
        if fetcher_type == "static":
            fetcher = AsyncFetcher()
            kwargs = {"timeout": timeout}
            if proxy:
                kwargs["proxy"] = proxy
            if cookies_dict:
                kwargs["cookies"] = cookies_dict
            return await fetcher.get(url, **kwargs)
        elif fetcher_type == "dynamic":
            kwargs = {"headless": True, "timeout": timeout}
            if proxy:
                kwargs["proxy"] = proxy
            if browser_cookies:
                kwargs["cookies"] = browser_cookies
            async with AsyncDynamicSession(**kwargs) as session:
                return await session.fetch(url)
        else: # Default is stealthy
            kwargs = {"headless": True, "timeout": timeout}
            if proxy:
                kwargs["proxy"] = proxy
            if browser_cookies:
                kwargs["cookies"] = browser_cookies
            async with AsyncStealthySession(**kwargs) as session:
                return await session.fetch(url)
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to fetch URL using fetcher '{fetcher_type}': {str(e)}"
        )

@app.get("/")
def read_root():
    return {
        "status": "online",
        "framework": "Scrapling",
        "endpoints": {
            "/fetch": "POST - Fetches full rendered HTML of a URL",
            "/extract": "POST - Fetches and extracts specific fields using CSS selectors"
        }
    }

@app.post("/fetch")
async def fetch_html(request: FetchRequest):
    """
    Fetches a web page and returns the full rendered HTML.
    Perfect for Java integration using Jsoup for local parsing.
    """
    page = await get_page(request.url, request.fetcher, request.timeout, request.proxy, request.cookies)
    return {
        "url": request.url,
        "fetcher_used": request.fetcher,
        "status_code": page.status,
        "html": page.text
    }

@app.post("/extract")
async def extract_data(request: ExtractRequest):
    """
    Fetches a web page, parses target CSS selectors, and returns clean structured JSON data.
    """
    page = await get_page(request.url, request.fetcher, request.timeout, request.proxy, request.cookies)
    
    extracted_data = {}
    for key, selector in request.selectors.items():
        try:
            # Check if selector specifies text extraction (e.g. ::text)
            # Scrapling css selectors support Scrapy-style ::text and ::attr(href)
            val = page.css(selector).getall()
            
            # If it's a single item list, unpack it for cleaner JSON
            if len(val) == 1:
                extracted_data[key] = val[0]
            elif len(val) == 0:
                extracted_data[key] = None
            else:
                extracted_data[key] = val
        except Exception as sel_err:
            extracted_data[key] = f"Error evaluating selector: {str(sel_err)}"

    return {
        "url": request.url,
        "fetcher_used": request.fetcher,
        "status_code": page.status,
        "data": extracted_data
    }
