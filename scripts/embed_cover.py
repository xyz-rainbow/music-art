#!/usr/bin/env python3
"""
embed_cover.py - Lossless Audio Cover Art Embedding Engine
Part of the 'music-art' universal AI skill.

Replaces or embeds album cover artwork into audio files (e.g. .m4a, .mp3)
with zero audio re-encoding (-c:a copy) and full metadata preservation.
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def run_cmd(cmd, check=True):
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=False)
    if check and res.returncode != 0:
        raise RuntimeError(f"Command failed:\n{' '.join(cmd)}\nStderr: {res.stderr}")
    return res


def embed_artwork(audio_file, cover_file, output_file=None, in_place=True):
    audio_path = Path(audio_file).resolve()
    cover_path = Path(cover_file).resolve()

    if not audio_path.exists():
        print(f"Error: Audio file '{audio_path}' does not exist.", file=sys.stderr)
        return False
    if not cover_path.exists():
        print(f"Error: Cover file '{cover_path}' does not exist.", file=sys.stderr)
        return False

    temp_dir = Path(tempfile.gettempdir())
    temp_out = temp_dir / f"music_art_embed_{os.getpid()}_{audio_path.name}"

    if temp_out.exists():
        temp_out.unlink()

    ffmpeg_cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-i", str(audio_path),
        "-i", str(cover_path),
        "-map", "0:a",
        "-map", "1:v",
        "-c:a", "copy",
        "-c:v", "copy",
        "-disposition:v:0", "attached_pic",
        "-map_metadata", "0",
        str(temp_out)
    ]

    try:
        run_cmd(ffmpeg_cmd)
        if not temp_out.exists() or temp_out.stat().st_size == 0:
            print(f"Error: Failed to embed cover into '{audio_path.name}'", file=sys.stderr)
            return False

        if output_file:
            dest = Path(output_file).resolve()
            shutil.move(str(temp_out), str(dest))
            print(f"✓ Embedded artwork written to: {dest}")
        elif in_place:
            shutil.move(str(temp_out), str(audio_path))
            print(f"✓ Embedded 1:1 artwork into: {audio_path.name}")
        else:
            print(f"✓ Embedded output at: {temp_out}")

        return True

    except Exception as e:
        if temp_out.exists():
            temp_out.unlink()
        print(f"Exception while embedding artwork: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Embed album cover art into audio without re-encoding.")
    parser.add_argument("audio", help="Path to target audio file (.m4a, .mp3, etc.)")
    parser.add_argument("cover", help="Path to cover art image (.jpg, .png)")
    parser.add_argument("--output", "-o", help="Optional output path (defaults to in-place replacement)")
    parser.add_argument("--no-in-place", action="store_true", help="Do not overwrite audio in-place")
    args = parser.parse_args()

    embed_artwork(args.audio, args.cover, output_file=args.output, in_place=not args.no_in_place)


if __name__ == "__main__":
    main()
