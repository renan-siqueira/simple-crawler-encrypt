import os
import requests
import re


class PageDownloader:
    def __init__(self, links_file: str, destination_folder: str):
        self.links_file = links_file
        self.destination_folder = destination_folder
        self.start_index = self._get_last_downloaded_index()
    
    def _download_page(self, page_url: str, save_path: str) -> None:
        response = requests.get(page_url)
        response.raise_for_status()
        with open(save_path, 'w', encoding='utf-8') as file:
            file.write(response.text)
    
    def _get_last_downloaded_index(self) -> int:
        """
            Check the download directory and return the index of the last downloaded file.
        """
        files = [f for f in os.listdir(self.destination_folder) if f.endswith('.html')]

        if not files:
            return 1
        
        indices = [int(f.split('_')[1].split('.html')[0]) for f in files]
        return max(indices) + 1


    def run(self):
        os.makedirs(self.destination_folder, exist_ok=True)

        with open(self.links_file, 'r', encoding='utf-8') as file:
            links = [line.strip() for line in file if line.strip()]

        for idx, link in enumerate(links, self.start_index):
            file_name = os.path.join(self.destination_folder, f"page_{idx}.html")
            self._download_page(link, file_name)
