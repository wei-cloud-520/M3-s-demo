#!/usr/bin/env python3
"""单独保存 DeepSeek 结果"""

import json, requests, os, time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAPTERS_DIR = os.path.join(BASE_DIR, "chapters")

DEEPSEEK_KEY = "sk-04be5f4139ed46778074b390d4bddeec"

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

print("=== DeepSeek V4-Pro (Think High) ===")
start = time.time()
resp = requests.post("https://api.deepseek.com/chat/completions",
    headers={"Authorization": f"Bearer {DEEPSEEK_KEY}", "Content-Type": "application/json"},
    json={
        "model": "deepseek-v4-pro",
        "messages": [
            {"role": "system", "content": "你是一个中文小说家。直接输出小说正文，不需要章节标题，不要任何前言后记。中文写作，4000-5000字。"},
            {"role": "user", "content": f"请根据以下信息重写第1章的完整正文：\n\n{CONTEXT}"}
        ],
        "max_tokens": 16000,
        "reasoning_effort": "high",
        "thinking": {"type": "enabled"}
    },
    timeout=600
)
elapsed = time.time() - start
data = resp.json()
content = data["choices"][0]["message"]["content"]
reasoning = data["choices"][0]["message"].get("reasoning_content", "")
usage = data.get("usage", {})
print(f"耗时: {elapsed:.1f}s")
print(f"Token 用量: {usage}")
print(f"推理长度: {len(reasoning)} 字符")

os.makedirs(CHAPTERS_DIR, exist_ok=True)
ds_path = os.path.join(CHAPTERS_DIR, "ch01_deepseek.md")
with open(ds_path, "w", encoding="utf-8") as f:
    f.write(f"# 第一章：编译（DeepSeek V4-Pro Think High）\n\n{content}")
print(f"\n已保存: {ds_path} ({len(content)} 字)")

# === GLM-5.1 ===
print("\n=== GLM-5.1 (Coding Endpoint) ===")
glm_key = "4a9f477b2a6b425d969c605e8bdd8114.WhSvKwjSSndiRuuV"
glm_start = time.time()
glm_resp = requests.post("https://open.bigmodel.cn/api/coding/paas/v4/chat/completions",
    headers={"Authorization": f"Bearer {glm_key}", "Content-Type": "application/json"},
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
glm_elapsed = time.time() - glm_start
glm_data = glm_resp.json()
print(f"GLM Status: {glm_resp.status_code}")
if glm_resp.status_code == 200:
    glm_content = glm_data["choices"][0]["message"]["content"]
    glm_usage = glm_data.get("usage", {})
    print(f"耗时: {glm_elapsed:.1f}s")
    print(f"Token 用量: {glm_usage}")
    glm_path = os.path.join(CHAPTERS_DIR, "ch01_glm51.md")
    with open(glm_path, "w", encoding="utf-8") as f:
        f.write(f"# 第一章：编译（GLM-5.1）\n\n{glm_content}")
    print(f"已保存: {glm_path} ({len(glm_content)} 字)")
else:
    print(f"错误: {glm_resp.text[:500]}")
