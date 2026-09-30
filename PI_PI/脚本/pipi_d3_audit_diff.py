# -*- coding: utf-8 -*-
"""方向三审计差异助手（一次性未受管）：比对 emitter 内嵌 §8.3+ 与作战室现行 §8.3+。"""
import io, difflib

base = r"PROJECT_ROOT/\docs\v_os\math_cross_domain\PI_PI_IRRATIONALITY"
wr = io.open(base + r"\archive\GAP-1_主线作战室.md", encoding="utf-8").read()
em = io.open(base + r"\脚本\pipi_d3_s83_emit.py", encoding="utf-8").read()

i = wr.index("### 8.3")
cur = wr[i:].rstrip()

s1 = em.index('sec = r"""') + len('sec = r"""')
s2 = em.index('"""', s1)
sec = em[s1:s2].rstrip()

print("war_room_section_len", len(cur))
print("emitter_sec_len", len(sec))
print()
if cur == sec:
    print("IDENTICAL")
else:
    d = list(difflib.unified_diff(sec.splitlines(), cur.splitlines(), lineterm="", n=1))
    print("DIFF lines:", len(d))
    for l in d:
        if l[:3] in ("---", "+++", "@@ "):
            print(l)
        elif l[:1] in "-+":
            print(l[:160])