#!/usr/bin/env python3
"""单独调用 GLM-5.1 Coding Endpoint 重写第一章"""

import json, requests, os, time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAPTERS_DIR = os.path.join(BASE_DIR, "chapters")
GLM_KEY = "4a9f477b2a6b425d969c605e8bdd8114.WhSvKwjSSndiRuuV"

def read_file(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

style = read_file(os.path.join(BASE_DIR, "standards", "style-guide.md"))
setting = read_file(os.path.join(BASE_DIR, "setting.md"))
outline = read_file(os.path.join(BASE_DIR, "outline.md"))
outline_ch1 = outline.split("**第2章")[0] if "**第2章" in outline else outline

CONTEXT = f"""## 写作规范
{style}

## 世界观设定
{setting}

## 第一章大纲
{outline_ch1}

## 写作要求
- 这是第一章"编译"，重写时保持核心剧情：深夜调试→段错误→逼真梦境→发现代码与梦对应
- 4000-5000字
- 直接输出小说正文，不需要章节标题，不要任何前言后记
- 风格克制留白，短句为主，通过感官细节传达情感
- 代码片段必须语法正确"""

print("=== GLM-5.1 (Coding Endpoint) ===")
start = time.time()
resp = requests.post("https://open.bigmodel.cn/api/coding/paas/v4/chat/completions",
    headers={"Authorization": f"Bearer {GLM_KEY}", "Content-Type": "application/json"},
    json={
        "model": "glm-5.1",
        "messages": [
            {"role": "system", "content": "你是一个中文小说家。直接输出小说正文，不需要章节标题，不要任何前言后记。中文写作，4000-5000字。"},
            {"role": "user", "content": f"请根据以下信息重写第1章的完整正文：\n\n{CONTEXT}"}
        ],
        "max_tokens": 16000,
        "temperature": 0.8
    },
    timeout=600
)
elapsed = time.time() - start
print(f"Status: {resp.status_code}")
print(f"耗时: {elapsed:.1f}s")

if resp.status_code != 200:
    print(f"错误: {resp.text[:500]}")
    exit(1)

data = resp.json()
content = data["choices"][0]["message"]["content"]
usage = data.get("usage", {})
print(f"Token 用量: {usage}")

os.makedirs(CHAPTERS_DIR, exist_ok=True)
path = os.path.join(CHAPTERS_DIR, "ch01_glm51.md")
with open(path, "w", encoding="utf-8") as f:
    f.write(f"# 第一章：编译（GLM-5.1）\n\n{content}")
print(f"\n已保存: {path} ({len(content)} 字)")
