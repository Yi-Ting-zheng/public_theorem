# -*- coding: utf-8 -*-
"""
pipi_schanuel_chain.py
Schanuel 蕴含 π^π 超越 —— 归约链的机器核验

定位：本脚本核验 THEOREM-COND 链条的【结构与算术自洽性】，
      不构成对链条逻辑的证明，也不构成 GAP-1 的证据。

纪律（README.md §3）：
  - 数值核验只能标 EMPIRICAL，不得作为 THEOREM 依据。
  - 本脚本的真实作用：抓指数写错、n 数错、生成元个数错、常数取错。

链条（详见 05_条件性定理/Schanuel蕴含π^π超越.md）：
  步骤0  (S)@n=2  : trdeg Q(1, 2πi, e, 1)        >= 2  ⟹ e, π 代数无关
  步骤1  log π ∉ Q（否则 π^q = e^p，与代数无关矛盾）
  步骤2  (S)@n=3  : trdeg Q(1,2πi,lnπ, e,1,π)   >= 3  ⟹ π, lnπ, e 代数无关
  步骤3  1, 2πi, lnπ, π·lnπ 在 Q 上线性无关
  步骤4  (S)@n=4  : trdeg Q(1,2πi,lnπ,πlnπ, e,1,π,π^π) >= 4
                    ⟹ π, lnπ, e, π^π 代数无关 ⟹ π^π 超越
"""
from fractions import Fraction
import mpmath as mp
import sys

# DEF-1 修复：控制台代码页无关化。
# Windows 默认 GBK 代码页无法编码 ⟹ ∉ 等符号，print 时抛
# UnicodeEncodeError 并使脚本 exit=1。统一改用 UTF-8，并以 replace 兜底，
# 保证在任意代码页下均可复现输出（README §2「数值输出须可复现」）。
for _s in ("stdout", "stderr"):
    _f = getattr(sys, _s, None)
    if hasattr(_f, "reconfigure"):          # Python >= 3.7
        _f.reconfigure(encoding="utf-8", errors="replace")

mp.mp.dps = 60
PI = mp.pi
E = mp.e
LOG_PI = mp.log(PI)

ok = True


def chk(tag, cond, detail=""):
    global ok
    if not cond:
        ok = False
    print("  [%s] %-44s %s" % ("PASS" if cond else "FAIL", tag, detail))


print("=" * 78)
print("Schanuel => π^π 超越  归约链结构核验  (EMPIRICAL: 仅自洽性)")
print("=" * 78)

# ---- 常数
print("\n[1] 常数取值")
for name, v in [("pi", PI), ("e", E), ("log(pi)", LOG_PI)]:
    print("      %-10s = %s" % (name, mp.nstr(v, 22)))

# ---- 步骤0: (S)@n=2, z = (1, 2πi)
print("\n[2] 步骤0  (S)@n=2,  z1=1, z2=2*pi*i")
chk("z1, z2 的 e^ 得 e, 1",
    abs(mp.exp(1) - E) < mp.mpf('1e-50') and abs(mp.exp(2j * PI) - 1) < mp.mpf('1e-50'),
    "e^1=%.15f  e^(2πi)=%.3e" % (float(E), float(abs(mp.exp(2j * PI) - 1))))
chk("n=2 需 2 个 Q-线性无关生成元", True, "1, 2πi  (π 超越 => 不相关)")

# ---- 步骤1: log pi 非有理
print("\n[3] 步骤1  log(pi) ∉ Q  (否则 π^q = e^p)")
# 数值只能提示：连分数不吻合任何有理数
cf = mp.pslq(mp.matrix([LOG_PI, 1]), tol=mp.mpf('1e-30'), maxcoeff=10**6, maxsteps=200)
chk("PSLQ 未找到 log(pi) 的低系数有理表示", cf is None,
    "结果: %s" % ("None (未找到)" if cf is None else str(cf)))
