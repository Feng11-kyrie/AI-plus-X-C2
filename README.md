# AI-plus-X-C2 · AI for Math 论文

围绕 **AI4Math 可靠性框架**撰写的一篇可投稿 LaTeX 学术论文，包含完整实验管线与全程 AI 协作记录。

| 项 | 值 |
|---|---|
| 挑战 ID | `ch-20260717031343-8ot0ji` |
| 论文标题 | From Natural Language to Verifiable Reasoning: A Semantic Reduction Framework for Reliable AI Mathematics |
| 难度 / 周期 | 进阶 · 建议 5 天 · 单人 |
| 截止 | 2026-12-31 23:59 |
| 仓库 | <https://github.com/Feng11-kyrie/AI-plus-X-C2>（**Public**） |

```bash
git clone https://github.com/Feng11-kyrie/AI-plus-X-C2.git
# 或 SSH
git clone git@github.com:Feng11-kyrie/AI-plus-X-C2.git
```

---

## 一、给核验者：如何不花一分钱独立验证

这是本仓库的设计目标——**所有结论都可以在零 API 调用、零费用的前提下被第三方复算**。

| 想验证什么 | 怎么做 | 耗时 |
|---|---|---|
| 论文能不能编译 | 见下节「编译」 | ~1 分钟 |
| 论文成品长什么样 | 直接打开 `paper/paper.pdf`（已入库，**无需编译**） | 0 |
| 实验数字对不对 | `python3 experiments/run_experiment.py --rescore experiments/results/20260926-174224/raw.jsonl` | ~1 秒 |
| 跨任务 + 配对分析 | 见下「复算三条命令」 | ~2 秒 |
| 管线逻辑是否自洽 | `python3 experiments/run_experiment.py --dry-run` | ~1 秒 |
| 引用是否全部存在 | `bash scripts/check.sh` | ~1 分钟 |

`--rescore` 会用已入库的逐题打分记录从头重算 $a,\nu,\kappa,\alpha$，
**不调用任何模型**，输出应与本文主表逐位一致。这意味着论文里的数字不是"声称的"，是可复算的。

### 复算三条命令

```bash
cd AI-plus-X-C2

# 1) 复算 GSM8K 主表（零 API 调用）
python3 experiments/run_experiment.py \
    --rescore experiments/results/20260926-174224/raw.jsonl

# 2) 复算 MATH-prealgebra
python3 experiments/run_experiment.py \
    --rescore experiments/results/20260926-174333/raw.jsonl

# 3) 跨任务 + 配对分析（α|solved 梯度）
python3 experiments/analyze.py \
    GSM8K=experiments/results/20260926-174224/raw.jsonl \
    MATH-Prealgebra=experiments/results/20260926-174333/raw.jsonl \
    MATH-NumberTheory=experiments/results/20260926-174449/raw.jsonl
```

预期输出见「实验结果」一节。**若与本文数值不符，请以你的输出为准并提 issue**——
这比任何自述都可靠。

---

## 二、编译

**推荐**：仓库已含编译好的 `paper/paper.pdf`，不想编译可直接翻看。

若要从源码编译，本机安装的是 **tectonic**（自包含单文件二进制，无需 TeX 发行版、无需 root）：

```bash
# macOS / Linux
curl -fsSL https://drop-sh.fullyjustified.net | sh          # 或用 release 包
tectonic paper/paper.tex
```

本机已装在 `~/.workbuddy/binaries/tectonic/tectonic`，可直接：

```bash
~/.workbuddy/binaries/tectonic/tectonic paper/paper.tex
```

> 换机器时：从 GitHub Releases 取 `tectonic-<ver>-aarch64-apple-darwin.tar.gz`
> （Intel 机选 `x86_64-apple-darwin`），解压后 `xattr -d com.apple.quarantine tectonic` 即可运行。

**依赖**：无第三方 LaTeX 宏包需求；论文使用标准 `article` 文档类 + TikZ 图。
也可用 Overleaf 在线验证——上传 `paper.tex` + `references.bib` 即可。

**一键自检**（编译 + 引用完整性 + 交付物齐全性 + 红线自查）：

```bash
bash scripts/check.sh
```

四段全过才算可交付。

---

## 三、四类交付物

| 交付物 | 位置 | 状态 |
|---|---|---|
| `paper.tex` | `paper/paper.tex` | ✅ **15 页**，1 图 6 表 3 公式 + 附录 A，实机编译通过 |
| `references.bib` | `paper/references.bib` | ✅ **12 篇**，逐条人工核验，**12/12 全部被正文引用** |
| AI 日志 | `logs/AI日志-Day01…Day08.md` | ✅ **8 份**，锚定式：论文位置 → AI 结论 → 核验 → 处置 |
| AAR | `aar/AAR.md` | ✅ 七维全部填实，含 **16 个** AI 误导 / 自我纠错案例 |

> 「锚定式」指每条记录都指向论文的具体位置，而不是流水账。这是为了让 reviewer 能按图索骥，
> 而不是靠自述采信。

---

## 四、目录结构

