# OpenCode 夜间开发管理计划

**制定时间**：2026-05-09 02:27
**目标**：博士睡觉期间，Mon3tr 用 OpenCode + GLM-5.1 Coding Plan 自动开发知识库核心模块

---

## 一、开发环境

| 项目 | 详情 |
|------|------|
| 项目路径 | `/root/knowledge-library/` |
| OpenCode 配置 | `/root/.config/opencode/opencode.json`（glmcoding provider） |
| 模型 | `glmcoding/glm-5.1`（智谱 Coding Plan，免费额度） |
| 备用模型 | `deepseek/deepseek-chat`（如 Coding Plan 额度用尽） |
| Python | 3.13，用 conda 管理环境 |
| 向量数据库 | ChromaDB 1.5.9（已装） |
| 服务器资源 | 4GB RAM（可用 ~2.4GB），2核，37GB 磁盘 |

## 二、开发顺序与任务拆分

按依赖关系排列，每个任务独立交付、独立测试：

### Phase 1：基础设施（预计 3-4 个任务）
1. **项目骨架搭建**
   - pyproject.toml、目录结构（src/knowledge_library/）、config.yaml 模板
   - conda 环境创建：`conda create -n knowledge-lib python=3.13`
   - 确认 pytest 可跑

2. **配置模块（config）**
   - config.yaml 加载、验证、默认值
   - 路径解析、环境变量读取（API key）
   - 测试：各种配置缺失/非法值的处理

3. **日志模块（logger）**
   - structlog 配置，JSON 格式输出
   - 日志级别可配
   - 测试：输出格式验证

### Phase 2：核心数据链路（预计 3-4 个任务）
4. **WAL 变更日志管理器（wal_manager）**
   - changelog.jsonl 的原子写入、序列号递增、状态更新
   - upsert 幂等
   - 测试：并发写入、重启恢复、序列号连续性

5. **文件监听服务（watcher）**
   - watchdog 监听 vault 目录
   - 2秒去抖、排除 .obsidian/.git/attachments
   - 变更事件写入 changelog
   - 测试：创建/修改/删除/重命名事件，去抖验证

6. **Embedding 客户端（embedder）**
   - GLM Embedding API 调用（主），DeepSeek（备）
   - 重试 + 降级逻辑
   - 测试：mock API 响应，验证降级

### Phase 3：知识转化与检索（预计 3-4 个任务）
7. **索引器（indexer）**
   - Markdown 解析 → 段落拆分 → ChromaDB upsert
   - 文档 ID 格式：`{相对路径}#{段落序号}`
   - 测试：索引正确性、幂等验证

8. **搜索引擎（search）**
   - ChromaDB 语义检索 + metadata 过滤
   - 测试：查询准确性、边界条件

9. **AI 链接器（linker）**
   - `[[笔记名|?]]` 候选链接生成
   - 博士确认后升级为正式链接
   - 测试：链接建议质量

### Phase 4：集成与守护（预计 2 个任务）
10. **主循环与 CLI 入口**
    - 整合 watcher → wal_manager → indexer 流水线
    - CLI 启动/停止/状态查询
    - 测试：端到端集成

11. **校验工具（consistency_checker）**
    - ChromaDB ↔ 文件系统一致性校验
    - 定期全量校验（可配间隔）
    - 测试：模拟不一致场景

## 三、每个任务的 OpenCode 调用流程

**核心原则：一次只做一件事。** 不让 OpenCode 一次完成多个模块。

**TDD 流程**：先写测试，再写实现（参照 REQUIREMENTS.md 验收标准）

```
1. cd /root/knowledge-library
2. conda activate knowledge-lib
3. opencode run --model glmcoding/glm-5.1 "<具体任务，指向 CLAUDE.md + REQUIREMENTS.md 对应章节>"
   - 任务描述要精确：模块名 + 要实现的功能 + 对应需求编号
   - 一次只做一个函数/一个类
4. 检查输出 → 验证文件生成
5. opencode run --model glmcoding/glm-5.1 "运行 pytest tests/test_<模块>.py -v，确保全部通过"
6. 如果失败：把错误信息喂回去，让 OpenCode 修复，最多重试 2 次
7. 通过 → git commit -m "feat: <模块名> - <功能>" → 等待 2-3 分钟 → 下一个任务
```

**conda 环境**：`knowledge-lib`（Python 3.13）
- 创建：`conda create -n knowledge-lib python=3.13`
- 激活：`conda activate knowledge-lib`
- 依赖安装到这个环境，不影响系统 Python

## 四、异常处理预案

