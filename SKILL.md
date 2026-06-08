---
name: ostar-git-info
description: |
  显示完整的 git 分支层级树状图。每个分支名都必须可见——
  绝对不要用 "..." 总结、折叠或替换任何文本。
  Display a complete git branch hierarchy tree. Every branch must be visible
  — do NOT summarize, collapse, or replace any text with "...".
  触发词：/ostar-git-info, "分支结构", "分支树", "git tree", "branch structure".
---

# Ostar Git Info — Git 分支树状图

直接运行脚本，完整输出，不做任何总结。

```bash
python3 <skill_dir>/scripts/git_branch_tree.py [repo_path]
```

关键规则：原样展示每一行。绝不用 "..." 替代任何分支名。