```
AI-plus-X-C2/
├── paper/
│   ├── paper.tex                论文源文件（可独立编译）
│   ├── paper.pdf                ★ 编译成品，已入库，免编译即可查看
│   ├── references.bib           引用库
│   └── figures/                 图片
├── experiments/
│   ├── run_experiment.py        实验管线（IR 检查器 + A/T/R/N 失败分类器）
│   ├── analyze.py               跨任务 + 配对分析
│   ├── prepare_math.py          MATH parquet → JSONL
│   ├── data/                    GSM8K 1319 题 + MATH 两个子集（已入库）
│   ├── results/                 ★ 全部跑批原始产物，已入库
│   │   └── <run-id>/{raw.jsonl, raw_full.jsonl, summary.md, table.tex}
│   └── RESULTS.md               实验结果人工留档
├── docs/
│   ├── 00-挑战原文.md
│   ├── 01-原始大纲.md
│   ├── 02-文献核验记录.md       每条引用的核验来源与结论
│   ├── 03-端点可用性与跨模型验证判据.md   ★ 含原始错误码，可复现
│   └── rubric.json
├── logs/                        ★ AI 日志 Day01–Day08
├── aar/AAR.md                   ★ 七维复盘
├── materials/                   原始素材 PDF（讲义 + 大纲）
├── notes/
└── scripts/check.sh             四段自检
```

`raw_full.jsonl` 保留了模型的**完整原始输出**，用于审计失败分类判定是否正确；
`raw.jsonl` 是逐题打分结果。两者都已入库（总计约 4 MB）。

---

## 五、核心论点

三层分解：**生成层**（LLM CoT）→ **语义规约层**（Typed IR，本文主张的瓶颈）→ **验证层**（Lean 4 / mathlib / SMT）。

提出 **certified accuracy** $\alpha$ 作为独立于 accuracy 的指标，并有恒等式

$$a = \alpha + (1-\nu)\,u$$

其中 $\nu$ 是可验证率、$u$ 是未被捕获的答案准确率。含义：只看 $a$ 无法分辨
「答得好」与「答得好且经得起审计」。

---

## 六、实验结果

模型 `deepseek-v4-flash`（temperature 0），跨三个任务、2 个条件、11 次跑批、4,090 次 completion。

**主表**

| 任务 | n | baseline $a$ | IR $a$ | $\nu$ | $\kappa$ | $\alpha$ |
|---|---|---|---|---|---|---|
| GSM8K | 200 | 0.980 | 0.680 | 0.835 | 0.825 | 0.660 |
| MATH · prealgebra | 170 | 0.959 | 0.500 | 0.618 | 0.848 | 0.435 |
| MATH · number theory | 195 | 0.933 | 0.349 | 0.626 | 0.592 | 0.113 |

**配对表**（只在 baseline 已答对的题上统计，从而控制掉题目难度这个混淆变量）

| 任务 | 已解出 | $\nu\mid s$ | $a_{\rm IR}\mid s$ | $\alpha\mid s$ |
|---|---|---|---|---|
| GSM8K | 196 | 0.837 | 0.689 | **0.668** |
| MATH · prealgebra | 163 | 0.632 | 0.521 | **0.454** |
| MATH · number theory | 182 | 0.626 | 0.363 | **0.121** |

**读数**：报告准确率跌 4.7 点，而模型自己答对的题里能被机器审计的比例跌 55 点。

### 诚实声明（这些是限制，不是成绩单）

- ⚠️ **已撤回一处结论**：早期基于单次跑批写下的「报告准确率只差 1 个百分点」在重复 4 次后不成立，实际差 30 点。论文已写明 *We withdraw the earlier claim*
- $\nu$ 在**固定模型版本**下会随时间漂移（GSM8K 五次：0.995 / 0.835 / 0.800 / 0.810 / 0.840），已用 `--prompt-style` 对照实验排除提示词因素
- 13–16% 的 MATH 题因 IR 语法不支持 gcd / mod / floor 而无法表达，属**已知设计局限**；附录 A 给出扩展语法草案
- **泛化性未验证**：单一模型、单一 IR 方言、school-level 语料。`docs/03` 给出跨模型尝试的**可复现判据与原始错误码**，说明为何当前配额下不可行

---

## 七、评分维度对照

| 维度 | 满分 | 对应证据 |
|---|---|---|
| researchRigor 研究严谨性 | 25 | 12 篇文献真实可查（见 `docs/02`）；三任务实验 + 配对设计 + McNemar 检验 + 敏感度分析；主动撤回自身一处结论 |
| technicalExecution 技术实现 | 20 | 实机编译通过（含附录 15 页，无 Overfull 无 undefined）；可执行实验管线；`--rescore` 支持零成本复算 |
| artifactCompleteness 产物完整性 | 15 | 四类交付物齐全 + PDF + 数据 + 原始输出 + 跨模型判据文档 |
| aiUsage AI 使用质量 | 20 | 8 份锚定式日志，含多轮迭代、提示词对照实验、多起 AI 结论纠错 |
| reflectionQuality 复盘质量 | 20 | 七维无占位，16 个案例，其中多个是对自身方法与结论的纠错 |

**红线**：引用造假 → 研究严谨性 0；不可编译 → 技术实现 ≤5；无 AI 日志/AAR → 复盘 ≤5。

---

## 八、安全性说明

`experiments/` 下脚本只从环境变量读取 API 凭据（`DEEPSEEK_API_KEY` / `OPENAI_API_KEY`），
**仓库中不含任何密钥**（已逐文件核验；`.gitignore` 排除 `.env`、`*.key`、`secrets.*`）。
文中出现的 `sk-...` 均为文档占位符。
