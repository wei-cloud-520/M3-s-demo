#!/usr/bin/env python3
"""
novel-writer.py — 代码梦境 自动写作脚本

用法:
  python3 scripts/novel-writer.py [章节号]        # 生成指定章节
  python3 scripts/novel-writer.py                 # 生成下一章
  python3 scripts/novel-writer.py --dry-run [章节号]  # 只生成节拍，不写正文

模型分配:
  - 正文扩写/大纲: deepseek-v4-pro
  - 节拍/检查/润色: deepseek-v4-flash
"""

import os
import sys
import json
import requests

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAPTERS_DIR = os.path.join(BASE_DIR, "chapters")
SUMMARIES_DIR = os.path.join(BASE_DIR, "summaries")

API_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-04be5f4139ed46778074b390d4bddeec")
API_URL = "https://api.deepseek.com/chat/completions"

# 大纲文件（每行格式：章节号|标题|剧情节拍描述）
OUTLINE_FILE = os.path.join(BASE_DIR, "outline.csv")


def read_file(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""


def read_chapter(num):
    path = os.path.join(CHAPTERS_DIR, f"ch{num:02d}.md")
    return read_file(path)


def read_summary(num):
    path = os.path.join(SUMMARIES_DIR, f"ch{num:02d}.md")
    return read_file(path)


def get_next_chapter():
    """找到下一章的编号"""
    existing = []
    if os.path.exists(CHAPTERS_DIR):
        for f in os.listdir(CHAPTERS_DIR):
            if f.startswith("ch") and f.endswith(".md"):
                try:
                    num = int(f[2:4])
                    existing.append(num)
                except ValueError:
                    pass
    if not existing:
        return 1
    return max(existing) + 1


def get_chapter_outline(num):
    """从大纲中获取指定章节的标题和节拍"""
    outline = read_file(os.path.join(BASE_DIR, "outline.md"))
    # 从大纲 markdown 中提取指定章节
    lines = outline.split("\n")
    in_chapter = False
    chapter_title = ""
    chapter_beats = []
    for line in lines:
        if line.strip().startswith(f"**第{num}章") or line.strip().startswith(f"**{num}"):
            in_chapter = True
            chapter_title = line.strip().replace("**", "").replace("—", "").strip()
            continue
        if in_chapter:
            if line.strip().startswith("**第") or line.strip().startswith(f"**{num+1}"):
                break
            if line.strip().startswith("---"):
                continue
            if line.strip().startswith("###"):
                break
            chapter_beats.append(line)
    return chapter_title, "\n".join(chapter_beats).strip()


def build_context(chapter_num, chapter_title, chapter_beats):
    """构建发送给模型的上下文"""
    style = read_file(os.path.join(BASE_DIR, "standards", "style-guide.md"))
    setting = read_file(os.path.join(BASE_DIR, "setting.md"))
    outline = read_file(os.path.join(BASE_DIR, "outline.md"))

    # 读取前一章正文
    prev_chapter = read_chapter(chapter_num - 1) if chapter_num > 1 else ""

    # 读取所有已有章节摘要（提供长期上下文）
    summaries = []
    if os.path.exists(SUMMARIES_DIR):
        for f in sorted(os.listdir(SUMMARIES_DIR)):
            if f.endswith(".md"):
                summaries.append(read_file(os.path.join(SUMMARIES_DIR, f)))
    all_summaries = "\n".join(summaries)

    context = f"""## 写作规范
{style}

## 世界观设定
{setting}

## 完整大纲
{outline}

## 已有章节摘要（保持一致性）
{all_summaries}

## 上一章正文
{prev_chapter[:3000] if prev_chapter else "（这是第一章）"}

## 当前任务：第{chapter_num}章 — {chapter_title}

剧情节拍：
{chapter_beats}"""

    return context


def call_deepseek(messages, model="deepseek-v4-pro", max_tokens=8000, temperature=0.8):
    """调用 DeepSeek API"""
    resp = requests.post(API_URL,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature
        },
        timeout=180
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def generate_chapter(chapter_num, dry_run=False):
    """生成一章"""
    title, beats = get_chapter_outline(chapter_num)
    if not beats:
        print(f"错误：找不到第{chapter_num}章的大纲")
        sys.exit(1)

    print(f"=== 第{chapter_num}章：{title} ===")

    if dry_run:
        print(f"剧情节拍：\n{beats}")
        print("\n[dry-run 模式，只生成节拍]")
        return

    context = build_context(chapter_num, title, beats)

    # Step 1: 生成正文
    print("正在生成正文...")
    messages = [
        {"role": "system", "content": "你是一个中文小说家。直接输出小说正文，不需要章节标题，不要任何前言后记。中文写作，2000-3000字。"},
        {"role": "user", "content": f"请根据以下信息写第{chapter_num}章的完整正文：\n\n{context}"}
    ]
    content = call_deepseek(messages, model="deepseek-v4-pro")

    # 保存正文
    os.makedirs(CHAPTERS_DIR, exist_ok=True)
    chapter_path = os.path.join(CHAPTERS_DIR, f"ch{chapter_num:02d}.md")
    with open(chapter_path, "w", encoding="utf-8") as f:
        f.write(f"# 第{chapter_num}章：{title}\n\n{content}")
    print(f"正文已保存：{chapter_path}")

    # Step 2: 生成摘要
    print("正在生成摘要...")
    summary_messages = [
        {"role": "system", "content": "用200字以内总结以下章节的关键事件、人物变化和伏笔。纯文本，不要markdown格式。"},
        {"role": "user", "content": content}
    ]
    summary = call_deepseek(summary_messages, model="deepseek-v4-flash", max_tokens=500, temperature=0.3)

    os.makedirs(SUMMARIES_DIR, exist_ok=True)
    summary_path = os.path.join(SUMMARIES_DIR, f"ch{chapter_num:02d}.md")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary)
    print(f"摘要已保存：{summary_path}")

    print(f"\n=== 第{chapter_num}章生成完成 ===")


if __name__ == "__main__":
    dry_run = "--dry-run" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]

    if args:
        chapter_num = int(args[0])
    else:
        chapter_num = get_next_chapter()

    generate_chapter(chapter_num, dry_run=dry_run)
