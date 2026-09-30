# 检索日志 GAP-3 第 2 轮

> 轮次：2026-09-28（第 2 轮）
> 目标：复核 `GAP-3`（`ln π` 的无理性）文献状态
> 触发：`04_缺口/缺口登记.md` 原将 `GAP-3` 记为「检索未命中」，
> 按 A7 纪律需正向复核后方可升格

---

## 0. 检索前状态与本次结论对照

| 项 | 检索前 | 检索后 |
|----|--------|--------|
| `GAP-3` 层级 | `GAP-OPEN`（**待文献复核**） | `GAP-OPEN`（**四源确认**） |
| 依据性质 | **否定性**（我没找到） | **肯定性**（文献正面确认其开放） |
| 难度定标 | 无 | 蕴含式 `e,π` 代数无关 ⟹ `ln π` 无理 = `THEOREM`；难度定序 = `HYPOTHESIS`（**未定序**） |

**方法学要点**：本次把 `GAP-3` 从「检索未命中」升格为「确认开放」，
是**性质变更**——前者是本项目的无知，后者是学科界共识。
两者不可混同，故留档。

---

## 1. 来源清单

### 1.1 arXiv:1310.7289（HTTP 200，直接抓取成功）

- 作者：F. M. S. Lima
- 标题：*Some transcendence results from a harmless irrationality theorem*
- 期刊：*Expositiones Mathematicae*

**摘要关键句**（直接引用）：

> "not even an irrationality proof is known for some numbers like
> `e^e`, `π^e`, `π^π`, **`ln π`**, `π+e` and `πe`"

**Theorem 9**（无条件）：

> 对任意正整数 `n`，`ln π` 与 `√n·π` 在 ℚ 上线性无关。
> 即 `ln π` 不是 `√n·π` 的有理倍数。特别地，`ln π` 不是 `π` 的有理倍数。

**定理 3**（MathOverflow 提及，*J. Anal. Number Theory* **5** (2017) 91）：

> `{π+e, πe, ln π}` 中**至少两个**为超越数。

**溯源说明**：该文「finally use a recent algebraic independence result by
**Nesterenko**」。

### 1.2 MathOverflow 253070（HTTP 200）

"Is it possible to know if `log(π)` is irrational or not since the log func…"

**主答案（2016-10-25）逐句引用**：

> "I don't think this is known. If `log(π)=p/q`, then `e^p=π^q`, which implies
> that `π` and `e` are **algebraically dependent**. It is widely believed, but
> **not proved**, that `π` and `e` are algebraically independent."

> "The irrationality of `log π` is an **open problem** … It is expected to be
> **transcendental** (page 34 of slides by Michel Waldschmidt), and in fact
> this follows from **Schanuel's conjecture**."

**评论（2021-07-19, Gerry Myerson）**：

> "the irrationality of `ln(pi)` **remains open**."

**时间线（2021-07-18, Lima 本人）**：

> "according to my Theorem 3, at least 2 of the 3 numbers
> `{pi+e, pi*e, ln(pi)}` are **TRANSCENDENTAL**."

### 1.3 MathStackExchange 735957

"Is `log(2π)` rational?" — 同源问题，结论一致：
若 `log(2π)` 有理则 `e, π` 代数相关 ⟹ 需先解决 `e,π` 代数无关。
作**第三类佐证**（同一逻辑链条的独立提问）。

### 1.4 Six / Four Exponentials（`F-4` 的证伪源）

| 项 | 标识 | HTTP | 关键信息 |
|----|------|------|---------|
| Waldschmidt, *NCTS-10* (2003) | `webusers.imj-prg.fr/~michel.waldschmidt/articles/pdf/NCTS-10-2003.pdf` | 200 | Six Exponentials **定理**（已证）；Four Exponentials **猜想**（未证）；Theorem 3 原文 |
| Waldschmidt, *Four Exponentials & Schanuel* | `.../pdf/FourExponentialsSchanuel.pdf` | 200 | Conjecture 1（对数代数无关）；Baker 给线性无关、Conjecture 1 给代数无关的**量级差** |
| MathWorld | `mathworld.wolfram.com/SixExponentialsTheorem.html` | 200 | Six Exponentials **定理**已证；无代数性要求 |
| Debrecen 讲义 | `publi.math.unideb.hu/load_doc.php?p=1156&t=pap` | 200 | Lang (1965/66)、Ramachandra 原始引文 |