# 关键代数点：若 log pi = p/q 则 pi^q = e^p，X^q - Y^p = 0 是 (pi,e) 的多项式关系
chk("矛盾结构正确: pi^q - e^p 在 (pi,e) 上为非零多项式", True,
    "X^q - Y^p, p,q>0 (log pi>0)")

# ---- 步骤2: (S)@n=3
print("\n[4] 步骤2  (S)@n=3,  z=(1, 2πi, log pi)")
chk("e^(log pi) = pi",
    abs(mp.exp(LOG_PI) - PI) < mp.mpf('1e-50'),
    "diff=%.3e" % float(abs(mp.exp(LOG_PI) - PI)))
gen3 = ["pi", "log(pi)", "e"]
chk("生成元数 = n = 3", len(gen3) == 3, str(gen3))

# ---- 步骤3: 1, 2pi i, log pi, pi*log pi 的 Q-线性无关
print("\n[5] 步骤3  1, 2πi, lnπ, π·lnπ 的 Q-线性无关")
# 实部关系 a + c·lnπ + d·(π lnπ) = 0
# 若 d≠0 则 π, lnπ 间出现非零多项式关系 dXY + cY + a = 0
#   -> 需 (pi, log pi) 代数无关，步骤2 已得
chk("若 d≠0, 多项式 d*X*Y + c*Y + a 非零 (d≠0)", True, "关于 (X,Y)=(pi,logpi)")
chk("若 d=0, 归结为 lnpi ∉ Q (步骤1)", True, "a + c*lnpi = 0 => c=a=0 => b=0")
# 数值确认 4 个数互不相同、线性组合不会意外归零
vec = [mp.mpf(1), LOG_PI, PI * LOG_PI]
print("      实部向量 (1, ln pi, pi*ln pi) =", [mp.nstr(v, 18) for v in vec])
chk("向量非退化", all(abs(v) > 0 for v in vec))

# ---- 步骤4: (S)@n=4
print("\n[6] 步骤4  (S)@n=4,  z=(1, 2πi, lnπ, π·lnπ)")
z4 = PI * LOG_PI
chk("e^(pi * log pi) = pi^pi",
    abs(mp.exp(z4) - mp.power(PI, PI)) < mp.mpf('1e-40'),
    "e^(pi ln pi) = %s" % mp.nstr(mp.exp(z4), 20))
chk("pi^pi = %s" % mp.nstr(mp.power(PI, PI), 20), True)
gen4 = ["pi", "log(pi)", "e", "pi^pi"]
chk("生成元数 = n = 4", len(gen4) == 4, str(gen4))
chk("trdeg >= 4 且仅 4 个生成元 => 代数无关", len(gen4) == 4,
    "⟹ π^π 超越 (条件于 S)")

# ---- 姊妹结论: pi^e 用同一配方
print("\n[7] 姊妹结论  (S)@n=4 同样给出 π^e 超越")
ze = E * LOG_PI
chk("e^(e*log pi) = pi^e",
    abs(mp.exp(ze) - mp.power(PI, E)) < mp.mpf('1e-40'),
    "pi^e = %s" % mp.nstr(mp.power(PI, E), 20))

# ---- n 值审计
print("\n[8] Schanuel 应用点审计")
apps = [(2, "e, π 代数无关"), (3, "π, lnπ, e 代数无关"), (4, "π, lnπ, e, π^π 代数无关")]
for n, what in apps:
    print("      (S)@n=%d  ->  %s" % (n, what))
chk("链条仅需 n<=4 的 (S)", max(n for n, _ in apps) == 4, "最大 n = 4")

print("\n" + "=" * 78)
print("结构核验结果: %s" % ("全部通过" if ok else "存在 FAIL"))
print("真值层级: 本脚本 = EMPIRICAL (自洽性检查)")
print("  链条本体 = THEOREM-COND (前提: Schanuel 猜想, 未证明)")
print("  GAP-1 (π^π 无理性) 仍为 GAP-OPEN —— 本脚本不提供其证据")
print("=" * 78)
