# Web Crawler with Optional Encryption

This Python project is designed to crawl web pages starting from a given URL and extract all internal links within the domain. Additionally, it offers an option to encrypt these links for privacy concerns.

---

## Dependencies:

- `requests`: For fetching web pages.

- `logging`: For keeping track of the crawling process.

- `criptography`: Used for encryption and decryption purposes.

- `bs4 (BeautifulSoup)`: For parsing HTML and extracting links.

- `config`: A custom module to manage configuration settings.

---

## Function Descriptions:

- `setup_logging()`: Set up logging with custom format and handlers.

- `generate_key`: Generate a new encryption key.

- `encrypt_link(key, link)`: Encrypt a link using a provided key.

- `decrypt_link(key, encrypted_link)`: Decrypt an encrypted link to its original form using the provided key.

- `write_links_to_file(key, links, output_filename)`: Save links to a specified file. If encryption is enabled, the links will be saved in encrypted form.

- `extract_links_from_html(content)`: Extract all links from an HTML content.

- `get_base_url(content)`: Retrieve the base URL from an HTML content if available.

- `crawl_and_extract_links(start_url, limit_domain, key)`: Crawl web pages starting from the provided URL, extracting and optionally encrypting links. It ensures not to crawl external links and to avoid revisiting links.

- `main(start_url, key)`: The main function that orchestrates the crawling process. It sets up logging, defines the domain limit, starts the crawling process, and then writes the links to the file.

---

## Usage:

1. Ensure that you have all the required dependencies installed.
2. Update the `config` module with your preferred settings.
    - `START_URL`: The starting URL for the crawl.
    - `BOOL_ENCRYPT`: A boolean value indicating whether to encrypt the links (`True` for encryption, `False` otherwise).
    - `PATH_OUTPUT_FILE`: Path to save the extracted links.
    - `PATH_LOG_FILE`: Path to save the log.
    - `PATH_KEY_ENCRYPTION`: Path to save the generated encryption key (if encryption is enabled).
3. Run the script: 
```python main.py```

---

## Note:

- If encryption is enabled, an encryption key will be generated and saved to the specified path in the `config` module. This key is crucial for decrypting the links back to their original form.

- Logs will provide information about the crawling process, including the number of links extracted from each page and any potencial error or issues faced during the crawl.

- Always make sure to keep the generated key safe and secure, as losing it will render the encrypted links unreadable.

---

## Potencial Enhancements:

1. Implemente multi-threading to speed up the crawling process.
2. Integrate proxy supoort to bypass rate limit or IP bans.
3. Implement a database storage option for scalability and more advanced querying capabilities.
