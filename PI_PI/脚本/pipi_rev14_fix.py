# -*- coding: utf-8 -*-
# rev14 修正（一次性未受管 helper）：
# 1) 校验作战室 head（§1-§8.2）关键标记未因发射器试运行而丢失；
# 2) 以 LF 统一换行重写作战室（内容字符级不变）——消除混合换行导致的字节漂移；
# 3) 重建发射器：sec 与 r""" 同起始行（消除首部多余 \\n），写盘 newline="\\n" 幂等。
import io

base = r"PROJECT_ROOT/\docs\v_os\math_cross_domain\PI_PI_IRRATIONALITY"
wr_path = base + r"\archive\GAP-1_主线作战室.md"
em_path = base + r"\脚本\pipi_d3_s83_emit.py"

wr = io.open(wr_path, encoding="utf-8").read()

markers = [
    "决策点 6", "7.1 方向二后台复扫协议", "状态：设计阶段已封存",
    "待办 7-8", "8. 发射器 `pipi_d3_s83_emit.py` 同步", "方向三审计闭环 + OBST 判定归档",
    "精确范围声明 v2", "8.3.4b 补充诊断", "8.3.6 数值自检附录", "rev 校正版",
]
missing = [m for m in markers if m not in wr]
print("missing markers:", missing if missing else "NONE (head/section intact)")

k = wr.index("### 8.3")
head, sec2 = wr[:k], wr[k:]

# --- 1) 统一 LF 重写作战室（字符内容不变） ---
with io.open(wr_path, "w", encoding="utf-8", newline="\n") as f:
    f.write(wr)
print("war room rewritten LF; chars:", len(wr))

# --- 2) 重建发射器（sec 无首部换行；幂等写盘） ---
header = (
    '# -*- coding: utf-8 -*-\n'
    'import io\n'
    '\n'
    "# rev14 校正（2026-09-30，用户裁定决策点6 选项A）：\n"
    "# 内嵌 sec 为 v2 权威版（OBST-4 精确范围声明 v2 + §8.3.4b + §8.3.6 + §8.4 新记账），\n"
    "# 与 `r\"\"\"` 同起始行（sec 运行时无首部换行）；写盘 newline=\"\\n\"（LF 幂等）。\n"
    "# 生成：pipi_rev14_sync_emitter.py / 校正：pipi_rev14_fix.py（均未受管 helper）。\n"
    '# 指针：archive/方向三封存_OBST判定.md（OBST 判定归档）。\n'
    'p = r"PROJECT_ROOT/\\docs\\v_os\\math_cross_domain\\PI_PI_IRRATIONALITY\\archive\\GAP-1_主线作战室.md"\n'
    't = io.open(p, encoding="utf-8").read()\n'
    'i = t.index("### 8.3")\n'
    'head = t[:i]\n'
    '\n'
    'sec = r"""'
)
assert '"""' not in sec2 and not sec2.startswith("\n"), "sec2 unexpected shape"
tail = (
    '"""\n'
    '\n'
    'with io.open(p, "w", encoding="utf-8", newline="\\n") as f:\n'
    '    f.write(head + sec)\n'
    '\n'
    'bad = [(n + 1, l) for n, l in enumerate(sec.split("\\n")) if l.count("$") % 2]\n'
    'print("rewrote section, chars:", len(sec))\n'
    'print("odd-dollar lines:", len(bad))\n'
    'for n, l in bad:\n'
    '    print("  ", n, "|", l[:120])\n'
)
new_em = header + sec2 + tail
with io.open(em_path, "w", encoding="utf-8", newline="\n") as f:
    f.write(new_em)
print("emitter rebuilt; chars:", len(new_em), " sec chars:", len(sec2))