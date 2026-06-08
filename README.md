# Ostar Git Info

显示完整的 Git 分支层级树状图。每个分支名都必须可见，绝不省略、折叠或替换任何文本。

Display a complete Git branch hierarchy tree. Every branch name must be visible — never summarize, collapse, or replace any text.

## 功能 / Features

- 完整展示所有本地分支的层级拓扑关系
- 显示各分支最新 commit 的短哈希
- 标注 HEAD 当前指向和 tag 标签
- 支持 **标准模式**（完整缩进树）和 **紧凑模式**（合并单链，用 `→` 连接）
- Node.js 版（主力）| Python 3 版（备用，main 分支）

## 使用方法 / Usage

```bash
# JS 版（推荐，零依赖）
node scripts/git_branch_tree.js [repo_path]

# Python 版（python3 备用）
python3 scripts/git_branch_tree.py [repo_path]

# 紧凑模式
node scripts/git_branch_tree.js --compact [repo_path]
```

## 作为 Claude Code Skill 使用 / Use as Claude Code Skill

触发词 / Triggers：`/ostar-git-info`、`分支结构`、`分支树`、`git tree`、`branch structure`

## 文件结构 / File Structure

```
ostar-git-info/
├── SKILL.md                    # Skill 定义
├── scripts/
│   ├── git_branch_tree.js      # 核心脚本（Node.js）
│   └── git_branch_tree.py      # 核心脚本（Python 备用）
├── README.md
└── LICENSE
```

## 依赖 / Dependencies

- Node.js（推荐）或 Python 3.6+
- Git

## 许可 / License

MIT License — 详见 [LICENSE](./LICENSE)
