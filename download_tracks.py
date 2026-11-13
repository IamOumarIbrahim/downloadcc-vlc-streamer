import os
import sys
import re
import json
import time
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.stdout.reconfigure(encoding='utf-8')

OUTPUT_DIR = r"D:\Music\milefx_top500"
TRACKLIST_FILE = os.path.join(OUTPUT_DIR, "tracklist.json")
MAX_WORKERS = 5

def sanitize_filename(name):
    # Remove characters not allowed in Windows filenames
    return re.sub(r'[\\/*?:"<>|]', '-', name).strip()

def download_track(track):
    rank = track['rank']
    artist = track['artist']
    title = track['title']

    clean_artist = sanitize_filename(artist)
    clean_title = sanitize_filename(title)
    base_name = f"{rank:03d} - {clean_artist} - {clean_title}"
    output_path = os.path.join(OUTPUT_DIR, f"{base_name}.m4a")

    # Check if already downloaded
    if os.path.exists(output_path) and os.path.getsize(output_path) > 100_000:
        return {"rank": rank, "status": "exists", "path": output_path, "artist": artist, "title": title}

    # Search and download using yt-dlp
    query = f"ytsearch1:{artist} - {title} audio"
    cmd = [
        "yt-dlp",
        "--no-playlist",
        "--default-search", "ytsearch",
        "-f", "ba[ext=m4a]/ba/b",
        "--add-metadata",
        "-o", output_path,
        query
    ]

    try:
        proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=90)
        if proc.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 50_000:
            return {"rank": rank, "status": "downloaded", "path": output_path, "artist": artist, "title": title}
        else:
            # Try fallback search without "audio" suffix if failed
            cmd_fallback = [
                "yt-dlp",
                "--no-playlist",
                "-f", "ba[ext=m4a]/ba/b",
                "-o", output_path,
                f"ytsearch1:{artist} - {title}"
            ]
            proc_fb = subprocess.run(cmd_fallback, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, timeout=90)
            if proc_fb.returncode == 0 and os.path.exists(output_path) and os.path.getsize(output_path) > 50_000:
                return {"rank": rank, "status": "downloaded", "path": output_path, "artist": artist, "title": title}
            return {"rank": rank, "status": "failed", "error": proc.stderr[-200:], "artist": artist, "title": title}
    except Exception as e:
        return {"rank": rank, "status": "error", "error": str(e), "artist": artist, "title": title}

def main():
    if not os.path.exists(TRACKLIST_FILE):
        print(f"Tracklist file not found: {TRACKLIST_FILE}")
        sys.exit(1)

    with open(TRACKLIST_FILE, 'r', encoding='utf-8') as f:
        tracks = json.load(f)

    print(f"Loaded {len(tracks)} tracks from {TRACKLIST_FILE}")
    print(f"Downloading to: {OUTPUT_DIR} (Concurrency: {MAX_WORKERS})\n")

    completed = 0
    downloaded = 0
    skipped = 0
    failed = []

    start_time = time.time()

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_track = {executor.submit(download_track, t): t for t in tracks}
        for future in as_completed(future_to_track):
            res = future.result()
            completed += 1
            rank = res['rank']
            artist = res['artist']
            title = res['title']

            if res['status'] == 'downloaded':
                downloaded += 1
                print(f"[{completed}/{len(tracks)}] [+] #{rank:03d} {artist} - {title} (Downloaded)")
            elif res['status'] == 'exists':
                skipped += 1
                print(f"[{completed}/{len(tracks)}] [=] #{rank:03d} {artist} - {title} (Already Exists)")
            else:
                failed.append(res)
                print(f"[{completed}/{len(tracks)}] [!] #{rank:03d} {artist} - {title} (FAILED)")

    elapsed = time.time() - start_time
    print(f"\n==========================================")
    print(f"Download Summary:")
    print(f"Total Processed: {completed}/{len(tracks)}")
    print(f"Downloaded     : {downloaded}")
    print(f"Already Existed: {skipped}")
    print(f"Failed         : {len(failed)}")
    print(f"Time Taken     : {elapsed:.1f}s")
    print(f"==========================================")

    if failed:
        failed_file = os.path.join(OUTPUT_DIR, "failed_downloads.json")
        with open(failed_file, 'w', encoding='utf-8') as f:
            json.dump(failed, f, indent=2)
        print(f"Failed tracks written to {failed_file}")

if __name__ == "__main__":
    main()
