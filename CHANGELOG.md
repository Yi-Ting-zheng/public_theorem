<!-- scan-record: F2,W2 -->

# CHANGELOG — public_theorem（统一大定理公开推导档案）

> 本文件是 `MANIFEST_PUBLIC.json` 所要求的登记处。哈希锁的处置条款：
> 「若为有意修改：重生成清单并在本文件记一笔」。

## [Unreleased] — 待发 v1.0.1

### 修复：`.zenodo.json` 混用 schema 代际 ⟹ Zenodo ingest 被拒（发布阻断级，**实证**）

| 项 | 值 |
|---|---|
| 记录 | https://github.com/Yi-Ting-zheng/public_theorem/releases/tag/1.0.0 |
| 症状 | Zenodo GitHub 集成 `Errors` 面板原文：`{'errors': "{'metadata': {'resource_type': ['Missing data for required field.']}}"}` |
| 后果 | 无 Zenodo 版本记录、无版本 DOI（概念 DOI 恒定，但 0 个版本落地） |
| 根因 | `.zenodo.json` 写成 `"upload_type": {"type": "publication", "subtype": "workingpaper"}`。Zenodo legacy 反序列化器的契约是**两个平级标量**：`upload_type`（String → `resource_type.type`）+ `publication_type`（String → `resource_type.subtype`）。`subtype` 是**新版 `resource_type` 内部**的键名，置于 `upload_type` 内不被识别 ⟹ 反序列化产不出 `resource_type` ⟹ 校验拒绝。`upload_type` 为对象（而非字符串）本身即足以致败 |
| 修正 | 改为扁平 `"upload_type": "publication"` + 平级 `"publication_type": "workingpaper"` |
| 依据 | ① Zenodo 官方文档示例为扁平 `"upload_type": "software"`；② legacy 受控词表列 `publication_type` ∈ {softwaredocumentation, taxonomictreatment, technicalnote, thesis, workingpaper, other}；③ Zenodo legacy schema 源码中 `upload_type = fields.String(attribute='resource_type.type')`、`publication_type` 映射 `resource_type.subtype` |
| 为何闸门未拦 | `release_preflight.py` 闸门 3 原只验「JSON 可解析 + title/description/creators/license 齐备」。**JSON 合法 ≠ Zenodo 接受**——缺陷恰落在两者之间 |
| 防线 | 闸门 3 增 `validate_zenodo_meta()`：按受控词表逐条验 `upload_type`（须字符串）/ `publication_type`（平级、词表内）/ `access_right`，并显式识别 `upload_type.subtype` 代际混用。新增 `--selftest`：**10 例正/反例，含本缺陷实际 payload**，漏拦 0 / 误拦 0 |
| 同源缺陷（误判记录） | 曾把「Zenodo 侧无记录」误判为服务端性能退化（并发两仓库卡住更强化了误判）。**真实原因是本地 schema 非法，服务端为即时确定性拒绝**。教训：错误面板原文优先于服务端行为推测 |
| 其他同步修正 | ① `description` 原含**字面换行**写入 JSON 字符串 ⟹ 文件本身非法 JSON（`json.JSONDecodeError`），已改为 `\n` 转义；② 原 HTML `<p>` 外壳未剥导致 Markdown 被 HTML 包裹，已剥除；③ 元数据声明「45 文件哈希锁」与 `MANIFEST_PUBLIC.json` 实际的 **47** 不符，已更正；④ 补文件末行换行 |
| **未修复项（阻断 v1.0.1）** | 元数据 description 仍声明 C(m)=√2·e^(−iπm/8) 的证据为「**残差 ≤1.05e−4**」。高精度复算显示**原始** B 分支阶梯为 5.837e−4 → 2.550e−5 → 1.859e−5（首项即超过该界），且原始阶梯非单调——故该数是**振荡幅度**而非收敛残差；反对称化后为 A ≤4.42e−5 / B ≤1.836e−5。该表述须待 C(m) 复认证（m=1..8 扫描 + N=51201/dps=120 阶梯）完成后定稿。**在定稿前不发版**，避免把已失效的认证写入不可撤回的 DOI 元数据 |

## [v1.0.0] — 2026-09-30 首次公开归档

### 克隆可验证性修正（发布阻断级，已含于本版）

