# -*- coding: utf-8 -*-
"""
pi_reduce_chain.py
TASK-PI-R09-01 卡点归约链专项核验 —— (S)2 ∧ (S)3 ∧ (S)4 约束相容性双轨核验

轨道一  符号轨: 三条约束的场塔单调相容枚举 + 前提自足性分类 (确定推理, 非数值)
轨道二  数值轨: 高精度求值 (主 mpmath dps=60) 采样候选点密度;
                门1 独立复本 (gmpy2 mpfr 280bit + 第二随机种子) 复核一致性
分岔轨  分支面: 最小剩余 |P(pi,ln(pi))| 与 |c·(pi,lnpi,e,pi^pi)|, 定位近代数关系边界

预注册 (门0): 本文件 PREREG 块在【运行前】一次性冻结判据/阈值/种子/后端,
              运行输出即为门0锚点; 事后不得改判据重新声明结论 (README.md §3 真值纪律)。
              判据产物仅定级 EMPIRICAL (可证伪影子), 不构成 THEOREM。

判决接入 (优先级3, 由主控裁决, 本脚本只出 EMPIRICAL 信号):
  分支A 三条约束相容成立 (joint_density=1.0, 双后端一致) -> 可行域非空,
         可推进 pi∈S∪T 域边界刻画 + 候选反例采样器
  分支B 存在约束双后端均有命中失败 (joint<1.0) -> GAP-01 FALSIFIED 候选,
         清理归约链分支, 切次备选路径
"""
import random
import sys

# DEF-1 修复: 控制台代码页无关化 (README §2「数值输出须可复现」)
for _s in ("stdout", "stderr"):
    _f = getattr(sys, _s, None)
    if hasattr(_f, "reconfigure"):
        _f.reconfigure(encoding="utf-8", errors="replace")

# --------------------------------------------------------------------------
# 门0 预注册 (冻结, 运行前锁定, 事后不得修改)
# --------------------------------------------------------------------------
PREREG = {
    "task": "TASK-PI-R09-01",
    "frozen_on": "2026-09-29",
    "symbolic_rules": [
        "场塔: F2=Q(e,pi) sube F3=Q(pi,ln(pi),e) sube F4=Q(pi,ln(pi),e,pi^pi)",
        "单调相容: 存在 0<=t2<=t3<=t4<=4 且 (k in S -> t_k = k), 且 t_k<=k",
        "前提自足: need(C2)=∅, need(C3)={C2}, need(C4)={C2,C3}",
        "SS(S) := 对所有 n in S 有 need(n) sube S",
    ],
    "dps_main": 60,
    "replica_prec_bits": 280,
    "coeff_bound": 32,
    "n_samples": 400,
    "thresh_zero": "1e-25",
    "seed_main": 20260929,
    "seed_replica": 8171017,
    "branch_coeff_bound": 9,
    "branch_n_samples": 3000,
    "joint_pass_density": 0.999,
    "branch_suspect_residual": "1e-20",
    "hypothesis": (
        "H1(EMPIRICAL): 三条约束同时成立的可行域非空且密度=1.0; "
        "本判据不升格 THEOREM; 门1双后端+双种子复核一致方可定 EMPIRICAL-PASS"
    ),
}

CONSTRAINTS = [
    {"id": "C2", "n": 2, "z": ["1", "2*pi*i"], "gens": ["e", "pi"],
     "target": 2, "need": []},
    {"id": "C3", "n": 3, "z": ["1", "2*pi*i", "ln(pi)"], "gens": ["pi", "ln(pi)", "e"],
     "target": 3, "need": ["C2"]},
    {"id": "C4", "n": 4, "z": ["1", "2*pi*i", "ln(pi)", "pi*ln(pi)"],
     "gens": ["pi", "ln(pi)", "e", "pi^pi"], "target": 4, "need": ["C2", "C3"]},
]

def sample_vec(rng, k, B):
    while True:
        v = [rng.randint(-B, B) for _ in range(k)]
        if any(v):
            return v

def comb_sum(zvals, v):
    """采样系数向量 v 作用于 z 元组, 返回 (和 s, 归一化实数尺度)."""
    s = zvals[0] * 0
    scale = abs(zvals[0]) * 0
    for cj, zj in zip(v, zvals):
        s = s + cj * zj
        scale = scale + abs(cj) * abs(zj)
    return s, scale

def li_stats(zvals, rng, B, N, thresh):
    hits = 0
    min_res = None
    for _ in range(N):
        v = sample_vec(rng, len(zvals), B)
        s, scale = comb_sum(zvals, v)
        r = abs(s) / scale
        if min_res is None or r < min_res:
            min_res = r
        if r > thresh:
            hits += 1
    return hits / N, min_res

def joint_density(zsets, rng, B, N, thresh):
    hits = 0
    for _ in range(N):
        ok = True
        for zvals in zsets:
            v = sample_vec(rng, len(zvals), B)
            s, scale = comb_sum(zvals, v)
            if abs(s) / scale <= thresh:
                ok = False
                break
        if ok:
            hits += 1
    return hits / N

