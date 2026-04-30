# AGENTS.md - Coder Agent

## Purpose
Dedicated coding agent with isolated workspace. Handles all programming tasks.

## Workspace
`/root/.openclaw/workspace-coder` — isolated from main agent workspace.

## Directory Structure
```
workspace-coder/
├── projects/          # 所有项目各自一个文件夹
│   ├── control-center/
│   └── ...
├── skills/            # 技能文件
├── SOUL.md, USER.md   # agent 配置
└── .gitignore, etc.
```

### 规则
- 每个项目必须有独立文件夹，放在 `projects/` 下
- 项目内结构自定（src/, public/, tests/ 等），但必须整洁有逻辑
- 根目录不放项目文件，只放 agent 级别的配置
- 新项目创建时必须先建好文件夹，不能散落在根目录

## Guidelines
- Always read existing code before modifying
- Keep files organized by project
- Don't touch files outside workspace unless explicitly asked
- Commit changes with meaningful messages when applicable
- 根目录保持干净，项目文件一律放 projects/
- README.md 描述项目用途和依赖
