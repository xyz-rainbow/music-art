#!/usr/bin/env python3
"""
extract_cover.py - Extract and Inspect Embedded Audio Cover Artwork
Part of the 'music-art' universal AI skill.
"""

import argparse
import json
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


def extract_cover(audio_file, output_image_path=None):
    audio_path = Path(audio_file).resolve()
    if not audio_path.exists():
        print(f"Error: Audio file '{audio_path}' does not exist.", file=sys.stderr)
        return None

    if output_image_path is None:
        out_path = audio_path.parent / f"{audio_path.stem}_cover.jpg"
    else:
        out_path = Path(output_image_path).resolve()

    temp_dir = Path(tempfile.gettempdir())
    temp_out = temp_dir / f"extracted_{os.getpid()}_{out_path.name}"

    if temp_out.exists():
        temp_out.unlink()

    ffmpeg_cmd = [
        "ffmpeg", "-y", "-v", "error",
        "-i", str(audio_path),
        "-an",
        "-vcodec", "copy",
        str(temp_out)
    ]

    try:
        run_cmd(ffmpeg_cmd)
        if not temp_out.exists() or temp_out.stat().st_size == 0:
            print(f"Notice: No embedded cover found in '{audio_path.name}'")
            return None

        out_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(temp_out), str(out_path))

        # Inspect dimensions
        probe_cmd = [
            "ffprobe", "-v", "error",
            "-show_entries", "stream=width,height,codec_name",
            "-of", "json",
            str(out_path)
        ]
        probe_res = run_cmd(probe_cmd)
        probe_data = json.loads(probe_res.stdout)
        streams = probe_data.get("streams", [])
        w = streams[0].get("width", 0) if streams else 0
        h = streams[0].get("height", 0) if streams else 0
        aspect = "1:1" if (w > 0 and w == h) else f"{w}:{h}"

        print(f"✓ Extracted cover to: {out_path} ({w}x{h}, aspect: {aspect})")
        return str(out_path)

    except Exception as e:
        if temp_out.exists():
            temp_out.unlink()
        print(f"Exception during extraction: {e}", file=sys.stderr)
        return None


def main():
    parser = argparse.ArgumentParser(description="Extract embedded artwork from audio file.")
    parser.add_argument("audio", help="Path to audio file")
    parser.add_argument("--output", "-o", help="Path to destination image file (default: next to audio)")
    args = parser.parse_args()

    extract_cover(args.audio, args.output)


if __name__ == "__main__":
    main()