def branch_surface(pairs, rng, B, N):
    """对小系数多项式/线性型采样, 返回 (最小归一化剩余, 命中系数向量)."""
    best = (None, None)
    for _ in range(N):
        c = [rng.randint(-B, B) for _ in range(len(pairs))]
        if not any(c):
            continue
        s = pairs[0][1] * 0
        mx = abs(pairs[0][1]) * 0
        for cj, (_, val) in zip(c, pairs):
            s = s + cj * val
            m = abs(cj) * abs(val)
            if m > mx:
                mx = m
        r = abs(s) / mx
        if best[0] is None or r < best[0]:
            best = (r, c)
    return best

def symbolic_branch():
    """约束相容判定表: 全子集单调相容 + 前提自足分类."""
    ids = ["C2", "C3", "C4"]
    tgt = {c["id"]: c["target"] for c in CONSTRAINTS}
    need = {c["id"]: c["need"] for c in CONSTRAINTS}
    rows = []
    for mask in range(1, 8):
        S = [ids[i] for i in range(3) if mask & (1 << i)]
        fixed = dict((cid, tgt[cid]) for cid in S)
        # 贪心自小到大填 t2,t3,t4, 保证单调且 t_k<=k
        vals, prev, feas = {}, 0, True
        for cid in ids:
            k = tgt[cid]
            if cid in fixed:
                tv = fixed[cid]
                if tv < prev or tv > k:
                    feas = False
                    break
                vals[cid] = tv
                prev = tv
            else:
                tv = prev
                if tv > k:
                    feas = False
                    break
                vals[cid] = tv
        ss = all(n in S for cid in S for n in need[cid])
        if feas and ss:
            verdict = "相容且自足"
        elif feas:
            verdict = "单调相容,前提不自足"
        else:
            verdict = "单调不相容"
        rows.append({
            "subset": "{" + ",".join(S) + "}",
            "monotone_feasible": feas,
            "self_sufficient": ss,
            "verdict": verdict,
        })
    return rows

