import json
import requests
from bs4 import BeautifulSoup

# URL is not meant to be changed, as this scraper is specifically for the Contexto answers page on YourDictionary
URL = "https://wordfinder.yourdictionary.com/contexto/"
OUTPUT_FILE = "contexto_answers.json"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ContextoScraper/1.0)"}


def scrape():
    response = requests.get(URL, headers=HEADERS, timeout=30)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")

    tables = soup.find_all("table", class_="answers")

    answers = {}
    for table in tables:
        for row in table.find_all("tr"):
            cells = row.find_all("td")
            if len(cells) != 3:
                continue
            game_id = cells[1].get_text(strip=True)
            answer = cells[2].get_text(strip=True)
            answers[game_id] = answer

    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        json.dump({"answers": answers}, out, indent=2)

    print(f"Saved {len(answers)} answers to {OUTPUT_FILE}")

if __name__ == "__main__":
    scrape()
