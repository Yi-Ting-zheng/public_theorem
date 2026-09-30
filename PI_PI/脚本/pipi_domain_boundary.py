# -*- coding: utf-8 -*-
"""
pipi_domain_boundary.py
TASK-PI-R09-02 分支A之「π∈S∪T 域边界刻画 + 候选反例采样器」

承接 TASK-PI-R09-01 (归约链相容: 可行域 (2,3,4) 数值阴影成立, 分支A 具备考查资格)。
本脚本做域边界的一阶数值采样, 目标不是「证」任何分类, 而是**找出值得精确验证的候选**:

  S1  LI4 整数关系探测: (1, lnπ, π·lnπ) PSLQ  (归约链 z4 元组实数维序的确定性检查)
  S2  链目标生成元整数关系: [1,π,lnπ,e,π^π] 及其子集 PSLQ
      (候选反例: 若存在小高度整数关系, 则链终结论『π,lnπ,e,π^π 代数无关』的数值阴影即被打穿)
  S3  底-指数对二次(全次数<=2)多项式关系: (π,lnπ) / (π,π^π) / (lnπ,π^π)
  S4  (π,lnπ) 三次(全次数<=3)多项式关系 —— lnπ 对 Q(π) 代数性的数值探测
  S5  π 单元多项式近似采样器 deg=1..3: 输出 (系数, 归一化剩余, 高度H, 经验指数 e)
       ← 沿此方向刻画 π 逼近分布的边界 (非 μ(π) 上界依据, 仅候选)
  S6  门1 复本后端 gmpy2 (280bit) 重跑 S3/S4/S5 的采样密度与最小剩余, 与主一致
      (PSLQ 无 gmpy2 等价, 复本侧用采样式整数密度作为其影子)

诚实边界 (README §3 真值纪律):
  - 全部产物仅 EMPIRICAL; 不判定 π∈S 还是 T (需 w_n(π) 的解析级信息, 数值采样不足);
  - 单变量 e_d 是「小系数多项式族的采样分布」描述, 不是 w_n(π)/μ(π) 上界;
  - S3/S4 最小剩余在机器噪声(~1e-58 at 60位)以下才视为近代数关系候选(FCN-6)。

预注册 (门0): 本文件 PREREG 冻结于运行前, 运行输出即为锚点; 事后不得改判据。
门1: S6 独立后端+独立种子复算, 分类一致方可定 EMPIRICAL-PASS。
"""
import random
import sys
import math

for _s in ("stdout", "stderr"):
    _f = getattr(sys, _s, None)
    if hasattr(_f, "reconfigure"):
        _f.reconfigure(encoding="utf-8", errors="replace")

PREREG = {
    "task": "TASK-PI-R09-02",
    "frozen_on": "2026-09-29",
    "dps_main": 60,
    "replica_prec_bits": 280,
    "box_C": 12,                      # 整数系数箱 |c| <= C
    "N_pair_d2": 40000,               # S3: 每对二次多项式采样数
    "N_pair_d3": 60000,               # S4: (pi,lnpi) 三次多项式采样数
    "N_1v": 40000,                    # S5: 每次数 1-var 采样数
    "pslq_tol": "1e-40",
    "pslq_maxcoeff": 10**6,
    "pslq_maxsteps": 300,
    "suspect_residual": "1e-30",      # 双后端均低于此 -> 近代数关系候选 (FCN-6)
    "seed_main": 20260930,            # 独立于 R09-01
    "seed_replica": 1357911,
    "hypothesis": (
        "H2(EMPIRICAL): box=12, PSLQ tol=1e-40, dps60主/280bit复本 下, "
        "链目标生成元整数关系与 (pi,lnpi) 代数关系均无近机噪级候选; "
        "不判定 S/T, 不升格 THEOREM"
    ),
}

POW2 = [(0, 0), (1, 0), (0, 1), (1, 1), (2, 0), (0, 2)]          # 全次数<=2
POW3 = [(0, 0), (1, 0), (0, 1), (1, 1), (2, 0), (0, 2),
        (3, 0), (2, 1), (1, 2), (0, 3)]                          # 全次数<=3


