<div align="center">
  <h1> downloadcc</h1>
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

downloadcc automates title validation, episode sorting, torrent downloading, and wireless VLC uploading in a single terminal interface.

## Key Features

- **Strict Title Matching**: Custom regex validation ensures search results exactly match your target title, eliminating false positives.
- **iPad/iPhone-Compatible Video Profiles**: Results rank H.264/.mp4 streams highest and deprioritize HEVC/x265, AV1, and 10-bit formats for guaranteed out-of-the-box playback on iOS.
- **Persistent Background Queue**: Download multiple shows/movies sequentially with live progress, automatic resume, and self-healing torrent switching.

## Installation

```bash
git clone https://github.com/IamOumarIbrahim/downloadcc.git
cd downloadcc
pip install requests beautifulsoup4 libtorrent pyinstaller pyfiglet
```

## Usage

```bash
python downloadcc.py "Mr. Robot"
```

## Configuration Schema (`~/.downloadcc/config.json`)

| Field | Description | Type |
| :--- | :--- | :--- |
| `ipad_ip` | The saved IP address of your iPad running VLC. | String |
| `iphone_ip` | The saved IP address of your iPhone running VLC. | String |

## Scope & Limitations

- **iOS Format Prioritization**: Specifically optimizes for H.264 formats which might deprioritize higher quality HEVC/4K rips.
- **Network Dependency**: Requires local Wi-Fi network connectivity to the iOS device for VLC transfers.

## License
MIT License © 2024 [IamOumarIbrahim](https://github.com/IamOumarIbrahim)
