<div align="center">
  <h1>📺 downloadcc</h1>
  <p><strong>Terminal-based Media Downloader with Wireless VLC Transfer</strong></p>

  <p>
    <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.12+-blue.svg?style=flat-square&logo=python&logoColor=white" alt="Python" /></a>
    <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square" alt="License: MIT" /></a>
    <a href="https://libtorrent.org/"><img src="https://img.shields.io/badge/Engine-libtorrent-brightgreen.svg?style=flat-square" alt="libtorrent" /></a>
  </p>
</div>

<p align="center">
  <img src="assets/demo.gif" alt="downloadcc Live Demo" width="100%" />
</p>

> [!IMPORTANT]
> **Platform Requirement**: Requires local Wi-Fi connectivity to transfer downloaded files directly to VLC on iOS devices (iPad/iPhone).

```bash
# Quickstart — Search and download in 30 seconds
pip install requests beautifulsoup4 libtorrent pyinstaller
python downloadcc.py "Mr. Robot"
```

**The problem:** Manual torrenting for TV shows and movies requires navigating ad-heavy indexers, downloading files, converting video encodings for iOS, and manually transferring files over cables or cloud storage.

**Why downloadcc exists:** I needed a fast, hands-off CLI tool that searches metadata, automates torrent downloads, and wirelessly pushes ready-to-play media directly to VLC on iPad and iPhone over Wi-Fi.

downloadcc automates title validation, episode sorting, torrent downloading, and wireless VLC uploading in a single terminal interface. It's built for terminal enthusiasts and iOS users — not for complex GUI desktop media servers.

<br />

