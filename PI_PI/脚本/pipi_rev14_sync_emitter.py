# -*- coding: utf-8 -*-
"""rev14 发射器重建器（一次性未受管 helper）。

从作战室抽取 "### 8.3"→EOF 权威段，重建 pipi_d3_s83_emit.py 的内嵌 sec。
用途：修复 rev12 登记时内嵌 v1 旧段、会冲刷 v2 权威内容的审计链破损
（用户裁定决策点 6 选项 A，触发 rev14）。重建后重跑发射器须幂等（diff=0）。
"""
import io

base = r"PROJECT_ROOT/\docs\v_os\math_cross_domain\PI_PI_IRRATIONALITY"
wr_path = base + r"\archive\GAP-1_主线作战室.md"
em_path = base + r"\脚本\pipi_d3_s83_emit.py"

wr = io.open(wr_path, encoding="utf-8").read()
marker = "### 8.3"
src_i = wr.index(marker)
sec = wr[src_i:]  # 含结尾换行，保证 head+sec 逐字节复现

assert '"""' not in sec, "sec contains triple-quote, raw-str embedding unsafe"

header = (
    '# -*- coding: utf-8 -*-\n'
    'import io\n'
    '\n'
    "# rev14 校正（2026-09-30，用户裁定决策点6 选项A）：\n"
    "# 内嵌 sec 由 v1 旧段升级为 v2 权威版（OBST-4 精确范围声明 v2 + §8.3.4b 结构诊断 +\n"
    "# §8.3.6 数值附录 + §8.4 新记账）。生成方式：pipi_rev14_sync_emitter.py 从作战室\n"
    '# 抽取 "### 8.3"→EOF 嵌入；重跑须幂等（war_room 复验 diff=0）。指针文件：\n'
    '# archive/方向三封存_OBST判定.md（OBST 判定归档，决策点4 不升格的归档产物）。\n'
    'p = r"PROJECT_ROOT/\\docs\\v_os\\math_cross_domain\\PI_PI_IRRATIONALITY\\archive\\GAP-1_主线作战室.md"\n'
    't = io.open(p, encoding="utf-8").read()\n'
    'i = t.index("### 8.3")\n'
    'head = t[:i]\n'
    '\n'
    'sec = r"""\n'
)

body = sec
tail = (
    '"""\n'
    '\n'
    'io.open(p, "w", encoding="utf-8").write(head + sec)\n'
    '\n'
    'bad = [(n + 1, l) for n, l in enumerate(sec.split("\\n")) if l.count("$") % 2]\n'
    'print("rewrote section, chars:", len(sec))\n'
    'print("odd-dollar lines:", len(bad))\n'
    'for n, l in bad:\n'
    '    print("  ", n, "|", l[:120])\n'
)

new_em = header + body + tail
io.open(em_path, "w", encoding="utf-8").write(new_em)
print("emitter rebuilt, chars:", len(new_em))
print("sec len:", len(sec))

# 立即复验：当前作战室中 marker 出现在 sec 中吗？
cnt = wr.count(marker)
print("war_room marker('### 8.3') occurrences:", cnt)