#!/usr/bin/env python3
"""gen_summary.py — 为已有章节补生成摘要"""
import os
import requests

CHAPTERS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "chapters")
SUMMARIES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "summaries")
API_KEY = os.environ.get("DEEPSEEK_API_KEY", "sk-04be5f4139ed46778074b390d4bddeec")

for f in sorted(os.listdir(CHAPTERS_DIR)):
    if not f.endswith(".md"):
        continue
    num = f[2:4]
    summary_path = os.path.join(SUMMARIES_DIR, f)
    if os.path.exists(summary_path):
        continue
    print(f"Generating summary for {f}...")
    with open(os.path.join(CHAPTERS_DIR, f), "r") as fh:
        content = fh.read()
    resp = requests.post("https://api.deepseek.com/chat/completions",
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json={
            "model": "deepseek-v4-flash",
            "messages": [
                {"role": "system", "content": "用200字以内总结以下章节的关键事件、人物变化和伏笔。纯文本，不要markdown格式。"},
                {"role": "user", "content": content}
            ],
            "max_tokens": 500, "temperature": 0.3
        }, timeout=60)
    summary = resp.json()["choices"][0]["message"]["content"]
    os.makedirs(SUMMARIES_DIR, exist_ok=True)
    with open(summary_path, "w") as fh:
        fh.write(summary)
    print(f"Done: {summary_path}")
