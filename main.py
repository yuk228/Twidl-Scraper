import os
import re
import time
import requests
from tqdm import tqdm
from colorama import Fore
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor

class TwidlScraper:
    def __init__(self, max_workers: int, amount: int):
        self.max_workers = max_workers
        self.amount = amount

        with open("data/log.txt", "r", encoding="utf-8", errors="ignore") as file:
            self.links = file.readlines()

    def get_url(self, i: int):
        res = requests.get(f"https://www.twi-dl.net/hozon.php?p={i}")
        soup = BeautifulSoup(res.text, "html.parser")
        hrefs = [link.get("href") for link in soup.find_all('a') if link.get("href") is not None]
        for href in hrefs:
            if "video" in href:
                pattern = r'(/v\.php\?video=\d+)'
                match = re.search(pattern, href)
                self.get_video("https://www.twi-dl.net"+match.group(0))

    def get_video(self, link: str):
        res = requests.get(link)
        soup = BeautifulSoup(res.text, "html.parser")
        link = None
        for a in soup.find_all("a", href=True):
            if a["href"].startswith("https://video.twimg.com/ext_tw_video"):
                link = a["href"]
                break
        if link:
            with open("data/log.txt", "a", encoding="utf-8", errors="ignore") as f:
                f.write(link + "\n")
                print(Fore.GREEN+"[FOUND] "+Fore.RESET+f"{link.split('/')[-1]}")
        else:
            pass

    def run(self):
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            executor.map(self.get_url, range(self.amount))

    def download(self):
        for link in tqdm(self.links, desc="Downloading", unit="file"):
            link = link.strip() 
            
            if link: 
                try:
                    response = requests.get(link, stream=True) 
                    response.raise_for_status()
                    
                    filename = link.split('/')[-1]
                    
                    path = os.path.join("data/videos", filename)
                    with open(path, "wb") as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    tqdm.write(Fore.GREEN+"[Success] "+Fore.RESET+f"{filename}")
                except Exception as e:
                    tqdm.write(Fore.GREEN+"[Failed] "+Fore.RESET+f"{link}")
    
    def send(self, webhook: str, limit: float):
        with open("data/log.txt", "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
            try:
                for line in lines:
                    time.sleep(float(limit))
                    res = requests.post(webhook, json={"content": line}, headers={"Content-Type": "application/json"})
                    if res.status_code == 404:
                        print("webhook not found")
                        break
                    print(res.status_code)
                print("sent")
            except Exception as e:
                print(e)

if __name__ == "__main__":
    TwidlScraper = TwidlScraper(max_workers=50, amount=33)
    TwidlScraper.send(webhook="webhook here", limit=1.45)