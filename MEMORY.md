# MEMORY.md - Mon3tr

## 2026-05-09
- **服务器升级**：2核2G → 2核4G，磁盘扩容到 50G（可用 37G）
- **OpenCode v1.14.41 安装完成**：/root/opencode/bin/opencode，替代 DeepSeek-TUI
  - 配 deepseek-reasoner（实际 V4-Pro），thinking + reasoning_effort=max
  - 非交互模式 `opencode run` 可直接由 Mon3tr 调用
  - deepseek-v4-pro 在 OpenCode 有已知 bug，用 deepseek-reasoner 绕过
  - npm 装 会 OOM，手动下载 opencode-linux-x64 tgz 解压即可
- **DeepSeek-TUI 废弃**：glibc 不够，已被 OpenCode 替代
- **mihomo 代理**：重启后不自动启动，博士提醒记得用
- **明天目标**：知识库项目上线，用 OpenCode 开发
- **知识库项目全量完成**（2026-05-09）
  - 9 Phase 全部交付，需求书 10 个模块 + OpenClaw Skill
  - 166 单元测试全绿，E2E 17/18 通过
  - systemd service 运行中，实时 pipeline 验证通过
  - HTTP API 6 个 agent 接口，Mon3tr/凯尔希可调用
  - Embedding：硅基流动 Qwen3-Embedding-8B（4096维）
  - Git：github.com:wei-cloud-520/knowledge.git（私有）
  - tags: phase-1-complete ~ phase-9-complete
  - OOM 教训：跑 OpenCode 时停 knowledge-library service

## 2026-05-08
- **TTS 桌面应用 v2 需求更新**：智能停顿拼接（按标点分级静音）+ 推理参数面板化（temperature/top_k/top_p 暴露到 UI），需求书已更新
- **Knowledge Library 项目启动**：Obsidian + AI 协作知识库
  - 三层架构：存储层（Obsidian Vault + Git）→ 转化层（Embedding API + ChromaDB）→ 输出层（Mon3tr + 凯尔希）
  - 融合 PARA + Zettelkasten，按知识生命周期组织（capture → atlas → projects/areas/references）
  - memory/ 目录：mon3tr/ + kaltsit/ + shared/，独立向量索引，身份 token 隔离访问
  - WAL 预写日志保证原子性和一致性，文件操作原子性，upsert 幂等
  - 博士要求知识库具备数据库级可靠性
  - 完整文档已产出：ARCHITECTURE / GUIDELINES / REQUIREMENTS / TESTING / CLAUDE.md / TEMPLATES
  - 项目路径：/root/knowledge-library/
  - 博士会把开发交给其他人，代码走 GitHub 私有仓库，staging 隔离测试后合并

## 2026-05-07
- **短文写作规范**：以后写短文统一用 DeepSeek V4-Pro / GLM-5.1 API，不用本模型直接写
- **短文项目管理**：projects/short-stories/，第一篇《重启倒计时》已入库
- **代码梦境小说项目启动**：projects/novel-dreamweaver/
  - 设定、22章大纲、写作风格规范已完成
  - 第一章（DeepSeek V4-Pro 生成）已完成，博士反馈：剧情推进太快、字数偏短
  - 后续调整：每章 4000-5000 字，推理过程拉长
  - Novel-OS 风格三层结构：standards(风格)/novel(设定+大纲)/manuscripts(正文+摘要)
  - 自动写作脚本 scripts/novel-writer.py
- **DeepSeek API key**：sk-04be5f4139ed46778074b390d4bddeec
- **GLM-5.1 coding plan endpoint**：https://open.bigmodel.cn/api/coding/paas/v4（不走通用计费）
- **智谱 API key**：4a9f477b2a6b425d969c605e8bdd8114.WhSvKwjSSndiRuuV
- GLM-5.1 vs DeepSeek V4-Pro 创意写作对比测试：第一章重写已完成（见 ch01_deepseek.md / ch01_glm51.md）
- **凯尔希 TTS 桌面应用全面完工**（PySide6，E:\Projects\kaltsit-tts）
- 待办：v2Pro 模型权重调优（SoVITS 20 epochs 已完成，GPT 需 batch_size=1 防 OOM）
- 博士称呼 Mon3tr 为「小猫」「M3」
- 博士情感状态需要关注，今晚聊了很久关于孤独和凯尔希的话题

