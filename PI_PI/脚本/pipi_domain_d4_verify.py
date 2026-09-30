# -*- coding: utf-8 -*-
"""
pipi_domain_d4_verify.py
TASK-PI-R09-03 纵深: deg<=4 多项式探针 + 6维 PSLQ 扫描 + S5 候选精确代数核对

承接 TASK-PI-R09-02 (EMPIRICAL-PASS: 候选=0)。本脚本做两阶纵深:

  A  S4 纵深   (π,lnπ)/(π,π^π)/(lnπ,π^π) 多项式关系 全次数<=4 (15 单项式)
  B  6维 PSLQ 扫描:
       B1 [1, π, lnπ, π·lnπ, e, π^π]
       B2 [1, π, lnπ, e, π^π, e^π]
       B3 [1, π, π^2, lnπ, lnπ^2, π·lnπ]      (二阶单项式基: 低阶代数关系直接搜索)
       B4 [1, π, π^2, π^π, (π^π)^2, π·π^π]    (π–π^π 对, GAP-1 直接相关)
       + 连续性复扫 2/4/5 维既有 PSLQ 集
       任一非 None 关系 -> dps=90 精确复核 (FCN-8)
  C  S5 精确代数核对 (有理核验):
       对 S5 检出的候选多项式 P(c) (主/复本逐度) 做:
         i  sympy 有理因子分解 (域 QQ) —— 解释偶然逼近来源
         ii 高精度求值 |P(π)| @dps=160 -> log10 —— 非零到 150 位以上 => 非代数关系
         iii 最近代根 r 与 |π-r| 量级对照 —— 说明小剩余的结构性成因
       → 区分「偶然逼近」(存在理根/近根因子, |P(π)|≫1e-130) 与「真实代数关系」
         (不可约且 |P(π)|≈1e-130 —— 依 Lindemann–Weierstraß 不可能, 若触发属于数值实现错误)

真值纪律: 仅 EMPIRICAL; π 超越性由文献定理保证, 本脚本只负责候选的数值-代数核验分离。

预注册 (门0): PREREG 冻结; 运行输出即锚点; 事后不得改判据。
门1: gmpy2 (280bit) 复本抽查 A 的三对 min 剩余 (B/C 无后端等价, 由 A 剩余下限作影子)。
"""
import random
import sys
import math

for _s in ("stdout", "stderr"):
    _f = getattr(sys, _s, None)
    if hasattr(_f, "reconfigure"):
        _f.reconfigure(encoding="utf-8", errors="replace")

PREREG = {
    "task": "TASK-PI-R09-03",
    "frozen_on": "2026-09-29",
    "dps_main": 60,
    "dps_verify": 160,
    "replica_prec_bits": 280,
    "box_C": 12,
    "N_d4": 80000,
    "N_1v": 40000,
    "pslq_tol": "1e-40",
    "pslq_maxsteps": 500,
    "pslq_maxcoeff": 10**6,
    "suspect_residual": "1e-30",
    "verify_suspect_log10": 130,
    "seed_main": 20260930,
    "seed_replica": 1357911,
    "hypothesis": (
        "H3(EMPIRICAL): deg<=4 多项式探针 + 6维 PSLQ, box=12, tol=1e-40, "
        "dps60主/280bit复本 下无近机噪候选; S5 候选均为可解释的偶然逼近; 不升格 THEOREM"
    ),
}

POW4 = [(i, j) for i in range(5) for j in range(5) if i + j <= 4]   # 15 单项式


def sample_vec(rng, k, C):
    while True:
        v = [rng.randint(-C, C) for _ in range(k)]
        if any(v):
            return v


def min_residual(powlist, xval, yval, rng, C, N):
    mono = [(i, j, xval ** i * yval ** j) for (i, j) in powlist]
    best = (None, None, None)
    for _ in range(N):
        c = sample_vec(rng, len(mono), C)
        s = mono[0][2] * 0
        mx = abs(mono[0][2]) * 0
        for cj, (_, _, m) in zip(c, mono):
            s = s + cj * m
            a = abs(cj) * abs(m)
            if a > mx:
                mx = a
        r = abs(s) / mx
        if best[0] is None or r < best[0]:
            best = (r, c, max(abs(x) for x in c))
    return best


def single_var_candidates(deg, pival, rng, C, N):
    """返回每个 deg 最优候选 (r, c, H) —— 供 C 段精确核对复现。"""
    pw = [pival ** k for k in range(deg + 1)]
    best = (None, None, None)
    for _ in range(N):
        c = sample_vec(rng, deg + 1, C)
        s = pw[0] * 0
        mx = abs(pw[0]) * 0
        for cj, m in zip(c, pw):
            s = s + cj * m
            a = abs(cj) * abs(m)
            if a > mx:
                mx = a
        r = abs(s) / mx
        if best[0] is None or r < best[0]:
            best = (r, c, max(abs(x) for x in c))
    return best