| 项 | 内容 |
|---|---|
| 缺陷 | 2 个 CRLF 文件（PI_PI/脚本/pipi_d3_s83_numeric_out.txt 69 处、pipi_f1_check.py 14 处）使哈希锁锁的是 CRLF 字节，而 git 提交时按 	ext 规范化为 LF => **新克隆必然 F5 哈希变更 FAIL** |
| 处置 | 两文件归一化为 LF（4022 / 3127 字节）；新增 .gitattributes（* text=auto eol=lf）固定检出行尾；MANIFEST_PUBLIC.json 重生（46 文件） |
| 证据 | 修复前新克隆实测 FAIL 2（F5 哈希变更 x2）；修复后新克隆实测 FAIL 0 |
| 性质 | 哈希锁是本仓库可验证性的唯一凭据；只在作者机器上成立的锁等于没有锁 |

---
| 闸门 | 新增 `release_preflight.py`（移植自姊妹仓库 emf_demo）：校验 tag 树而非工作区 —— ① tag==HEAD ② 归档树含 `.gitattributes`(eol=lf) ③ `.zenodo.json` 可解析 ④ **解包 tag 树在副本上实跑 `verify_public.py`** |
| 复验 | `release_preflight.py --tag 1.0.0` 判 **0 项阻断**（归档副本内 `verify_public.py` = FAIL 0） |

### 收录
| 资产 | 源 | 脱敏后体量 |
|---|---|---|
| 勘误附录 F_v1.0_W3-W4（§12.20–§12.25 推导主档案） | `M4-MILESTONE-04` | 152 KB |
| 统一大定理存档 v2.2（定稿存档） | `V5_UNIFIED_THEOREM` | 22 KB |
| π^π 专项（立项/文献/工具边界/归约链/缺口/条件性定理 + 18 脚本） | `PI_PI_IRRATIONALITY` | 34 文件 / 394 KB |

### 脱敏（21 处替换，规则按"具体→通用"优先级）
| 规则 | 命中 | 涉及文件 |
|---|---|---|
| 本地用户目录 | 1 | 1 |
| 工程根目录（双反斜杠） | 2 | 2 |
| 工程根目录（单反斜杠） | 17 | 16 |
| 内部品牌代号 | 1 | 1 |

主动排除 1 项：内部 `MANIFEST_PIPI.json`（哈希锁针对脱敏前内容，公开后必然全失效；理由已登记，非静默丢弃）。

### 新增工具
- `verify_public.py`：发布校验器，5 条 FAIL 断言 + 2 条 WARN 规则 + **19 例自测**
  （纪律依据 GAP-03：自审查不出漏检，故每条规则必须有正例且反例不触发）
- 声明式自扫描排除：校验器不扫描自身与脱敏报告（规则表按定义含被禁词字面量），
  排除清单在校验输出中打印，可被审计

### 本轮修掉的自身缺陷（3 类同族假阳性）
| 告警 | 实为 | 结构性修复 |
|---|---|---|
| 11 位数字疑似手机号 ×36 | π 小数展开、SHA256 十六进制 | 词边界 + 十六进制/小数上下文 |
| 「预算/基金/经费」×56 | `误差预算`、`剂量预算` | 术语上下文排除 |
| 盘符路径 `f:\` | Python 转义换行 `as f:\n` | 要求后随路径段 |
| 尖括号「占位符」×19 | 规则表自指、散文比较符、代码哨兵 | F4 改结构判别 + 仅作用 Markdown/JSON |

> 与 U+FFFD 同源：**缺陷标记符与被记录证据同形 → 扫描在该文件恒假阳性、信号归零**。

### 未解决 / 开放
- 统一定理主结果仍为 `THEOREM-COND`（条件于 `GAP-OPEN` 引理 6.0，未证）
- `Re a` 弧上全局单峰性无解析证明（`GAP-OPEN`）
- `C(m)=√2e^{−iπm/8}` 解析推导未完成（`EMPIRICAL` 强证据）
- π^π 不承诺证明；条件性定理（Schanuel 蕴含）依赖未决前提
- Zenodo DOI 待铸（本仓库首次 release 联动后生成，concept DOI 恒定）

---

`统一大定理 | public_theorem | v1.0.0 | THEOREM-COND | GAP-OPEN 引理 6.0 | E5 纪律 | 引用须带真值层级`
