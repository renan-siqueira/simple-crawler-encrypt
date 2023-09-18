import os
import argparse

from src.crawler import LinkCrawler
from src.page_downloader import PageDownloader
from src.utils import generate_key
import config


def main(start_url: str, is_batch: bool):
    LinkCrawler.create_project_structure(
        os.path.dirname(config.PATH_KEY_ENCRYPTION),
        os.path.dirname(config.PATH_OUTPUT_FILE),
        os.path.dirname(config.PATH_LOG_FILE)
    )

    key = generate_key(config.BOOL_ENCRYPT, config.PATH_KEY_ENCRYPTION)

    output_path = config.PATH_OUTPUT_FILE_BATCH if is_batch else config.PATH_OUTPUT_FILE

    crawler = LinkCrawler(
        start_url, 
        output_path, 
        config.PATH_LOG_FILE,
        key,
        is_batch=is_batch
    )
    
    crawler.run()

    page_downloader = PageDownloader(
        output_path, config.PATH_HTML_FILES
    )

    page_downloader.run()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="LinkCrawler entry point.")
    parser.add_argument('--url', help="Starting URL for crawling.", default=config.START_URL)    
    parser.add_argument('--batch', help="Indicate if it's a batch processing.", action='store_true')

    args = parser.parse_args()

    main(args.url, args.batch)