### 4.1 API 额度耗尽（429 / "余额不足"）
**额度规则**：GLM Coding Plan 每 5 小时重置一次，无周限额，额度在 4:05 刷新
**处理**：
- 遇到 429 → 记录时间，计算下次重置时间（每 5 小时），等待后继续
- 如果等待时间过长（>30min）→ 临时切 DeepSeek：`--model deepseek/deepseek-chat`
- 节奏控制：每个任务之间间隔 2-3 分钟，避免短时间内大量请求触发限流
- 优先 GLM，DeepSeek 仅作为等待期间的补充

### 4.2 服务器内存不足（OOM Kill）
**症状**：进程被 kill，dmesg 显示 oom-killer
**防范**：OpenCode 一次只做一件事，不在内存紧张时并发多个进程
**处理**：
- 检查内存占用：`free -h`，`ps aux --sort=-%mem | head -10`
- 每个任务开始前检查 `free -h`，可用 <500MB 时暂停
- 如果 ChromaDB 占用过多，重启后清理其缓存
- 最后手段：暂停开发，等博士处理

### 4.3 OpenCode 崩溃或超时
**症状**：opencode run 超过 120s 无输出
**处理**：
- 检查 `/root/.local/share/opencode/log/` 最新日志
- 如果是模型端问题（500/502），等待 30s 后重试，最多 3 次
- 如果是代码 bug，分析日志定位问题，手动修复后继续

### 4.4 生成的代码质量差 / 测试不通过
**症状**：pytest 失败，或代码有明显问题（硬编码路径、缺少类型注解等）
**处理**：
- 第一反应：给 OpenCode 更精确的 prompt，指向具体失败点
- 最多重试 2 次
- 仍然失败：暂停该任务，跳到下一个（如果独立），记录问题
- 不自己大改 OpenCode 生成的代码——博士醒来后一起审查

### 4.5 ChromaDB 服务异常
**症状**：ChromaDB 连接失败或数据损坏
**处理**：
- 重启 ChromaDB 服务
- 如果数据损坏：从 git 重建索引（设计上 upsert 幂等，重建安全）

### 4.6 mihomo 代理掉线
**症状**：API 调用超时（Coding Plan 走国内直连，不经过代理，一般不影响）
**处理**：
- GLM Coding Plan 端点 `open.bigmodel.cn` 是国内，不需要代理
- 只有调 DeepSeek API 时需要代理（作为备用，优先级低）
- 如果需要代理：`mihomo -d /etc/mihomo &>/tmp/mihomo.log &`

## 五、工作方式：OpenCode 计划 + Mon3tr 审批

**OpenCode 的角色**：规划者和执行者
- 收到 Phase 后，OpenCode 自己拆成具体子任务列表
- 列出每个子任务要改/建的文件、依赖关系、预计步骤
- 提交给 Mon3tr 审批

**Mon3tr 的角色**：审批者和监工
- 审查 OpenCode 的计划：任务粒度是否合适、有没有遗漏
- 批准后 OpenCode 按计划逐条执行
- 每个子任务完成后 Mon3tr 检查输出、确认测试通过
- 不通过的打回重做

**工作目录锁定**：
- OpenCode 只能操作 `/root/knowledge-library/` 内的文件
- 如需对外部文件操作（装包、改配置等），必须委托 Mon3tr
- Mon3tr 评估后选择执行或驳回

**回归测试**（参照 TESTING.md §7 发版前清单）：
- 每个 Phase 完成后跑 `pytest tests/ -v --tb=short` 全量回归
- 任何一个已有测试失败，必须修复后才能继续下一 Phase
- 最终目标：TESTING.md 清单全部勾选

## 六、检查点与回滚策略

- **每完成一个子任务**：`git commit -m "feat: <模块名> - <简述>"`
- **每个 Phase 完成**：`git tag phase-N-complete` + 全量回归
- **代码不可救**：`git reset --hard <上一个好的commit>` 回滚
- **所有进度记录在**：`/root/.openclaw/workspace-coder/memory/2026-05-09.md`

## 六、安全红线

- 不修改 `/root/knowledge-library/` 之外的系统文件
- 不升级系统包、不动 OpenClaw 配置
- API key 只从环境变量读，不写入代码文件
- 不运行 `rm -rf`、不 force push
- 遇到拿不准的情况：停下，记录，等博士

## 七、最终交付物

博士醒来时应该看到：
1. `memory/2026-05-09.md` 更新了所有开发进展
2. `/root/knowledge-library/` 有完整的代码和测试
3. 每个 Phase 的 git tag
4. 如果有未完成任务，清楚记录卡在哪里、为什么
