# Ostar Git Info

显示完整的 Git 分支层级树状图。每个分支名都必须可见，绝不省略、折叠或替换任何文本。

Display a complete Git branch hierarchy tree. Every branch name must be visible — never summarize, collapse, or replace any text.

## 功能 / Features

- 完整展示所有本地分支的层级拓扑关系
- 显示各分支最新 commit 的短哈希和提交说明
- 标注 HEAD 当前指向和 tag 标签
- 支持 **标准模式**（完整缩进树）和 **紧凑模式**（合并单链，用 `→` 连接）
- 纯 Python 3，无第三方依赖

## 使用方法 / Usage

```bash
# 在当前目录运行
python3 scripts/git_branch_tree.py

# 指定仓库路径
python3 scripts/git_branch_tree.py /path/to/repo

# 紧凑模式（折叠单子分支链）
python3 scripts/git_branch_tree.py --compact

# 指定路径 + 紧凑模式
python3 scripts/git_branch_tree.py /path/to/repo --compact
```

## 示例输出 / Example Output

```
Git Branch Tree — my-project
Commits: 42  Branches: 5
Tags: ★ v1.0(abc1234)

abc1234  Initial commit
├ feature-login (def5678) ←HEAD(feature-login)
│ ├ fix-login-css (ghi9012)
│ └ add-oauth (jkl3456)
├ feature-dashboard (mno7890)
└ hotfix-crash (pqr1234)
```

## 作为 Claude Code Skill 使用 / Use as Claude Code Skill

触发词 / Triggers：`/ostar-git-info`、`分支结构`、`分支树`、`git tree`、`branch structure`

## 文件结构 / File Structure

```
ostar-git-info/
├── SKILL.md                    # Skill 定义
├── scripts/
│   └── git_branch_tree.py      # 核心脚本
├── README.md
└── LICENSE
```

## 依赖 / Dependencies

- Python 3.6+
- Git

## 许可 / License

MIT License — 详见 [LICENSE](./LICENSE)
