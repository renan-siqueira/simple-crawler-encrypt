import requests
import logging
import config

from typing import Set, List, Optional, Union
from cryptography.fernet import Fernet
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup


def setup_logging() -> None:
    log_format = "%(asctime)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, 
                        format=log_format,
                        handlers=[
                            logging.FileHandler(config.PATH_LOG_FILE),
                            logging.StreamHandler()
                        ])
    

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


def encrypt_link(key: bytes, link: str) -> str:
    """
    Encrypt a link using a given key.
    """
    cipher_suite = Fernet(key)
    encrypted_text = cipher_suite.encrypt(link.encode())
    return encrypted_text.decode('utf-8')


def decrypt_link(key: bytes, encrypted_link: str) -> str:
    """
    Decrypt a link using a given key.
    """
    cipher_suite = Fernet(key)
    decrypted_text = cipher_suite.decrypt(encrypted_link.encode())
    return decrypted_text.decode('utf-8')


def write_links_to_file(key: bytes, links: List[str], output_filename: str) -> None:
    with open(output_filename, 'w', encoding='utf-8') as file:
        for link in links:
            encrypted_link = encrypt_link(key, link)
            file.write(encrypted_link + '\n')


def extract_links_from_html(content: bytes) -> List[str]:
    soup = BeautifulSoup(content, 'html.parser')
    links = [a['href'] for a in soup.find_all('a', href=True)]
    return links


def get_base_url(content: bytes) -> Optional[str]:
    soup = BeautifulSoup(content, 'html.parser')
    base_tag = soup.find('base')
    if base_tag and base_tag.has_attr('href'):
        return base_tag['href']
    return None


def safe_urljoin(base: str, url: str) -> Optional[str]:
    try:
        return urljoin(base, url)
    except ValueError:
        logging.warning(f"Invalid URL encountered: {url}")
        return None


def crawl_and_extract_links(start_url: str, limit_domain: str, key: bytes) -> Set[str]:
    visited_links = set()
    to_visit = [start_url]
    
    while to_visit:
        url = to_visit.pop()

        logged_url = encrypt_link(key, url) if config.BOOL_ENCRYPT and key else url
        logging.info(f"Accessing URL: {logged_url}")
        
        if url in visited_links:
            continue
        
        visited_links.add(url)
        
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            base_url = get_base_url(response.content) or url
            
            new_links = extract_links_from_html(response.content)

            new_links = [safe_urljoin(base_url, link) for link in new_links]
            new_links = [link for link in new_links if link]
            
            logging.info(f"Found {len(new_links)} new links from {logged_url}")
            
            new_links = [link for link in new_links if urlparse(link).netloc == limit_domain and link not in visited_links]

            to_visit.extend(new_links)
        
        except requests.RequestException:
            logging.error(f"Failed to retrieve {logged_url}")
    
    return visited_links


def main(start_url: str, key: Optional[bytes]) -> None:
    setup_logging()

    domain = requests.utils.urlparse(start_url).netloc
    all_links = crawl_and_extract_links(start_url, domain, key)

    write_links_to_file(key, all_links, config.PATH_OUTPUT_FILE)


if __name__ == '__main__':
    key = generate_key(config.BOOL_ENCRYPT)
    main(config.START_URL, key)
