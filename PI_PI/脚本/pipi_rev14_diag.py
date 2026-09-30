# -*- coding: utf-8 -*-
"""诊断：emitter 内嵌 sec 与作战室现行动 ¶分 的精确差异（rev14 中途核查用）。"""
import io

base = r"PROJECT_ROOT/\docs\v_os\math_cross_domain\PI_PI_IRRATIONALITY"
wr = io.open(base + r"\archive\GAP-1_主线作战室.md", encoding="utf-8").read()
em = io.open(base + r"\脚本\pipi_d3_s83_emit.py", encoding="utf-8").read()

s1 = em.index('sec = r"""') + len('sec = r"""')
s2 = em.index('"""', s1)
sec = em[s1:s2]
i = wr.index("### 8.3")
cur = wr[i:]

print("sec==cur ?", sec == cur)
print("len sec", len(sec), " len cur", len(cur))
print("EMIT-SEC head:", repr(sec[:60]))
print("EMIT-SEC tail:", repr(sec[-60:]))
print("WAR-CUR  head:", repr(cur[:60]))
print("WAR-CUR  tail:", repr(cur[-60:]))
print("war room len:", len(wr))
print()
# 定位首个差异
if sec != cur:
    n = min(len(sec), len(cur))
    k = next((j for j in range(n) if sec[j] != cur[j]), n)
    print("first diff at char", k)
    print("  sec:", repr(sec[max(0, k - 40):k + 40]))
    print("  cur:", repr(cur[max(0, k - 40):k + 40]))
    print("  sec[:k+1] is all newline?", set(sec[:k]) <= {"\n"})
    print("  cur[:k+1] is all newline?", set(cur[:k]) <= {"\n"})