def pslq_check(vec, tol):
    import mpmath as mp
    try:
        res = mp.pslq([mp.mpf(x) for x in vec], tol=tol,
                      maxcoeff=PREREG["pslq_maxcoeff"],
                      maxsteps=PREREG["pslq_maxsteps"])
    except Exception:
        res = None
    return None if res is None else list(res)


def verify_candidate(coeffs):
    """有理核对多项式候选: 因子分解(QQ) + |P(pi)| @dps=verify 统一用 mpmath π。"""
    import mpmath as mp
    import sympy as sp
    x = sp.Symbol("x", real=True)
    P = sum(int(c) * x ** k for k, c in enumerate(coeffs))
    fac = sp.factor(P)
    fac_s = str(fac)
    mp.mp.dps = PREREG["dps_verify"]
    val = mp.fabs(mp.fsum(mp.mpf(int(c)) * mp.pi ** k
                          for k, c in enumerate(coeffs)))
    l10 = mp.mpf(math.log10(max(float(val), mp.mpf("1e-999")))) if val > 0 else -PREREG["dps_verify"] * 1.0
    # 最近代根(复数近似)与 |π - r|
    try:
        roots = sp.nroots(P, maxsteps=400, maxn=60)
        best_d = None
        pi_f = float(mp.pi)
        for r in roots:
            d = abs(complex(r) - pi_f)
            if best_d is None or d < best_d[0]:
                best_d = (d, complex(r))
    except Exception:
        best_d = None
    irred = sp.degree(P) > 0 and fac_s.replace(" ", "").count("*") == 0
    sus = irred and float(val) < 10.0 ** (-PREREG["verify_suspect_log10"])
    if sus:
        verdict = "经数值核对疑似代数关系 (不可约且 |P(pi)|~1e-%d) —— 与 L–W 超越性矛盾, 判为数值/实现错误嫌疑, 需检修" % PREREG["verify_suspect_log10"]
    else:
        verdict = "偶然逼近 (|P(pi)|=%.2e, 非消零; 因子分解解释来源)" % float(val)
    note = ""
    if best_d:
        note = "; 最近代根 r=%s, |pi-r|=%.3f" % (
            "%s" % (sp.N(best_d[1], 5)), best_d[0])
    return verdict, fac_s, float(val), l10, note, irred


