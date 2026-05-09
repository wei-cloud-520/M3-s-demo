"""
从 HuggingFace deepghs/arknights_voices_zh 的 voices.tar 中
用 HTTP Range 按偏移量提取凯尔希的中文语音文件。
offset 直接指向 WAV 数据（无 tar header）。
"""

import json
import os
import urllib.request
import urllib.parse
import re
import time

PROXY = "http://127.0.0.1:7890"
TAR_URL = "https://huggingface.co/datasets/deepghs/arknights_voices_zh/resolve/main/voices.tar"
META_URL = "https://huggingface.co/datasets/deepghs/arknights_voices_zh/resolve/main/voices.json"
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "kaltsit_zh")
os.makedirs(OUTPUT_DIR, exist_ok=True)


def proxy_opener():
    proxy = urllib.request.ProxyHandler({"https": PROXY, "http": PROXY})
    return urllib.request.build_opener(proxy)


def fetch_json(url):
    opener = proxy_opener()
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with opener.open(req, timeout=30) as resp:
        return json.loads(resp.read())


def download_range(url, offset, size):
    opener = proxy_opener()
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Range": f"bytes={offset}-{offset + size - 1}",
    }
    req = urllib.request.Request(url, headers=headers)
    with opener.open(req, timeout=120) as resp:
        return resp.read()


def main():
    print("Fetching voices.json metadata...")
    data = fetch_json(META_URL)
    files = data["files"]

    # 筛选凯尔希的文件
    kal_files = {k: v for k, v in files.items() if "kalts" in k.lower()}
    sorted_files = sorted(kal_files.items(), key=lambda x: x[1]["offset"])
    print(f"Found {len(sorted_files)} Kaltsit voice files, total ~{sum(v['size'] for _,v in sorted_files)//1024//1024}MB\n")

    # 逐个下载
    success = 0
    for i, (filename, info) in enumerate(sorted_files):
        offset = info["offset"]
        size = info["size"]
        print(f"[{i+1}/{len(sorted_files)}] {filename} ({size//1024}KB)...", end=" ", flush=True)

        try:
            wav_data = download_range(TAR_URL, offset, size)
            out_path = os.path.join(OUTPUT_DIR, filename)
            with open(out_path, "wb") as f:
                f.write(wav_data)
            print(f"ok ({len(wav_data)//1024}KB)")
            success += 1
        except Exception as e:
            print(f"FAILED: {e}")

        time.sleep(0.2)

    print(f"\nExtracted {success}/{len(sorted_files)} files")

    # 获取文本标注
    print("\nFetching text annotations from PRTS...")
    fetch_prts_texts(OUTPUT_DIR)


def fetch_prts_texts(output_dir):
    opener = proxy_opener()
    page = urllib.parse.quote("凯尔希/语音记录")
    url = f"https://prts.wiki/api.php?action=parse&page={page}&prop=wikitext&format=json"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with opener.open(req, timeout=15) as resp:
        data = json.loads(resp.read())
    wt = data["parse"]["wikitext"]["*"]

    # 解析: |语音N=CN_XXX.wav 对应 |标题N=... |台词N=...
    texts = {}
    pattern = r'\|标题(\d+)=(.+?)(?:\n|\|).*?\|语音\1=(.+?)(?:\n|\|).*?\|台词\1=\{\{VoiceData/word\|中文\|(.+?)\}\}'
    for m in re.finditer(pattern, wt, re.DOTALL):
        title = m.group(2).strip()
        voice_file = m.group(3).strip()
        text = re.sub(r'\{\{[^}]+\}\}', '', m.group(4)).strip()
        texts[voice_file] = {"title": title, "text": text}

    # 匹配本地文件
    metadata = []
    for lf in sorted(os.listdir(output_dir)):
        if not lf.endswith('.wav'):
            continue
        basename = os.path.splitext(lf)[0]  # char_003_kalts_CN_001
        # 提取 CN_001 部分
        cn_id = lf.replace('char_003_kalts_', '').replace('.wav', '')
        info = texts.get(cn_id, {"title": cn_id, "text": ""})
        metadata.append({
            "file": lf,
            "title": info["title"],
            "text": info["text"],
            "path": os.path.join(output_dir, lf),
        })

    meta_path = os.path.join(output_dir, "metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    matched = sum(1 for m in metadata if m["text"])
    print(f"Metadata: {matched}/{len(metadata)} entries matched with text")
    print(f"Saved to {meta_path}")


if __name__ == "__main__":
    main()
