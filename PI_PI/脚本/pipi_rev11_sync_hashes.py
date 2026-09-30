import hashlib, json, os, sys, io

base = r"PROJECT_ROOT/\docs\v_os\math_cross_domain\PI_PI_IRRATIONALITY"
targets = [
    "05_条件性定理/Schanuel蕴含π^π超越.md",
    "04_缺口/缺口登记.md",
    "01_文献/文献基线.md",
    "03_归约链/GAP-1a_分割的严格化_裁定.md",
    "README.md",
]
out = {}
for rel in targets:
    p = os.path.join(base, rel)
    with open(p, "rb") as f:
        data = f.read()
    out[rel] = {"bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}

with io.open(os.path.join(os.path.dirname(__file__), "rev11_hashes.json"), "w", encoding="utf-8") as f:
    json.dump(out, f, ensure_ascii=False, indent=2)
print(json.dumps(out, ensure_ascii=False, indent=2))