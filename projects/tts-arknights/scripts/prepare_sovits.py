"""
将凯尔希语音数据转换为 GPT-SoVITS 训练所需的格式。
在容器内运行，或本地运行后把产物复制进容器。

GPT-SoVITS 需要的格式:
  audio_path|speaker_name|language|text

音频需要放在固定目录下，格式: <speaker_name>/<filename>
"""

import json
import os
import shutil

# 配置
INPUT_DIR = "/workspace/input"  # 容器内路径
DATA_DIR = os.path.join(INPUT_DIR, "kaltsit_zh")  # 解压后的数据目录
SPEAKER_NAME = "kaltsit"
LANG = "zh"

# SoVITS 训练需要的音频存放目录
AUDIO_OUTPUT = os.path.join(INPUT_DIR, "audio", SPEAKER_NAME)
os.makedirs(AUDIO_OUTPUT, exist_ok=True)


def main():
    meta_path = os.path.join(DATA_DIR, "metadata.json")
    with open(meta_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)

    # 只用有文本标注的文件（基础37条）
    valid = [m for m in metadata if m.get("text")]
    print(f"Total: {len(metadata)}, with text: {len(valid)}")

    # 复制音频到 SoVITS 格式目录
    list_path = os.path.join(INPUT_DIR, f"{SPEAKER_NAME}.list")
    with open(list_path, "w", encoding="utf-8") as lf:
        for m in valid:
            src = os.path.join(DATA_DIR, m["file"])
            dst_name = os.path.basename(m["file"])
            dst = os.path.join(AUDIO_OUTPUT, dst_name)
            if not os.path.exists(dst):
                shutil.copy2(src, dst)

            # 格式: audio_path|speaker|language|text
            audio_path = f"audio/{SPEAKER_NAME}/{dst_name}"
            lf.write(f"{audio_path}|{SPEAKER_NAME}|{LANG}|{m['text']}\n")

    print(f"Generated {list_path}")
    print(f"Audio files in {AUDIO_OUTPUT}")
    print(f"\nExample entries:")
    with open(list_path, "r", encoding="utf-8") as lf:
        for i, line in enumerate(lf):
            if i >= 3:
                break
            print(f"  {line.strip()}")


if __name__ == "__main__":
    main()
