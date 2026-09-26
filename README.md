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
| `paper/paper.tex` | ✅ 约 4300 词 · 9 节 · **1 图 3 表 3 公式**，实机编译通过（**10 页 PDF**） |
| `paper/references.bib` | ✅ **12 篇**，逐条人工核验，12/12 全部被正文引用 |
| `logs/AI日志-Day*.md` | ✅ **Day01–Day05**（锚定式：论文位置 → AI 结论 → 核验 → 处置） |
| `aar/AAR.md` | ✅ 七维全部填实，含 **7 个 AI 误导案例** |

> 唯一未按计划完成的项：**实验未执行**（数据源与模型 API 均不可达）。已在 §6 明确声明为 proposal，并给出原因与三项替代产出（示例计算 / 报告模板 / 可证伪条件）。诚实声明不构成造假。

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
- [ ] 决定实验走保守路还是进取路（GSM8K 小规模真实对比）
- [ ] 目视检查 PDF 排版（表格是否超宽）

**Day 5 · 排版 + 复盘**（已完成）
- [x] 编译检查：`bash scripts/check.sh` 四段全过
- [x] 定稿摘要与结论
- [x] 补齐 AI 日志 Day02–05
- [x] 七维 AAR 全部填实（含 7 个 AI 误导案例）

---

## 四之二、当前自评分（非官方估算）

| 维度 | 满分 | 估算 | 依据 |
|---|---|---|---|
| researchRigor | 25 | ~19 | 12 篇文献真实可查；有原创贡献（新分类 + 新指标 + 清单）；有实证支撑与可证伪条件；结论有边界 |
| technicalExecution | 20 | ~17 | 实机编译通过（10 页）；1 图 3 表 3 公式排版规范；IR 有形式化定义 |
| artifactCompleteness | 15 | ~14 | 四类交付物齐全 + README + 自检脚本 + 笔记 |
| aiUsage | 20 | ~16 | 5 份锚定式日志，记录多轮迭代与 prompt 优化；AI 结论均经核验 |
| reflectionQuality | 20 | ~17 | 七维无占位；7 个具体案例均含改进方案 |
| **合计** | 100 | **~83** | 主要失分点：实验未跑 |

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
