<div align="center">

<img src="./assets/banner.svg" alt="Music-XYZ-Skill Banner" width="100%" />

# 🎵 music-xyz-skill
### Universal AI Audio Engineering, Parallel FLAC Downloader & 1:1 Album Artwork Suite

[![Skills](https://img.shields.io/badge/skills.sh-music--xyz--skill-7928ca.svg?style=for-the-badge)](https://skills.sh/)
[![License: MIT](https://img.shields.io/badge/License-MIT-00f0ff.svg?style=for-the-badge)](LICENSE)
[![Platforms: Windows | Linux | macOS](https://img.shields.io/badge/Platform-Win%20%7C%20Linux%20%7C%20macOS-ff007f.svg?style=for-the-badge)]()
[![Multi-Agent](https://img.shields.io/badge/Multi--Agent-Antigravity%20%7C%20Grok%20%7C%20ChatGPT%20%7C%20Claude-10b981.svg?style=for-the-badge)]()

</div>

---

**`music-xyz-skill`** (evolved from `music-art`) is a full-lifecycle AI audio engineering suite designed for music collectors, audiophiles, and autonomous AI agents:

1. **Bit-Perfect Parallel FLAC Downloader**:
   - Multi-source search across **Soulseek** (slskd), **Archive.org** streaming, and **Rutracker**.
   - Concurrently downloads studio FLACs while protecting mechanical HDDs from seek thrashing.
   - Decodes full audio with **FFmpeg** (`-f null -`) to detect invalid residuals or sync frame corruptions.
   - Cross-checks Vorbis title metadata to prevent wrong-track delivery.
   - Enforces a strict duration ceiling (**<= 18 minutes**) to reject uncut continuous sets.
   - Auto-rejects live, bootleg, and concert recordings (studio only).
2. **Strict Library Sanitization & Purity**:
   - Zero tolerance for non-audio scraping artifacts (`.sqlite`, `.xml`, `.cue`, `.log`).
   - Libraries contain strictly: `.flac` audio, `.lrc` synced lyrics, and `.jpg`/`.png` artwork.
3. **Synced Lyrics Automation**:
   - Automatically queries and saves synced `.lrc` files via LRCLIB.
4. **Lossless Cover Art Embedding**:
   - Embeds 1:1 square artwork directly into FLAC Vorbis comments (Picture type 3) without re-encoding audio.
5. **Intelligent Dynamic Compression (music-art core)**:
   - Compresses audio down to strict limits (e.g. **<= 100 MB**) with dynamic mathematical bitrate maximization.

---

## ⚡ Quick Start & Installation

Install globally for all your AI coding agents (**Antigravity**, **Claude Code**, **Cursor**, **Grok**, etc.) via the [Skills CLI](https://skills.sh):

```bash
# Global installation (recommended)
npx skills add xyz-rainbow/music-art -g

# Or direct clone into agent skills path
git clone https://github.com/xyz-rainbow/music-art.git ~/.agents/skills/music-xyz-skill
```

---

## 🛠️ Modular Script Catalog

* **`scripts/flac_downloader.py`**: Parallel FLAC download engine with FFmpeg verification, tag checking, and lyrics.
* **`scripts/flac_cleaner.py`**: Sanitizes directories: purges `.sqlite`/`.xml` artifacts, flags files > 18m, checks cover art.
* **`scripts/embed_cover.py`**: Losslessly injects 1:1 covers into audio containers (`.flac`, `.m4a`, `.mp3`).
* **`scripts/optimize_audio.py`**: Dynamic mathematical bitrate compression to guarantee <= 100 MB limits.
* **`scripts/extract_cover.py`**: Dumps embedded front cover art from audio files to standalone `.jpg`.
* **`scripts/storage_prompter.py`**: Prompts user interactively for cover art storage location.

---

## 📄 License

MIT License. Designed with precision by [xyz-rainbow](https://github.com/xyz-rainbow).
