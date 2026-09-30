# -*- coding: utf-8 -*-
import json, io

path = r"PROJECT_ROOT/\docs\v_os\math_cross_domain\PI_PI_IRRATIONALITY\MANIFEST_PIPI.json"
with io.open(path, "r", encoding="utf-8") as f:
    m = json.load(f)

# --- files 段 (rev11 变更的 5 个受管文件) ---
files = m["files"]
updates = {
 "01_文献/文献基线.md": (52504, "089a321416cfdeea29e1eb7a34b88f2862dd4271b359616a74a9eafdaf44fb45",
   "ext_old"),
 "03_归约链/GAP-1a_分割的严格化_裁定.md": (8568, "99d2e3e19f66da345d8b2ac4d690f38c91aacf1613682cdf8ff9b1708db39d9e", "ext_old"),
 "04_缺口/缺口登记.md": (25557, "c479cd95c6cd3fee18ccd88b626fb533779b61abdab54f40d2de79c3255b61cc", "ext_old"),
 "05_条件性定理/Schanuel蕴含π^π超越.md": (14728, "d1c0e48ffbfdde81dc6060da867a4ef0627a2cb63c076060ad160ba08f06edaf", "ext_old"),
 "README.md": (19501, "60dd82df439b5243407fa6bcf55f2e4eb9bed9f23b335a60138b3ee05be5bf26", "ext_old"),
}
purposes = {
 "01_文献/文献基线.md": ("文献基线 L1-L21; §1.6 L13/L14 超越自指幂反例; §1.7 Caveny (机制D, rev08 出版方章级 DOI 确证 + F-11 正名 + Caveny/Tubbs 两章拆分); §1.7a L18 Mahler 分类(rev09 依 F-12 改采四源一致的 w_n 标准定义, elibm 二手综述降级为不可靠源)/L19 μ(π) 上界(rev09: 撤销其『π 非 T-数』推论)/L20 Caveny-Tubbs 开放问题/L21 Mahler 1953 代数数的对数非 U-数 (rev08 新增, 不受 F-12 影响); §1.8 B-W 书目 (rev08 五源闭合); L2/L6 依据升级; §1.9 rev11 新增 L-AP4 (ProofWiki 佐证 TC-4′ 步骤1) + L-AP1 (μ(π)≤7.101862832357, PREPRINT 仅登记, 不触发分支状态变更); §5 转换层失真纪律 + §5a R7 (rev07) + §5b R8 (rev08) + §5c R9 (rev09, F-12 完整证据链)"),
 "03_归约链/GAP-1a_分割的严格化_裁定.md": ("F-2 裁定 (FALSIFIED); F-2a 保留; F-5 措辞约束; §6 rev11 加注: 替代物 TC-4 已由 TC-4′ (S)₂∧(S)₄ 弱化, 裁定三点结论不变"),
 "04_缺口/缺口登记.md": ("GAP-1/GAP-3 台账; 已撤回/已作废缺口; GAP-1 四机制夹击 + 3 条陷阱登记; rev09 F-12 双表登记 + 机制D 修正三分支表 + 计数口径 rev09; **rev11 (第六次): GAP-1 卡点由 (S)₂∧(S)₃∧(S)₄ 弱化为 (S)₂∧(S)₄ (TC-4′), TC-4/TC-4c → TC-4′/TC-4′c, GAP-3 与链条关系改指 (S)₂@(lnπ,2πi)**"),
 "05_条件性定理/Schanuel蕴含π^π超越.md": ("TC-1..TC-5 条件链; §5 已撤回; **rev11: 现行链重构为 3 步 2 实例 ((S)₂@(lnπ,2πi) + (S)₄@(1,2πi,lnπ,πlnπ)), TC-4→TC-4′, (S)₃ 冗余已证, 旧链保留 §2.4; §4.3 实例数不对称 (弱化专属于 u=π, TC-3/π^e 仍需 (S)₃); rev11 增补 3 处 (步骤1 隐依赖/逻辑区分, §4.2 配方约束, TC-5 数值强度边界)**"),
 "README.md": ("项目索引/真值纪律/目录约定; F 编号表 + 计数口径 rev09; §3 纪律条目9 授权表 (**rev11 增第三类『主线索工作——归约深化』**); **rev11 修订记录第八次 (GAP-1 主线启动, TC-4′ 弱化, L-AP1/L-AP4 登记, GAP-1/3 推进量仍为 0)**; 纪律条目10/11 (F-10a/F-11a); 纪律条目12 (rev09, F-12)"),
}
for ent in files:
    p = ent["path"]
    if p in updates:
        ent["bytes"], ent["sha256"], _ = updates[p]
        if p in purposes:
            ent["purpose"] = purposes[p]

# --- rev 字段 ---
m["rev"] = 11