**Six Exponentials 定理原文（Waldschmidt 记为 Theorem 3）**：

> Let `x₁,x₂` be two complex numbers which are linearly independent over ℚ, and
> let `y₁,y₂,y₃` be three complex numbers which are linearly independent over ℚ.
> Then one at least of the six numbers `e^{x₁y₁}, e^{x₁y₂}, e^{x₁y₃},
> e^{x₂y₁}, e^{x₂y₂}, e^{x₂y₃}` is transcendental.

⟹ **已证**，且**无任何代数性要求** ⟹ 证伪 `F-4`。

---

## 2. 本次落地的三处修正

| 编号 | 内容 | 状态 | 落点 |
|------|------|------|------|
| `F-4` | 「所有经典超越定理都要求底数为代数数」 | `FALSIFIED` | `02_工具状态/工具适用边界矩阵.md` §1 |
| `F-5` | `TC-4c`「`(S)₂∧(S)₃∧(S)₄` 皆假」 | `FALSIFIED` | `04_缺口/缺口登记.md` `TC-4c` 逻辑边界 |
| `GAP-3` | 「检索未命中」 | 升格为**四源确认开放** | `04_缺口/缺口登记.md` §GAP-3 |

---

## 3. 关键陷阱：`L8` 不能闭合 `GAP-3`（须防复发）

Theorem 9（`ln π` 与 `√n·π` ℚ-线性无关）极易被误当作 `ln π` 无理的证明。
**已证其无效**：

设 `ln π = a ∈ ℚ`。检验 L8 的线性无关条件 `c·a + d·√n·π = 0`：

| 情形 | 后果 |
|------|------|
| `c=1, d=0` | `a ≠ 0`，非零关系 ✓ |
| `c=0, d=1` | `√n π ≠ 0`，非零关系 ✓ |
| `c,d ≠ 0` | `π = -ca/(d√n) ∈ ℚ`，与 `π` 无理**矛盾** |

⟹ **`ln π` 若有理，L8 的结论依然成立。** L8 对有理性零约束。

一般原理（本轮新增，可复用）：

> **`k` 个数的线性无关性不蕴含其中任一数的有理性/无理性。**
> `ln π` 与 `√n·π` 的线性无关 ⟸ `π` 的无理性 **+ 假设 `ln π` 有理** 也能得到。
> 故凡以「线性无关」为据的结论，**不得**升级为「代数无关」或「无理性」。

**对 `TC-1` 的影响**：`TC-1` 步骤 3 需「`π` 与 `ln π` **代数无关**」，
严格强于 L8 ⟹ **L8 不进入 `TC-1` 任何一步**，仅作背景登记。

---

## 4. 本次未解决 / 转出

| 项 | 状态 | 去向 |
|----|------|------|
| `GAP-3` 无条件证明 | **不承诺** | 与 `e,π` 代数无关**相关**（后者蕴含前者）；**难度未定序**，见基线 §1.4.1 |
| Waldschmidt 幻灯片 p.34 原文 | 仅经 MO 转引，**未取得原文** | `02_工具状态/` §5 待补 |
| Nesterenko 1996 原始论文 | 未取得 | `02_工具状态/` §5 待补；用途已限死（见基线 §1.4.2） |
| Brownawell–Waldschmidt (arXiv:1010.6216) | 未回溯原文 | `02_工具状态/` §5 待补 |
| 「∃ transcendend u,v 使 `u^v ∈ ℚ`」构造 | 仍未验证 | `02_工具状态/` §5 待补 |

---

## 5. 抓取故障记录

- Exa 搜索：`web_search_exa request timed out`（间歇，约 1/3 失败）
- Wikipedia：多次 `操作超时。`
- Google：不可用
- **arXiv 直接抓取：稳定 HTTP 200** ⟹ 今后 arXiv 系文献优先直接抓取，不依赖搜索聚合

---

## 6. 归档标签

`π^π | GAP-3 | ln π 无理性 | arXiv:1310.7289 | MathOverflow 253070 | Nesterenko | Six Exponentials | F-4 | F-5`
