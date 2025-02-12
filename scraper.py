import streamlit as st
import requests
from bs4 import BeautifulSoup
import csv
from io import StringIO

def fetch_sitemap_urls(sitemap_url):
    """Fetches and parses the sitemap to extract URLs using lxml-xml."""
    try:
        response = requests.get(sitemap_url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Use lxml-xml parser for proper XML parsing
        soup = BeautifulSoup(response.content, "lxml-xml") 
        urls = [loc.text for loc in soup.find_all("loc")]
        return urls
    except requests.RequestException as e:
        st.error(f"Error fetching sitemap: {e}")
        return []

def scrape_page_content(url):
    """Fetches and extracts text content from a page."""
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        # Extract visible text from the page
        page_content = soup.get_text(separator="\n", strip=True)
        return page_content
    except requests.RequestException as e:
        st.warning(f"Failed to fetch {url}: {e}")
        return None

st.title("Sitemap Scraper")

# Get the sitemap URL from the user
sitemap_url = st.text_input(
    "Enter your sitemap URL:",
    value="https://www.freshclinics.com/sitemap.xml",
    help="Enter a valid XML sitemap URL."
)

# When the user clicks the 'Scrape' button
if st.button("Scrape"):
    st.info("Scraping in progress...")
    
    # Fetch all URLs from the sitemap
    urls = fetch_sitemap_urls(sitemap_url)
    if not urls:
        st.stop()  # Stop execution if no URLs are found
    
    # Scrape each URL for text content
    scraped_data = []
    for i, url in enumerate(urls, start=1):
        st.write(f"Scraping ({i}/{len(urls)}): {url}")
        content = scrape_page_content(url)
        if content:
            scraped_data.append([url, content])
    
    # Build the CSV in memory
    csv_buffer = StringIO()
    writer = csv.writer(csv_buffer)
    writer.writerow(["URL", "Content"])  # Header row
    writer.writerows(scraped_data)
    csv_data = csv_buffer.getvalue()
    
    st.success("Scraping completed!")

    # Provide a download button for the CSV
    st.download_button(
        label="Download CSV",
        data=csv_data,
        file_name="scraped_data.csv",
        mime="text/csv",
    )