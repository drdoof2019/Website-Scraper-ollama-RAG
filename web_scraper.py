import requests
from bs4 import BeautifulSoup
import markdown
import json
from urllib.parse import urljoin, urlparse
import os
import urllib3
import warnings
import html

# Disable SSL warnings if verify=False is used
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class WebScraper:
    def __init__(self, verify_ssl=False):  # Default to False for problematic certificates
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.session.verify = verify_ssl
        self.current_url = None  # Store current URL for making relative URLs absolute

    def _get_soup(self, url):
        """Get BeautifulSoup object from URL"""
        try:
            response = self.session.get(url)
            response.raise_for_status()
            # Detect and use the correct encoding
            if response.encoding is None or response.encoding == 'ISO-8859-1':
                # Try to detect encoding from content
                response.encoding = response.apparent_encoding
            return BeautifulSoup(response.content, 'html.parser', from_encoding=response.encoding)
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def _fix_text(self, text):
        """Fix text encoding issues and HTML entities"""
        if text:
            # Unescape HTML entities
            text = html.unescape(text)
            return text
        return ""

    def _extract_content(self, soup):
        """Extract main content from soup object"""
        if not soup:
            return ""

        # Remove unwanted elements
        for tag in soup(['script', 'style', 'iframe', 'nav', 'footer']):
            tag.decompose()
        
        # Try to find main content
        main_content = None
        possible_content_tags = soup.find_all(['article', 'main', 'div'], class_=lambda x: x and any(word in str(x).lower() for word in ['content', 'article', 'main', 'post', 'docs']))
        
        if possible_content_tags:
            main_content = possible_content_tags[0]
        else:
            main_content = soup.find('body')

        if not main_content:
            return ""

        # Convert to markdown
        content = ""
        for elem in main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'ol', 'li', 'a', 'img', 'pre', 'code']):
            if elem.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                content += '#' * int(elem.name[1]) + ' ' + self._fix_text(elem.get_text().strip()) + '\n\n'
            elif elem.name == 'p':
                content += self._fix_text(elem.get_text().strip()) + '\n\n'
            elif elem.name == 'a':
                href = elem.get("href", "")
                if href:
                    # Make relative URLs absolute
                    if not href.startswith(('http://', 'https://')):
                        href = urljoin(self.current_url, href)
                    content += f'[{self._fix_text(elem.get_text().strip())}]({href})\n'
                else:
                    content += self._fix_text(elem.get_text().strip()) + '\n'
            elif elem.name == 'img':
                src = elem.get("src", "")
                if src and not src.startswith(('http://', 'https://')):
                    src = urljoin(self.current_url, src)
                alt = self._fix_text(elem.get("alt", ""))
                content += f'![{alt}]({src})\n'
            elif elem.name in ['ul', 'ol']:
                for li in elem.find_all('li', recursive=False):
                    content += f"* {self._fix_text(li.get_text().strip())}\n"
                content += '\n'
            elif elem.name in ['pre', 'code']:
                code_content = elem.get_text().strip()
                if code_content:
                    content += f'```\n{code_content}\n```\n\n'

        return content.strip()

    def scrape_single_url(self, url):
        """Scrape single URL and return content in markdown format"""
        self.current_url = url  # Store current URL for making relative URLs absolute
        soup = self._get_soup(url)
        if not soup:
            return None

        title = self._fix_text(soup.title.string if soup.title else url)
        content = self._extract_content(soup)
        
        result = {
            'url': url,
            'title': title,
            'content': content
        }
        
        return result

    def scrape_urls_from_file(self, file_path):
        """Scrape multiple URLs from a text file"""
        results = []
        failed_urls = []
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
            
            total = len(urls)
            print(f"\nProcessing {total} URLs...")
            
            for i, url in enumerate(urls, 1):
                try:
                    print(f"\nURL {i}/{total}: {url}")
                    result = self.scrape_single_url(url)
                    if result:
                        results.append(result)
                        print("Successfully processed.")
                    else:
                        failed_urls.append(url)
                        print("Failed to process content.")
                except Exception as e:
                    failed_urls.append(url)
                    print(f"Error processing URL: {str(e)}")
                    continue  # Continue with next URL
                    
        except FileNotFoundError:
            print(f"File not found: {file_path}")
        except Exception as e:
            print(f"Error reading file: {e}")
        
        # Print summary
        if failed_urls:
            print(f"\nFailed to process {len(failed_urls)} URLs:")
            for url in failed_urls:
                print(f"- {url}")
        
        print(f"\nSuccessfully processed {len(results)}/{total} URLs.")
        return results

    def find_urls_in_page(self, url):
        """Find all URLs in a given webpage that belong to the same domain"""
        self.current_url = url
        soup = self._get_soup(url)
        if not soup:
            return []

        # Extract base domain from the input URL
        base_domain = urlparse(url).netloc
        if base_domain.startswith('www.'):
            base_domain = base_domain[4:]

        urls = set()
        for link in soup.find_all('a'):
            href = link.get('href')
            if href:
                # Make relative URLs absolute
                if not href.startswith(('http://', 'https://')):
                    href = urljoin(url, href)
                
                # Check if URL belongs to the same domain
                parsed_href = urlparse(href)
                href_domain = parsed_href.netloc
                if href_domain.startswith('www.'):
                    href_domain = href_domain[4:]
                
                if href_domain == base_domain:
                    urls.add(href)

        return sorted(list(urls))

    def save_urls_to_file(self, urls, output_file):
        """Save found URLs to a text file"""
        try:
            # Only create directory if output_file has a directory part
            directory = os.path.dirname(output_file)
            if directory:
                os.makedirs(directory, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                for url in urls:
                    f.write(url + '\n')
            return True
        except Exception as e:
            print(f"Error saving URLs to file: {e}")
            return False

    def save_markdown(self, result, output_dir):
        """Save scraped content as markdown file"""
        try:
            if not result:
                return None

            os.makedirs(output_dir, exist_ok=True)
            
            # Create a safe filename from the title
            safe_title = "".join(c for c in result['title'] if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_title = safe_title[:50]  # Limit filename length
            
            output_file = os.path.join(output_dir, f"{safe_title}.md")
            
            with open(output_file, 'w', encoding='utf-8') as f:
                # Write metadata
                f.write(f"# {result['title']}\n\n")
                f.write(f"Source: {result['url']}\n\n")
                f.write("---\n\n")
                # Write content
                f.write(result['content'])
            
            return output_file
        except Exception as e:
            print(f"Error saving markdown: {e}")
            return None
