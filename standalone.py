#!/usr/bin/env python3
"""
test.py - Script simples para testar .env, paths de som e execução do player.
Não depende do Discord.
"""

import os
import platform
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --------------------------
# Load channel configs
# --------------------------
def _strip_quotes(v: str | None) -> str | None:
    if v is None:
        return None
    v = v.strip()
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        return v[1:-1]
    return v

channels = []
idx = 1
while True:
    id_key = f"TARGET_CHANNEL_ID_{idx}"
    name_key = f"TARGET_CHANNEL_NOME_{idx}"
    sound_key = f"TARGET_CHANNEL_SOUND_FILE_{idx}"

    raw_id = os.getenv(id_key)
    if not raw_id:
        break

    name = _strip_quotes(os.getenv(name_key)) or f"channel_{raw_id}"
    sound = _strip_quotes(os.getenv(sound_key)) or ""
    channels.append({"id": int(raw_id), "name": name, "sound": sound})
    idx += 1

if not channels:
    print("No channels configured in .env")
    exit(1)

print("Channels loaded from .env:")
for c in channels:
    print(f" - {c['name']} ({c['id']}) -> {c['sound']}")

# --------------------------
# Sound player (system fallback)
# --------------------------
SYSTEM = platform.system()

def play_sound(path: str):
    p = Path(path)
    if not p.exists():
        print(f"[sound] file not found: {path}")
        return

    print(f"[sound] playing: {path}")

    if SYSTEM == "Darwin":
        subprocess.run(["afplay", str(p)], check=False)
        return

    if SYSTEM == "Windows":
        try:
            ps_cmd = [
                "powershell",
                "-NoProfile",
                "-Command",
                f'(New-Object Media.SoundPlayer "{str(p)}").PlaySync();'
            ]
            subprocess.run(ps_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception as e:
            print(f"[sound] Windows fallback failed: {e}")
        return

    # Linux fallback
    for cmd in [["ffplay", "-nodisp", "-autoexit", str(p)],
                ["paplay", str(p)],
                ["aplay", str(p)],
                ["mpv", "--no-video", str(p)]]:
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
            return
        except FileNotFoundError:
            continue
    print("[sound] No suitable player found; install ffmpeg (ffplay), mpv, paplay or aplay.")

# --------------------------
# Test all channels
# --------------------------
for c in channels:
    print(f"\n[TEST] Channel {c['name']} ({c['id']})")
    play_sound(c["sound"])
