from bs4 import BeautifulSoup
import httpx
from typing import List, Dict, Any, Optional
from urllib.parse import urljoin, urlparse

class HTMLParser:
    """Parser for HTML content to extract links and other information"""
    
    def __init__(self):
        self.client = httpx.AsyncClient()
    
    async def fetch_url(self, url: str) -> Optional[str]:
        """Fetch HTML content from a URL"""
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.text
        except httpx.HTTPError as e:
            # Log the error
            print(f"Error fetching URL {url}: {e}")
            return None
    
    def parse_html(self, html_content: str) -> BeautifulSoup:
        """Parse HTML content into BeautifulSoup object"""
        return BeautifulSoup(html_content, 'lxml')
    
    def extract_links(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract all links from the parsed HTML"""
        links = []
        for a_tag in soup.find_all('a', href=True):
            link = {
                'url': a_tag['href'],
                'text': a_tag.get_text(strip=True),
                'title': a_tag.get('title', ''),
            }
            links.append(link)
        return links
    
    def extract_metadata(self, soup: BeautifulSoup) -> Dict[str, str]:
        """Extract metadata from the HTML"""
        metadata = {}
        
        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.get_text(strip=True)
        
        # Extract meta tags
        for meta in soup.find_all('meta'):
            name = meta.get('name', meta.get('property', ''))
            if name and meta.get('content'):
                metadata[name] = meta.get('content')
        
        return metadata
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
        
    def parse_links(self, html_content: str, base_url: str) -> List[Dict[str, Any]]:
        """Parse HTML content and extract links with base URL resolution"""
        soup = self.parse_html(html_content)
        links = self.extract_links(soup)
        
        # Process links to resolve relative URLs and add additional metadata
        processed_links = []
        base_domain = urlparse(base_url).netloc
        
        for link in links:
            # Resolve relative URLs
            absolute_url = urljoin(base_url, link['url'])
            link_domain = urlparse(absolute_url).netloc
            
            processed_link = {
                'url': absolute_url,
                'title': link.get('title', ''),
                'link_text': link.get('text', ''),
                'domain': link_domain,
                'is_external': link_domain != base_domain
            }
            processed_links.append(processed_link)
            
        return processed_links
        
    def extract_page_metadata(self, html_content: str) -> Dict[str, str]:
        """Extract metadata from the page such as title, description, etc."""
        soup = self.parse_html(html_content)
        metadata = {}
        
        # Extract title
        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.get_text(strip=True)
        else:
            metadata['title'] = ''
            
        # Extract description from meta tags
        description_tag = soup.find('meta', attrs={'name': 'description'}) or \
                          soup.find('meta', attrs={'property': 'og:description'})
        if description_tag and description_tag.get('content'):
            metadata['description'] = description_tag.get('content')
        else:
            metadata['description'] = ''
            
        # Extract keywords if available
        keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
        if keywords_tag and keywords_tag.get('content'):
            metadata['keywords'] = keywords_tag.get('content')
            
        # Extract canonical URL if available
        canonical_tag = soup.find('link', attrs={'rel': 'canonical'})
        if canonical_tag and canonical_tag.get('href'):
            metadata['canonical_url'] = canonical_tag.get('href')
            
        return metadata