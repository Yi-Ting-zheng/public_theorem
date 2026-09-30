#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
verify_public.py — 公开集发布校验器（无任何内部路径，可随仓库发布）

断言（FAIL 即阻断发布）：
  F1 U+FFFD 腐坏字符 == 0
  F2 Windows 绝对路径 == 0
  F3 内部品牌/代号 == 0
  F4 未填占位符 == 0        ← 来自 Zenodo v1.0.0 的教训：占位符一旦发布即成为公开记录
  F5 哈希锁一致（--lock 生成 / 默认校验）

告警（WARN，需人工裁决，不阻断）：
  W1 疑似手机号（词边界+十六进制上下文排除后的严格规则）
  W2 经费/资助语义（排除 `误差预算`/`剂量预算` 等术语）

用法:
    python verify_public.py --lock     # 生成 MANIFEST_PUBLIC.json
    python verify_public.py            # 校验
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import shutil
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

ROOT = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(ROOT, "MANIFEST_PUBLIC.json")
SKIP_DIR = {".git", "__pycache__", ".venv", "archive"}
SKIP_FILE = {"MANIFEST_PUBLIC.json"}

# 扫描器不扫描自身与脱敏报告：这些文件按定义必然包含被禁词与占位符的字面量
# （规则表）。声明式排除，不隐式跳过——排除清单在此打印，可被审计。
SELF_SCAN_EXCLUDE = {"verify_public.py", "REDACTION_REPORT.md", "REDACTION_REPORT.json"}

# ---- 规则表 ------------------------------------------------------------
# F2 的判别式是"路径段"而非"盘符+反斜杠"：排除 Python 字符串的转义序列
# （as f:\n 会被误判为 f: 盘符）。这一修正是第三类假阳性的结构性修复。
FAIL_RULES = [
    ("F1", "U+FFFD-腐坏", re.compile("\ufffd")),
    ("F2", "Windows绝对路径",
     re.compile(r"(?<![A-Za-z0-9])[A-Za-z]:\\(?!['\"0-7nrtxuN\\])")),
    ("F3", "内部品牌", re.compile(r"望易|wangyi", re.I)),
]

# F4 改为**结构判别**：尖括号 token 且不在 HTML 标签白名单内 → 未填占位符。
# 字面量黑名单会被规则表自身触发，且无法覆盖新写法；结构判别可泛化。
HTML_TAGS = {
    "p", "h1", "h2", "h3", "h4", "strong", "em", "code", "pre", "br", "li",
    "ul", "ol", "table", "tr", "td", "th", "div", "span", "a", "hr", "b", "i",
    "sub", "sup", "blockquote", "del", "ins", "figure", "figcaption",
}
TOKEN_RX = re.compile(r"<([^<>\s/][^<>\s]{0,30})>")
# 纯数学记号（希腊字母/上下标/竖线组合）不算占位符
MATHISH = re.compile(r"^[\u0370-\u03ff\u2c60-\u2c7f|\\{}\[\]^_=+\-*/0-9a-zA-Z.,:;'\"() ]{1,30}$")
# 散文里的比较符跨越（`th<pi/2`）、`->`）会凑成"token"——含反引号或 CJK 标点即排除
PROSE_CROSS = re.compile(r"[`、，。；：（）！？…—～]")


# 判据档案豁免（scan-record）：判据档案必须复述触发形态才能被审查，
# 于是记录本身必然触发同一形态的规则（见 SELF_AUDIT.md §4 的五次复发）。
# 与 SELF_SCAN_EXCLUDE 的区别：这里是**声明式 + 逐条降级 + 计数可见**，不是整文件跳过。
#   - 须在文件头 5 行内声明 <!-- scan-record: F1,F2,... -->
#   - 只降级被声明的规则，其余规则照常阻断
#   - 声明含未知规则编号 ⟹ fail-closed（豁免不生效）
#   - 无声明 ⟹ 不豁免
SCAN_RECORD_RX = re.compile(r"<!--\s*scan-record:\s*([^>]*?)-->")
SCAN_RECORD_HEAD = 5
SCAN_RECORD_RULES = {"F1", "F2", "F3", "F4", "F5", "W1", "W2", "W3"}
SCAN_RECORD_COUNT = {}


