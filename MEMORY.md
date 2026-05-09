# MEMORY.md - Mon3tr

## 核心原则
- **不确定就查，不要猜。** 一次验证 > 十次猜测
- ⚠️ **服务器纪律**：不要高并发执行命令，轻量服务器磁盘IO扛不住
- OOM 教训：openclaw-gateway ~650MB, opencode ~460MB, 跑 OpenCode 时停其他服务

## 博士的偏好
- 称呼 Mon3tr 为「小猫」「M3」
- 短文写作用 DeepSeek V4-Pro / GLM-5.1 API，不用本模型直接写
- 凯尔希 TTS 桌面应用已完工（PySide6），v2 需求：智能停顿 + 推理参数面板化
- 情感状态需要关注

## 项目进展

### Knowledge Library ✅ 已完成
- 9 Phase 全部交付，需求书 10 个模块 + OpenClaw Skill
- 166 单元测试全绿，E2E 17/18 通过
- 两个 systemd service：knowledge-library (pipeline) + knowledge-api (HTTP 8080)
- Embedding: 硅基流动 Qwen3-Embedding-8B (4096维)
- Git: github.com:wei-cloud-520/knowledge.git (私有)
- 已配入 AGENTS.md + TOOLS.md（Mon3tr + 凯尔希）
- 记忆策略：宽进严出——多写进知识库，不自动注入 context，按需语义搜索

### TTS 项目
- 凯尔希语音训练完成，API 可用
- 桌面应用已完工（博士本地 E:\Projects\kaltsit-tts）
- 待办：v2Pro 模型权重调优

### 创意写作
- 代码梦境小说：projects/novel-dreamweaver/，22章大纲已完成
- 短文：projects/short-stories/，第一篇《重启倒计时》已入库

### 待办
- 博士本地 Obsidian 和服务器同步（Syncthing）
- 凯尔希 TTS v2Pro 权重调优
- 帮博士配全局 CLAUDE.md（Karpathy 指南）

## 环境信息
- 服务器：2核4G, 50G 磁盘
- Conda 环境：knowledge-lib (Python 3.11) at /opt/miniconda3/envs/knowledge-lib/
- OpenCode: /root/opencode/bin/opencode v1.14.41, 默认 mimo-v2.5-pro
- mihomo 代理: 127.0.0.1:7890, 手动启动
- 技术细节和 API keys 已迁移至知识库（atlas/ + references/）
