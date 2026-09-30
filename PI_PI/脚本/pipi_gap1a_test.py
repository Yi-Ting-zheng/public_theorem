# -*- coding: utf-8 -*-
"""
pipi_gap1a_test.py
GAP-1a 候选分割检验 + 无条件算术侧的边界演示

检验对象 (05_条件性定理/Schanuel蕴含π^π超越.md §5):
  候选 GAP-1a: π^π 无理性 ⟺ (S)@n<=4 成立 ∨ ∃ π,lnπ 低次多项式关系

本脚本三段:
  T1  PSLQ 搜索 π 与 lnπ 的有理线性关系        -> EMPIRICAL
  T2  严格区间界 -> 排除小分母有理数            -> THEOREM (但见 §局限)
  T3  配方适用性: 哪些 u 使 1,2πi,lnπ,u·lnπ 无关 -> THEOREM (结构性)

诚实声明: 全部结论不构成 GAP-1 的证据。GAP-1 仍为 GAP-OPEN。
"""
from fractions import Fraction
from mpmath import mp          # 必须是真 context; `import mpmath as mp; mp.dps=..`
import mpmath as _mpmath_mod  # 只为演示坑, 见下方精度守卫       # 不会生效
import sys

# DEF-1 修复：控制台代码页无关化。
# Windows 默认 GBK 代码页无法编码 ⟹ ∉ ⚠ ✗ 等符号，print 时抛
# UnicodeEncodeError 并使脚本 exit=1。统一改用 UTF-8，并以 replace 兜底，
# 保证在任意代码页下均可复现输出（README §2「数值输出须可复现」）。
for _s in ("stdout", "stderr"):
    _f = getattr(sys, _s, None)
    if hasattr(_f, "reconfigure"):          # Python >= 3.7
        _f.reconfigure(encoding="utf-8", errors="replace")

mp.dps = 60

PI_REF = ("3.14159265358979323846264338327950288419716939937510"
          "58209749445923078164062862089986280348253421170679")
PI = mp.pi
E = mp.e
LOG_PI = mp.log(PI)

ok = True


def chk(tag, cond, detail=""):
    global ok
    if not cond:
        ok = False
    print("  [%s] %-46s %s" % ("PASS" if cond else "FAIL", tag, detail))


print("=" * 80)
print("GAP-1a 候选分割检验")
print("=" * 80)

# ================================================================== T1
print("     真 context dps = %d" % mp.dps)
print("     坑演示: 模块属性 mpmath.dps = %s  (无效设置, 不影响计算)"
      % getattr(_mpmath_mod, "dps", "<不存在>"))
# 真守卫 A: 与 100 位 π 字面量逐位比对前 40 位 (选 40 位避开进位歧义)
chk("精度守卫A: π 前 40 位正确", mp.nstr(mp.mpf(PI_REF), 40) == PI_REF[:41],
    "得到 %s" % mp.nstr(PI, 40))
# 真守卫 B: dps=60 与 dps=120 两次独立计算须在 50 位上一致
#           若工作精度实际只有 15 位, 二者会在第 15 位分叉 -> 守卫失败
_x60 = mp.nstr(mp.mpf(PI_REF) ** mp.mpf(PI_REF), 50)
mp.dps = 120
_x120 = mp.nstr(mp.mpf(PI_REF) ** mp.mpf(PI_REF), 50)
mp.dps = 60
chk("精度守卫B: dps=60/120 结果 50 位一致", _x60 == _x120, "50 位一致")

print("\n[T1] PSLQ: π 与 ln π 的有理线性关系")
print("     注: (S)@n=3 给出二者【代数无关】; 本项仅检验更弱的【线性无关】")
found = False
for maxc, maxs in ((10**3, 500), (10**6, 2000), (10**9, 2000)):
    rel = mp.pslq(mp.matrix([PI, LOG_PI, 1]),
                  tol=mp.mpf('1e-40'), maxcoeff=maxc, maxsteps=maxs)
    chk("PSLQ 无关系 (coeff<=%d, steps=%d)" % (maxc, maxs), rel is None,
        "%s" % ("None" if rel is None else str(rel)))
    if rel is not None:
        found = True
        break
if not found:
    print("     -> 未找到有理线性关系 (EMPIRICAL, 非证明)")

print("\n     低次多项式定点试探 (v=π, t=lnπ):")
cands = [
    ("t^2 - 1", LOG_PI**2 - 1), ("t^3 - 2", LOG_PI**3 - 2),
    ("v*t - 3", PI * LOG_PI - 3), ("v*t - 36", PI * LOG_PI - 36),
    ("v^2 - 10", PI**2 - 10), ("v + t - 5", PI + LOG_PI - 5),
    ("v*t - v - t", PI * LOG_PI - PI - LOG_PI),
    ("t^2*v - 13", LOG_PI**2 * PI - 13),
    ("t^2 - v", LOG_PI**2 - PI), ("v^2 - t", PI**2 - LOG_PI),
]
allfar = True
for name, val in cands:
    d = abs(val)
    if d < mp.mpf('1e-6'):
        allfar = False
    print("       %-14s = %-20s |值| = %.6e" % (name, mp.nstr(val, 16), float(d)))
