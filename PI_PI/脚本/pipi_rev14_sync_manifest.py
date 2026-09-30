# -*- coding: utf-8 -*-
"""rev14 MANIFEST 同步器（一次性，未受管 helper；rev14 不变更 files 数量）。

变更:
- 脚本/pipi_d3_s83_emit.py: 内嵌 §8.3->EOF 升级 v2 权威版 + 幂等性修正 (决策点6 选项 A)
  bytes 10019 -> 13802 ; sha256 -> 4859959bb76011ceae77abf255537a9865c1021d20692cbd15a2d99044a44f20
- README.md: 修订记录第十一次 / 授权表第三类追加 rev14 / 归档标签 rev13->rev14
  bytes 22048 -> 22916 ; sha256 -> 2054e422c10a1a6b9b7629c8102ab660cbf19211888c70ea14d4a43ea521b02a

同步项: rev int(14) / files 两项哈希 / authorized_classes[2](主线索工作) revisions / 
invariants_held 追加 / rev_history[14] / lastUpdated 保持 2026-09-30。
"""
import io
import json

base = r"PROJECT_ROOT/\docs\v_os\math_cross_domain\PI_PI_IRRATIONALITY"
mf_path = base + r"\MANIFEST_PIPI.json"

mf = json.load(io.open(mf_path, encoding="utf-8"))

assert mf["rev"] == 13, mf["rev"]
mf["rev"] = 14

# --- files 两项哈希 ---
repl = {
    "脚本/pipi_d3_s83_emit.py": {
        "bytes": 13802,
        "sha256": "4859959bb76011ceae77abf255537a9865c1021d20692cbd15a2d99044a44f20",
        "purpose": "方向三 §8.3.0-8.4 发射器 (E-1/E-2/E-3 修正 + OBST-1..4 + OBST-4 精确范围 v2); 现行正确版, 迁入脚本/, rev12 登记; **rev14 (决策点6 选项A): 内嵌 §8.3→EOF 升级 v2 权威版 (补 OBST-4 精确范围声明 v2 + §8.3.4b + §8.3.6 + §8.4 新记账), 幂等性修正 (sec 无首部换行, 写盘 LF), 重跑哈希稳定**",
    },
    "README.md": {
        "bytes": 22916,
        "sha256": "2054e422c10a1a6b9b7629c8102ab660cbf19211888c70ea14d4a43ea521b02a",
        "purpose": "项目索引/真值纪律/目录约定; F 编号表 + 计数口径 rev09; §3 纪律条目9 授权表 (**rev11 增第三类『主线索工作——归约深化』; rev12 增第四类『受管清单扩充』**); **rev12 修订记录第九次 (受管清单扩充 13->24, 11 现行脚本登记, 排除错误版; 授权边界例外: 受管文件数量变动仅经用户明确指令, rev12 例)**; 纪律条目10/11 (F-10a/F-11a); 纪律条目12 (rev09, F-12); rev13: §3 L6 详卡升级为已核实 (author-side 三线佐证), 修订记录第十次 + 授权表第三类 rev13; **rev14: 修订记录第十一次 (发射器 v2 权威化 + 幂等修正, 方向三审计闭环收口) + 授权表第三类追加 rev14 + 归档标签 rev13->rev14**",
    },
}
for f in mf["files"]:
    if f["path"] in repl:
        f.update(repl[f["path"]])

# --- authorized_classes[2] (主线索工作——归约深化) 追加 rev14 ---
cls = mf["hash_recompute_authorization"]["authorized_classes"]
c3 = next((c for c in cls if c["class"].startswith("主线索工作")), None)
assert c3 is not None
rev14_entry = ("rev14 (1 脚本: 脚本/pipi_d3_s83_emit.py 内嵌 §8.3→EOF 升级 v2 权威版 "
               "+ 幂等性修正 (决策点6 选项 A, 方向三审计闭环收口); "
               "files 段仍 24 项无增删; GAP-1/GAP-3 推进量仍为 0)")
c3["revisions"].append(rev14_entry)

# --- invariants_held 追加 rev14 段 ---
ih = mf["hash_recompute_authorization"]["invariants_held"]
ih += "; rev14: files 段仍 24 项 (仅 脚本/pipi_d3_s83_emit.py + README 哈希更新, 无增删); f_registry 状态未变"
mf["hash_recompute_authorization"]["invariants_held"] = ih

# --- rev_history[14] ---
mf["rev_history"]["14"] = (
    "发射器 v2 权威化 + 幂等修正 (rev14, 决策点6 选项 A): 受管发射器 脚本/pipi_d3_s83_emit.py "
    "内嵌 §8.3→EOF 由 v1 旧版升级为 v2 权威版 (补 OBST-4 精确范围声明 v2 + §8.3.4b + §8.3.6 + §8.4 新记账), "
    "并修正幂等性缺陷 (sec 字面量首部多余换行 + 混合换行致漂移: 修正后重跑两次哈希一致 749a2404…, "
    "内嵌段与作战室现行段逐字节一致, LF 统一换行); 用户裁定执行, 授权类别: 主线索工作——归约深化 "
    "(方向三审计闭环收口); 变更文件 2 个 (脚本/pipi_d3_s83_emit.py + README.md), files 段仍 24 项无增删, "
    "f_registry 23 条口径不变; 作战室决策点 6 已决议、§8.2 待办 8 闭环、§7.1 后续轮复扫协议不变, 基线锚定 rev14; "
    "GAP-1/GAP-3 推进量仍为 0"
)

with io.open(mf_path, "w", encoding="utf-8", newline="\n") as f:
    json.dump(mf, f, ensure_ascii=False, indent=2)
print("MANIFEST rev ->", mf["rev"], "files", len(mf["files"]))