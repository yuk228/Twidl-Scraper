import requests
import re
from bs4 import BeautifulSoup
from colorama import Fore
from concurrent.futures import ThreadPoolExecutor

class TwidlScraper:
    def __init__(self, max_workers: int, amount: int):
        self.max_workers = max_workers
        self.amount = amount

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
    
if __name__ == "__main__":
    TwidlScraper = TwidlScraper(max_workers=50, amount=33)
    TwidlScraper.run()