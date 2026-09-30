#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
release_preflight.py — 发布前置闸门（public_theorem）

移植自姊妹仓库 emf_demo 的同名闸门，适配本文档仓库的校验器（verify_public.py）。

为什么需要
----------
2026-09-30 在姊妹仓库连续发生两起**只有解包产物才能发现**的发布缺陷：

  1. 哈希锁形同虚设：core.autocrlf=true 且无 .gitattributes ⟹ 新克隆 12/12 文件
     被 CRLF 化，清单锁的字节与检出字节全部不符；本机 --verify 却显示 [OK]。
  2. tag 指向陈旧 commit ⟹ Zenodo 归档了修复前的坏版本。

本仓库亦为同类风险：MANIFEST_PUBLIC.json 锁的是**文件字节**，一旦检出行尾被
转换，公开可验证性即归零。故本闸门不读工作区，而是

    把 tag 指向的树解包到临时目录，在**那个副本**上跑 verify_public.py

判定"Zenodo 实际会归档的东西"是否自洽。

用法:
    python release_preflight.py                # 校验 HEAD
    python release_preflight.py --tag 1.0.0
    python release_preflight.py --tag 1.0.0 --allow-tag-behind-head

退出码: 0 = 可发布 / 1 = 阻断 / 2 = 用法或环境错误
"""
from __future__ import annotations

import argparse
import io
import json
import os
import shutil
import subprocess
import sys
import tarfile
import tempfile

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.abspath(__file__))

# git 定位：优先 PATH；不在 PATH 时用 --git <路径> 显式指定。
# 刻意不在此处硬编码任何机器的 git 安装路径——那既是机器相关信息，
# 也会成为校验器 F2（绝对路径）的靶子。发布脚本不该携带作者机器的痕迹。
GIT = shutil.which("git")

TEXT_EXT = {".py", ".md", ".json", ".yml", ".yaml", ".txt"}


def git(*args: str) -> tuple[int, str, str]:
    p = subprocess.run([GIT, *args], cwd=ROOT, capture_output=True,
                       text=True, encoding="utf-8")
    return p.returncode, (p.stdout or "").strip(), (p.stderr or "").strip()


def hr(t: str) -> None:
    print(f"\n=== {t} " + "=" * max(0, 58 - len(t)))


def check_tag_vs_head(tag: str, allow_behind: bool) -> list[str]:
    rc_t, out_t, _ = git("rev-parse", f"{tag}^{{commit}}")
    rc_h, _, _ = git("rev-parse", "HEAD")
    if rc_t or rc_h:
        return [f"无法解析 {tag} 或 HEAD（tag 未推送？）"]
    behind = git("log", f"{tag}..HEAD", "--oneline")[1]
    n = len(behind.splitlines()) if behind else 0
    if n == 0:
        print(f"[OK] tag {tag} == HEAD（{out_t[:7]}）")
        return []
    print(f"[FAIL] tag {tag} 落后 HEAD {n} 笔 ⟹ Zenodo 将归档未经验证的内容：")
    for l in behind.splitlines():
        print("         " + l)
    if allow_behind:
        print("       --allow-tag-behind-head 已给，仅告警")
        return []
    return [f"tag {tag} 落后 HEAD {n} 笔"]


def check_gitattributes(tag: str) -> list[str]:
    if git("cat-file", "-e", f"{tag}:.gitattributes")[0]:
        print("[FAIL] 该树内无 .gitattributes ⟹ core.autocrlf=true 下克隆会改写字节，"
              "哈希锁在克隆后必然失效")
        return ["缺少 .gitattributes"]
    if "eol=lf" not in git("cat-file", "-p", f"{tag}:.gitattributes")[1]:
        print("[FAIL] .gitattributes 存在但未固定 eol=lf")
        return [".gitattributes 未固定 eol=lf"]
    print("[OK] .gitattributes 已固定 eol=lf")
    return []


def check_zenodo(tag: str) -> list[str]:
    if git("cat-file", "-e", f"{tag}:.zenodo.json")[0]:
        print("[FAIL] 该树内无 .zenodo.json ⟹ Zenodo 元数据将退回 GitHub 默认值"
              "（v1.0.0 类缺陷）")
        return ["缺少 .zenodo.json"]
    body = git("cat-file", "-p", f"{tag}:.zenodo.json")[1]
    try:
        meta = json.loads(body)
    except json.JSONDecodeError as e:
        print(f"[FAIL] .zenodo.json 不可解析：{e}")
        return [".zenodo.json 不可解析"]
    bad = [k for k in ("title", "description", "creators", "license")
           if not meta.get(k) or "占位" in str(meta.get(k))]
    if bad:
        print(f"[FAIL] .zenodo.json 字段缺失或含占位：{bad}")
        return [f".zenodo.json 字段异常 {bad}"]
    print("[OK] .zenodo.json 可解析，关键字段齐备")
    return []


def check_archive_artifact(tag: str) -> list[str]:
    """决定性闸门：解包 tag 树，在副本上实跑校验器。"""
    blockers: list[str] = []
    tmp = tempfile.mkdtemp(prefix="theorem_preflight_")
    work = os.path.join(tmp, "x")
    try:
        blob = os.path.join(tmp, "tree.tar")
        if git("archive", "--format=tar", "-o", blob, tag)[0]:
            print("[FAIL] git archive 失败")
            return ["git archive 失败"]
        os.makedirs(work, exist_ok=True)
        with tarfile.open(blob) as tf:
            tf.extractall(work, filter="data")

        crlf = []
        for dp, dn, fn in os.walk(work):
            dn[:] = [d for d in dn if d not in {".git", "__pycache__"}]
            for f in fn:
                if os.path.splitext(f)[1].lower() not in TEXT_EXT:
                    continue
                p = os.path.join(dp, f)
                with io.open(p, "rb") as fh:
                    if b"\r\n" in fh.read():
                        crlf.append(os.path.relpath(p, work).replace("\\", "/"))
        if crlf:
            print(f"[FAIL] 归档树内 {len(crlf)} 个文本文件含 CRLF ⟹ 哈希锁在该副本上必然失效：")
            for c in crlf:
                print("         " + c)
            blockers.append(f"归档树含 CRLF ×{len(crlf)}")
        else:
            print("[OK] 归档树内文本文件行尾统一")

        r = subprocess.run([sys.executable, os.path.join(work, "verify_public.py")],
                           cwd=work, capture_output=True, text=True, encoding="utf-8")
        if r.returncode == 0:
            last = [l for l in r.stdout.splitlines() if "FAIL" in l]
            print("[OK] 归档树内 verify_public.py 通过：" + (last[-1].strip() if last else ""))
        else:
            print("[FAIL] 归档树内 verify_public.py 未通过：")
            for l in (r.stdout + r.stderr).strip().splitlines()[:20]:
                print("         " + l)
            blockers.append("归档树 verify_public.py 未通过")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return blockers


def main() -> int:
    global GIT
    ap = argparse.ArgumentParser()
    ap.add_argument("--tag", default="HEAD")
    ap.add_argument("--allow-tag-behind-head", action="store_true")
    ap.add_argument("--git", dest="git_override", default=None,
                    help="git 可执行文件路径（git 不在 PATH 时使用）")
    args = ap.parse_args()
    if args.git_override:
        GIT = args.git_override
    if not GIT or not os.path.exists(GIT):
        print("[FAIL] 未找到 git。请把 git 加入 PATH，或用 --git <git 可执行路径> 指定。",
              file=sys.stderr)
        return 2

    print(f"发布前置闸门 | public_theorem | 目标：{args.tag}")
    hr("闸门 1  tag 与 HEAD 一致性")
    b1 = check_tag_vs_head(args.tag, args.allow_tag_behind_head)
    hr("闸门 2  归档树含 .gitattributes（eol=lf）")
    b2 = check_gitattributes(args.tag)
    hr("闸门 3  归档树含可解析的 .zenodo.json")
    b3 = check_zenodo(args.tag)
    hr("闸门 4  归档产物自洽性（解包后实跑 verify_public.py）")
    b4 = check_archive_artifact(args.tag)

    blockers = b1 + b2 + b3 + b4
    print()
    if blockers:
        print("=" * 64)
        print(f"裁定：❌ 不得发布 —— {len(blockers)} 项阻断")
        for b in blockers:
            print(f"  · {b}")
        print("=" * 64)
        return 1
    print("=" * 64)
    print("裁定：✅ 可发布（产物在 tag 指向的树上自洽）")
    print("=" * 64)
    return 0


if __name__ == "__main__":
    sys.exit(main())
