#!/usr/bin/env python3
"""Compact git branch hierarchy tree. Each node = branch_name (hash)."""

import subprocess, sys, os
from collections import defaultdict

def run(cmd, cwd):
    r = subprocess.run(["git"]+cmd, capture_output=True, text=True, cwd=cwd)
    if r.returncode != 0: sys.exit(1)
    return r.stdout

def get_data(cwd):
    fmt = "%H|%h|%P|%s|%D"
    out = run(["log","--all",f"--format={fmt}","--date-order"], cwd)
    commits = {}
    for line in out.split("\n"):
        if not line.strip(): continue
        parts = line.split("|", 5)
        if len(parts) < 5: continue
        fh, sh, parents, subject, refs_str = parts
        pl = [p.strip() for p in parents.split()] if parents.strip() else []
        refs = {"tags":[],"branches":[],"head":None}
        if refs_str.strip():
            for r in refs_str.split(","):
                r = r.strip()
                if r.startswith("tag: "): refs["tags"].append(r[5:])
                elif "HEAD ->" in r: refs["head"] = r.split("->")[-1].strip()
                elif r.startswith("origin/"):
                    n = r[7:]
                    if n not in ("HEAD","main","master"): refs["branches"].append(n)
                elif r not in ("main","master"): refs["branches"].append(r)
        commits[fh] = {"short":sh,"parents":pl,"subject":subject.strip(),"refs":refs}
    # main chain (newest->oldest)
    head = next((h for h,c in commits.items() if c["refs"]["head"]), None)
    if not head: head = max(commits.keys(), key=lambda h: commits[h]["date"])
    chain = []; cur = head
    while cur and cur in commits:
        chain.append(cur); cur = commits[cur]["parents"][0] if commits[cur]["parents"] else None
    # branch tips
    br = run(["show-ref","--heads"], cwd)
    tips = {}
    for line in br.split("\n"):
        if not line.strip(): continue
        p = line.split()
        if len(p)>=2: tips[p[1].replace("refs/heads/","")] = p[0]
    return commits, chain, tips

def build_tree(commits, chain, tips):
    root = chain[-1]; main_set = set(chain)
    interesting = {root} | {h for bn,h in tips.items() if bn not in ("main","master")}
    children = defaultdict(list)
    for h in interesting:
        if h == root: continue
        cur = commits[h]["parents"][0] if commits[h]["parents"] else None
        while cur and cur in commits:
            if cur in interesting: children[cur].append(h); break
            cur = commits[cur]["parents"][0] if commits[cur]["parents"] else None
        else: children[root].append(h)
    for p in children:
        children[p].sort(key=lambda h: chain.index(h) if h in main_set else 9999)
    seen = set()
    def make(h):
        if h in seen: return None
        seen.add(h); c = commits[h]
        names = list(dict.fromkeys(
            bn for bn,tip in tips.items() if bn not in ("main","master") and tip == h
        ))
        subj = c["subject"]
        if len(subj) > 70: subj = subj[:67]+"..."
        node = {"h":h,"s":c["short"],"subj":subj,"names":names,
                "tags":list(c["refs"]["tags"]),"head":c["refs"]["head"],"kids":[]}
        for ch in children.get(h,[]):
            kid = make(ch)
            if kid: node["kids"].append(kid)
        return node
    return make(root)

# ── Standard render (full tree with indentation) ──────────────

def render(node, pref="", last=True, root=True):
    out = []
    if root:
        c = node; names = c["names"]; subj = c.get("subj","")
        label = f"{c['s']}  {subj}" if subj else c["s"]
        out.append(label)
    else:
        conn = "└ " if last else "├ "
        nxt  = "  " if last else "│ "
        names = node["names"]
        if names:
            bn = names[0]
            if len(bn)>40: bn = bn[:37]+"..."
            line = f"{pref}{conn}{bn} ({node['s']})"
            for n in names[1:]:
                nn = n if len(n)<=40 else n[:37]+"..."
                line += f"\n{pref}{nxt}├ {nn} ({node['s']},同commit)"
        else:
            line = f"{pref}{conn}{node['s']}"
        ann = []
        if node["tags"]:
            for t in node["tags"]: ann.append(f"★{t}")
        if node["head"]: ann.append(f"←HEAD({node['head']})")
        if ann: line += " "+" ".join(ann)
        out.append(line); pref = pref + nxt
    for i, kid in enumerate(node["kids"]):
        out.extend(render(kid, pref, i==len(node["kids"])-1, False))
    return out

# ── Compact render (collapse single-child chains with -> arrows) ──

def _compact_label(node):
    parts = []
    s = node["s"]
    names = node["names"]
    if names:
        bn = names[0]
        if len(bn) > 40: bn = bn[:37] + "..."
        label = f"{bn} ({s})"
        if len(names) > 1:
            extra = ", ".join(names[1:])
            if len(extra) > 40: extra = extra[:37] + "..."
            label += f" [+{extra}]"
        parts.append(label)
    else:
        parts.append(s)
    ann = []
    if node["tags"]:
        for t in node["tags"]: ann.append(f"★{t}")
    if node["head"]: ann.append(f"←HEAD({node['head']})")
    if ann: parts.append(" ".join(ann))
    return " ".join(parts)

def render_compact(node, pref="", last=False, root=True):
    out = []
    if root:
        line = _compact_label(node)
        cur = node
        while len(cur["kids"]) == 1:
            cur = cur["kids"][0]
            line += " → " + _compact_label(cur)
        out.append(line)
        for i, kid in enumerate(cur["kids"]):
            out.extend(render_compact(kid, "", i == len(cur["kids"]) - 1, False))
    else:
        conn = "└ " if last else "├ "
        nxt  = "  " if last else "│ "
        line = pref + conn + _compact_label(node)
        cur = node
        while len(cur["kids"]) == 1:
            cur = cur["kids"][0]
            line += " → " + _compact_label(cur)
        out.append(line)
        new_pref = pref + nxt
        for i, kid in enumerate(cur["kids"]):
            out.extend(render_compact(kid, new_pref, i == len(cur["kids"]) - 1, False))
    return out

def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("repo_path", nargs="?", default=None)
    p.add_argument("--compact", action="store_true",
                   help="Collapse single-child chains with -> arrows")
    a = p.parse_args()
    cwd = os.path.abspath(a.repo_path) if a.repo_path else os.getcwd()
    try: run(["rev-parse","--git-dir"], cwd)
    except SystemExit: print(f"Not a git repo: {cwd}"); return
    commits, chain, tips = get_data(cwd)
    if not commits: print("No commits."); return
    root = build_tree(commits, chain, tips)
    all_br = [bn for bn in tips if bn not in ("main","master")]
    tags = [(c["short"],t) for c in commits.values() for t in c["refs"]["tags"]]
    print(f"\nGit Branch Tree — {os.path.basename(cwd)}")
    print(f"Commits: {len(commits)}  Branches: {len(all_br)}")
    if tags: print(f"Tags: "+", ".join(f"★ {t}({s})" for s,t in tags))
    print()
    render_fn = render_compact if a.compact else render
    for line in render_fn(root): print(line)
    print()

if __name__ == "__main__":
    main()
