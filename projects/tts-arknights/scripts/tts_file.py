"""
凯尔希 TTS - 在Docker容器内运行
用法: docker exec -it <容器ID> bash -c "python /data/tts_file.py /data/input.txt"
输出: /data/output.wav
"""

import sys
import os
import shutil
from gradio_client import Client

API_URL = "http://127.0.0.1:9872"
REF_AUDIO = "/data/kaltsit_zh/char_003_kalts_boc#6_CN_001.wav"
TOP_K = 20
TOP_P = 0.6
TEMPERATURE = 0.3

def tts(text):
    c = Client(API_URL)

    if len(text) > 100:
        slice_mode = "凑四句一切"
    else:
        slice_mode = "不切分"

    result = c.predict(
        REF_AUDIO, "", "Chinese",
        text, "Chinese",
        slice_mode,
        TOP_K, TOP_P, TEMPERATURE,
        True,
        fn_index=3
    )
    return result

def main():
    if len(sys.argv) < 2:
        print("用法: python /data/tts_file.py /data/input.txt [output.wav]")
        return

    input_file = sys.argv[1]

    if len(sys.argv) >= 3:
        output_file = sys.argv[2]
    else:
        output_file = os.path.splitext(input_file)[0] + ".wav"

    if not os.path.exists(input_file):
        print(f"文件不存在: {input_file}")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        text = f.read().strip()

    if not text:
        print("文件内容为空!")
        return

    print(f"输入: {input_file}")
    print(f"文本: {text[:80]}{'...' if len(text) > 80 else ''}")
    print("正在合成...")

    try:
        result = tts(text)
        shutil.copy2(result, output_file)
        print(f"输出: {output_file}")
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    main()
