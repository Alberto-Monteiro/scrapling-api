import time
from scrapling.fetchers import Fetcher, StealthyFetcher

def test_static_scraping():
    print("\n--- 1. Testing Static Scraping (Fetcher) ---")
    url = "https://quotes.toscrape.com/"
    print(f"Fetching static page: {url}")
    
    # Fetch a static web page
    page = Fetcher.fetch(url)
    
    # Extract quotes and authors
    quotes = page.css('.quote')
    print(f"Found {len(quotes)} quotes!")
    
    for i, quote in enumerate(quotes[:3], 1):
        text = quote.css('.text::text').get()
        author = quote.css('.author::text').get()
        print(f"  {i}. \"{text}\" - By {author}")

def test_dynamic_scraping():
    print("\n--- 2. Testing Dynamic Scraping (StealthyFetcher with Playwright) ---")
    url = "https://quotes.toscrape.com/js/"
    print(f"Fetching JS-rendered page: {url}")
    
    # StealthyFetcher handles dynamic rendering and anti-bot checks under the hood
    # The official Scrapling Docker image has all necessary browsers installed!
    page = StealthyFetcher.fetch(url, headless=True, timeout=30000)
    
    quotes = page.css('.quote')
    print(f"Found {len(quotes)} dynamically rendered quotes!")
    
    for i, quote in enumerate(quotes[:3], 1):
        text = quote.css('.text::text').get()
        author = quote.css('.author::text').get()
        print(f"  {i}. \"{text}\" - By {author}")

def test_adaptive_scraping():
    print("\n--- 3. Testing Adaptive/Self-Healing Selectors ---")
    url = "https://quotes.toscrape.com/"
    print(f"Fetching page: {url} to demonstrate adaptive selector fingerprinting...")
    
    # Fetch and turn on auto-saving of elements' fingerprints 
    page = Fetcher.fetch(url)
    
    # By using `auto_save=True`, Scrapling automatically stores the elements' 
    # structural and semantic fingerprint in a local directory (`.scrapling_fingerprints/` by default).
    # Next time, if the CSS path changes, it can still recover it using the fingerprint!
    title_element = page.css('h1 a::text', auto_save=True).get()
    print(f"Successfully bookmarked and extracted title: '{title_element}'")
    print("Fingerprint saved. If the website structural details change in the future,")
    print("Scrapling can locate it adaptively when calling page.css(..., adaptive=True)!")

if __name__ == "__main__":
    print("=========================================")
    print("      SCRAPLING DOCKER PLAYGROUND        ")
    print("=========================================")
    
    start_time = time.time()
    
    try:
        # Test basic static HTTP scraper
        test_static_scraping()
        
        # Test headless browser rendering
        test_dynamic_scraping()
        
        # Test the unique adaptive scraping feature
        test_adaptive_scraping()
        
        print("\n=========================================")
        print(f"Success! All tests completed in {time.time() - start_time:.2f}s!")
        print("=========================================")
    except Exception as e:
        print(f"\n[ERROR] An error occurred during scraping tests: {e}")
        print("Please verify your internet connection or container resources.")
        print("=========================================")
