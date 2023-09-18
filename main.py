import os
import requests
import logging
import config

from typing import Set, List, Optional
from cryptography.fernet import Fernet
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from contextlib import contextmanager


class LinkCrawler:
    def __init__(self, start_url: str, key: Optional[bytes] = None):
        self.start_url = start_url
        self.domain = urlparse(start_url).netloc
        self.key = key
        self.visited_links = set()

    @staticmethod
    def _setup_logging() -> None:
        log_format = "%(asctime)s - %(levelname)s - %(message)s"
        logging.basicConfig(
            level=logging.INFO,
            format=log_format,
            handlers=[
                logging.FileHandler(config.PATH_LOG_FILE),
                logging.StreamHandler()
            ]
        )
    
    @contextmanager
    def _encrypt_log_context(self, url: str):
        encrypted_url = self._encrypt_link(url) if self.key else url
        logging.info(f"Accessing URL: {encrypted_url}")
        yield

    def _encrypt_link(self, link: str) -> str:
        """
            Encrypt a link using a given key.
        """
        if not self.key:
            return link
        
        cipher_suite = Fernet(self.key)
        encrypted_text = cipher_suite.encrypt(link.encode())
        return encrypted_text.decode('utf-8')

    def _decrypt_link(self, encrypted_link: str) -> str:
        """
            Decrypt a link using a given key.
        """
        cipher_suite = Fernet(self.key)
        decrypted_text = cipher_suite.decrypt(encrypted_link.encode())
        return decrypted_text.decode('utf-8')

    def _write_links_to_file(self, links: Set[str]) -> None:
        with open(config.PATH_OUTPUT_FILE, 'w', encoding='utf-8') as file:
            for link in links:
                encrypted_link = self._encrypt_link(link)
                file.write(encrypted_link + '\n')
    
    def _extract_links_from_html(self, content: bytes) -> List[str]:
        soup = BeautifulSoup(content, 'html.parser')
        links = [a['href'] for a in soup.find_all('a', href=True)]
        return links


    def _get_base_url(self, content: bytes) -> Optional[str]:
        soup = BeautifulSoup(content, 'html.parser')
        base_tag = soup.find('base')
        if base_tag and base_tag.has_attr('href'):
            return base_tag['href']
        return None

    def _safe_urljoin(self, base: str, url: str) -> Optional[str]:
        try:
            return urljoin(base, url)
        except ValueError:
            logging.warning(f"Invalid URL encountered: {url}")
            return None
    
    def crawl_and_extract_links(self) -> Set[str]:
        to_visit = [self.start_url]

        while to_visit:
            url = to_visit.pop()

            if url in self.visited_links:
                continue

            with self._encrypt_log_context(url):
                try:
                    response = requests.get(url, timeout=10)
                    response.raise_for_status()

                    base_url = self._get_base_url(response.content) or url

                    new_links = self._extract_links_from_html(response.content)

                    sanitized_links = filter(None, map(lambda link: self._safe_urljoin(base_url, link), new_links))
                    relevant_links = {link for link in sanitized_links if urlparse(link).netloc == self.domain and link not in self.visited_links}

                    to_visit.extend(relevant_links)
                    self.visited_links.update(relevant_links)
                
                except requests.RequestException:
                    logging.error(f"Failed to retrieve {url}")
            
        return self.visited_links
    
    def run(self) -> None:
        self._setup_logging()
        all_links = self.crawl_and_extract_links()
        self._write_links_to_file(all_links)


def ensure_directory_exists(directory: str) -> None:
    os.makedirs(directory, exist_ok=True)
    print(f'Directory {directory} ensured to exist.')

def create_project_structure() -> None:
    directories = [
        os.path.dirname(config.PATH_KEY_ENCRYPTION),
        os.path.dirname(config.PATH_OUTPUT_FILE),
        os.path.dirname(config.PATH_LOG_FILE)
    ]

    for directory in directories:
        ensure_directory_exists(directory)

def generate_key(encrypt: bool) -> Optional[bytes]:
    """
        Generate a new encryption key.
    """
    if encrypt:
        key = Fernet.generate_key()        
        with open(config.PATH_KEY_ENCRYPTION, "wb") as key_file:
            key_file.write(key)

        return key
    else:
        return None


if __name__ == '__main__':
    create_project_structure()
    key = generate_key(config.BOOL_ENCRYPT)
    crawler = LinkCrawler(config.START_URL, key)
    crawler.run()
