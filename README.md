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
| `paper/paper.tex` | 骨架完成 |
| `paper/references.bib` | 11 篇，已核验 |
| `logs/AI日志-Day*.md` | Day01 |
| `aar/AAR.md` | 模板已建 |

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

**Day 2 · 相关工作 + 批判性综述**
- [ ] 精读讲义第 4 章（AI 证明定理），提取可引用的技术事实
- [ ] 写第 5 节 Related Work：按「生成侧 / 验证侧 / 搜索侧」分类对比，不做摘要搬运
- [ ] 每条对比都要落到「它没解决什么」

**Day 3 · 核心论证**
- [ ] 写第 2–3 节：三层分解 + 语义规约瓶颈的形式化论证
- [ ] 补 Typed IR 的类型系统与操作语义（可用一小段 BNF 或推导规则）
- [ ] 画第 4 节的框架图（TikZ 或外部图片）

**Day 4 · 实验设计 + 修正**
- [ ] 写第 6 节：指标定义（accuracy / verifiability / consistency）
- [ ] 显式写出局限性与「未完成的实验」——诚实是加分项
- [ ] 全文人工核验一遍 AI 生成的每一条论断

**Day 5 · 排版 + 复盘**
- [ ] 编译检查：`bash scripts/check.sh`
- [ ] 定稿摘要与结论
- [ ] 补齐 AI 日志 Day02–05
- [ ] 写七维 AAR（必须写「AI 误导案例」）

---

## 四、已发现的 AI 误导案例（写进 AAR 的素材）

1. 素材大纲正文把 **GSM8K** 误写成 **"GSV8K"**。
2. 大纲第 2.3 节把验证工具列为 **Coq / Agda**，但讲义第 4 章明确当前主流是 **Lean 4 + mathlib**（AlphaProof 路线）。论文中已按事实改为 Lean 4，并在 `docs/02-文献核验记录.md` 留档。

---

## 五、编译

本机没有 LaTeX 发行版时，可用在线编译器（Overleaf）验证，或安装 BasicTeX。
仓库内自检脚本：

```bash
bash scripts/check.sh
```
