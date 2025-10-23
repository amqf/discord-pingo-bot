#!/usr/bin/env python3
"""
Discord multi-channel alert sound bot (single-file).
- Config via .env (see README for format).
- No optional binary Python audio libs required; uses system players as fallback.
- Debounce per-channel to avoid spam (configurable via DEBOUNCE_SECONDS).
"""
from __future__ import annotations

import asyncio
import os
import platform
import shlex
import subprocess
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from dotenv import load_dotenv
import discord
from discord import Intents

# --------------------------
# Load env
# --------------------------
load_dotenv()

TOKEN = os.getenv("TOKEN") or ""
if not TOKEN:
    raise SystemExit("ERROR: TOKEN not found in .env")

# Debounce window (seconds) to avoid repeated plays on spammy channels
try:
    DEBOUNCE_SECONDS = float(os.getenv("DEBOUNCE_SECONDS", "10"))
except ValueError:
    DEBOUNCE_SECONDS = 10.0

# --------------------------
# Channel config loader
# --------------------------
@dataclass
class ChannelConfig:
    name: str
    id: int
    sound: str  # path to sound file (can be relative)
    enabled: bool = True


def _strip_quotes(v: Optional[str]) -> Optional[str]:
    if v is None:
        return None
    v = v.strip()
    if (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
        return v[1:-1]
    return v


def load_channel_configs() -> List[ChannelConfig]:
    chans: List[ChannelConfig] = []
    idx = 1
    while True:
        id_key = f"TARGET_CHANNEL_ID_{idx}"
        name_key = f"TARGET_CHANNEL_NOME_{idx}"
        sound_key = f"TARGET_CHANNEL_SOUND_FILE_{idx}"

        raw_id = os.getenv(id_key)
        if not raw_id:
            break
        try:
            cid = int(raw_id.strip())
        except Exception:
            print(f"[warn] invalid {id_key}='{raw_id}', skipping")
            idx += 1
            continue

        name = _strip_quotes(os.getenv(name_key)) or f"channel_{cid}"
        sound = _strip_quotes(os.getenv(sound_key)) or ""
        chans.append(ChannelConfig(name=name, id=cid, sound=sound))
        idx += 1
    return chans


TARGET_CHANNELS = load_channel_configs()
if not TARGET_CHANNELS:
    raise SystemExit("ERROR: No TARGET_CHANNEL_ID_N entries found in .env")

# build map id -> config
CHANNEL_MAP: Dict[int, ChannelConfig] = {c.id: c for c in TARGET_CHANNELS}

print("Configured channels:")
for c in TARGET_CHANNELS:
    print(f" - {c.name} ({c.id}) -> {c.sound}")

# --------------------------
# Sound player (system fallback)
# --------------------------
SYSTEM = platform.system()


def _exists_sound(path: str) -> bool:
    return Path(path).is_file()


def _play_via_subprocess(cmd: List[str]) -> None:
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=False)
    except Exception as e:
        print(f"[sound] subprocess failed {cmd}: {e}")


def play_sound(path: str) -> None:
    """
    Try a sequence of players appropriate for the OS.
    This is synchronous and intended to be run in executor to avoid blocking the event loop.
    """
    p = Path(path)
    if not p.exists():
        print(f"[sound] file not found: {path}")
        return

    if SYSTEM == "Darwin":
        # macOS: afplay exists by default
        _play_via_subprocess(["afplay", str(p)])
        return

    if SYSTEM == "Windows":
        # Try powershell PlaySync (works for WAV/MP3 on many installs)
        try:
            # Use -NoProfile -Command to avoid loading profile
            ps_cmd = [
                "powershell",
                "-NoProfile",
                "-Command",
                f'(New-Object Media.SoundPlayer "{str(p)}").PlaySync();' if str(p).lower().endswith(".wav") else f'(New-Object Media.SoundPlayer "{str(p)}").PlaySync();'
            ]
            _play_via_subprocess(ps_cmd)
            return
        except Exception:
            pass
        # fallback to 'start' (may open external app)
        try:
            os.startfile(str(p))
        except Exception as e:
            print(f"[sound] windows fallback failed: {e}")
        return

    # For Linux and other Unixes: try ffplay, paplay, aplay, mpv, xdg-open
    # prefer ffplay (from ffmpeg) since it supports many formats
    linux_cmds = [
        ["ffplay", "-nodisp", "-autoexit", str(p)],
        ["paplay", str(p)],
        ["aplay", str(p)],
        ["mpv", "--no-video", str(p)],
        ["xdg-open", str(p)],
    ]
    for cmd in linux_cmds:
        try:
            _play_via_subprocess(cmd)
            return
        except FileNotFoundError:
            continue
    # If none found, last attempt: use xdg-open (already attempted) or print message
    print("[sound] No suitable player found; install ffmpeg (ffplay) or mpv or paplay/aplay.")


# --------------------------
# Discord bot
# --------------------------
intents = Intents.default()
intents.messages = True
intents.message_content = True
intents.guilds = True

client = discord.Client(intents=intents)

# last play timestamp per channel id (for debounce)
_last_play_ts: Dict[int, float] = {}


@client.event
async def on_ready():
    print(f"[bot] Connected as {client.user} (id={client.user.id})")


@client.event
async def on_message(message: discord.Message):
    # ignore bot's own messages
    if message.author.id == client.user.id:
        return

    cfg = CHANNEL_MAP.get(message.channel.id)
    if not cfg or not cfg.enabled:
        return

    # debounce
    now = time.time()
    last = _last_play_ts.get(cfg.id, 0.0)
    if now - last < DEBOUNCE_SECONDS:
        # skip
        # print(f"[debounce] skipping play for {cfg.name} ({cfg.id}), {now-last:.1f}s < {DEBOUNCE_SECONDS}s")
        return

    if not cfg.sound:
        print(f"[warn] no sound configured for channel {cfg.name} ({cfg.id})")
        return

    # resolve relative path from script cwd
    sound_path = cfg.sound
    if not Path(sound_path).is_absolute():
        sound_path = str(Path.cwd() / sound_path)

    if not _exists_sound(sound_path):
        print(f"[warn] sound file for channel {cfg.name} not found: {sound_path}")
        return

    print(f"[event] message in {message.channel} by {message.author} -> playing {sound_path}")
    # schedule play in executor so we don't block the event loop
    loop = asyncio.get_running_loop()
    loop.run_in_executor(None, play_sound, sound_path)
    _last_play_ts[cfg.id] = now


# --------------------------
# Graceful shutdown support
# --------------------------
async def _shutdown_signal():
    # wait until client closes or cancelled
    try:
        await client.wait_until_close()
    except Exception:
        pass


def main():
    try:
        client.run(TOKEN)
    except KeyboardInterrupt:
        print("Interrupted by user")
    except Exception as e:
        print(f"[error] client.run failed: {e}")
        raise


if __name__ == "__main__":
    main()
