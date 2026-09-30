# -*- coding: utf-8 -*-
# rev12 MANIFEST 登记器: files 13 -> 24 (新增 11 现行脚本), 授权表第四类, rev_history[12]
import hashlib, json, io, os

base = r"PROJECT_ROOT/\docs\v_os\math_cross_domain\PI_PI_IRRATIONALITY"
path = os.path.join(base, "MANIFEST_PIPI.json")
m = json.load(io.open(path, encoding="utf-8"))

NEW = {
    "脚本/pi_reduce_chain.py": ("script", "归约链独立复核脚本 (π^π 有理归约步骤字面复核); 既有未受管, rev12 依用户决策点5 补登 (保留一手溯源)"),
    "脚本/pipi_domain_boundary.py": ("script", "R09-02 域边界采样探针 (dof 趋近边界 deg 无跳变, EMPIRICAL-PASS); 既有未受管, rev12 依用户决策点5 补登"),
    "脚本/pipi_domain_d4_verify.py": ("script", "R09-03 deg<=4 探针 (6维PSLQ/S5 精确核对/门1 gmpy2) 源头脚本; rev10 --domain 并入 gap1a_test 的核验基; 既有未受管, rev12 补登"),
    "脚本/pipi_rev11_sync_hashes.py": ("script", "rev11 哈希表生成器 (五受管文件 bytes+sha256 -> rev11_hashes.json); 会话脚本迁入脚本/, rev12 登记"),
    "脚本/pipi_rev11_sync_manifest.py": ("script", "rev11 MANIFEST 四同步写盘器 (files/授权表第三类/rev_history[11]/discipline/open_note); 迁入脚本/, rev12 登记"),
    "脚本/pipi_rev11_verify_hashes.py": ("script", "通用哈希核验器 (动态读 MANIFEST rev/files, MATCH/MISMATCH + f_registry 状态分布); rev12 起沿用为核验工具; 迁入脚本/, rev12 登记"),
    "脚本/pipi_rev11_sync_changelog.py": ("script", "rev11 changelog 增量同步发射器 (manifest_changelog rev11 节); 迁入脚本/, rev12 登记"),
    "脚本/pipi_d3_warroom_record.py": ("script", "方向三 §8.1 主控草稿/立案标签表/待办 入库发射器 (作战室未受管); 迁入脚本/, rev12 登记"),
    "脚本/pipi_d3_s83_emit.py": ("script", "方向三 §8.3.0-8.4 发射器 (E-1/E-2/E-3 修正 + OBST-1..4 + OBST-4 精确范围 v2); 现行正确版, 迁入脚本/, rev12 登记"),
    "脚本/pipi_d3_s83_numeric.py": ("script", "方向三数值自检 (下正则化 Gamma E_N=e^z·P(N+1,z), dps=120; 判据[1]-[6] + [4b] OBST-4 v1 反例); 迁入脚本/, rev12 登记"),
    "脚本/pipi_rev12_sync_manifest.py": ("script", "rev12 MANIFEST 登记器 (本文件): files 13->24 (11 现行脚本), 授权表第四类, rev_history[12], counts; 自包含哈希"),
}

for rel, (cat, purpose) in NEW.items():
    full = os.path.join(base, rel)
    with open(full, "rb") as f:
        data = f.read()
    m["files"].append({
        "path": rel,
        "category": cat,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "purpose": purpose,
    })

# --- counts 更新 ---
old_total, old_script = m["counts"]["total"], m["counts"]["script"]
m["counts"]["total"] = m["counts"]["total"] + len(NEW)
m["counts"]["script"] = m["counts"]["script"] + len(NEW)
print("counts: total %d -> %d | script %d -> %d" % (old_total, m["counts"]["total"], old_script, m["counts"]["script"]))

# --- rev ---
m["rev"] = "12"

# --- 授权表第四类 (受管清单扩充) ---
hra = m["hash_recompute_authorization"]
hra["principle"] = hra["principle"].replace("(rev11 起为三类)", "(rev12 起为四类)")
hra["authorized_classes"].append({
    "class": "受管清单扩充（用户指令的可复现脚本登记）",
    "definition": "用户决策点5 明确指令: 将迁入 脚本/ 的现行可复现脚本与既有未受管脚本纳入受管 files 段以获得版本溯源; 选择性登记(排除错误/废弃/可再生成版本, 仅留审计链); 不改变任何真值层级/结论/缺口状态",
    "granted_on": "2026-09-30",
    "recorded_in": "README.md §3 纪律条目 9 (rev12 增列) + archive/manifest_changelog.md rev12",
    "revisions": ["rev12 (11 脚本: 3 既有未受管 + 7 迁入现行 + 1 新增 rev12 登记器; files 13->24, script 3->14; 排除 3 项 *_ERRONEOUS / *_SUPERSEDED / 可再生成输出 _numeric_out.txt)"]
})

