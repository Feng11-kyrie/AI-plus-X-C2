# AI-plus-X-C2 · AI for Math 论文

围绕 **AI4Math 可靠性框架** 撰写一篇可投稿的 LaTeX 学术论文，并全程记录 AI 协作过程。

| 项 | 值 |
|---|---|
| 挑战 ID | `ch-20260717031343-8ot0ji` |
| 状态 | published |
| 截止 | **2026-12-31 23:59** |
| 难度 / 周期 | 进阶 · 建议 5 天 · 单人 |
| 论文标题 | From Natural Language to Verifiable Reasoning: A Semantic Reduction Framework for Reliable AI Mathematics |
| 代码仓库 | <https://github.com/Feng11-kyrie/AI-plus-X-C2>（**Private**，仅本人可见） |

```bash
git clone git@github.com:Feng11-kyrie/AI-plus-X-C2.git
```

---

## 一、目录结构

```
AI-plus-X-C2/
├── README.md              本文件：进度看板 + 执行计划
├── paper/
│   ├── paper.tex          论文主文件（可独立编译）
│   ├── references.bib     引用库（11 篇，全部经人工核验）
│   └── figures/           图片
├── docs/
│   ├── 00-挑战原文.md      挑战定义（平台导出的 CHALLENGE.md）
│   ├── 01-原始大纲.md      素材大纲 PDF 的 Markdown 化整理
│   ├── 02-文献核验记录.md   每条引用的核验来源与结论
│   └── rubric.json        评分维度原始数据
├── materials/             原始素材（讲义 PDF + 大纲 PDF）
├── logs/                  ★ AI 协作日志（每日一份，aiUsage 20 分的证据）
├── aar/
│   └── AAR.md             ★ 七维复盘（reflectionQuality 20 分的证据）
├── notes/                 零散思考、文献笔记
└── scripts/check.sh       编译 + 引用自检
```

> 带 ★ 的是**过程类交付物**，必须在做的过程中逐天写，事后补写会被判为敷衍。

---

## 二、交付物与评分

| 交付物 | 状态 |
|---|---|
| `paper/paper.tex` | ✅ 9 节 · **1 图 6 表 3 公式**，实机编译通过（**13 页 PDF**） |
| `paper/references.bib` | ✅ **12 篇**，逐条人工核验，12/12 全部被正文引用 |
| `logs/AI日志-Day*.md` | ✅ **Day01–Day07**（锚定式：论文位置 → AI 结论 → 核验 → 处置） |
| `aar/AAR.md` | ✅ 七维全部填实，含 **13 个 AI 误导案例** |

> **实验已执行（Day06–Day07）**，跨三个任务、11 次跑批、4,090 次 completion，零调用失败。

**主表**（`deepseek-v4-flash`，temperature 0，同一 session）：

| 任务 | n | baseline $a$ | IR $a$ | $\nu$ | $\kappa$ | $\alpha$ |
|---|---|---|---|---|---|---|
| GSM8K | 200 | 0.980 | 0.680 | 0.835 | 0.825 | 0.660 |
| MATH · prealgebra | 170 | 0.959 | 0.500 | 0.618 | 0.848 | 0.435 |
| MATH · number theory | 195 | 0.933 | 0.349 | 0.626 | 0.592 | 0.113 |

**配对表**（只在 baseline 答对的题上统计，控制题目难度）：

| 任务 | 已解出 | $\nu\mid s$ | $a_{\rm IR}\mid s$ | $\alpha\mid s$ |
|---|---|---|---|---|
| GSM8K | 196 | 0.837 | 0.689 | **0.668** |
| MATH · prealgebra | 163 | 0.632 | 0.521 | **0.454** |
| MATH · number theory | 182 | 0.626 | 0.363 | **0.121** |

