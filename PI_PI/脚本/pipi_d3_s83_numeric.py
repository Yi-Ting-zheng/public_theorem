# -*- coding: utf-8 -*-
"""§8.3 数值自检（EMPIRICAL 级）。

稳定性说明：E_N = e^z - S_N(z) 直接相减在高 N 下灾难性抵消
（log10(E_N) ≈ (N+1)log10(z) - log10(N!)），故改用正则化不完全 Gamma
闭式 E_N(z) = e^z * P(N+1, z)（下正则化；恒等 P(1,z)=1-e^{-z}）。
注意：上正则化 Q(N+1,z)=e^{-z}*sum_{k<=N}z^k/k! 代入会给 e^z*Q=1 的错误
结果（初版犯此错），禁用。初版用 mp.quad 积分 (1-t)^N 在 N>100 挂死，已弃用。
输出：pipi_d3_s83_numeric_out.txt（同目录）。真值层级 = EMPIRICAL。
"""
import io, os
from mpmath import mp, mpf, exp, log, pi, factorial, nstr, nint, gammainc

mp.dps = 120
out = []
W = out.append


def nint_dist(x):
    return abs(x - mpf(nint(x)))


def S_N(zz, N):
    return sum(zz ** n / factorial(n) for n in range(N + 1))


def E_N(zz, N):
    return exp(zz) * gammainc(N + 1, 0, zz, regularized=True)


def E_N_quad(zz, N):
    return zz ** (N + 1) / factorial(N) * mp.quad(
        lambda t: exp(zz * t) * (1 - t) ** N, [0, 1])


out_file = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "pipi_d3_s83_numeric_out.txt")

z = pi * log(pi)
W("§8.3 数值自检（EMPIRICAL；不构成 GAP-1 证据）")
W("z = pi*ln(pi) = %s" % nstr(z, 25))
W("")

W("[1] 余项闭式交叉验证: E_N = e^z*Q(N+1,z)  vs  积分式 z^{N+1}/N!*I_N")
for N in [0, 1, 2, 3, 5, 8, 12]:
    a, b = E_N(z, N), E_N_quad(z, N)
    W("    N=%-3d gamma=%s  quad=%s  rel=%.3e"
      % (N, nstr(a, 12), nstr(b, 12), abs((a - b) / b)))
W("")

W("[2] 渐近 R_N = E_N*N!*(N+1-z)/z^{N+1}  (应 -> 1)")
for N in [20, 50, 100, 200, 400]:
    R = E_N(z, N) * factorial(N) * (N + 1 - z) / z ** (N + 1)
    W("    N=%-4d R_N = %s" % (N, nstr(R, 18)))
W("")

W("[3] T1 判别量 D_N(q) = dist(q*S_N(z),Z)/(q*E_N(z))  [目标 z，未假定 H]")
W("    H 为真时必有 D_N(q) -> 1；故对目标观测 D_N 是否远离 1")
for q in [1, 2, 3]:
    row = []
    for N in [10, 20, 40]:
        row.append("N=%d:%.6f" % (N, nint_dist(q * S_N(z, N)) / (q * E_N(z, N))))
    W("    q=%-3d %s" % (q, "  ".join(row)))
W("    注: 分子 dist(q*S_N,Z) -> dist(qe^z,Z) 固定, 分母阶乘级->0")
W("        => 目标处 D_N -> +∞ (与 H 缺陷行为一致; EMPIRICAL, 仅反证线索)")
W("")

z0 = log(mpf(3) / 2)
W("[4] 对照组 z0 = ln(3/2) = %s" % nstr(z0, 25))
W("    e^z0 = %s   恰为 3/2 ? %s" % (nstr(exp(z0), 30), abs(exp(z0) - mpf(3) / 2) < mpf(10) ** -60))
W("    (z0 超越: e^{非零代数数} 超越 <-> ln(3/2) 超越)")
W("    T1 精确验证 (此处 H 真成立, q=2, 期望 D_N -> 1):")
for N in [5, 10, 20, 40, 80, 160]:
    W("      N=%-4d D_N(2) = %s" % (N, nstr(nint_dist(2 * S_N(z0, N)) / (2 * E_N(z0, N)), 18)))
W("      注: N>=80 后 2*E_N 低于精度地板(120位), D_N 退化为数值噪声, 不再输出")
W("    H 不成立时 (q=1,3,5, 期望 D_N 远离 1 且发散):")
for q in [1, 3, 5]:
    row = []
    for N in [10, 20, 40]:
        row.append("N=%d:%.4f" % (N, nint_dist(q * S_N(z0, N)) / (q * E_N(z0, N))))
    W("      q=%-2d %s" % (q, "  ".join(row)))
W("")
W("[4b] OBST-4 作用域反例检验: z0=ln(3/2) 超越 且 e^z0=3/2 有理,")
W("     其无理性**可经其他经典手段证明**(Lambert 连分数级 / apéry型对")
W("     atanh 的 Padé 逼近) => 超越数自身不阻断'经典路线'")
W("     -> §8.3.3 COROLLARY-OBST-4 的'经典 Hermite-Padé 型结构性不可用'")
W("        表述**过强**, 须收窄作用域(见 §8.3.3 修正声明)")
W("")

W("[5] 初稿 E-3 数值否证: r_N = N!*E_N(z) 的量级 (初稿断言恒 <1)")
for N in [10, 20, 40, 80, 160]:
    W("    N=%-4d N!*E_N = %s" % (N, nstr(factorial(N) * E_N(z, N), 10)))
W("    结论: r_N 随 N 爆炸增长 -> 初稿 '0<r_N<1' 断言已数值否证")
W("")

W("[6] T2 断裂确认: 清分母乘子 N! 对 S_N 的放大 vs 对余项的放大")
W("    关键障碍是**结构性**的(OBST-3): 任何 s!=0 都使 s*S_N(z) 超越,")
W("    而非's 大小不够'——故 '把余项压回 (0,1)' 与 'S_N 变有理' 不能并存")
for N in [5, 10, 20]:
    W("    N=%-3d E_N=%s  若欲 s*E_N<1 需 s>%.3g (先决不成立, s*S_N 恒超越)"
      % (N, nstr(E_N(z, N), 6), float(1 / E_N(z, N))))
W("")

W("[7] OBST-2 数值侧面: S_N(z)-1 的小数部分 (数值无法证非有理, 仅示无短结构)")
for N in [2, 3, 4, 6]:
    W("    N=%-2d S_N(z)-1 = %s" % (N, nstr(S_N(z, N) - 1, 30)))

txt = "\n".join(out) + "\n"
io.open(out_file, "w", encoding="utf-8").write(txt)
print(txt)
print("written:", out_file)
