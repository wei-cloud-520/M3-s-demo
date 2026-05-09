#!/usr/bin/env python3
"""辅助排查音频标注是否正确。播放音频的同时显示对应文本。"""

import json
import subprocess
import sys
import os
import time

# 配置
METADATA_FILE = "boc6_metadata.json"
AUDIO_DIR = "."
PLAYER = "ffplay"  # Windows 上也适用，需在 PATH 中；或改为 "ffplay.exe"
PLAYER_ARGS = ["-nodisp", "-autoexit", "-loglevel", "quiet"]

def play_audio(filepath):
    """播放音频文件，等待播放结束"""
    if not os.path.exists(filepath):
        print(f"  [错误] 文件不存在: {filepath}")
        return False
    proc = subprocess.run([PLAYER, *PLAYER_ARGS, filepath], timeout=60)
    return proc.returncode == 0

def main():
    meta_path = sys.argv[1] if len(sys.argv) > 1 else METADATA_FILE
    audio_dir = sys.argv[2] if len(sys.argv) > 2 else AUDIO_DIR

    with open(meta_path, "r", encoding="utf-8") as f:
        entries = json.load(f)

    print(f"共 {len(entries)} 条，从第 0 条开始\n")
    print("操作: Enter=下一条  r=重播当前  p=上一条  q=退出  [数字]=跳转到指定序号\n")

    i = 0
    while i < len(entries):
        e = entries[i]
        wav = os.path.join(audio_dir, e["file"])
        print(f"--- [{i+1}/{len(entries)}] {e['title']} ---")
        print(f"文件: {e['file']}")
        print(f"文本: {e['text']}")
        print()

        play_audio(wav)

        while True:
            try:
                cmd = input("→ ").strip().lower()
            except (EOFError, KeyboardInterrupt):
                print("\n退出")
                return

            if cmd == "" or cmd == "n":
                i += 1
                break
            elif cmd == "r":
                play_audio(wav)
            elif cmd == "p":
                if i > 0:
                    i -= 1
                break
            elif cmd == "q":
                print("退出")
                return
            elif cmd.isdigit():
                idx = int(cmd) - 1
                if 0 <= idx < len(entries):
                    i = idx
                break
            else:
                print("无效输入")

    print(f"\n全部 {len(entries)} 条检查完毕")

if __name__ == "__main__":
    main()