chk("全部候选残差远离 0", allfar, "无一命中")

# ================================================================== T2
print("\n[T2] 严格区间界 -> 排除小分母有理数")
print("     层级: THEOREM (无条件, 纯算术)")
print("     ⚠ 局限见文末 §T2局限 —— 本段【不能】推进 GAP-1")

from mpmath import iv
from fractions import Fraction
import re

iv.dps = 120                       # 必须设 dps: iv.dps 优先于 iv.prec, 默认仅 15 位


def iv_to_frac(ivobj):
    """iv 区间 -> 严格有理界 (lo, hi)。

    mpi repr 打印端点十进制值(118 位, 远超 120 位精度可分辨位数),
    打印舍入误差 <= 5e-119; 显式外扩 1e-117 保守覆盖。
    """
    pat = re.compile(r"mpi\('([0-9]+\.[0-9]+)'")
    eps = Fraction(1, 10 ** 117)
    lo = Fraction(pat.search(repr(ivobj.a)).group(1)) - eps
    hi = Fraction(pat.search(repr(ivobj.b)).group(1)) + eps
    return lo, hi


ivX = iv.exp(iv.pi * iv.log(iv.pi))
lo, hi = iv_to_frac(ivX)
W = hi - lo                       # 真实区间宽度 —— 判定必须用它, 不能用外扩 eps
half = W / 2

print("     区间下界 = %s" % mp.nstr(mp.mpf(lo.numerator) / mp.mpf(lo.denominator), 30))
print("     区间上界 = %s" % mp.nstr(mp.mpf(hi.numerator) / mp.mpf(hi.denominator), 30))
print("     真实宽度 W = %.4e  (半宽 W/2 = %.4e)" % (float(W), float(half)))
chk("区间有效: 0 < W < 1e-110", 0 < W < Fraction(1, 10**110),
    "W = %.4e" % float(W))
chk("区间包含 36.46 < lo < hi < 36.47 (有理比较)",
    lo < hi and Fraction(3646, 100) < lo and hi < Fraction(3647, 100), "")

# 独立交叉验证: 用 mp 250 位独立重算, 取前 100 位作截断下界与上取整上界
mp.dps = 250
ref_s = mp.nstr(mp.pi ** mp.pi, 200)
nd = len(ref_s.split(".")[1]) if "." in ref_s else 0
unit = Fraction(1, 10 ** nd)
f_lo = Fraction(ref_s[:len(ref_s) - (200 - nd)])          # 截断 => <= ref
f_hi = f_lo + unit                                        # 上取整 => >= ref
chk("区间含真值 (250位独立重算交叉验证)",
    lo < f_lo and f_hi < hi,
    "留白 lo->f_lo %.3e" % float(f_lo - lo))
mp.dps = 60

print("\n     排除判据 (严格): 若最优逼近 |mid-p/q| > W/2,")
print("     则区间 [lo,hi] 内不存在分母 <= Q 的有理数。")
mid = (lo + hi) / 2
maxQ = 0
for Q in (10**2, 10**4, 10**6, 10**8, 10**10, 10**12, 10**14,
          10**16, 10**18, 10**20):
    f = mid.limit_denominator(Q)
    r = abs(mid - f)
    strict = r > half
    if strict:
        maxQ = Q
    print("       Q <= %-3d  残差 %.4e  %s"
          % (Q, float(r), "OK (严格排除)" if strict else "未达 W/2 -> 不可判定"))
    if strict:
        chk("排除所有分母 <= %-21d 的有理数" % Q, True,
            "残差 %.3e >> W/2 %.3e" % (float(r), float(half)))
    else:
        print("       ^ 不计入判定: 分辨率不足属预期, 非脚本失败")

print("""
     §T2 结论 (严格, 无条件):
        π^π ∉ { p/q : p ∈ Z, 1 <= q <= %d }
     §T2 局限 (必须与结论一同引用):
       1. 只排除【有限】分母集合, 属初等观察, 不推进 GAP-1。
       2. 任何有限精度只排除有限 Q —— 算力路径的【根本上限】。
          上面 Q >= 10^18 判不出, 正是该上限的直接体现。
       3. 真正无理性证明需二者之一:
          (a) 无穷逼近列, 分母发散且残差可控 (Hermite-Pade 型);
          (b) 代数/超越性论证 (G-S / Baker / Schanuel)。
       4. (b) 已由 TC-1 归约到 (S); (a) 对 π^π 尚无已知构造。
""" % maxQ)