# --- hash_recompute_authorization ---
hra = m["hash_recompute_authorization"]
hra["principle"] = "受管文件哈希原则上登记后不得重算; 仅开放下列授权类别 (rev11 起为三类)"
hra["authorized_classes"].append({
  "class": "主线索工作——归约深化（GAP-1 主线）",
  "definition": "用户主动指令『开始 GAP-1 主线』并在其下进行的受管文档深化: 归约链前提弱化 (TC-4′)、缺口定位更新、主线索文献登记等; 每次修订须写明 GAP-1/GAP-3 推进量 (仍为 0)",
  "granted_on": "2026-09-30",
  "recorded_in": "README.md §3 纪律条目 9 (rev11 增列) + archive/manifest_changelog.md rev11 + archive/GAP-1_主线作战室.md",
  "revisions": ["rev11 (5 文件: 05_条件性定理 TC-4′ 弱化重写 + 04_缺口 卡点/替代定位 (S)₂∧(S)₄ + 01_文献 L-AP4/L-AP1 + 03_归约链 §6 加注 + README 修订记录/授权表/§4 编号/归档标签; GAP-1/GAP-3 推进量仍为 0)"]
})
hra["invariants_held"] = ("files 段恒为 13 项 (rev07/rev08/rev09/rev10/rev11 均未新增/删除受管文件; R7 检索记录写入既有 文献基线.md §5a、rev08 写入 §5b、rev09 写入 §5c、rev10 并入既有脚本 pipi_gap1a_test.py 而非新建脚本文件、rev11 写入既有 文献基线.md §1.9 L-AP1/L-AP4 与既有 03/04/05 文档, 未新建受管文件; 域边界封存与主线作战室写入既有 archive 系 append-only, 不进入 files 段); 分类计数 script=3/ledger=1/doc=8/index=1 未变; f_registry 既有条目状态未因重算而改变")

# --- rev_history ---
m["rev_history"]["11"] = ("**GAP-1 主线启动 (rev11, 归约深化) ⟹ TC-4′**: 用户指令『开始 GAP-1 主线』(长期课题) + 裁定『并入受管, 触发 rev11』。主线索第一成果: GAP-1 归约卡点由 `(S)₂∧(S)₃∧(S)₄` **弱化**为 **`(S)₂∧(S)₄`** —— 旧链 (S)₃ 应用 (z=(1,2πi,lnπ)) 与旧步骤0 ((S)₂@(1,2πi)) 均被证明冗余: 新步骤1 `(S)₂@(lnπ,2πi)` 直接给出 {π,lnπ} 代数无关 (副产物 lnπ 无理, 外部佐证 ProofWiki L-AP4, 同实例 iπ); 现行链 3 步 2 实例 (n=2, n=4), 见 05_条件性定理 §2/§3/§5.0。TC-4 (前提含 (S)₃) 降格为历史对照, 现行 TC-4′/TC-4′c。正确性边界: ① 弱化专属于 u=π 链, TC-3 (π^e) 仍需 (S)₃ (§4.3 实例数不对称, 因 {e,lnπ} 不能由单 (S)₂ 实例给出); ② π,lnπ 代数无关/lnπ 无理的**无条件**状态 (GAP-3) 不变; ③ GAP-1 推进量仍为 0。文献: 新增 L-AP4 (ProofWiki 佐证) + L-AP1 (arXiv:2609.11276, μ(π)≤7.101862832357, **PREPRINT 仅登记**, 不触发任何分支状态变更; 02 工具有效性矩阵 μ 记录是否同步留待主线作战室决策点2)。受管文件: 5 文件哈希更新 (05 条件性定理 / 04 缺口 / 01 文献 / 03 归约链 / README), archive 双向追加 (manifest_changelog rev11; 新建未受管 archive/GAP-1_主线作战室.md 工作台)。files 段仍 13 项, f_registry 23 条与计数口径不变 (无新 F-n)。**GAP-1/GAP-3 推进量仍为 0** (本轮为归约链前提的最小化与外部佐证, 前提仍为未证猜想实例)")

# --- tool_failure_mechanisms consequence ---
m["tool_failure_mechanisms"]["consequence"] = ("不存在仅凭底数超越性的一般判据; GAP-1 必须依赖 π 的特有信息, 唯一未被否掉的方向是归约链 (卡点已显式写为 (S)₂∧(S)₄, rev11 TC-4′)")

# --- discipline 数组: 条目8 授权类别列举更新 ---
d = m["discipline"]
for i, s in enumerate(d):
    if "受管文件哈希重算须落在用户授权类别" in s:
        d[i] = s.replace("『用户指令的常驻守卫并进』", "『用户指令的常驻守卫并进』或『主线索工作——归约深化』")
        break

# --- open_pending_decision_note 追加 rev11 说明 ---
m["open_pending_decision_note"] = m["open_pending_decision_note"] + " **rev11 更新 (GAP-1 主线, 无新裁定项)**: 未能产生 F-n 级待裁定项; 主线作战室登记**决策点** ① TC-4′ 并入受管 (已决议: 触发 rev11) ② L-AP1 (μ(π) PREPRINT) 是否同步 02_工具状态 矩阵 (待用户答复, 当前保持仅 01_文献 登记) ③ 弱化是否上溯 UI/V5 侧 (待答复)。GAP-1/GAP-3 推进量仍为 0 (前提弱化为 (S)₂∧(S)₄, TC-4′)"

with io.open(path, "w", encoding="utf-8") as f:
    json.dump(m, f, ensure_ascii=False, indent=2)

print("rev ->", m["rev"], "| files len ->", len(m["files"]))
print("authorized_classes ->", [c["class"] for c in m["authorized_classes"]])
print("rev_history keys ->", sorted(m["rev_history"].keys(), key=int))