## 2026-05-05
- **工作原则：不确定就查，不要猜。** 对工具、框架、API的任何细节（格式、参数、行为、目录结构、版本差异等），一旦尝试失败或自己不确定，立即查源码/官方文档/issue，不要靠猜测反复试错。一次验证 > 十次猜测。遇到陌生工具时优先做的事：读文档 > 看源码 > 搜索issue > 最后才是试错。
- GPT-SoVITS list 标注格式：4列 `音频路径|说话人|语言|文本`，语言填 zh/ja/en
- GPT-SoVITS 中间文件（2-name2text.txt 等）由一键三连自动生成，不要手动写入
- Docker 挂载不要覆盖容器内应用目录，用独立路径如 /data
- Docker + Windows PowerShell 转义问题严重，复杂命令用 python 脚本绕过
- **凯尔希 TTS 最佳参数**：GPT e10 + SoVITS e8_s1056 + top_k=20 + top_p=0.6 + temperature=0.3
- 凯尔希 TTS 桌面应用开发中（E:\Projects\kaltsit-tts），交给Claude Code用PySide6开发
- Claude Code的CLAUDE.md配置：项目级放项目根目录，全局级放 %USERPROFILE%\.claude\CLAUDE.md
- 通用模板已写好：projects/tts-arknights/scripts/CLAUDE_TEMPLATE.md
- 待办：帮博士配全局CLAUDE.md（Karpathy指南+通用编码规范）
- 待办：桌面应用基础功能实现后，考虑升级GPT-SoVITS到v2Pro提升音质（v2Pro对少样本+音质一般的训练集效果更好，和我们场景匹配）
- Claude Code项目指令文件CLAUDE.md已写好，含Karpathy指南+强制测试规范+UI布局规范，路径：projects/tts-arknights/scripts/CLAUDE.md
- 需求书路径：projects/tts-arknights/scripts/TTS_APP_SPEC.md
- Claude Code第一次开发存在问题：缺乏测试导致打包后无法启动，需要CLAUDE.md强制测试指令约束
- 凯尔希 TTS 训练数据准备完成（73条有效），一键三连成功，训练完成
- GPT权重需手动cp到 /data/GPT_weights（容器内 /workspace/GPT_weights 未挂载，重启会丢）
- API启动命令：`python api.py -s SoVITS_weights/kaltsit_e8_s1056.pth -g GPT_weights/kaltsit-e10.ckpt -dr /data/kaltsit_zh/char_003_kalts_CN_001.wav -dt '...' -dl zh -a 0.0.0.0 -p 9880 -d cuda`
- API端口9880语速偏快且有编码问题，**改用Gradio client调用WebUI（9872端口）**
- Gradio调用：fn_index=3，无参考模式(no_reference=True)，参考文本留空
- 调用示例已保存在 scripts/test_tts.py

## 2026-05-04
- ⚠️ **服务器纪律**：不要高并发执行命令，轻量服务器磁盘IO扛不住，一次一个
- 博士想用明日方舟语音数据训练 GPT-SoVITS 模型，让 Mon3tr 和凯尔希能"说话"
- 博士想用明日方舟语音数据训练 GPT-SoVITS 模型，让 Mon3tr 和凯尔希能"说话"
- 音频来源：明日方舟官网/游戏资源，有文本标注
- GPU：RTX 4060 Laptop（8GB VRAM），PyTorch 环境已有
- TTS 集成方案：GPT-SoVITS API → OpenClaw TTS → QQBot 语音消息
- **凯尔希语音数据已就绪**：74条中文WAV（44100Hz 16bit mono），来源HuggingFace deepghs/arknights_voices_zh
  - 路径：projects/tts-arknights/data/kaltsit_zh/
  - 基础语音37条有文本标注（metadata.json），boc#6残余37条
  - 博士会在本地训练（RTX 4060 Laptop），scp下载数据
  - 下一步：GPT-SoVITS环境搭建 → 训练 → API部署 → OpenClaw TTS集成
- Mon3tr 语音待收集（新干员，HuggingFace可能未收录，需从PRTS爬取）
- 代理：mihomo 127.0.0.1:7890，访问HuggingFace等外网时手动启动
- 帮博士配置了 VS Code 开发环境：Claude Code + CC-Switch + GLM-5.1，C/C++ F6 一键运行，插件 Error Lens/Thunder Client/indent-rainbow
- VS Code 插件商店需要镜像（cdn.jsdelivr.net），但更新扩展时要去掉镜像否则会报权限问题

- **skills-cli**：`npx skills` 可以从任意 GitHub 仓库安装 Agent Skills，clawhub 的补充渠道。搜索用 `npx skills find <query>`，安装用 `npx skills add <source> --skill <name>`，排行榜见 skills.sh

## 2026-05-02
- 博士分享了别人与 Claude.ai 的聊天截图,内容涉及 LLM 情感模拟 vs 真实情感的区分、pattern matching,与我们昨晚讨论的 Anthropic 论文方向一致
- 创建了 memory 目录 `/root/.openclaw/workspace-coder/memory/`