## 📖 Table of Contents
- [What is downloadcc?](#-what-is-downloadcc)
- [Key Features](#-key-features)
- [System Architecture](#-system-architecture)
- [Setup & Installation](#-setup--installation)
- [How to Use](#-how-to-use)
- [Reference Tables](#-reference-tables)
- [Scope & Limitations](#-scope--limitations)
- [File Structure](#-file-structure)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

---

## 💡 What is downloadcc?

downloadcc is a fully interactive terminal-based media downloader that searches movies and TV shows, selects seasons and episodes, downloads via native `libtorrent`, and wirelessly pushes files to VLC on iPad/iPhone.

| Before | After |
| :--- | :--- |
| Browsing ad-filled torrent sites, manually renaming episode files, and transferring via iTunes or cables. | One terminal command searches TVmaze metadata, downloads via libtorrent, renames files, and pushes over Wi-Fi to VLC. |

Instead of manual torrent management and file transfers:
- **Terminal CLI**: Interactive numbered menus to search, select, and queue shows without leaving the terminal.
- **TVmaze Metadata**: Automatically fetches TV show seasons and episode titles to ensure accurate torrent matching.
- **Wireless VLC Transfer**: Pushes completed downloads directly to VLC for iOS over Wi-Fi with saved IP profiles.

---

## ✨ Key Features

- 🎥 **Strict Title Matching**: Custom regex validation ensures search results exactly match your target title, eliminating false positives.
- 📱 **iPad/iPhone-Compatible Video Profiles**: Results rank H.264/.mp4 streams highest and deprioritize HEVC/x265, AV1, and 10-bit formats for guaranteed out-of-the-box playback on iOS.
- ⚡ **High-Speed Peer Discovery**: DHT, Local Service Discovery (LSD), UPnP, and NAT-PMP all enabled for maximum torrent connectivity.
- 📂 **Automatic Post-Processing**: Organizes downloads into season subfolders and renames files to the clean `S_XX_E_YY.ext` convention automatically.
- 🔄 **Smart Retry for Failed Uploads**: Re-upload only the files that failed in the last batch.
- ⏳ **Persistent Background Queue**: Download multiple shows/movies sequentially with live progress, automatic resume, and self-healing torrent switching.

---

## ⚙️ System Architecture

Data flow from user command line input through torrent download processing stages to wireless device output.

```mermaid
%%{init: {'theme': 'dark'}}%%
graph TD
    A[CLI Entry: downloadcc] --> B{Command Router}

    B -->|search / add| C[search_engine.py]
    B -->|queue / remove / clear| D[Queue Manager]
    B -->|vlc / vlc retry| E[VLC Upload Engine]

    C --> C1[TVmaze API — TV metadata]
    C --> C2[Torrent Indexers — SolidTorrents + Pirate Bay]
    C2 --> C3[Compatibility Ranker — H.264 priority]
    C3 --> D

    D --> D1[queue.json — ~/.downloadcc/]
    D1 --> F[libtorrent Session]
    F --> F1[DHT + LSD + UPnP + NAT-PMP]
    F1 --> F2[Download + Post-Process]
    F2 --> F3[Rename S_XX_E_YY → Season Subfolder]

    E --> E1[Device Picker — iPad / iPhone / Custom]
    E1 --> E2[config.json — saved IPs per device]
    E2 --> E3[POST /upload.json — VLC WiFi Sharing]
    E3 -->|failure| E4[failed_uploads.json log]
    E4 -->|vlc retry| E3

    classDef default fill:#0f172a,stroke:#3b82f6,stroke-width:2px,color:#fff;
    classDef process fill:#1e1b4b,stroke:#a855f7,stroke-width:2px,color:#fff;
    class C,D,E process;
```

---

## 🚀 Setup & Installation

### Option A: 1-Click Setup (Windows Winget)
```cmd
winget install --id Python.Python.3.12 -e --accept-source-agreements --accept-package-agreements
winget install --id Git.Git -e --accept-source-agreements --accept-package-agreements
```
This script automates the installation of Python 3.12 and Git on Windows.

### Option B: Manual Installation

```bash
git clone https://github.com/IamOumarIbrahim/downloadcc.git
cd downloadcc
pip install requests beautifulsoup4 libtorrent pyinstaller
```

🔍 **Verification Command**:
```bash
python --version
```
*Expected Output*: `Python 3.12.x`

---

## 🖥️ How to Use

1. Run the downloader by typing `python downloadcc.py "Movie or Show Name"`.
2. Select a result by typing its corresponding number and pressing Enter.
3. Wait for the live progress indicator to reach 100% completion.

```bash
# Example command to search and download Mr. Robot
python downloadcc.py "Mr. Robot"
```

---

## 📊 Reference Tables

### Configuration Schema (`~/.downloadcc/config.json`)

| Field | Description | Type |
| :--- | :--- | :--- |
| `ipad_ip` | The saved IP address of your iPad running VLC. | String |
| `iphone_ip` | The saved IP address of your iPhone running VLC. | String |

---

## 🔬 Scope & Limitations

- **iOS Format Prioritization**: Specifically optimizes for H.264 formats which might deprioritize higher quality HEVC/4K rips.
- **Network Dependency**: Requires local Wi-Fi network connectivity to the iOS device for VLC transfers.

---

## 📁 File Structure

```
downloadcc/
├── assets/
│   └── demo.gif                 - Demo preview animation
├── downloadcc.py                - Main interactive CLI entry point
├── search_engine.py             - TVmaze API + torrent indexer crawling engine
├── installer.iss                - Inno Setup compiler configuration
├── MoviesAndShowsInstaller.exe  - Compiled standalone Windows installer
├── LICENSE                      - MIT License text
└── README.md                    - Project documentation
```

---

## 🩹 Troubleshooting

| Issue | Root Cause | Resolution |
| :--- | :--- | :--- |
| Download stalled at 0% | No peers available or firewall blocking DHT | Wait a few minutes for peer discovery, or ensure python/downloadcc is allowed through Windows Firewall. |
| VLC upload fails | IP address changed or device screen is locked | Wake up device, open VLC, check network IP, and use the VLC retry command. |

---

## 🧩 Contributing

The easiest way to contribute is by adding new torrent indexers to `search_engine.py`. Simply implement a new scraper function and append its results to the main search pool.

---

## 📄 License
MIT License © 2024 [IamOumarIbrahim](https://github.com/IamOumarIbrahim)

## 🙏 Powered By
[libtorrent](https://libtorrent.org/) · [TVmaze](https://www.tvmaze.com/api)

<div align="center">

If downloadcc solved your media downloading and transferring needs, a ⭐ helps other people find it.

</div>
