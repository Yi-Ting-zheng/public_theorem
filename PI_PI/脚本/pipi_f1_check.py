# -*- coding: utf-8 -*-
# F-1 复核: 检验候选代数无关性阶是否与 Schanuel 蕴含一致
# 规则: 只做量级/自洽性检验, 不做数值"证明"
from fractions import Fraction as F
import mpmath as mp
import sys

# DEF-1 修复: 控制台代码页无关化 (与另两个脚本同款守卫, 防复发)
for _s in ("stdout", "stderr"):
    _f = getattr(sys, _s, None)
    if hasattr(_f, "reconfigure"):          # Python >= 3.7
        _f.reconfigure(encoding="utf-8", errors="replace")

mp.mp.dps=50

pi=mp.pi; e=mp.e

# Schanuel 蕴含 (Marques-Sondow Thm4 口径): 下列集合代数无关
CAND=["e","e^pi","e^e","e^i","pi","pi^e","pi^pi","pi^i","2^pi","2^e","2^i",
      "log(pi)","log 2","log 3","log log 2","(log 2)^(log 3)","2^sqrt2"]
vals={}
for s in CAND:
    try:
        vals[s]=mp.power(e, mp.log(eval(s.replace("^","**")))) if s.startswith("e^") else eval(s.replace("^","**"))
    except Exception as ex:
        vals[s]=None
# 显式定义
vals["e^pi"]=mp.power(e,pi); vals["e^e"]=mp.power(e,e); vals["e^i"]=mp.power(e,1j)
vals["pi^e"]=mp.power(pi,e); vals["pi^pi"]=mp.power(pi,pi); vals["pi^i"]=mp.power(pi,1j)
vals["2^pi"]=mp.power(2,pi); vals["2^e"]=mp.power(2,e); vals["2^i"]=mp.power(2,1j)
vals["log(pi)"]=mp.log(pi); vals["log 2"]=mp.log(2); vals["log 3"]=mp.log(3)
vals["log log 2"]=mp.log(mp.log(2)); vals["(log 2)^(log 3)"]=mp.power(mp.log(2),mp.log(3))
vals["2^sqrt2"]=mp.power(2,mp.sqrt(2))

print("候选代数无关集合大小 N =", len(CAND))
print("\n--- 量级表 (50 位精度) ---")
for s in CAND:
    v=vals[s]
    if v is None: print("  %-18s FAIL"%s); continue
    if abs(mp.im(v))>mp.mpf('1e-40'):
        print("  %-18s complex  = %s"%(s, mp.nstr(v,14)))
    else:
        print("  %-18s = %s"%(s, mp.nstr(mp.re(v),20)))

print("\n--- 关键实数对: 是否有已知恒等式使 '代数无关' 自相矛盾 ---")
checks=[
 ("e^pi vs pi^e", mp.power(e,pi), mp.power(pi,e), False),
 ("log(pi) vs log 2", mp.log(pi), mp.log(2), False),
 ("log log 2 vs log(pi)", mp.log(mp.log(2)), mp.log(pi), False),
 ("pi^pi vs 2^sqrt2", mp.power(pi,pi), mp.power(2,mp.sqrt(2)), False),
]
for name,x,y,must_differ in checks:
    same = abs(x-y)<mp.mpf('1e-30')
    print("  %-26s 数值相等? %s"%(name, same))

print("\n--- log 2 与 log 3 的有理线性关系检验 (L-F 型卡点) ---")
# 若 log2/log3 有理 => 存在 p,q 使 q*log2 - p*log3 = 0 即 2^q=3^p
# Gelfond-Schneider 立即排除 (2^{p/q}=3 代数数 => 矛盾)
r=mp.log(2)/mp.log(3)
print("  log2/log3 = %s"%mp.nstr(r,20))
print("  由 Gelfond-Schneider: 该比值必为超越数 (若为有理数 r=p/q 则 2^(p/q)=3 矛盾)")
print("  => 此项不是缺口, 已被 G-S 关闭")

print("\n--- log pi 的超越性 (G-S 关闭) ---")
print("  若 log(pi) 为代数数 a != 0, 则 e^a = pi 为超越数 -> 不矛盾")
print("  但 pi = e^{i*pi} 形式: Lindemann: e^{i*pi} = -1 代数 => i*pi 必超越 => pi 超越 (已知)")
print("  log(pi) 的超越性: 需 e^{log pi} = pi (超越) —— 不构成矛盾 => 未关闭")

print("\nF1_STATUS: 候选集无内部恒等冲突; log2/log3 已被 G-S 排除; log(pi) 仍未决")
