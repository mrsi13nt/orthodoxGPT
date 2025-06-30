#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# WEB CRAWLER - ST-TAKLA.ORG ARCHIVE
# Extracts all text content from the website and saves to single file

import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
import time
import os

# ===== CONFIGURATION ===== #
BASE_URL = "https://st-takla.org/P-1_.html"
OUTPUT_FILE = "st-takla_archive.txt"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
REQUEST_DELAY = 1  # Seconds between requests
# ========================= #

class SiteCrawler:
    def __init__(self):
        self.visited = set()
        self.to_visit = set([BASE_URL])
        self.content = []
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": USER_AGENT})
        
    def is_valid_url(self, url):
        """Check if URL belongs to target domain and is HTML page"""
        return (
            url.startswith("https://st-takla.org/") and 
            not url.endswith(('.jpg', '.png', '.pdf', '.doc', '.zip')) and
            '/Full-Free-Coptic-Books/' not in url
        )
    
    def extract_content(self, soup):
        """Extract main textual content from page"""
        # Remove unnecessary elements
        for element in soup(["script", "style", "header", "footer", "nav", "aside"]):
            element.decompose()
        
        # Focus on main content areas
        content_areas = soup.find_all(['div', 'section', 'article', 'main'])
        text_blocks = []
        
        for area in content_areas:
            # Skip non-content containers
            if not area.find(['p', 'h1', 'h2', 'h3', 'li']):
                continue
                
            # Clean and extract text
            text = area.get_text(separator='\n', strip=True)
            if len(text.split()) > 20:  # Only keep substantial content
                text_blocks.append(text)
        
        return "\n\n".join(text_blocks)
    
    def find_links(self, soup, base):
        """Extract all valid links from page"""
        for link in soup.find_all('a', href=True):
            url = urljoin(base, link['href'])
            if self.is_valid_url(url) and url not in self.visited:
                self.to_visit.add(url)
    
    def crawl_page(self, url):
        """Process single page"""
        try:
            print(f"[*] Crawling: {url}")
            response = self.session.get(url, timeout=15)
            response.encoding = 'utf-8'
            
            if response.status_code != 200:
                print(f"[!] Failed: HTTP {response.status_code}")
                return
                
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract and save content
            content = self.extract_content(soup)
            if content:
                self.content.append(f"\n\n{'='*80}\nURL: {url}\n{'='*80}\n\n")
                self.content.append(content)
            
            # Find new links
            self.find_links(soup, url)
            
        except Exception as e:
            print(f"[!] Error on {url}: {str(e)}")
        finally:
            self.visited.add(url)
    
    def save_content(self):
        """Save all extracted content to file"""
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            f.write("\n".join(self.content))
        print(f"\n[+] Saved {len(self.content)//2} pages to {OUTPUT_FILE}")
        print(f"[+] Total size: {os.path.getsize(OUTPUT_FILE)//1024} KB")
    
    def run(self):
        """Main crawling execution"""
        print(f"[*] Starting crawl from {BASE_URL}")
        print("[*] This may take several minutes...\n")
        
        while self.to_visit:
            url = self.to_visit.pop()
            if url not in self.visited:
                self.crawl_page(url)
                time.sleep(REQUEST_DELAY)
        
        self.save_content()

if __name__ == "__main__":
    print(r"""
      ____          _      __  __       _    _           _   
     / ___|___   __| | ___|  \/  | __ _| | _| |__   __ _| |_ 
    | |   / _ \ / _` |/ _ \ |\/| |/ _` | |/ / '_ \ / _` | __|
    | |__| (_) | (_| |  __/ |  | | (_| |   <| |_) | (_| | |_ 
     \____\___/ \__,_|\___|_|  |_|\__,_|_|\_\_.__/ \__,_|\__|
    """)
    
    crawler = SiteCrawler()
    crawler.run()