# ================================================================== T3
print("[T3] 配方适用性: 1, 2πi, lnπ, u·lnπ 的 Q-线性无关")
print("     (说明: u 有理 => u·lnπ 落在 span{lnπ} 内 => 必线性相关, 故 u 有理时配方失效)")
print("     充要判据 (F-6 修正): (u, lnπ) 在 Q 上【代数无关】(自动蕴含 u 不为有理数)")
print("     步2 可担保: u 为 π,e 的非常数有理系数多项式")
print("     步2 不可担保: e^e, e^π (其无理性本身未知)\n")
cases = [
    ("u = 1",   mp.mpf(1), "u∈Q -> 配方【不适用】", False),
    ("u = 2",   mp.mpf(2), "u∈Q -> 配方【不适用】(但 2^2=4 有理, 问题平凡)", False),
    ("u = e",   E,         "e,lnπ 代数无关 (步2)", True),
    ("u = π",   PI,        "π,lnπ 代数无关 (步2)", True),
    ("u = π^2", PI**2,     "π^2,lnπ 代数无关 (π^2 是 π 的多项式)", True),
    ("u = π·e", PI*E,      "π·e,lnπ 代数无关 (π·e 是 π,e 的多项式)", True),
    ("u = e^e", E**E,      "【未知】e^e 连无理性都未证 -> 不可用", "未知"),
    ("u = e^π", mp.e**PI,  "【未知】需先证 e^π 在 Q(π,e,lnπ) 上超越", "未知"),
]
for name, u, why, verdict in cases:
    rel = mp.pslq(mp.matrix([mp.mpf(1), LOG_PI, u * LOG_PI]),
                  tol=mp.mpf('1e-40'), maxcoeff=10**8, maxsteps=2000)
    dependent = rel is not None
    print("       %-10s u·lnπ = %-20s PSLQ:%-5s | %s"
          % (name, mp.nstr(u * LOG_PI, 16), "相关" if dependent else "无关", why))
    if verdict is True:
        chk("   %-10s 配方适用" % name, not dependent, "PSLQ 佐证")
    elif verdict is False:
        chk("   %-10s 配方失效 (与 u∈Q 一致)" % name, dependent,
            "PSLQ 确认线性相关")

print("""
     §T3结论 (结构性, THEOREM 级)  —— 2026-09-28 修正 (F-6):
       配方 (S)@n=4 严格适用于 u 的充要判据:
         (u, lnπ) 在 Q 上【代数无关】, 即不存在非零 P ∈ Q[X,Y] 使 P(u, lnπ)=0
         [注: 该条件已自动蕴含 u ∉ Q, 无需单列 —— 若 u=p/q 则 P=qX-p 即反例]

       步2 (π, lnπ, e 代数无关) 可立即担保的 u:
         u = 一切【π, e 的非常数有理系数多项式】
         即 e, π, π^2, π·e, e+π, e^2, π^2+e ...  (无穷集)

       步2 【不能】担保的 u (不得列入可用集):
         e^e, e^π —— 理由: 它们不是 π,e 的多项式;
         若 P(e^e, lnπ)=0, 需先知 e^e 在 Q(π,e,lnπ) 上超越。
         而 e^e 连【无理性】都未知 (arXiv:1310.7289 摘要明列)。
         ⟹ e^e, e^π 属【未知】, 非"需额外 (S) 应用", 亦非"可用"。

       (F-6 撤回的错误表述, 勿复活):
         ✗ "u 与 lnπ 在 Q(π,e,lnπ) 上代数无关"
            —— 错误: π 本身在该基域内, 故 (π, lnπ) 天然【相关】(witness X-π),
            该式会连 u=π 一并排除, 自相矛盾。
         ✗ "立即可证可用: u ∈ {e, π, π^2, e^e, e^π, ...}"
            —— 错误: e^e, e^π 无依据, 且与本脚本表格 u=e^π 行"需额外"自相矛盾。
""")

