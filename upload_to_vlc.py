import os
import sys
import json
import time
import requests

sys.stdout.reconfigure(encoding='utf-8')

DEFAULT_MUSIC_DIR = r"D:\Music\milefx_top500"
VLC_URLS = ["http://10.52.255.193", "http://iphone.local"]

class ProgressFileWrapper:
    def __init__(self, filename, callback):
        self._file = open(filename, 'rb')
        self._total_size = os.path.getsize(filename)
        self._bytes_read = 0
        self._callback = callback

    def read(self, size=-1):
        data = self._file.read(size)
        self._bytes_read += len(data)
        if self._callback:
            self._callback(self._bytes_read, self._total_size)
        return data

    def close(self):
        self._file.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

def find_working_vlc_url(candidates):
    for base in candidates:
        url = base.rstrip('/')
        try:
            r = requests.get(url, timeout=3)
            if r.status_code == 200:
                print(f"[+] Successfully connected to VLC at {url}")
                return url
        except Exception:
            pass
    return None

def format_size(bytes_val):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_val < 1024.0:
            return f"{bytes_val:.1f} {unit}"
        bytes_val /= 1024.0
    return f"{bytes_val:.1f} TB"

def upload_all(music_dir=DEFAULT_MUSIC_DIR, vlc_url=None):
    if not vlc_url:
        vlc_url = find_working_vlc_url(VLC_URLS)
        if not vlc_url:
            print("[-] Could not reach VLC on either http://10.52.255.193 or http://iphone.local.")
            print("[-] Please ensure VLC is active on your iPhone with 'Sharing via Wi-Fi' enabled.")
            return False

    upload_endpoint = f"{vlc_url.rstrip('/')}/upload.json"

    audio_extensions = ['.m4a', '.mp3', '.webm', '.opus', '.flac', '.wav', '.aac']
    files_to_upload = []
    for root, _, files in os.walk(music_dir):
        for f in sorted(files):
            ext = os.path.splitext(f)[1].lower()
            if ext in audio_extensions:
                files_to_upload.append(os.path.join(root, f))

    if not files_to_upload:
        print(f"[-] No audio files found in {music_dir}")
        return False

    print(f"\n[*] Found {len(files_to_upload)} songs ready for transfer.")
    print(f"[*] Target Device: {vlc_url}")
    print("=" * 60)

    failed_files = []
    for idx, filepath in enumerate(files_to_upload, 1):
        filename = os.path.basename(filepath)
        size_str = format_size(os.path.getsize(filepath))
        print(f"\n[{idx}/{len(files_to_upload)}] {filename} ({size_str})")

        def progress_callback(bytes_read, total_size):
            pct = (bytes_read / total_size) * 100 if total_size > 0 else 0
            bar_len = 25
            filled = int(bar_len * bytes_read // total_size) if total_size > 0 else 0
            bar = '=' * filled + '-' * (bar_len - filled)
            print(f"\r  Upload: [{bar}] {pct:5.1f}% | {format_size(bytes_read)}/{format_size(total_size)}", end="", flush=True)

        try:
            wrapped = ProgressFileWrapper(filepath, progress_callback)
            resp = requests.post(
                upload_endpoint,
                files={'files[]': (filename, wrapped, 'audio/mp4')},
                timeout=120
            )
            wrapped.close()

            if resp.status_code in [200, 201, 204]:
                print(f"\n  [✓] Success")
            else:
                print(f"\n  [✗] Failed (Status: {resp.status_code})")
                failed_files.append(filepath)
        except Exception as e:
            print(f"\n  [!] Error: {e}")
            failed_files.append(filepath)

    print("\n" + "=" * 60)
    print(f"Upload Complete! {len(files_to_upload) - len(failed_files)}/{len(files_to_upload)} transferred successfully.")

    failed_log = os.path.join(music_dir, "failed_uploads.json")
    if failed_files:
        with open(failed_log, 'w', encoding='utf-8') as f:
            json.dump({'vlc_url': vlc_url, 'failed_files': failed_files}, f, indent=2)
        print(f"[!] {len(failed_files)} file(s) failed. Stored in {failed_log}")
    else:
        if os.path.exists(failed_log):
            os.remove(failed_log)
        print("[✓] All songs uploaded to iPhone VLC without errors!")

    return len(failed_files) == 0

if __name__ == "__main__":
    target_url = sys.argv[1] if len(sys.argv) > 1 else None
    upload_all(vlc_url=target_url)
