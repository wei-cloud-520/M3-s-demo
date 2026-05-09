"""
从 PRTS Wiki 下载凯尔希的中文语音和文本标注。
音频源: https://prts.wiki (torappu.prts.wiki CDN)
"""

import re
import json
import urllib.request
import urllib.parse
import os
import time

CHAR_KEY = "char_003_kalts"
AUDIO_BASE = "https://torappu.prts.wiki"
AUDIO_PATH = f"voice_cn/{CHAR_KEY}"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "kaltsit_zh")
os.makedirs(OUTPUT_DIR, exist_ok=True)

def fetch_wikitext():
    """从 PRTS API 获取语音记录页面的 wikitext"""
    page = urllib.parse.quote("凯尔希/语音记录")
    url = f"https://prts.wiki/api.php?action=parse&page={page}&prop=wikitext&format=json"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read())
    return data["parse"]["wikitext"]["*"]


def parse_voice_entries(wt):
    """解析语音条目，返回 [(filename, title, cn_text), ...]"""
    entries = []
    # 匹配 |标题N=... |台词N=... |语音N=...
    pattern = (
        r'\|标题(\d+)=(.+?)(?:\n|\|)'
        r'.*?\|台词\1=(?:\{\{VoiceData/word\|中文\|(.+?))\}\}'
        r'.*?\|语音\1=(.+?)(?:\n|\|)'
    )
    for m in re.finditer(pattern, wt, re.DOTALL):
        idx, title, text, voice_file = m.groups()
        title = title.strip()
        text = text.strip()
        voice_file = voice_file.strip()
        # 清理文本中的模板标记
        text = re.sub(r'\{\{[^}]+\}\}', '', text).strip()
        if voice_file:
            entries.append((voice_file, title, text))
    return entries


def download_audio(filename):
    """下载单个音频文件，返回本地路径"""
    url = f"{AUDIO_BASE}/{AUDIO_PATH}/{urllib.parse.quote(filename)}"
    local_path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(local_path):
        print(f"  [skip] {filename} already exists")
        return local_path
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            with open(local_path, "wb") as f:
                f.write(resp.read())
        size_kb = os.path.getsize(local_path) / 1024
        print(f"  [ok] {filename} ({size_kb:.1f} KB)")
        return local_path
    except Exception as e:
        print(f"  [fail] {filename}: {e}")
        return None


def main():
    print("Fetching wikitext from PRTS...")
    wt = fetch_wikitext()

    print("Parsing voice entries...")
    entries = parse_voice_entries(wt)
    print(f"Found {len(entries)} voice entries\n")

    metadata = []
    success = 0
    for i, (voice_file, title, text) in enumerate(entries):
        print(f"[{i+1}/{len(entries)}] {title}: {text[:40]}...")
        local = download_audio(voice_file)
        if local:
            metadata.append({
                "file": voice_file,
                "title": title,
                "text": text,
                "path": os.path.abspath(local),
            })
            success += 1
        time.sleep(0.3)  # 礼貌爬取

    # 保存元数据
    meta_path = os.path.join(OUTPUT_DIR, "metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    print(f"\nDone! Downloaded {success}/{len(entries)} files")
    print(f"Metadata saved to {meta_path}")


if __name__ == "__main__":
    main()
