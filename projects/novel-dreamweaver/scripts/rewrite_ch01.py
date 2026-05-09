#!/usr/bin/env python3
"""重写第一章，并行调用 DeepSeek V4-Pro 和 GLM-5.1 对比"""

import json
import requests
import os
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CHAPTERS_DIR = os.path.join(BASE_DIR, "chapters")

DEEPSEEK_KEY = "sk-04be5f4139ed46778074b390d4bddeec"
GLM_KEY = "4a9f477b2a6b425d969c605e8bdd8114.WhSvKwjSSndiRuuV"

def read_file(path):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    return ""

style = read_file(os.path.join(BASE_DIR, "standards", "style-guide.md"))
setting = read_file(os.path.join(BASE_DIR, "setting.md"))
outline = read_file(os.path.join(BASE_DIR, "outline.md"))

# 只取第一章的节拍
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
- 直接输出小说正文，不需要章节标题，不要前言后记
- 风格克制留白，短句为主，通过感官细节传达情感
- 代码片段必须语法正确"""

def call_deepseek():
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
    return content, elapsed, usage

def call_glm():
    print("=== GLM-5.1 ===")
    start = time.time()
    resp = requests.post("https://open.bigmodel.cn/api/paas/v4/chat/completions",
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
    data = resp.json()
    content = data["choices"][0]["message"]["content"]
    usage = data.get("usage", {})
    print(f"耗时: {elapsed:.1f}s")
    print(f"Token 用量: {usage}")
    return content, elapsed, usage

if __name__ == "__main__":
    import concurrent.futures
    
    os.makedirs(CHAPTERS_DIR, exist_ok=True)
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        ds_future = pool.submit(call_deepseek)
        glm_future = pool.submit(call_glm)
        
        ds_result = ds_future.result()
        glm_result = glm_future.result()
    
    ds_content, ds_time, ds_usage = ds_result
    glm_content, glm_time, glm_usage = glm_result
    
    # 保存 DeepSeek 版本（覆盖 ch01.md）
    ds_path = os.path.join(CHAPTERS_DIR, "ch01_deepseek.md")
    with open(ds_path, "w", encoding="utf-8") as f:
        f.write(f"# 第一章：编译（DeepSeek V4-Pro Think High）\n\n{ds_content}")
    print(f"\nDeepSeek 版本已保存: {ds_path} ({len(ds_content)} 字)")
    
    # 保存 GLM 版本
    glm_path = os.path.join(CHAPTERS_DIR, "ch01_glm51.md")
    with open(glm_path, "w", encoding="utf-8") as f:
        f.write(f"# 第一章：编译（GLM-5.1）\n\n{glm_content}")
    print(f"GLM 版本已保存: {glm_path} ({len(glm_content)} 字)")
    
    # 汇总对比
    print("\n========== 对比 ==========")
    print(f"DeepSeek V4-Pro: {len(ds_content)} 字, {ds_time:.1f}s, tokens={ds_usage}")
    print(f"GLM-5.1:         {len(glm_content)} 字, {glm_time:.1f}s, tokens={glm_usage}")
