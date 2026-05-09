"""
凯尔希 TTS 推理脚本
用法: python tts_kaltsit.py "要合成的文本"
输出: output.wav（自动播放）
"""

import sys
import os
from gradio_client import Client

API_URL = "http://127.0.0.1:9872"
REF_AUDIO = "/data/kaltsit_zh/char_003_kalts_boc#6_CN_001.wav"
TOP_K = 20
TOP_P = 0.6
TEMPERATURE = 0.3
SLICE_MODE = "不切分"

# 如果文本超过一定长度，用"凑四句一切"来避免截断
MAX_LEN = 100

def tts(text):
    c = Client(API_URL)

    if len(text) > MAX_LEN:
        slice_mode = "凑四句一切"
    else:
        slice_mode = SLICE_MODE

    result = c.predict(
        REF_AUDIO,
        "",          # 无参考模式，参考文本留空
        "Chinese",
        text,
        "Chinese",
        slice_mode,
        TOP_K, TOP_P, TEMPERATURE,
        True,        # 无参考模式
        fn_index=3
    )
    return result

def main():
    if len(sys.argv) < 2:
        print("用法: python tts_kaltsit.py \"要合成的文本\"")
        print("示例: python tts_kaltsit.py \"博士，我们又见面了。\"")
        # 交互模式
        text = input("输入文本（多行输入空行结束）:\n")
    else:
        text = sys.argv[1]

    if not text.strip():
        print("文本为空，退出。")
        return

    print(f"正在合成: {text[:50]}{'...' if len(text) > 50 else ''}")

    try:
        result = tts(text)
        print(f"生成成功: {result}")

        # 拷贝到当前目录
        output = "output.wav"
        os.system(f'copy "{result}" "{output}"" >nul 2>&1')
        # 用Windows自带播放
        os.system(f'start "" "{output}"')
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    main()
