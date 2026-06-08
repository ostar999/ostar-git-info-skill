#!/usr/bin/env node
"use strict";
const { execSync } = require("child_process");
const path = require("path");

// Resolve target repo path
const repoPath = process.argv[2]
  ? path.resolve(process.argv[2])
  : process.cwd();

function git(cmd, cwd = repoPath) {
  try {
    return execSync(`git ${cmd}`, { cwd, encoding: "utf8", stdio: ["pipe", "pipe", "pipe"] }).trim();
  } catch (e) {
    process.exit(1);
  }
}

// --- Load data ---

function getData() {
  const fmt = "%H|%h|%P|%s|%D";
  const out = git(`log --all --format="${fmt}" --date-order`);
  const commits = {};
  for (const line of out.split("\n")) {
    if (!line.trim()) continue;
    const parts = line.split("|", 5);
    if (parts.length < 5) continue;
    const [fh, sh, parents, subject, refsStr] = parts;
    const pl = parents.trim() ? parents.trim().split(/\s+/) : [];
    const refs = { tags: [], branches: [], head: null };
    if (refsStr.trim()) {
      for (let r of refsStr.split(",")) {
        r = r.trim();
        if (r.startsWith("tag: ")) refs.tags.push(r.slice(5));
        else if (r.includes("HEAD ->")) refs.head = r.split("->")[1].trim();
        else if (r.startsWith("origin/")) {
          const n = r.slice(7);
          if (n !== "HEAD" && n !== "main" && n !== "master") refs.branches.push(n);
        } else if (r !== "main" && r !== "master") refs.branches.push(r);
      }
    }
    commits[fh] = { short: sh, parents: pl, subject: subject.trim(), refs };
  }

  // Main chain (newest→oldest)
  const headHash = Object.values(commits).find(c => c.refs.head)?.hash ??
    Object.keys(commits).sort((a, b) => (commits[b].date || "") > (commits[a].date || "") ? 1 : -1)[0];
  const chain = [];
  let cur = Object.keys(commits).find(h => commits[h].refs.head) ||
    Object.keys(commits)[0]; // fallback
  // Better: start from head ref
  for (const [h, c] of Object.entries(commits)) {
    if (c.refs.head) { cur = h; break; }
  }
  while (cur && commits[cur]) {
    chain.push(cur);
    const p = commits[cur].parents;
    cur = p.length > 0 ? p[0] : null;
  }

  // Branch tips from show-ref
  const brOut = git("show-ref --heads");
  const tips = {};
  for (const line of brOut.split("\n")) {
    if (!line.trim()) continue;
    const p = line.split(/\s+/);
    if (p.length >= 2) tips[p[1].replace("refs/heads/", "")] = p[0];
  }

  return { commits, chain, tips };
}

// --- Build tree ---

function buildTree(commits, chain, tips) {
  const root = chain[chain.length - 1];
  const mainSet = new Set(chain);
  const interesting = new Set([root]);
  for (const [bn, h] of Object.entries(tips)) {
    if (bn !== "main" && bn !== "master") interesting.add(h);
  }

  // children: parent_hash → [child_hash]
  const children = {};
  for (const h of interesting) {
    if (h === root) continue;
    let cur = commits[h].parents[0] ?? null;
    while (cur && commits[cur]) {
      if (interesting.has(cur)) {
        if (!children[cur]) children[cur] = [];
        children[cur].push(h);
        break;
      }
      cur = commits[cur].parents[0] ?? null;
    }
    if (!cur) {
      if (!children[root]) children[root] = [];
      children[root].push(h);
    }
  }

  // Sort children by main chain position
  for (const p of Object.keys(children)) {
    children[p].sort((a, b) => {
      const ai = chain.indexOf(a), bi = chain.indexOf(b);
      return (ai === -1 ? 9999 : ai) - (bi === -1 ? 9999 : bi);
    });
  }

  const seen = new Set();
  function makeNode(h) {
    if (seen.has(h)) return null;
    seen.add(h);
    const c = commits[h];
    const names = [];
    for (const [bn, tip] of Object.entries(tips)) {
      if (bn !== "main" && bn !== "master" && tip === h) names.push(bn);
    }
    // dedup
    const uniq = [...new Set(names)];
    let subj = c.subject;
    if (subj.length > 70) subj = subj.slice(0, 67) + "...";
    const node = { h, s: c.short, subj, names: uniq, tags: [...c.refs.tags], head: c.refs.head, kids: [] };
    for (const ch of (children[h] || [])) {
      const kid = makeNode(ch);
      if (kid) node.kids.push(kid);
    }
    return node;
  }
  return makeNode(root);
}

// --- Render ---

function render(node, pref = "", last = true, root = true) {
  const out = [];
  if (root) {
    const label = node.subj ? `${node.s}  ${node.subj}` : node.s;
    out.push(label);
  } else {
    const conn = last ? "└ " : "├ ";
    const nxt = last ? "  " : "│ ";
    const names = node.names;
    let line;
    if (names.length > 0) {
      let bn = names[0];
      if (bn.length > 40) bn = bn.slice(0, 37) + "...";
      line = `${pref}${conn}${bn} (${node.s})`;
      for (let i = 1; i < names.length; i++) {
        let nn = names[i];
        if (nn.length > 40) nn = nn.slice(0, 37) + "...";
        line += `\n${pref}${nxt}├ ${nn} (${node.s},同commit)`;
      }
    } else {
      line = `${pref}${conn}${node.s}`;
    }
    const ann = [];
    if (node.tags.length) for (const t of node.tags) ann.push(`★${t}`);
    if (node.head) ann.push(`←HEAD(${node.head})`);
    if (ann.length) line += " " + ann.join(" ");
    out.push(line);
    pref = pref + nxt;
  }
  for (let i = 0; i < node.kids.length; i++) {
    out.push(...render(node.kids[i], pref, i === node.kids.length - 1, false));
  }
  return out;
}

// --- Main ---

function main() {
  const data = getData();
  if (!data.commits || Object.keys(data.commits).length === 0) {
    console.log("No commits found.");
    return;
  }
  const root = buildTree(data.commits, data.chain, data.tips);
  const allBr = Object.keys(data.tips).filter(b => b !== "main" && b !== "master");
  const tags = [];
  for (const c of Object.values(data.commits)) {
    for (const t of c.refs.tags) tags.push(`★${t}(${c.short})`);
  }

  console.log(`\nGit Branch Tree — ${path.basename(repoPath)}`);
  console.log(`Commits: ${Object.keys(data.commits).length}  Branches: ${allBr.length}`);
  if (tags.length) console.log(`Tags: ${tags.join(", ")}`);
  console.log();
  for (const line of render(root)) console.log(line);
  console.log();
}

main();