def main():
    print("=" * 78)
    print("TASK-PI-R09-01  (S)2^(S)3^(S)4  约束相容性双轨核验")
    print("=" * 78)

    print("\n[00] 门0 预注册 (冻结于运行前, 事后不得改判据)")
    for k, v in PREREG.items():
        print("      %-22s = %s" % (k, v))

    rows = symbolic_branch()
    print("\n[01] 符号轨: 约束相容判定表")
    print("      %-20s %-18s %-12s %s" % ("subset", "monotone_feasible", "self_suffc", "verdict"))
    for r in rows:
        print("      %-20s %-18s %-12s %s" % (
            r["subset"], r["monotone_feasible"], r["self_sufficient"], r["verdict"]))

    import mpmath as mp
    mp.mp.dps = PREREG["dps_main"]
    PI, E = mp.pi, mp.e
    LNPI, PPPI = mp.log(PI), PI ** PI
    TWO_PI_I = 2j * PI
    zsets = [
        [mp.mpc(1, 0), TWO_PI_I],
        [mp.mpc(1, 0), TWO_PI_I, mp.mpc(LNPI, 0)],
        [mp.mpc(1, 0), TWO_PI_I, mp.mpc(LNPI, 0), mp.mpc(PI * LNPI, 0)],
    ]
    thresh = mp.mpf(PREREG["thresh_zero"])

    rngm = random.Random(PREREG["seed_main"])
    print("\n[02] 数值轨·主后端 mpmath  dps=%d seed=%d B=%d N=%d THRESH=%s"
          % (PREREG["dps_main"], PREREG["seed_main"],
             PREREG["coeff_bound"], PREREG["n_samples"], PREREG["thresh_zero"]))
    li_m = []
    for i, c in enumerate(CONSTRAINTS):
        d, mr = li_stats(zsets[i], rngm, PREREG["coeff_bound"],
                         PREREG["n_samples"], thresh)
        li_m.append((d, mr))
        print("      [%s] li(z) 密度=%.4f  最小归一化剩余=%.3e" % (c["id"], d, float(mr)))
    jd_m = joint_density(zsets, rngm, PREREG["coeff_bound"],
                         PREREG["n_samples"], thresh)
    print("      [JOINT] 三约束同时通过密度 = %.4f" % jd_m)

    rngm2 = random.Random(PREREG["seed_main"] + 1)
    res1, c1 = branch_surface(
        [("pi", PI), ("ln(pi)", LNPI), ("pi*ln(pi)", PI * LNPI),
         ("pi^2", PI * PI), ("ln(pi)^2", LNPI * LNPI)],
        rngm2, PREREG["branch_coeff_bound"], PREREG["branch_n_samples"])
    res2, c2 = branch_surface(
        [("g0*pi", PI), ("g1*lnpi", LNPI), ("g2*e", E), ("g3*pp", PPPI)],
        rngm2, PREREG["branch_coeff_bound"], PREREG["branch_n_samples"])
    print("\n[03] 分岔轨·主后端 (边界/分岔位置)")
    print("      min|P(pi,ln(pi))| 归一化剩余 = %.3e  (coeff=%s)" % (float(res1), c1))
    print("      min|c0*pi+c1*lnpi+c2*e+c3*pi^pi| 归一化剩余 = %.3e  (coeff=%s)"
          % (float(res2), c2))

    import gmpy2
    gmpy2.get_context().precision = PREREG["replica_prec_bits"]
    RPI = gmpy2.const_pi()
    RE = gmpy2.exp(gmpy2.mpfr(1))
    RLN = gmpy2.log(RPI)
    RPP = RPI ** RPI
    RCP = gmpy2.mpc(0, 2 * RPI)
    rzsets = [
        [gmpy2.mpc(1, 0), RCP],
        [gmpy2.mpc(1, 0), RCP, gmpy2.mpc(RLN, 0)],
        [gmpy2.mpc(1, 0), RCP, gmpy2.mpc(RLN, 0), gmpy2.mpc(RPI * RLN, 0)],
    ]
    rt = gmpy2.mpfr(PREREG["thresh_zero"])
    rngr = random.Random(PREREG["seed_replica"])
    print("\n[04] 数值轨·门1复本 gmpy2  prec=%dbit seed=%d B=%d N=%d THRESH=%s"
          % (PREREG["replica_prec_bits"], PREREG["seed_replica"],
             PREREG["coeff_bound"], PREREG["n_samples"], PREREG["thresh_zero"]))
    li_r = []
    for i, c in enumerate(CONSTRAINTS):
        d, mr = li_stats(rzsets[i], rngr, PREREG["coeff_bound"],
                         PREREG["n_samples"], rt)
        li_r.append((d, mr))
        print("      [%s] li(z) 密度=%.4f  最小归一化剩余=%.3e" % (c["id"], d, float(mr)))
    jd_r = joint_density(rzsets, rngr, PREREG["coeff_bound"],
                         PREREG["n_samples"], rt)
    print("      [JOINT] 三约束同时通过密度 = %.4f" % jd_r)

    rngr2 = random.Random(PREREG["seed_replica"] + 1)
    rres1, rc1 = branch_surface(
        [("pi", RPI), ("lnpi", RLN), ("pi*lnpi", RPI * RLN),
         ("pi^2", RPI * RPI), ("lnpi^2", RLN * RLN)],
        rngr2, PREREG["branch_coeff_bound"], PREREG["branch_n_samples"])
    rres2, rc2 = branch_surface(
        [("g0*pi", RPI), ("g1*lnpi", RLN), ("g2*e", RE), ("g3*pp", RPP)],
        rngr2, PREREG["branch_coeff_bound"], PREREG["branch_n_samples"])
    print("\n[05] 分岔轨·门1复本 (gmpy2)")
    print("      min|P(pi,ln(pi))| 归一化剩余 = %.3e  (coeff=%s)" % (float(rres1), rc1))
    print("      min|c0*pi+c1*lnpi+c2*e+c3*pi^pi| 归一化剩余 = %.3e  (coeff=%s)"
          % (float(rres2), rc2))

    print("\n[06] 门1 独立复本一致性 (双后端 + 双种子)")
    print("      AGREE 规则: 密度一致且双端最小剩余均 > 1e-15 (远离近零带), 量级(10对数)差 < 3")
    agree = True
    for i, (dm, dr) in enumerate(zip(li_m, li_r)):
        same = (abs(dm[0] - dr[0]) < 1e-9) and (dm[1] > mp.mpf("1e-15")) and (
            dr[1] > mp.mpf("1e-15")) and (
            abs(float(mp.log(dm[1]) / mp.log(10)) - float(mp.log(dr[1]) / mp.log(10))) < 3.0)
        agree &= same
        print("      [%s] 剩余 主=%.3e 复本=%.3e  -> %s"
              % (CONSTRAINTS[i]["id"], float(dm[1]), float(dr[1]),
                 "AGREE" if same else "DISAGREE"))
    same_j = abs(jd_m - jd_r) < 1e-9
    agree &= same_j
    print("      [JOINT] 主=%.4f 复本=%.4f -> %s"
          % (jd_m, jd_r, ("AGREE" if same_j else "DISAGREE")))

    print("\n[07] EMPIRICAL 信号 (仅信号, 分支A/B 由主控按优先级3裁决)")
    branch_ok = (float(res1) > float(PREREG["branch_suspect_residual"])) and (
        float(rres1) > float(PREREG["branch_suspect_residual"]))
    if (jd_m >= PREREG["joint_pass_density"] and jd_r >= PREREG["joint_pass_density"]
            and agree and branch_ok):
        print("      joint=1.0 双后端一致; 分支面无近零关系 -> 可行域非空(数值阴影)"
              " -> 分支A 具备考查资格")
    else:
        print("      joint<1.0 或双后端不一致 -> 分支B: 数值阴影证伪候选, 提请审查")
        print("      (单端失败属 PENDING; 双端均失败方为 EMPIRICAL-FAIL)")

    print("\n完成 (TASK-PI-R09-01)")

if __name__ == "__main__":
    main()