# --- invariants_held 修订 (rev12 首次扩 files) ---
hra["invariants_held"] = ("files 段 rev07-rev11 恒为 13 项; rev12 依用户决策点5 明确指令扩为 24 项 (新增 11 现行脚本: 3 既有未受管 + 7 迁入现行 + 1 rev12 登记器; 排除 3 项 *_ERRONEOUS / *_SUPERSEDED / 可再生成输出), 目录约定以 README §2 为锁; 分类计数 script=3->14/ledger=1/doc=8/index=1; f_registry 既有条目状态未因重算而改变")

# --- discipline 第 8 条授权类别清单追加第四类 ---
d = [s for s in m["discipline"]]
for i, s in enumerate(d):
    if "受管文件哈希重算须落在用户授权类别" in s and "受管清单扩充" not in s:
        d[i] = s.replace("『主线索工作——归约深化』", "『主线索工作——归约深化』或『受管清单扩充（用户指令的可复现脚本登记）』")
        break
m["discipline"] = d

# --- rev_history[12] ---
m["rev_history"]["12"] = (
    "**受管清单扩充 (rev12, 用户决策点5)** ⟹ files 13→24: 用户裁定『登记现行脚本, 排除错误版, 走 rev12』。登记集 11 现行可复现脚本"
    "(A) 3 既有未受管补登: pi_reduce_chain.py / pipi_domain_boundary.py (R09-02) / pipi_domain_d4_verify.py (R09-03 源头); "
    "(B) 7 迁入脚本/ 的会话现行工具: rev11 四同步 (sync_hashes/sync_manifest/verify_hashes/sync_changelog) + 方向三工具 (warroom_record/s83_emit/s83_numeric); "
    "(C) 新增 rev12 登记器 pipi_rev12_sync_manifest.py。排除集 3 项不入 files 仅留审计链: pipi_d3_s83_emit_v1_ERRONEOUS.py / pipi_d3_fix_dollar_SUPERSEDED.py / pipi_d3_s83_numeric_out.txt(可再生成输出)。"
    "同步配套: 授权表第四类『受管清单扩充』, README 修订记录第九次 + 授权表第四行 + 13→24 计数 + 授权边界例外(受管文件数量变动仅经用户明确指令, rev12 例), 归档标签补 rev12, changelog rev12 节。"
    "不升格项 (决策点4 已决议): OBST-1..4 不升格入 05_条件性定理 —— 语义错配, OBST 是障碍诊断/负向证据(在进行时), 非 THEOREM-COND 条件结论, 留作战室 §8; 待某条结晶为可证伪 no-go 论证时再以 THEOREM-COND/FALSIFIED 升格。"
    "fn 状态: f_registry 23 条与计数口径不变 (无新 F-n); open_pending_decision 0。**GAP-1/GAP-3 推进量仍为 0** (本轮不涉及缺口的确定性输入)。"
)

# --- open_pending_decision_note 追加 rev12 ---
m["open_pending_decision_note"] = m["open_pending_decision_note"] + (
    " **rev12 更新 (受管清单扩充, 决策点4/5 已决议)**: 决策点4 (OBST 是否升格 05) ——已决议**不升格**: "
    "05_条件性定理 语义被 README 锁死为 THEOREM-COND '在显式前提下的结论', OBST 是障碍诊断/负向证据(进行时), 非条件定理; "
    "留作战室 §8, 待结晶为可证伪 no-go 论证再升格。决策点5 (会话脚本纳入 MANIFEST) ——已决议**选择性纳入** 11 现行可复现脚本、排除错误版, 触发 rev12 (files 13→24, script 3→14)。"
    "受管文件数变更仅经用户明确指令 (rev12 例)。GAP-1/GAP-3 推进量仍为 0"
)

with io.open(path, "w", encoding="utf-8") as f:
    json.dump(m, f, ensure_ascii=False, indent=2)

print("rev ->", m["rev"], "| files len ->", len(m["files"]))
print("counts ->", m["counts"])
print("authorized class names ->", [c["class"][:18] for c in m["hash_recompute_authorization"]["authorized_classes"]])
print("rev_history keys ->", sorted(m["rev_history"].keys(), key=int))