#!/usr/bin/env python3
"""
storage_prompter.py - Interactive Storage Directory Resolution Protocol
Part of the 'music-art' universal AI skill.

Manages cover image storage paths for the active session. AI agents must check or ask
the user where newly generated 1:1 cover images should be stored before generating files.
"""

import argparse
import json
import os
import sys
from pathlib import Path

CONFIG_FILE = ".music_art_session.json"


def get_stored_session_path(context_dir=None):
    search_dirs = [Path.cwd()]
    if context_dir:
        search_dirs.insert(0, Path(context_dir))

    for d in search_dirs:
        cfg = d / CONFIG_FILE
        if cfg.exists():
            try:
                data = json.loads(cfg.read_text(encoding="utf-8"))
                p = data.get("cover_storage_dir")
                if p and Path(p).exists():
                    return Path(p)
            except Exception:
                pass
    return None


def set_session_storage_path(target_dir, context_dir=None):
    dest = Path(target_dir).resolve()
    dest.mkdir(parents=True, exist_ok=True)
    cfg_dir = Path(context_dir) if context_dir else Path.cwd()
    cfg_path = cfg_dir / CONFIG_FILE
    cfg_path.write_text(json.dumps({"cover_storage_dir": str(dest)}, indent=2), encoding="utf-8")
    print(f"✓ Cover storage directory registered for session: {dest}")
    return dest


def prompt_user_dialog():
    """
    Recommended questionnaire prompt for AI Agents (Antigravity, Grok, ChatGPT, Gemini, MiniMax):
    """
    return {
        "question": "Where should generated 1:1 album cover images be stored for this session?",
        "options": [
            "Use a dedicated central folder (e.g. U:\\Music\\ADHD\\cover or custom directory)",
            "Create a local '/cover' subfolder inside the active music folder",
            "Store next to each audio file with identical basename (.jpg)",
            "Embed directly into audio files and discard standalone image files"
        ]
    }


def main():
    parser = argparse.ArgumentParser(description="Query or set the cover image storage path for the session.")
    parser.add_argument("--get", action="store_true", help="Get current session storage path")
    parser.add_argument("--set", help="Set new session storage path")
    parser.add_argument("--context", help="Working context directory (defaults to cwd)")
    parser.add_argument("--prompt", action="store_true", help="Print standard AI agent interactive question")
    args = parser.parse_args()

    if args.prompt:
        print(json.dumps(prompt_user_dialog(), indent=2, ensure_ascii=False))
        return

    if args.set:
        set_session_storage_path(args.set, args.context)
        return

    stored = get_stored_session_path(args.context)
    if stored:
        print(str(stored))
    else:
        print("None")


if __name__ == "__main__":
    main()
