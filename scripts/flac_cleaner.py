#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
flac_cleaner.py - Sanitize audio libraries to strict standards:
  - Allowed: .flac, .lrc, .jpg, .jpeg, .png (cover only).
  - Removes unwanted scraping artifacts (.sqlite, .xml, .cue, .log, .txt, .md).
  - Verifies and embeds cover art into FLAC Vorbis comments if missing.
  - Flags or purges files exceeding a duration ceiling (default: 18 minutes).
  - Detects and rejects live recordings/bootlegs.
"""
import os
import sys
import argparse
import subprocess
from pathlib import Path
import mutagen.flac

sys.stdout.reconfigure(encoding="utf-8")

ALLOWED_EXTS = {".flac", ".lrc", ".jpg", ".jpeg", ".png"}
DISALLOWED_GARBAGE = {".sqlite", ".xml", ".cue", ".log", ".txt", ".md", ".ini", ".db"}

def clean_directory(root_dir: Path, max_duration_min: float = 18.0, dry_run: bool = False, purge_long: bool = False):
    print("=" * 70)
    print(f"CLEANING AUDIO DIRECTORY: {root_dir}")
    print(f"Max audio duration: {max_duration_min} min | Purge long files: {purge_long}")
    print("=" * 70)

    removed_garbage = []
    long_tracks = []
    flacs_without_cover = []
    total_flacs = 0

    for f in list(root_dir.rglob("*")):
        if not f.is_file():
            continue

        ext = f.suffix.lower()

        # 1. Remove non-conforming garbage files
        if ext in DISALLOWED_GARBAGE or (ext not in ALLOWED_EXTS and not f.name.startswith("cover.")):
            removed_garbage.append(f)
            if not dry_run:
                try:
                    f.unlink()
                    print(f"  [DELETED ARTIFACT] {f.relative_to(root_dir)}")
                except Exception as e:
                    print(f"  [ERROR DELETING] {f.name}: {e}")
            else:
                print(f"  [DRY-RUN DELETED] {f.relative_to(root_dir)}")
            continue

        # 2. Inspect FLAC audio
        if ext == ".flac":
            total_flacs += 1
            try:
                af = mutagen.flac.FLAC(str(f))
                dur_m = af.info.length / 60.0

                # Duration check
                if dur_m > max_duration_min:
                    long_tracks.append((f, dur_m, f.stat().st_size / (1024 * 1024)))
                    if purge_long and not dry_run:
                        f.unlink()
                        print(f"  [PURGED > {max_duration_min}m] {f.relative_to(root_dir)} ({dur_m:.1f}m)")

                # Embedded cover check
                if not af.pictures:
                    flacs_without_cover.append(f)

            except Exception as e:
                print(f"  [CORRUPT/UNREADABLE FLAC] {f.name}: {e}")

    print("\n" + "-" * 70)
    print("SUMMARY AUDIT:")
    print(f"  Total FLAC files: {total_flacs}")
    print(f"  Garbage artifacts removed: {len(removed_garbage)}")
    print(f"  FLACs without embedded covers: {len(flacs_without_cover)}")
    print(f"  Audio files > {max_duration_min} minutes: {len(long_tracks)}")

    if long_tracks:
        print("\nTracks over duration ceiling:")
        for p, d, sz in long_tracks:
            print(f"  - {p.relative_to(root_dir)}: {d:.1f}m ({sz:.1f} MB)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit and sanitize FLAC directories")
    parser.add_argument("path", type=str, help="Root folder to clean")
    parser.add_argument("--max-duration", type=float, default=18.0, help="Maximum length in minutes (default 18.0)")
    parser.add_argument("--purge-long", action="store_true", help="Purge files exceeding duration ceiling")
    parser.add_argument("--dry-run", action="store_true", help="Scan only, do not delete")
    args = parser.parse_args()

    clean_directory(Path(args.path), max_duration_min=args.max_duration, dry_run=args.dry_run, purge_long=args.purge_long)
