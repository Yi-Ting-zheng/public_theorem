# -*- coding: utf-8 -*-
import hashlib, json, io, os, sys

base = r"PROJECT_ROOT/\docs\v_os\math_cross_domain\PI_PI_IRRATIONALITY"
man = json.load(io.open(os.path.join(base, "MANIFEST_PIPI.json"), encoding="utf-8"))
rev = man["rev"]
n = len(man["files"])
ok = 0
bad = []
for ent in man["files"]:
    p = os.path.join(base, ent["path"])
    with open(p, "rb") as f:
        data = f.read()
    h = hashlib.sha256(data).hexdigest()
    b = len(data)
    if h == ent["sha256"] and b == ent["bytes"]:
        ok += 1
    else:
        bad.append((ent["path"], ent["bytes"], b, ent["sha256"], h))
print("rev=%d files=%d MATCH=%d MISMATCH=%d" % (rev, n, ok, len(bad)))
for tup in bad:
    print("MISMATCH", tup[0], "bytes_exp/got", tup[1], tup[2])
    print("  sha_exp ", tup[3])
    print("  sha_got ", tup[4])

# 额外: F 计数一致性抽查
fs = man["f_registry"]
stats = man["f_registry_stats"]
cnt = {}
for e in fs:
    cnt[e["status"]] = cnt.get(e["status"], 0) + 1
print("f_registry len=%d  status分布=%s  recorded=%s" % (len(fs), cnt, {k: stats[k] for k in ("FALSIFIED","RESOLVED","RETRACTED","counted","total")}))