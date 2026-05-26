import asyncio
from scrapling.fetchers import AsyncStealthySession

async def main():
    url = "https://meli.la/2N1eLiq"
    print(f"Fetching {url} via AsyncStealthySession...")
    async with AsyncStealthySession(headless=True) as session:
        page = await session.fetch(url)
        print("Final URL:", page.url)
        
        # Check page title
        title = page.css("title::text").get()
        print("Page Title:", title)
        
        # Try extracting h1 title
        h1 = page.css("h1::text").getall()
        print("All H1 tags:", h1)
        
        # Try extracting prices
        prices = page.css(".andes-money-amount__fraction::text").getall()
        print("All prices found:", prices[:10])
        
        # Let's inspect meta tags
        meta_title = page.css('meta[property="og:title"]::attr(content)').get()
        print("Meta OG Title:", meta_title)

if __name__ == "__main__":
    asyncio.run(main())