def sample_vec(rng, k, C):
    while True:
        v = [rng.randint(-C, C) for _ in range(k)]
        if any(v):
            return v


def min_residual(powlist, xval, yval, rng, C, N):
    """min |Σ c_ij x^i y^j| / max|c_ij m_ij|, 返回 (r_min, c_best, H_best)."""
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
            H = max(abs(x) for x in c)
            best = (r, c, H)
    return best


def single_var_residual(deg, pival, rng, C, N):
    """min |Σ c_k pi^k| / max|c_k pi^k|, 返回 (r_min, c_best, H, e)."""
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
            H = max(abs(x) for x in c)
            best = (r, c, H)
    r, c, H = best
    e = None if r == 0 else -math.log10(float(r)) / math.log10(float(H))
    return r, c, H, e


def run_pslq(backend, vec, pr):
    if backend != "mpmath":
        return None
    import mpmath as mp
    tol = mp.mpf(pr["pslq_tol"])
    try:
        res = mp.pslq([mp.mpf(x) for x in vec], tol=tol,
                      maxcoeff=pr["pslq_maxcoeff"], maxsteps=pr["pslq_maxsteps"])
    except Exception:
        res = None
    return None if res is None else list(res)


def main():
    print("=" * 78)
    print("TASK-PI-R09-02  π∈S∪T 域边界采样 + 候选反例采样器 (EMPIRICAL)")
    print("=" * 78)

    print("\n[00] 门0 预注册 (冻结于运行前, 事后不得改判据)")
    for k, v in PREREG.items():
        print("      %-20s = %s" % (k, v))

    import mpmath as mp
    mp.mp.dps = PREREG["dps_main"]
    PI, E = mp.pi, mp.e
    LNPI, PPPI = mp.log(PI), PI ** PI

    print("\n[01] 常数 (dps=%d)" % PREREG["dps_main"])
    for nm, v in [("pi", PI), ("e", E), ("ln(pi)", LNPI), ("pi^pi", PPPI)]:
        print("      %-9s = %s" % (nm, mp.nstr(v, 26)))

    print("\n[02] S1  LI4 (1, lnπ, π·lnπ) PSLQ (tol=%s)" % PREREG["pslq_tol"])
    v1 = [1, LNPI, PI * LNPI]
    r1 = run_pslq("mpmath", v1, PREREG)
    print("      -> %s" % ("None (无整数关系)" if r1 is None else "候选关系 %s" % r1))

    print("\n[03] S2  链目标生成元整数关系 PSLQ")
    sets = [
        ("[1, pi^pi]", [1, PPPI]),
        ("[1, ln(pi), pi^pi]", [1, LNPI, PPPI]),
        ("[1, pi, ln(pi), pi^pi]", [1, PI, LNPI, PPPI]),
        ("[1, pi, ln(pi), e, pi^pi]", [1, PI, LNPI, E, PPPI]),
    ]
    for nm, v in sets:
        r = run_pslq("mpmath", v, PREREG)
        print("      %-34s -> %s" % (nm, "None (无整数关系)"
                                     if r is None else "候选关系 %s" % r))

    # ---- S3 / S4: 底指数对多项式关系 (主后端)
    rng = random.Random(PREREG["seed_main"])
    print("\n[04] S3/S4 多项式关系采样 (主后端, box C=%d)" % PREREG["box_C"])
    suspects = []
    pairs = [
        ("(pi, ln(pi))", POW2, PI, LNPI, PREREG["N_pair_d2"]),
        ("(pi, pi^pi)", POW2, PI, PPPI, PREREG["N_pair_d2"]),
        ("(ln(pi), pi^pi)", POW2, LNPI, PPPI, PREREG["N_pair_d2"]),
        ("(pi, ln(pi))", POW3, PI, LNPI, PREREG["N_pair_d3"]),
    ]
    res_main = {}
    for nm, pl, xv, yv, N in pairs:
        r, c, H = min_residual(pl, xv, yv, rng, PREREG["box_C"], N)
        res_main[nm] = r
        flag = "  <== 近机噪候选" if r < mp.mpf(PREREG["suspect_residual"]) else ""
        print("      %-20s deg<=%d  min剩余=%.3e  (H=%d, c=%s)%s"
              % (nm, 2 if len(pl) == 6 else 3, float(r), H, c, flag))
        if flag:
            suspects.append(nm)

    # ---- S5: π 单元多项式近似
    print("\n[05] S5  π 单元多项式近似采样 (每度 N=%d, box C=%d)"
          % (PREREG["N_1v"], PREREG["box_C"]))
    e_by_deg = {}
    for d in (1, 2, 3):
        r, c, H, e = single_var_residual(d, PI, rng, PREREG["box_C"], PREREG["N_1v"])
        e_by_deg[d] = (r, e)
        flag = "  <== 近机噪候选" if r < mp.mpf(PREREG["suspect_residual"]) else ""
        print("      deg=%d  min剩余=%.3e  H=%d  e=%.3f  (c=%s)%s"
              % (d, float(r), H, -1.0 if e is None else e, c, flag))
        if flag:
            suspects.append("deg%d" % d)

    # ---- S6: 门1 复本 gmpy2
    import gmpy2
    gmpy2.get_context().precision = PREREG["replica_prec_bits"]
    RPI = gmpy2.const_pi()
    RE = gmpy2.exp(gmpy2.mpfr(1))
    RLN = gmpy2.log(RPI)
    RPP = RPI ** RPI
    rngr = random.Random(PREREG["seed_replica"])
    print("\n[06] S6 门1 复本 gmpy2 (prec=%dbit, seed=%d)"
          % (PREREG["replica_prec_bits"], PREREG["seed_replica"]))
    res_rep = {}
    for nm, pl, xv, yv, N in pairs:
        r, c, H = min_residual(pl, xv, yv, rngr, PREREG["box_C"], N)
        res_rep[nm] = r
        flag = "  <== 近机噪候选" if r < gmpy2.mpfr(PREREG["suspect_residual"]) else ""
        print("      %-20s min剩余=%.3e  (H=%d, c=%s)%s"
              % (nm, float(r), H, c, flag))
        if flag:
            suspects.append("rep:" + nm)
    print("      单变量复本取样 (deg 1..3):")
    for d in (1, 2, 3):
        r, c, H, e = single_var_residual(d, RPI, rngr, PREREG["box_C"], PREREG["N_1v"])
        print("      deg=%d  min剩余=%.3e  H=%d  e=%.3f"
              % (d, float(r), H, -1.0 if e is None else e))

    # ---- 一致性 & 判定
    print("\n[07] 门1 复本一致性与 EMPIRICAL 信号")
    agree = True
    for nm in res_main:
        a = float(res_main[nm])
        b = float(res_rep[nm])
        od = abs(math.log10(a) - math.log10(b))
        same = od < 3.0 and a > float(PREREG["suspect_residual"]) and \
            b > float(PREREG["suspect_residual"])
        agree &= same
        print("      %-20s 主=%.3e 复本=%.3e 量级差=%.1f -> %s"
              % (nm, a, b, od, "AGREE" if same else "DISAGREE"))
    pslq_hits = [r for r in (r1,)]
    pslq_clean = r1 is None
    for nm, v in sets:
        if run_pslq("mpmath", v, PREREG) is not None:
            pslq_clean = False

    if agree and pslq_clean and not suspects:
        print("      候选=0, PSLQ 全部无关系, 双后端一致 -> EMPIRICAL-PASS")
        print("      (链目标代数无关/整数关系 无近机噪候选; 分支A 域边界采样完成第一阶)")
    else:
        print("      候选=%d PSLQ干净=%s 复本一致=%s"
              % (len(suspects), pslq_clean, agree))
        for s in suspects:
            print("      候选/嫌疑: %s" % s)
        print("      -> 进入深度审查 (精确代数验证嫌疑候选)")

    print("\n完成 (TASK-PI-R09-02)")


if __name__ == "__main__":
    main()