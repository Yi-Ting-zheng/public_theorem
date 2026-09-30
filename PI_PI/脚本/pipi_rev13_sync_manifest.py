# -*- coding: utf-8 -*-
"""
rev13 MANIFEST 同步器（一次性，未受管 helper；rev13 不变更 files 数量）
变更: 01_文献/文献基线.md (L6 详卡 EWJ 卷期页 [待核实]->已核实) + README.md (修订记录/授权表/归档标签)
授权类别: 主线索工作——归约深化（主线索文献核验登记）
"""
import hashlib, json, io, os

base = r"PROJECT_ROOT/\docs\v_os\math_cross_domain\PI_PI_IRRATIONALITY"
man_path = os.path.join(base, "MANIFEST_PIPI.json")
man = json.load(io.open(man_path, encoding="utf-8"))

def sha_bytes(rel):
    p = os.path.join(base, rel)
    with open(p, "rb") as f:
        data = f.read()
    return len(data), hashlib.sha256(data).hexdigest()

targets = {
    "01_文献/文献基线.md": "; **rev13: §3 L6 详卡 EWJ 卷期页 [待核实]->已核实 (Sondow 作者主页书目 + arXiv:1010.6216 + mat.unb.br PDF 三线佐证, 2026-09-30 方向二复扫)**",
    "README.md": "; rev13: §3 L6 详卡升级为已核实 (author-side 三线佐证), 修订记录第十次 + 授权表第三类 rev13",
}

for rel, pur in targets.items():
    b, h = sha_bytes(rel)
    for ent in man["files"]:
        if ent["path"] == rel:
            ent["bytes"] = b
            ent["sha256"] = h
            ent["purpose"] = ent["purpose"] + pur
            print("updated", rel, "bytes=%d" % b, "sha=%s" % h[:16])

assert len(man["files"]) == 24, "files count changed!"

man["rev"] = 13
man["lastUpdated"] = "2026-09-30"

# 授权表第三类（索引 2: 主线索工作——归约深化）追加 rev13
cls = man["hash_recompute_authorization"]["authorized_classes"]
rev13_entry = ("rev13 (2 文件: 01_文献/文献基线.md §3 L6 详卡 EWJ 卷期页 [待核实]->已核实 "
               "(author-side 三线佐证) + README 修订记录/授权表/归档标签; files 段仍 24 项无增删; "
               "GAP-1/GAP-3 推进量仍为 0)")
assert cls[2]["class"].startswith("主线索工作"), cls[2]["class"]
cls[2]["revisions"].append(rev13_entry)

# invariants_held 追加 rev13 段
iv = man["hash_recompute_authorization"]["invariants_held"]
man["hash_recompute_authorization"]["invariants_held"] = iv + (
    "; rev13: files 段仍 24 项 (仅 01_文献/README 哈希更新, 无增删); f_registry 状态未变")

man["rev_history"]["13"] = (
    "L6 详卡 EWJ 卷期页 [待核实]->已核实 (rev13): 方向二复扫产出 author-side 三线佐证 "
    "(Sondow 作者主页书目 + arXiv:1010.6216 + mat.unb.br PDF 一致) ⟹ 01_文献/文献基线.md §3 L6 详卡 "
    "由『未独立核实卷期页』升级为『已核实』; 用户授权执行; 授权类别: 主线索工作——归约深化"
    " (主线索文献核验登记); 变更文件 2 个 (01_文献/文献基线.md + README.md), files 段仍 24 项无增删, "
    "f_registry 23 条口径不变; GAP-1/GAP-3 推进量仍为 0")

with io.open(man_path, "w", encoding="utf-8") as f:
    json.dump(man, f, ensure_ascii=False, indent=2)
print("MANIFEST rev=%d files=%d written" % (man["rev"], len(man["files"])))