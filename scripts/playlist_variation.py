#!/usr/bin/env python3
"""
playlist_variation.py - Chromatic & Character Playlist Variation Engine
Part of the 'music-art' universal AI skill.

Analyzes playlist track titles and generates non-repetitive, thematic 1:1 cover art prompts
with dynamic color palettes (Purple, Violet, Cyan, Lime Green, Molten Orange, Pastels)
and rotating character avatars to produce cohesive yet diverse album collections.
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Curated Chromatic Palettes
PALETTES = [
    {
        "id": "neon_purple",
        "name": "Neon Violet & Magenta",
        "keywords": ["head", "mind", "voice", "doll", "wushu", "psych", "amnesia", "dream"],
        "bg": "Electric deep violet-purple (#3b0764) with glowing neon magenta accents",
        "lighting": "Hyper-saturated neon ultraviolet and magenta rim lighting"
    },
    {
        "id": "electric_cyan",
        "name": "Electric Cyan & Teal",
        "keywords": ["probe", "cloud", "laguna", "water", "street", "gutter", "downunder", "atlantis"],
        "bg": "Vibrant electric cyan (#06b6d4) and deep aquatic teal (#083344) with Night City reflections",
        "lighting": "High-voltage neon cyan and cool ice-blue illumination"
    },
    {
        "id": "toxic_lime",
        "name": "Toxic Lime & Acid Green",
        "keywords": ["scavenger", "scav", "hunt", "juiced", "toxic", "acid", "mine", "mining", "gang"],
        "bg": "Hazardous toxic lime-green (#84cc16) and bio-luminescent acid green (#4ade80)",
        "lighting": "Acidic neon lime glow with harsh industrial yellow-green shadows"
    },
    {
        "id": "molten_orange",
        "name": "Molten Orange & Solar Amber",
        "keywords": ["extraction", "action", "outsider", "kang", "down", "nomad", "passage", "rite", "desert"],
        "bg": "Intense molten solar orange (#ea580c) and radiant warm amber (#f59e0b)",
        "lighting": "Blazing sunset amber with high-contrast fiery backlight"
    },
    {
        "id": "blood_crimson",
        "name": "Blood Crimson & Obsidian Red",
        "keywords": ["rebel", "path", "code", "red", "hell", "smasher", "trouble", "adam", "lockdown"],
        "bg": "Menacing blood crimson (#b91c1c) and obsidian dark red (#450a0a)",
        "lighting": "Intense emergency strobe crimson and dramatic red specular highlights"
    },
    {
        "id": "imperial_gold",
        "name": "Imperial Gold & Scarlet",
        "keywords": ["parade", "hanako", "yorinobu", "sacred", "profane", "arasaka", "cathedral", "suits"],
        "bg": "Opulent metallic imperial gold (#eab308) and lacquer scarlet red (#991b1b)",
        "lighting": "Rich golden specular reflections and regal crimson contrasts"
    },
    {
        "id": "pastel_dream",
        "name": "Pastel Lavender & Mint",
        "keywords": ["cloudy", "forgive", "again", "good", "know", "never", "fade", "away", "peace"],
        "bg": "Dreamy cyberpunk pastel lavender (#d8b4fe) and soft pale mint (#a7f3d0)",
        "lighting": "Soft diffused pastel dreamglow with delicate neon edge highlights"
    }
]

# Character & Archetype Roster (e.g. for Cyberpunk universe)
CYBERPUNK_AVATARS = [
    {"role": "Male V", "desc": "male cyberpunk mercenary with cybernetic ocular implant, buzzcut, and iconic Samurai jacket with cyan glowing collar"},
    {"role": "Female V", "desc": "badass female cyberpunk mercenary with side-shaved hair, tactical harness, and glowing mantis blades extended"},
    {"role": "Johnny Silverhand", "desc": "charismatic rockstar rockerboy with iconic chrome cybernetic arm, aviator sunglasses, and unbuttoned vest"},
    {"role": "Netrunner", "desc": "futuristic netrunner with neural jack cables, holographic visor, and glowing digital cyberspace runes across fingertips"},
    {"role": "Trauma Team Medic", "desc": "armored high-threat Trauma Team emergency operator with tactical helmet, green/white visor, and heavy medical carbine"},
    {"role": "Nomad Badlander", "desc": "rugged nomad warrior with wind-weathered jacket, goggles, dust-covered cyberware, and sniper rifle"},
    {"role": "Mox Bouncer", "desc": "stylish Mox punk bouncer with neon pink hair, spiked leather jacket, cyber-baseball bat, and glowing tattoo sleeves"},
    {"role": "Arasaka Cyberninja", "desc": "lethal high-tech corporate cyberninja with sleek black armor, glowing thermal katana, and face-concealing mask"},
    {"role": "Maelstrom Cyborg", "desc": "intimidating full-cyber optic borg with five glowing red ocular lenses and chrome skull plating"},
    {"role": "Corpo Operative", "desc": "impeccably dressed corporate security executive in tailored ballistic suit with discreet chrome neck plugs"}
]


def match_palette(title, index):
    lower = title.lower()
    for pal in PALETTES:
        for kw in pal["keywords"]:
            if re.search(r"\b" + re.escape(kw) + r"\b", lower):
                return pal
    # Fallback rotation
    return PALETTES[index % len(PALETTES)]


def match_avatar(title, index):
    lower = title.lower()
    if "rebel" in lower or "silverhand" in lower or "fade away" in lower:
        return CYBERPUNK_AVATARS[2] # Johnny
    if "extraction" in lower or "code red" in lower:
        return CYBERPUNK_AVATARS[4] # Trauma Team
    if "outsider" in lower or "passage" in lower:
        return CYBERPUNK_AVATARS[5] # Nomad
    if "probe" in lower or "mining" in lower or "atlantis" in lower:
        return CYBERPUNK_AVATARS[3] # Netrunner
    if "smasher" in lower or "scavenger" in lower:
        return CYBERPUNK_AVATARS[8] # Borg
    if "ninja" in lower or "hanako" in lower or "parade" in lower:
        return CYBERPUNK_AVATARS[7] # Cyberninja
    if "doll" in lower or "trouble" in lower:
        return CYBERPUNK_AVATARS[6] # Mox
    if index % 2 == 1:
        return CYBERPUNK_AVATARS[1] # Female V
    return CYBERPUNK_AVATARS[index % len(CYBERPUNK_AVATARS)]


def build_prompt(track_title, track_number, palette, avatar, franchise="Cyberpunk 2077"):
    prompt = (
        f"A high-end 1:1 square music album cover art for '{track_title}'. "
        f"Maintaining the authentic {franchise} Original Score collector aesthetic with a {palette['name']} theme. "
        f"Background: {palette['bg']}, featuring distant silhouettes of futuristic Night City architecture. "
        f"Character: {avatar['desc']}, posed dynamically in the center-foreground with {palette['lighting']}. "
        f"Typography: Integrated bold angular cyberpunk styling with technical geometric framing reading '{track_number}. {track_title}'. "
        f"High-contrast, cinematic, collectible vinyl soundtrack quality."
    )
    return prompt


def generate_playlist_plan(tracklist):
    plan = []
    for i, raw_title in enumerate(tracklist):
        clean = re.sub(r"^\d+\s*", "", raw_title).strip()
        clean = re.sub(r"\.(flac|mp3|m4a)$", "", clean, flags=re.IGNORECASE)
        num_str = f"{(i + 1):02d}"

        pal = match_palette(clean, i)
        ava = match_avatar(clean, i)
        p = build_prompt(clean, num_str, pal, ava)

        plan.append({
            "track_number": num_str,
            "raw_filename": raw_title,
            "title": clean,
            "palette": pal["name"],
            "palette_id": pal["id"],
            "character": ava["role"],
            "prompt": p
        })
    return plan


def main():
    parser = argparse.ArgumentParser(description="Generate chromatic and character variation plan for playlists.")
    parser.add_argument("tracks", nargs="*", help="List of track titles or files")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    args = parser.parse_args()

    if not args.tracks:
        # Example demo
        args.tracks = ["01 V", "02 Extraction Action", "03 The Rebel Path", "04 The Streets Are Long-Ass Gutters", "05 Outsider No More", "06 Cloudy Day"]

    plan = generate_playlist_plan(args.tracks)
    if args.json:
        print(json.dumps(plan, indent=2, ensure_ascii=False))
    else:
        print("\n=== PLAYLIST VARIATION PLAN ===")
        for item in plan:
            print(f"\n[{item['track_number']}] {item['title']}")
            print(f"  🎨 Palette:   {item['palette']}")
            print(f"  👤 Avatar:    {item['character']}")
            print(f"  📝 Prompt:    {item['prompt'][:120]}...")


if __name__ == "__main__":
    main()