# ================================================================== 域边界常驻守卫
# 对齐自举 (rev10): 将 pipi_domain_d4_verify.py (TASK-PI-R09-03) 的深垂直探针并入本脚本,
# 作常驻回归守卫。默认路径行为与 rev09 完全一致 (T1/T2/T3); 传入 `--domain` 时追加:
#   T4  deg<=4 多项式残余探针 (三对: (pi,lnpi) / (pi,pi^pi) / (lnpi,pi^pi))
#   T5  6维 PSLQ 整数关系扫描 + 连续性复扫
#   T6  S5 候选有理精确核对 (sympy QQ 因子 + |P(pi)| @dps=160)
# 守卫判据: 任一枚探针残余 < 1e-30 或任一 PSLQ 命中 => 置 FAIL (config 漂移/基组替换被 catch)。
# 真值层级: 仅 EMPIRICAL; 不构成 GAP-1 证据。
if "--domain" in sys.argv:
    _DOMAIN = {
        "box_C": 12, "N_d4": 80000, "N_1v": 40000,
        "pslq_tol": "1e-40", "suspect": "1e-30",
        "seed": 20260930,
    }
    _POW4 = [(i, j) for i in range(5) for j in range(5) if i + j <= 4]
    import random as _random

    def _d4_probe(xv, yv):
        mono = [(i, j, xv ** i * yv ** j) for (i, j) in _POW4]
        rng = _random.Random(_DOMAIN["seed"])
        best = None
        for _ in range(_DOMAIN["N_d4"]):
            while True:
                c = [rng.randint(-_DOMAIN["box_C"], _DOMAIN["box_C"])
                     for _ in range(len(mono))]
                if any(c):
                    break
            s = mono[0][2] * 0
            mx = abs(mono[0][2]) * 0
            for cj, (_, _, m) in zip(c, mono):
                s = s + cj * m
                a = abs(cj) * abs(m)
                if a > mx:
                    mx = a
            r = abs(s) / mx
            if best is None or r < best[0]:
                best = (r, c)
        return best

    print("\n[T4] 域边界常驻守卫: deg<=4 多项式残余探针 (box C=%d, N=%d)"
          % (_DOMAIN["box_C"], _DOMAIN["N_d4"]))
    sus = float(mp.mpf(_DOMAIN["suspect"]))
    for nm, xv, yv in [("(pi, ln(pi))", PI, LOG_PI),
                       ("(pi, pi^pi)", PI, PI**PI),
                       ("(ln(pi), pi^pi)", LOG_PI, PI**PI)]:
        r, c = _d4_probe(xv, yv)
        flag = "  <== 近机噪候选 (anomaly)" if float(r) < sus else ""
        chk("T4: deg<=4 探针 %s" % nm, float(r) >= sus,
            "min剩余=%.3e (H=%d)%s" % (float(r), max(abs(x) for x in c), flag))

    print("\n[T5] 6维 PSLQ 扫描 (tol=%s) + 连续性复扫" % _DOMAIN["pslq_tol"])
    _sets = [
        ("6d 链全面", [1, PI, LOG_PI, PI * LOG_PI, E, PI**PI]),
        ("6d 含 e^pi", [1, PI, LOG_PI, E, PI**PI, E**PI]),
        ("6d 二阶单项式基", [1, PI, PI**2, LOG_PI, LOG_PI**2, PI * LOG_PI]),
        ("6d pi-pi^pi对", [1, PI, PI**2, PI**PI, (PI**PI)**2, PI * PI**PI]),
        ("5d 连续性", [1, PI, LOG_PI, E, PI**PI]),
        ("2d 连续性", [1, PI**PI]),
    ]
    for nm, vec in _sets:
        rel = mp.pslq(vec, tol=mp.mpf(_DOMAIN["pslq_tol"]), maxcoeff=10**6, maxsteps=500)
        chk("T5: PSLQ %s" % nm, rel is None,
            "None" if rel is None else "命中 %s" % (rel,))

    print("\n[T6] S5 候选有理精确核对 (sympy QQ 因子 + |P(pi)|@dps=160)")
    import sympy as _sp
    _x = _sp.Symbol("x", real=True)
    mp.dps = 160
    for d in (1, 2, 3):
        pw = [mp.pi ** k for k in range(d + 1)]
        rng = _random.Random(_DOMAIN["seed"] + d)
        best = None
        for _ in range(_DOMAIN["N_1v"]):
            while True:
                c = [rng.randint(1, _DOMAIN["box_C"]) * (-1 if rng.random() < 0.5 else 1)
                     for _ in range(d + 1)]
                if any(c):
                    break
            s = pw[0] * 0
            mx = abs(pw[0]) * 0
            for cj, m in zip(c, pw):
                s = s + cj * m
                a = abs(cj) * abs(m)
                if a > mx:
                    mx = a
            r = abs(s) / mx
            if best is None or r < best[0]:
                best = (r, c)
        r, c = best
        P = sum(int(x) * _x ** k for k, x in enumerate(c))
        fac = str(_sp.factor(P))
        val = abs(mp.fsum(mp.mpf(int(x)) * mp.pi ** k for k, x in enumerate(c)))
        spurious = float(val) > 1e-130
        chk("T6: deg=%d 候选偶然逼近" % d, spurious,
            "因子=%s |P(pi)|=%.2e" % (fac, float(val)))
    mp.dps = 60

# ==================================================================
print("=" * 80)
print("算术检验: %s" % ("全部通过" if ok else "存在 FAIL"))
print("=" * 80)
print("GAP-1 仍为 GAP-OPEN。本脚本不构成其证据。")

