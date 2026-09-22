#!/usr/bin/env python3
"""
optimize_audio.py - Dynamic High-Fidelity Audio Compression Engine
Part of the 'music-art' universal AI skill.

Optimizes audio files (e.g., .m4a, .mp3, .flac, .wav) to strictly respect a maximum
size ceiling (default: 100 MB) while mathematically maximizing audio bitrate and quality.
"""

import argparse
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def run_cmd(cmd, check=True):
    res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, shell=False)
    if check and res.returncode != 0:
        raise RuntimeError(f"Command failed (code {res.returncode}):\n{' '.join(cmd)}\nStderr: {res.stderr}")
    return res


def get_media_info(file_path):
    cmd = [
        "ffprobe", "-v", "error",
        "-show_entries", "format=duration,size,bit_rate:stream=codec_type,codec_name,width,height,bit_rate",
        "-of", "json",
        str(file_path)
    ]
    res = run_cmd(cmd)
    data = json.loads(res.stdout)
    duration = float(data.get("format", {}).get("duration", 0.0))
    size = int(data.get("format", {}).get("size", os.path.getsize(file_path)))
    
    streams = data.get("streams", [])
    audio_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)
    video_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
    
    return {
        "duration": duration,
        "size": size,
        "audio_stream": audio_stream,
        "video_stream": video_stream,
        "format": data.get("format", {})
    }


def calculate_optimal_bitrate(duration_sec, safe_mb=93.0, max_bitrate_kbps=256):
    """
    Computes highest standard AAC bitrate that guarantees the resulting file
    stays strictly under the safe budget.
    """
    if duration_sec <= 0:
        return 192
    
    target_bits = safe_mb * 1024 * 1024 * 8
    calc_kbps = math.floor(target_bits / duration_sec / 1000)
    
    standard_steps = [256, 224, 192, 160, 144, 140, 128, 112, 96, 72, 64, 48]
    for step in standard_steps:
        if step <= max_bitrate_kbps and calc_kbps >= step:
            return step
    
    return max(48, min(calc_kbps, max_bitrate_kbps))


def optimize_file(input_file, target_max_mb=100.0, safe_margin_mb=93.0, max_bitrate_kbps=256, in_place=True):
    path = Path(input_file).resolve()
    if not path.exists():
        print(f"Error: File '{path}' does not exist.", file=sys.stderr)
        return False

    orig_size = path.stat().st_size
    orig_size_mb = orig_size / (1024 * 1024)
    info = get_media_info(path)
    duration = info["duration"]
    duration_min = duration / 60.0

    print(f"\nEvaluating: {path.name}")
    print(f"  Duration: {duration_min:.2f} min ({duration:.1f}s)")
    print(f"  Current Size: {orig_size_mb:.2f} MB")

    if orig_size_mb <= target_max_mb and orig_size_mb <= safe_margin_mb:
        print(f"  Notice: File is already within safe size ({orig_size_mb:.2f} MB <= {safe_margin_mb} MB).")

    bitrate = calculate_optimal_bitrate(duration, safe_mb=safe_margin_mb, max_bitrate_kbps=max_bitrate_kbps)
    print(f"  Selected Bitrate: {bitrate} kbps (Maximizing quality under {target_max_mb} MB)")

    # Transcode using temp file
    temp_dir = Path(tempfile.gettempdir())
    temp_out = temp_dir / f"music_art_opt_{os.getpid()}_{path.stem[:12]}.m4a"

    if temp_out.exists():
        temp_out.unlink()

    ffmpeg_cmd = [
        "ffmpeg", "-y", "-v", "error", "-stats",
        "-i", str(path),
        "-map", "0",
        "-c:a", "aac", "-b:a", f"{bitrate}k",
        "-c:v", "copy",
        "-disposition:v:0", "attached_pic",
        "-map_metadata", "0",
        str(temp_out)
    ]

    try:
        run_cmd(ffmpeg_cmd)
        if not temp_out.exists():
            print(f"  Error: Transcoding failed to generate output.", file=sys.stderr)
            return False

        new_size = temp_out.stat().st_size
        new_size_mb = new_size / (1024 * 1024)
        print(f"  Result Size: {new_size_mb:.2f} MB")

        if new_size_mb > target_max_mb:
            print(f"  Error: Output {new_size_mb:.2f} MB exceeds max ceiling {target_max_mb} MB. Aborting.", file=sys.stderr)
            temp_out.unlink()
            return False

        if in_place:
            shutil.move(str(temp_out), str(path))
            savings = (1.0 - (new_size / orig_size)) * 100.0
            print(f"  ✓ Successfully optimized in-place! Size reduction: {savings:.1f}%")
        else:
            print(f"  ✓ Output written to: {temp_out}")

        return True

    except Exception as e:
        if temp_out.exists():
            temp_out.unlink()
        print(f"  Exception during optimization: {e}", file=sys.stderr)
        return False


def main():
    parser = argparse.ArgumentParser(description="Optimize audio files for size ceiling with maximum bitrate.")
    parser.add_argument("input", help="Path to audio file or directory of audio files.")
    parser.add_argument("--max-size-mb", type=float, default=100.0, help="Maximum allowed file size in MB (default: 100.0)")
    parser.add_argument("--safe-margin-mb", type=float, default=93.0, help="Target budget for calculation safety margin (default: 93.0)")
    parser.add_argument("--max-bitrate", type=int, default=256, help="Maximum AAC bitrate in kbps (default: 256)")
    parser.add_argument("--no-in-place", action="store_true", help="Do not overwrite original file; keep output in temp.")
    args = parser.parse_args()

    input_path = Path(args.input)
    if input_path.is_dir():
        files = [f for f in input_path.glob("*.m4a")] + [f for f in input_path.glob("*.mp3")]
        print(f"Found {len(files)} audio tracks in '{input_path}'")
        for f in files:
            optimize_file(f, target_max_mb=args.max_size_mb, safe_margin_mb=args.safe_margin_mb,
                          max_bitrate_kbps=args.max_bitrate, in_place=not args.no_in_place)
    else:
        optimize_file(input_path, target_max_mb=args.max_size_mb, safe_margin_mb=args.safe_margin_mb,
                      max_bitrate_kbps=args.max_bitrate, in_place=not args.no_in_place)


if __name__ == "__main__":
    main()
