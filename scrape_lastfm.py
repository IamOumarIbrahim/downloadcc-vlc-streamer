import os
import sys
import time
import json
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

sys.stdout.reconfigure(encoding='utf-8')

OUTPUT_DIR = r"D:\Music\milefx_top500"
TRACKLIST_FILE = os.path.join(OUTPUT_DIR, "tracklist.json")
TOTAL_PAGES = 10  # 10 pages * 50 = 500 tracks

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load existing progress if any
existing_tracks = []
if os.path.exists(TRACKLIST_FILE):
    try:
        with open(TRACKLIST_FILE, 'r', encoding='utf-8') as f:
            existing_tracks = json.load(f)
            print(f"Loaded {len(existing_tracks)} existing tracks from {TRACKLIST_FILE}")
    except Exception:
        existing_tracks = []

if len(existing_tracks) >= 500:
    print("Already have 500 tracks!")
    sys.exit(0)

options = Options()
options.add_argument('--headless=new')
options.add_argument('--disable-gpu')
options.add_argument('--no-sandbox')
options.add_argument('--window-size=1920,1080')
options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36')

driver = webdriver.Chrome(options=options)

all_tracks = []
# Map existing tracks by rank
tracks_by_rank = {t['rank']: t for t in existing_tracks}

try:
    for page in range(1, TOTAL_PAGES + 1):
        # Check if we already have all 50 ranks for this page
        expected_ranks = list(range((page - 1) * 50 + 1, page * 50 + 1))
        if all(r in tracks_by_rank for r in expected_ranks):
            print(f"Page {page}/10 already cached. Skipping.")
            continue

        url = f"https://www.last.fm/user/milefx/library/tracks?page={page}"
        print(f"Fetching page {page}/{TOTAL_PAGES} from {url}...")

        success = False
        for attempt in range(1, 6):
            driver.get(url)
            time.sleep(3 + attempt)
            
            title = driver.title
            if "Temporarily Unavailable" in title or "Challenge" in title or "503" in title:
                print(f"  [Attempt {attempt}/5] Received '{title}', waiting before retrying...")
                time.sleep(4 * attempt)
                continue

            soup = BeautifulSoup(driver.page_source, 'html.parser')
            rows = soup.find_all('tr', class_='chartlist-row')

            if len(rows) > 0:
                print(f"  Page {page}: Successfully extracted {len(rows)} tracks.")
                for idx, r in enumerate(rows, 1):
                    name_td = r.find('td', class_='chartlist-name')
                    artist_td = r.find('td', class_='chartlist-artist')
                    index_td = r.find('td', class_='chartlist-index')

                    title_str = name_td.find('a').get_text(strip=True) if name_td and name_td.find('a') else ''
                    artist_str = artist_td.find('a').get_text(strip=True) if artist_td and artist_td.find('a') else ''
                    
                    try:
                        rank_num = int(index_td.get_text(strip=True)) if index_td else (page - 1) * 50 + idx
                    except Exception:
                        rank_num = (page - 1) * 50 + idx

                    tracks_by_rank[rank_num] = {
                        "rank": rank_num,
                        "artist": artist_str,
                        "title": title_str,
                        "page": page
                    }
                success = True
                break
            else:
                print(f"  [Attempt {attempt}/5] 0 rows found. Retrying in {3 * attempt}s...")
                time.sleep(3 * attempt)

        if not success:
            print(f"Failed to fetch page {page} after 5 attempts!")

        # Periodically save progress
        sorted_tracks = [tracks_by_rank[r] for r in sorted(tracks_by_rank.keys())]
        with open(TRACKLIST_FILE, 'w', encoding='utf-8') as f:
            json.dump(sorted_tracks, f, indent=2, ensure_ascii=False)

finally:
    driver.quit()

sorted_tracks = [tracks_by_rank[r] for r in sorted(tracks_by_rank.keys())]
with open(TRACKLIST_FILE, 'w', encoding='utf-8') as f:
    json.dump(sorted_tracks, f, indent=2, ensure_ascii=False)

print(f"\nCompleted! Total tracks saved: {len(sorted_tracks)} in {TRACKLIST_FILE}")