def scan_record_decl(path: str):
    try:
        head = "\n".join(io.open(path, encoding="utf-8").read().splitlines()[:SCAN_RECORD_HEAD])
    except Exception:
        return set(), set()
    m = SCAN_RECORD_RX.search(head)
    if not m:
        return set(), set()
    raw = {x.strip() for x in m.group(1).split(",") if x.strip()}
    return raw & SCAN_RECORD_RULES, raw - SCAN_RECORD_RULES


def exempt_record(code: str, rel: str, path: str):
    """返回 (是否豁免, 未知编号集合)。降级为 INFO 而非删除 —— 豁免须可见。"""
    declared, unknown = scan_record_decl(path)
    if unknown:
        return False, unknown
    if code in declared:
        SCAN_RECORD_COUNT[code] = SCAN_RECORD_COUNT.get(code, 0) + 1
        return True, set()
    return False, set()


def is_placeholder(token: str) -> bool:
    if token.lower() in HTML_TAGS:
        return False
    if PROSE_CROSS.search(token):
        return False
    if MATHISH.match(token):
        return False
    return True


# F4 只作用于会被直接粘贴的正文文件（Markdown / JSON）。
# 代码里的 "<不存在>" 一类是 getattr 默认值等合法哨兵字面量，不是未填占位符。
F4_SUFFIX = (".md", ".json")


WARN_RULES = [
    # 严格手机号：前后不得为数字/十六进制/小数点 → 排除 π 小数展开与 SHA256
    ("W1", "疑似手机号", re.compile(r"(?<![0-9A-Fa-f.])1[3-9]\d{9}(?![0-9A-Fa-f.])")),
    # 经费语义：先剔除术语再匹配
    ("W2", "经费语义", re.compile(r"(?<!误差)(?<!剂量)预算|资助|融资|估值|万元|基金会")),
]