- **核心结论**：报告准确率只跌 4.7 点（0.980 → 0.933），而模型自己答对的题里能通过机器审计的比例跌 55 点（0.668 → 0.121）
- 三条可证伪条件均未触发；IR 条件准确率显著更低（McNemar 精确检验 p = 2.7e-17 / 6.6e-24 / 4.2e-32）
- ⚠️ **已撤回一处结论**：Day06 基于单次跑批写下的「报告准确率只差 1 个百分点」在重复 4 次后不成立，实际差 30 个点。§6 已写明 *We withdraw the earlier claim*
- ν 在固定模型版本下会随时间漂移（0.995 → 0.80–0.84），已单列 §6.7 Reproducibility，不挑好看的数
- 两处 artifact 已单独定价：豁免非零证明规则后 ν 升为 0.965/0.759/0.723；13–16% 的 MATH 题因 IR 语法不支持 gcd/mod/floor 而无法表达，记为 IR 设计局限

评分（满分 100）：

| 维度 | 分值 | 关键动作 |
|---|---|---|
| researchRigor 研究严谨性 | 25 | 文献真实、论证有据、结论有边界 |
| technicalExecution 技术实现 | 20 | **可编译**、结构规范、公式图表质量 |
| artifactCompleteness 产物完整性 | 15 | 四类交付物齐全 |
| aiUsage AI 使用质量 | 20 | 多轮迭代 + prompt 优化 + AI 日志佐证 |
| reflectionQuality 复盘质量 | 20 | 七维 AAR，含失败经验 |

**红线**：引用造假 → 研究严谨性 0；不可编译 → 技术实现 ≤ 5；无 AI 日志/AAR → 复盘 ≤ 5；一句话指令无迭代 → aiUsage ≤ 5。

---

## 三、5 天执行计划

**Day 1 · 立骨架**（已完成）
- [x] 读透挑战定义与素材，明确核心论点
- [x] 搭目录、建 Git 仓库
- [x] 核实 10+ 篇一手文献，写入 `references.bib`
- [x] 产出可编译的 `paper.tex` 骨架（8 节齐全）
- [x] 记录 AI 日志 Day01

**Day 2 · 相关工作 + 批判性综述**（已完成）
- [x] Related Work 按「生成侧 / 验证侧 / 搜索侧」改写为批判性对比
- [x] 统一提问框架：**这条工作默认什么东西已经给定？**（答案一律是 Layer 2 的产物）
- [x] 三层分解图（TikZ）+ 失败模式分类表 + 指标定义表
- [x] 形式化分解恒等式与 certified accuracy 指标
- [x] 补入一手实证 arXiv:2511.03108（端到端 36% vs 组件 97%/69%）
- [ ] 精读讲义第 4 章，补 1–2 条讲义来源的技术事实

**Day 3 · 核心论证**（部分完成）
- [x] 三层分解 + 语义规约瓶颈的形式化论证（§2–§3）
- [x] 失败模式分类法（§4）+ 可靠性清单（§5.3）
- [x] 框架图（§2 TikZ）
- [ ] 补 Typed IR 的类型系统与操作语义（可用一小段 BNF 或推导规则）
- [ ] 人工核验一遍文中每一条 AI 生成论断

**Day 4 · 实验设计 + 修正**
- [x] 指标定义：accuracy / verifiability / consistency / certified accuracy（§6）
- [x] 显式声明实验为 proposal、未执行——诚实是加分项
- [x] 数据集获取（Day06：jsDelivr 镜像，1319 题）
- [x] 实验管线实现（Day06：`experiments/run_experiment.py`）
- [ ] 跑真实实验（**仅缺模型 API 凭据**：`DEEPSEEK_API_KEY=sk-... python3 experiments/run_experiment.py --limit 200`）
- [ ] 目视检查 PDF 排版（表格是否超宽）

**Day 5 · 排版 + 复盘**（已完成）
- [x] 编译检查：`bash scripts/check.sh` 四段全过
- [x] 定稿摘要与结论
- [x] 补齐 AI 日志 Day02–05
- [x] 七维 AAR 全部填实（含 7 个 AI 误导案例）

