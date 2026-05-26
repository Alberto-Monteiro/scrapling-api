# 🕷️ Scrapling API Microservice (Docker & FastAPI)

🌐 **[English](README.md) | [Português](README.pt.md)**

This repository contains a production-ready, **high-performance Web Scraping Microservice** built on top of the **FastAPI** framework and the **Scrapling** library. 

It is specifically designed to be consumed by other programming languages (such as **Java**, C#, Node.js, etc.) running isolated inside Docker with all headless browsers and anti-bot evasions pre-configured.

---

## 🚀 How to Start the Service

To build and spin up the service in the background (daemon mode) on your local machine or server:

```bash
docker compose up --build -d
```

The service will immediately be available on port **`8000`** (`http://localhost:8000`).

---

## 🌐 Available Endpoints

The API exposes two primary POST endpoints:

### 1. `POST /fetch` (Get Rendered HTML)
Downloads and renders the complete target web page, returning the raw HTML string. Best suited if you already have a HTML parsing library on your client side (like **Jsoup** in Java).

* **Example Payload:**
```json
{
    "url": "https://quotes.toscrape.com/js/",
    "fetcher": "stealthy"
}
```

* **Response:**
```json
{
    "url": "https://quotes.toscrape.com/js/",
    "fetcher_used": "stealthy",
    "status_code": 200,
    "html": "<html>...</html>"
}
```

---

### 2. `POST /extract` (Get Structured Data in JSON)
Performs fetching and parses the target data from the HTML directly inside the microservice, returning a clean JSON containing only the requested fields.

* **Example Payload:**
```json
{
    "url": "https://quotes.toscrape.com/",
    "fetcher": "static",
    "selectors": {
        "title": "h1 a::text",
        "first_quote": ".quote .text::text"
    }
}
```

* **Response:**
```json
{
    "url": "https://quotes.toscrape.com/",
    "fetcher_used": "static",
    "status_code": 200,
    "data": {
        "title": "Quotes to Scrape",
        "first_quote": "“The world as we have created it is a process of our thinking...”"
    }
}
```

---

## 🛠️ Payload Parameters

Both endpoints accept the following optional configuration parameters:

| Field | Type | Default | Description |
| :--- | :--- | :--- | :--- |
| **`url`** | *String* | *(Required)* | The URL of the target website you wish to scrape. |
| **`fetcher`** | *String* | `"stealthy"` | Scraper engine: `"static"` (fast HTTP), `"dynamic"` (JS Browser), or `"stealthy"` (anti-bot browser). |
| **`timeout`** | *Integer* | `30000` | Maximum timeout in milliseconds. |
| **`proxy`** | *String* | `null` | Proxy connection URL (e.g. `http://user:password@p.webshare.io:80`). |
| **`cookies`** | *String/Object*| `null` | Cookie string copied from your browser to bypass logins/auth. |
| **`selectors`** | *Object* | *(Only /extract)* | Dictionary containing keys and their CSS/XPath selectors. |

---

## 🎯 Advanced Selector Syntaxes (Scrapling)

To extract specific data from HTML tags accurately inside the `"selectors"` parameter:

* **Extract the text inside a tag:** Append `::text` to the selector.
  * *Example:* `"title": "h1::text"` ➔ Returns `"Example Title"`
* **Extract a link's URL (`href`):** Append `::attr(href)` to the selector.
  * *Example:* `"product_link": ".product_pod h3 a::attr(href)"` ➔ Returns `"catalogue/..."`
* **Extract an image URL (`src`):** Append `::attr(src)` to the selector.
  * *Example:* `"image_url": "img.thumbnail::attr(src)"`
* **Extract meta tag content (SEO fields):**
  * *Example:* `"price": "meta[property=\"product:price:amount\"]::attr(content)"`

---

## 🥷 Advanced Practical Examples

### A. Dynamic & JS-Heavy Scraping (JS Quotes Sandbox)
To scrape elements that fully rely on JavaScript execution on the page using the `"fetcher": "dynamic"` or `"stealthy"` mode:

```bash
curl --location 'http://localhost:8000/extract' \
--header 'Content-Type: application/json' \
--data '{
    "url": "https://quotes.toscrape.com/js/",
    "fetcher": "dynamic",
    "selectors": {
        "quotes": ".quote .text::text",
        "authors": ".quote .author::text"
    }
}'
```

### B. Scraping Lists, Links and Image Sources (Bookstore Sandbox)
A complete example extracting product titles, visual prices, detail page URLs, and cover image links from a grid list statically:

```bash
curl --location 'http://localhost:8000/extract' \
--header 'Content-Type: application/json' \
--data '{
    "url": "https://books.toscrape.com/",
    "fetcher": "static",
    "selectors": {
        "book_titles": ".product_pod h3 a::text",
        "detail_links": ".product_pod h3 a::attr(href)",
        "cover_images": ".product_pod .image_container img::attr(src)",
        "prices": ".product_pod .price_color::text"
    }
}'
```

### C. Advanced Scraping with Combined Proxy & Cookies
When you need to scrape a complex page that requires an active logged-in session while maintaining IP reputation to prevent blocks:

```bash
curl --location 'http://localhost:8000/extract' \
--header 'Content-Type: application/json' \
--data '{
    "url": "https://httpbin.org/anything",
    "fetcher": "stealthy",
    "proxy": "http://your_user:your_password@p.webshare.io:80",
    "cookies": "session_id=12345abcde; user_token=98765qwerty; authenticated=true",
    "selectors": {
        "outgoing_ip": "json::attr(origin)",
        "received_cookies": "json::attr(headers.Cookie)"
    }
}'
```
> [!NOTE]
> In the example above, we use the `httpbin.org/anything` endpoint which acts as a request mirror, returning the exact proxy IP used for the download and confirming that the cookies were successfully injected into the browser/HTTP headers.

---

## ☕ Java Integration Example (Java 11+)

Sample utility class in Java to hit the API and retrieve the fully rendered HTML:

```java
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;

public class ScraplingClient {
    public static String fetchPageHtml(String targetUrl) throws Exception {
        HttpClient client = HttpClient.newHttpClient();
        
        String jsonPayload = String.format("""
            {
                "url": "%s",
                "fetcher": "stealthy"
            }
            """, targetUrl);

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create("http://localhost:8000/fetch"))
                .header("Content-Type", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(jsonPayload))
                .build();

        HttpResponse<String> response = client.send(request, HttpResponse.BodyHandlers.ofString());
        return response.body(); // Returns the JSON with the rendered HTML in "html" field
    }
}
```