def sha256(p: str) -> str:
    h = hashlib.sha256()
    with io.open(p, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def collect() -> dict:
    out = {}
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [d for d in dn if d not in SKIP_DIR]
        for f in sorted(fn):
            if f in SKIP_FILE:
                continue
            p = os.path.join(dp, f)
            r = os.path.relpath(p, ROOT).replace("\\", "/")
            out[r] = {"sha256": sha256(p), "bytes": os.path.getsize(p)}
    return out


def text_files() -> list:
    out = []
    for dp, dn, fn in os.walk(ROOT):
        dn[:] = [d for d in dn if d not in SKIP_DIR]
        for f in sorted(fn):
            if f in SKIP_FILE:
                continue
            p = os.path.join(dp, f)
            try:
                io.open(p, encoding="utf-8").read()
            except Exception:
                continue
            out.append(p)
    return out


def selftest() -> int:
    """扫描器自身的负向/正向自测。

    纪律依据（GAP-03）：自审查不出漏检。一个从未触发过的规则与假阴性无异，
    因此每条规则都必须有**必须触发**的正例与**必须不触发**的反例。
    """
    cases = [
        # (规则, 文本, 后缀, 期望触发?)
        ("F1", "坏字符 \ufffd 在此", ".md", True),
        ("F1", "正常文本", ".md", False),
        ("F2", r"路径 D:\SiliconLifeOS\docs\x.md", ".md", True),
        ("F2", 'print("%s" % getattr(m, "dps", "x")) as f:\n', ".py", False),
        ("F3", "内部代号 望易 出现", ".md", True),
        ("F3", "英文 wangyi 出现", ".md", True),
        ("F3", "无敏感词", ".md", False),
        ("F4", "版本 | <版本号> | 日期 | <日期>", ".md", True),
        ("F4", "HTML 段落 <p>正文</p>", ".md", False),
        ("F4", "区间 th<pi/2`）、`->", ".md", False),
        ("F4", 'getattr(m, "dps", "<不存在>")', ".py", False),
        ("W1", "电话 13800138000 结束", ".md", True),
        ("W1", "π 小数 3.141592653589793238462643383279502884197169399375105820974944592307816406286", ".md", False),
        ("W1", "sha 18a96e4081f8425a85caa21c9c571f9a", ".md", False),
        ("W2", "内部策略 融资扩军 记录", ".md", True),
        ("W2", "数学术语 误差预算 与 剂量预算 D_", ".md", False),
    ]
    bad = 0
    print("=" * 78)
    print("扫描器自测 — %d 例" % (len(cases) + 3))
    print("=" * 78)
    for code, text, suf, expect in cases:
        fired = set()
        for c, name, rx in FAIL_RULES:
            if c == code and rx.search(text):
                fired.add(code)
        if code == "W1" or code == "W2":
            for c, name, rx in WARN_RULES:
                if c == code and rx.search(text):
                    fired.add(code)
        if code == "F4":
            for m in TOKEN_RX.finditer(text):
                if suf.lower().endswith(F4_SUFFIX) and is_placeholder(m.group(1)):
                    fired.add(code)
        got = code in fired
        ok = (got == expect)
        if not ok:
            bad += 1
        print("  %s %s 期望=%-5s 实际=%-5s  %s"
              % ("[OK] " if ok else "[FAIL]", code, expect, got, text[:46].replace("\n", "\\n")))

    # 判据档案豁免的三条边界（同一机制，正反双向断言）——
    # 只有"免检通道"被堵住，豁免机制本身才可信。
    import tempfile
    tmp = tempfile.mkdtemp()
    decl = "<!-- scan-record: F2 -->\n"
    for name, content, expect_exempt in (
        ("b1_rec.md", decl + "盘符 f:\\ 出现在判据档案\n", True),
        ("b2_plain.md", "盘符 f:\\ 出现在普通文档\n", False),
        ("b3_bad.md", "<!-- scan-record: F9 -->\n盘符 f:\\ 出现在声明无效的档案\n", False),
    ):
        p = os.path.join(tmp, name)
        io.open(p, "w", encoding="utf-8", newline="\n").write(content)
        got, unknown = exempt_record("F2", name, p)
        ok = (got == expect_exempt) and (not unknown or not expect_exempt)
        if not ok:
            bad += 1
        print("  %s %s 期望豁免=%-5s 实际=%-5s  未知编号=%s"
              % ("[OK] " if ok else "[FAIL]", "SCAN-REC", expect_exempt, got,
                 ",".join(sorted(unknown)) or "-"))
    shutil.rmtree(tmp, ignore_errors=True)

    print("-" * 78)
    total = len(cases) + 3
    print("自测合计：%d/%d 通过" % (total - bad, total))
    if bad:
        print("裁定：❌ 扫描器规则不可信（存在漏检或误报）")
        return 1
    print("裁定：✅ 扫描器规则可信（每条规则均有正例且反例不触发）")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lock", action="store_true", help="生成 MANIFEST_PUBLIC.json")
    ap.add_argument("--selftest", action="store_true", help="扫描器自身负向/正向自测")
    args = ap.parse_args()

    if args.selftest:
        return selftest()

    files = collect()
    fails, warns, infos, decl_err = [], [], [], []

    for p in text_files():
        rel = os.path.relpath(p, ROOT).replace("\\", "/")
        if rel in SELF_SCAN_EXCLUDE:
            continue
        t = io.open(p, encoding="utf-8").read()
        for code, name, rx in FAIL_RULES:
            for m in rx.finditer(t):
                line = t[:m.start()].count("\n") + 1
                hit = (code, name, rel, line, m.group(0)[:40])
                ok, unknown = exempt_record(code, rel, p)
                if unknown and (rel, code) not in decl_err:
                    decl_err.append((rel, code))
                    warns.append(("W9", "判据档案声明含未知规则编号", rel, line,
                                  ",".join(sorted(unknown))))
                (infos if ok else fails).append(hit)
        for m in TOKEN_RX.finditer(t):
            tok = m.group(1)
            if rel.lower().endswith(F4_SUFFIX) and is_placeholder(tok):
                line = t[:m.start()].count("\n") + 1
                hit = ("F4", "未填占位符", rel, line, "<%s>" % tok)
                ok, unknown = exempt_record("F4", rel, p)
                (infos if ok else fails).append(hit)
        for code, name, rx in WARN_RULES:
            for m in rx.finditer(t):
                line = t[:m.start()].count("\n") + 1
                hit = (code, name, rel, line, m.group(0)[:30])
                ok, unknown = exempt_record(code, rel, p)
                (infos if ok else warns).append(hit)

    print("=" * 78)
    print("公开集发布校验 — %d 文件" % len(files))
    print("自扫描排除（声明式）：%s" % ", ".join(sorted(SELF_SCAN_EXCLUDE)))
    if SCAN_RECORD_COUNT:
        print("判据档案豁免：%s（已降为 INFO，逐条可见）"
              % "  ".join("%s:%d" % kv for kv in sorted(SCAN_RECORD_COUNT.items())))
    print("=" * 78)

    if args.lock:
        doc = {
            "set": "public_theorem",
            "generated_at": datetime.now().isoformat(timespec="seconds"),
            "file_count": len(files),
            "note": ("公开集哈希锁。脱敏留痕见 REDACTION_REPORT.md；"
                     "校验器见 verify_public.py（含 Zenodo v1.0.0 占位符复发防线 F4）。"),
            "files": files,
        }
        io.open(MANIFEST, "w", encoding="utf-8", newline="\n").write(
            json.dumps(doc, ensure_ascii=False, indent=2))
        print("[OK] MANIFEST_PUBLIC.json 已生成：%d 文件" % len(files))
    else:
        if not os.path.exists(MANIFEST):
            fails.append(("F5", "清单缺失", "MANIFEST_PUBLIC.json", 0, "--lock 未生成"))
        else:
            old = json.load(io.open(MANIFEST, encoding="utf-8")).get("files", {})
            added = sorted(set(files) - set(old))
            removed = sorted(set(old) - set(files))
            changed = sorted(k for k in set(old) & set(files) if old[k]["sha256"] != files[k]["sha256"])
            for k in added:
                fails.append(("F5", "清单未收录", k, 0, "新增"))
            for k in removed:
                fails.append(("F5", "清单悬空", k, 0, "已删除"))
            for k in changed:
                fails.append(("F5", "哈希变更", k, 0, "内容已改"))
            if not (added or removed or changed):
                print("[OK] 哈希锁一致：%d 文件全部未变" % len(files))

    for code, name, rel, line, snip in warns:
        print("[WARN] %s %-10s %s:%d  %s" % (code, name, rel, line, snip))
    for code, name, rel, line, snip in infos:
        print("[INFO] %s %-10s %s:%d  %s  ← 判据档案声明豁免" % (code, name, rel, line, snip))
    for code, name, rel, line, snip in fails:
        print("[FAIL] %s %-10s %s:%d  %s" % (code, name, rel, line, snip))

    print("-" * 78)
    print("合计：FAIL %d 项，WARN %d 项，INFO %d 项"
          % (len(fails), len(warns), len(infos)))
    if fails:
        print("裁定：❌ 不得发布（FAIL 必须清零）")
        return 1
    print("裁定：✅ 通过（WARN 需人工裁决，不阻断）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
