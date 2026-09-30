# -*- coding: utf-8 -*-
import io, re

p = r"PROJECT_ROOT/\docs\v_os\math_cross_domain\PI_PI_IRRATIONALITY\archive\GAP-1_主线作战室.md"
t = io.open(p, encoding="utf-8").read()
i = t.index("### 8.3")
head, sec = t[:i], t[i:]

lines = sec.split("\n")
fixed = 0
for k, l in enumerate(lines):
    if l.count("$") % 2 == 0:
        continue
    if l.strip().startswith("$$"):
        continue
    orig = l
    # 1) 与反引号相邻的孤立 $ 直接删除（`X$` / `$`X）
    l = l.replace("$`", "`").replace("`$", "`")
    # 2) 仍为奇数：逐对扫描，定位落单的 $ 并删除
    if l.count("$") % 2 == 1:
        pos = [m.start() for m in re.finditer(r"(?<!\\)\$", l)]
        # 贪心配对：相邻两两配对，剩余的按位序判断落单位置
        pair = pos[:len(pos) - 1:2]
        unpaired = pos[len(pos) - 1]
        l = l[:unpaired] + l[unpaired + 1:]
    if l != orig:
        lines[k] = l
        fixed += 1

sec2 = "\n".join(lines)
io.open(p, "w", encoding="utf-8").write(head + sec2)

bad = [(n + 1, l) for n, l in enumerate(sec2.split("\n")) if l.count("$") % 2]
print("lines fixed:", fixed)
print("remaining odd-dollar lines:", len(bad))
for n, l in bad:
    print(" ", n, "|", l[:160])