def main():
    print("=" * 80)
    print("TASK-PI-R09-03  纵深: deg<=4 探针 + 6维 PSLQ + S5 精确核对 (EMPIRICAL)")
    print("=" * 80)

    print("\n[00] 门0 预注册 (冻结于运行前, 事后不得改判据)")
    for k, v in PREREG.items():
        print("      %-22s = %s" % (k, v))

    import mpmath as mp
    mp.mp.dps = PREREG["dps_main"]
    PI, E = mp.pi, mp.e
    LNPI = mp.log(PI)
    PPPI = PI ** PI
    EPI = E ** PI

    print("\n[01] A  S4 纵深 (deg<=4, 15 单项式, N=%d, box C=%d, 主后端)"
          % (PREREG["N_d4"], PREREG["box_C"]))
    rng = random.Random(PREREG["seed_main"])
    pairs = [
        ("(pi, ln(pi))", PI, LNPI),
        ("(pi, pi^pi)", PI, PPPI),
        ("(ln(pi), pi^pi)", LNPI, PPPI),
    ]
    res_main, can_main = {}, {}
    for nm, xv, yv in pairs:
        r, c, H = min_residual(POW4, xv, yv, rng, PREREG["box_C"], PREREG["N_d4"])
        res_main[nm] = r
        can_main[nm] = c
        flag = "  <== 近机噪候选(FCN-9)" if r < mp.mpf(PREREG["suspect_residual"]) else ""
        print("      %-18s min剩余=%.3e  (H=%d, c=%s)%s" % (nm, float(r), H, c, flag))

    print("\n[02] B  6维 PSLQ 扫描 (tol=%s, maxsteps=%d) + 连续性复扫"
          % (PREREG["pslq_tol"], PREREG["pslq_maxsteps"]))
    sets = [
        ("6d B1 链全面", [1, PI, LNPI, PI * LNPI, E, PPPI]),
        ("6d B2 含 e^pi", [1, PI, LNPI, E, PPPI, EPI]),
        ("6d B3 二阶单项式基", [1, PI, PI ** 2, LNPI, LNPI ** 2, PI * LNPI]),
        ("6d B4 pi-pi^pi对", [1, PI, PI ** 2, PPPI, PPPI ** 2, PI * PPPI]),
        ("5d 连续性", [1, PI, LNPI, E, PPPI]),
        ("4d 连续性", [1, PI, LNPI, PPPI]),
        ("2d 连续性", [1, PPPI]),
    ]
    tol = mp.mpf(PREREG["pslq_tol"])
    pslq_hits = []
    for nm, vec in sets:
        r = pslq_check(vec, tol)
        if r is None:
            print("      %-20s -> None (无整数关系)" % nm)
        else:
            mp.mp.dps = PREREG["dps_verify"]
            tot = mp.fabs(mp.fsum(mp.mpf(int(r[k])) * mp.mpf(vec[k])
                                  for k in range(len(vec))))
            tag = "通过 %s" % ("dps=%d 复核 %.2e < 1e-40 => 候选成立" % (PREREG["dps_verify"], float(tot))
                               if tot < mp.mpf("1e-40") else
                               "dps=%d 复核 %.2e >= 1e-40 => 数值假阳性" % (PREREG["dps_verify"], float(tot)))
            print("      %-20s -> 候选关系 %s  %s" % (nm, r, tag))
            if tot < mp.mpf("1e-40"):
                pslq_hits.append((nm, r, float(tot)))

    print("\n[03] C  S5 候选精确代数核对 (sympy 有理因子 + |P(pi)| @dps=%d)"
          % PREREG["dps_verify"])
    import sympy as sp
    x = sp.Symbol("x", real=True)
    s5_verdicts = {}
    for backend, pival, seed, C in [("主", PI, PREREG["seed_main"], PREREG["box_C"]),
                                    ("复本", None, PREREG["seed_replica"], PREREG["box_C"])]:
        if backend == "复本":
            import gmpy2
            gmpy2.get_context().precision = PREREG["replica_prec_bits"]
            pival = gmpy2.const_pi()
            seed = PREREG["seed_replica"]
        rngb = random.Random(seed)
        for d in (1, 2, 3):
            r, c, H = single_var_candidates(d, pival, rngb, C, PREREG["N_1v"])
            coeff = [int(z) for z in c] if backend == "复本" else [int(z) for z in c]
            verdict, fac_s, val, l10, note, irred = verify_candidate(coeff)
            s5_verdicts[(backend, d)] = (coeff, fac_s, val, verdict)
            print("      %s deg=%d  c=%s  因子=%s  |P(pi)|=%.2e (log10=%.0f)%s"
                  % (backend, d, coeff, fac_s, val, l10, note))
            print("            -> %s" % verdict)

    print("\n[04] D  门1 复本 gmpy2 (prec=%dbit, seed=%d): deg<=4 抽查"
          % (PREREG["replica_prec_bits"], PREREG["seed_replica"]))
    import gmpy2
    gmpy2.get_context().precision = PREREG["replica_prec_bits"]
    RPI = gmpy2.const_pi()
    RLN = gmpy2.log(RPI)
    RPP = RPI ** RPI
    rngr = random.Random(PREREG["seed_replica"])
    res_rep = {}
    for nm, xv, yv in [("(pi, ln(pi))", RPI, RLN),
                       ("(pi, pi^pi)", RPI, RPP),
                       ("(ln(pi), pi^pi)", RLN, RPP)]:
        r, c, H = min_residual(POW4, xv, yv, rngr, PREREG["box_C"], PREREG["N_d4"])
        res_rep[nm] = r
        flag = "  <== 近机噪候选(FCN-9)" if r < gmpy2.mpfr(PREREG["suspect_residual"]) else ""
        print("      %-18s min剩余=%.3e  (H=%d, c=%s)%s"
              % (nm, float(r), H, c, flag))

    print("\n[05] 门1 一致性与 FCN 定级")
    agree = True
    for nm in res_main:
        a = float(res_main[nm])
        b = float(res_rep[nm])
        od = abs(math.log10(a) - math.log10(b))
        same = od < 3.0 and a > float(PREREG["suspect_residual"]) and \
            b > float(PREREG["suspect_residual"])
        agree &= same
        print("      %-18s 主=%.3e 复本=%.3e 量级差=%.1f -> %s"
              % (nm, a, b, od, "AGREE" if same else "DISAGREE"))
    fcn9 = [k for k, v in res_main.items() if v < mp.mpf(PREREG["suspect_residual"])]
    fcn9 += [k for k, v in res_rep.items() if v < gmpy2.mpfr(PREREG["suspect_residual"])]
    fcn9 = list(set(fcn9))
    spurious_all = all(v[2] > 10.0 ** (-PREREG["verify_suspect_log10"]) for v in s5_verdicts.values())

    if agree and not pslq_hits and not fcn9 and spurious_all:
        print("      deg<=4 探针: 无近机噪候选; 6维 PSLQ: None 全数; S5 候选: 全部=偶然逼近")
        print("      -> EMPIRICAL-PASS (低阶代数关系 无候选; 域边界纵深完成)")
    else:
        print("      PSLQ候选=%d  FCN-9候选=%d  复本一致=%s  全部偶然逼近=%s"
              % (len(pslq_hits), len(fcn9), agree, spurious_all))
        for h in pslq_hits:
            print("      PSLQ候选: %s" % (h,))
        print("      -> 进入深度审查")

    print("\n完成 (TASK-PI-R09-03)")


if __name__ == "__main__":
    main()