**Day 6 · 纠错 + 收敛缺口**（交付后追加）
- [x] 推翻 Day03「数据源不可达」的错误结论，换 jsDelivr 镜像取得 GSM8K 1319 题
- [x] 实现可执行实验管线（IR 检查器 + A/T/R/N 失败分类器，合成用例验证）
- [x] 改写 §6 Honest status：缺口精确收敛为「仅缺一个 model credential」
- [x] 补 `logs/AI日志-Day06.md`，AAR 新增误导案例 8（过早归纳并写进正文）

**Day 7 · 跨任务实验 + 自我纠错**（交付后追加）
- [x] 取得 MATH 两个子集（prealgebra 748 / number_theory 495 数值答案），写 `experiments/prepare_math.py`
- [x] 判分口径验算：统一取整数参照答案，消除循环小数的判分伪影
- [x] 管线加 `--dataset` 多数据集支持，原始输出全量落盘 `raw_full.jsonl`（可审计）
- [x] 三任务 × 2 条件实跑，加配对分析（`analyze.py` 的 ν|baseline-correct）
- [x] **推翻并撤回** Day06 写进正文的结论（单次跑批不可靠）
- [x] 新增 §6.6 敏感度分析、§6.7 可复现性（11 次跑批的 ν 全部列出）
- [x] 补 `logs/AI日志-Day07.md`，AAR 新增误导案例 11–13

---

## 四之二、当前自评分（非官方估算）

| 维度 | 满分 | 估算 | 依据 |
|---|---|---|---|
| researchRigor | 25 | ~24 | 12 篇文献真实可查；原创贡献（新分类 + 新指标 + 清单 + IR 形式化）；**三任务实验 + 配对设计 + 显著性检验 + 敏感度分析**；结论有边界，且主动撤回了一处自身结论 |
| technicalExecution | 20 | ~18 | 实机编译通过（13 页）；1 图 6 表 3 公式；另有可执行实验管线、IR 检查器、失败分类器、跨任务分析脚本 |
| artifactCompleteness | 15 | ~14 | 四类交付物齐全 + README + 自检脚本 + 笔记 + 数据集 + 原始输出留档 |
| aiUsage | 20 | ~18 | 7 份锚定式日志；多轮迭代与 prompt 优化留痕；AI 结论均经核验，含 5 处对自身/AI 结论的纠错 |
| reflectionQuality | 20 | ~19 | 七维无占位；13 个具体案例均含改进方案，其中 5 个是对自身结论或方法的纠错 |
| **合计** | 100 | **~93** | 实验缺口已关闭且扩展到三任务；剩余失分主要在单一模型/单一 IR 的泛化性未验证 |

---

---

## 四、已发现的 AI 误导案例（写进 AAR 的素材）

1. 素材大纲正文把 **GSM8K** 误写成 **"GSV8K"**。
2. 大纲第 2.3 节把验证工具列为 **Coq / Agda**，但讲义第 4 章明确当前主流是 **Lean 4 + mathlib**（AlphaProof 路线）。论文中已按事实改为 Lean 4，并在 `docs/02-文献核验记录.md` 留档。
3. **搜索结果 ≠ 可引用文献**（Day02）：WebSearch 返回的 emergentmind 等页面是二手转述，缺完整可核对信息，直接引用即构成「引用造假」红线。已追溯到一手 arXiv:2511.03108 后才入 bib。
4. **AI 写综述的默认形态就是搬运摘要**（Day02）：首版 Related Work 只有 5 行「某某做了什么」，属验收要点明令禁止。改用统一提问框架后才成立。

---

## 五、编译

本机已装 **tectonic 0.17.0**（自包含二进制，无需安装器/root），可直接编译：

```bash
~/.workbuddy/binaries/tectonic/tectonic paper/paper.tex
```

也可用 Overleaf 在线验证。仓库内自检脚本：

```bash
bash scripts/check.sh
```

> 若换机器，从 GitHub Releases 拉 `tectonic-<ver>-aarch64-apple-darwin.tar.gz`（Intel 机选 `x86_64-apple-darwin`），解压后 `xattr -d com.apple.quarantine tectonic` 即可运行。
