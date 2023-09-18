import os
import logging
from collections import deque
from typing import Set, List, Optional
from urllib.parse import urljoin, urlparse
from contextlib import contextmanager

import requests
from bs4 import BeautifulSoup
from cryptography.fernet import Fernet


class LinkCrawler:
    """
        A web crawler to extract links from web pages and optionally encrypt them.
    """
    def __init__(
            self, 
            start_url: str, 
            output_file: str,
            log_file: str,
            key: Optional[bytes] = None,
            is_batch: bool = False
        ):
        self.start_url = start_url
        self.domain = urlparse(start_url).netloc
        self.output_file = output_file
        self.log_file = log_file
        self.key = key
        self.visited_links = set()
        self.cipher = Fernet(self.key) if self.key else None
        self.is_batch = is_batch
    
    @staticmethod
    def ensure_directory_exists(directory: str) -> None:
        os.makedirs(directory, exist_ok=True)
        print(f'Directory {directory} ensured to exist.')

    @staticmethod
    def create_project_structure(
        key_file: str,
        output_file: str,
        log_file: str
    ) -> None:
        directories = [key_file, output_file, log_file]

        for directory in directories:
            LinkCrawler.ensure_directory_exists(directory)
    
    def _setup_logging(self, log_level=logging.INFO) -> None:
        log_format = "%(asctime)s - %(levelname)s - %(message)s"
        logging.basicConfig(
            level=log_level,
            format=log_format,
            handlers=[
                logging.FileHandler(self.log_file),
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
        if not self.cipher:
            return link
        
        encrypted_text = self.cipher.encrypt(link.encode())
        return encrypted_text.decode('utf-8')

    def _decrypt_link(self, encrypted_link: str) -> str:
        """
            Decrypt a link using a given key.
        """
        decrypted_text = self.cipher.decrypt(encrypted_link.encode())
        return decrypted_text.decode('utf-8')

    def _write_links_to_file(self, links: Set[str], mode: str='w') -> None:
        with open(self.output_file, mode, encoding='utf-8') as file:
            file.write('\n'.join(map(self._encrypt_link, links)) + '\n')
    
    def _extract_links_from_html(self, content: bytes) -> List[str]:
        soup = BeautifulSoup(content, 'html.parser')
        return [a['href'] for a in soup.find_all('a', href=True)]

    def _get_base_url(self, content: bytes) -> Optional[str]:
        soup = BeautifulSoup(content, 'html.parser')
        base_tag = soup.find('base')
        return base_tag['href'] if base_tag and base_tag.has_attr('href') else None

    def _safe_urljoin(self, base: str, url: str) -> Optional[str]:
        """
            Safely join a base URL with a provided URL and handle exceptions.
        """
        try:
            return urljoin(base, url)
        except ValueError:
            logging.warning(f"Invalid URL encountered: {url}")
            return None
    
    def crawl_and_extract_links(self) -> Set[str]:
        to_visit = deque([self.start_url])

        while to_visit:
            url = to_visit.popleft()

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
                
                except (requests.RequestException, ValueError) as e:
                    logging.error(f"Failed to retrieve/process {url} - Error: {str(e)}")
            
        return self.visited_links
    
    def run(self) -> None:
        self._setup_logging()
        all_links = self.crawl_and_extract_links()
        write_mode = 'a' if self.is_batch else 'w'
        self._write_links_to_file(all_links, write_mode)
