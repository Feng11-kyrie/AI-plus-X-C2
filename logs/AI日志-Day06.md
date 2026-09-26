# AI 日志 · Day06（交付后追加轮次）

> 时间：2026-09-26（与 Day01–05 同一工作日内的后续阶段）
> 触发问题：「为什么跑实验需要模型 API？」
> 本轮性质：**纠错 + 收敛缺口**。发现 Day03 的一个错误结论，并把它写进了正文，本轮修正。

---

## 一、本轮起点：我自己的一个错误结论

Day03 我做过两次数据获取尝试：

| 尝试 | 目标 | 结果 | 我当时下的结论 |
|---|---|---|---|
| 1 | `raw.githubusercontent.com/.../test.jsonl` | `exit 28`（超时） | 不可达 |
| 2 | `huggingface.co/.../test-00000-of-00001.parquet` | `HTTP=000` | 不可达 |

据此在论文 §6 写下：

> the benchmark corpora were unreachable (both the upstream GSM8K source and its
> mirror were not retrievable)

**这句话现在是错的。** 本轮换路径后一次成功：

| 尝试 | 目标 | 结果 |
|---|---|---|
| 3 | `cdn.jsdelivr.net/gh/openai/grade-school-math@master/.../test.jsonl` | **HTTP 200，749738 bytes，1319 题** |

校验：
- `wc -l` = 1319
- 逐行 `json.loads` 全部通过（首次下载曾被截断到 378149 bytes，靠 `content-length` 对比发现并重下）
- 字段 `['question','answer']`，1319/1319 含 `#### <number>` 答案标记

**AI 结论 → 人工核验 → 处置**：
- AI 结论：「数据源不可达，实验只能走保守路」
- 核验：换两条镜像路径实测，均 HTTP 200
- 处置：数据落盘 `experiments/data/gsm8k_test.jsonl`（MD5 `6493e22fc90d491ae8da0b88ffcfebae`）；改写 §6 声明；本条记入 AAR 案例 8

---

## 二、为什么跑实验必须要模型 API（本轮的核心回答）

实验要测的不是「我能不能算对题」，而是**四个量的对比**，其中三个跟模型无关：

| 符号 | 含义 | 谁来判定 |
|---|---|---|
| $a$ | 最终答案对不对 | 脚本（跟参考答案比） |
| $\nu$ | 输出能否构成可检查的形式对象 | **本地检查器** |
| $\kappa$ | 形式对象是否真的表达了模型想说的那句话 | **本地检查器** |
| $\alpha$ | 可验证 ∧ 已验证 ∧ 一致 | 脚本 |

**被测对象必须是一个「固定版本、可用同样输入重复调用」的模型。**

- 脚本、检查器、判分：我能写，已写完 ✅
- 题目数据：已拿到 ✅
- 被评测模型：需要一个能发几百次 chat-completion 的端点 ❌ ← **唯一缺口**

为什么不能由我（会话中的 AI）直接当被测模型：

1. **不可复现**。评审无法重新发起「2026-09-26 的这一次会话」，模型版本、采样、上下文都不可固定，重跑必然得到不同结果。一篇主张「可验证性」的论文，自己的实验却不可复现，是自相矛盾的。
2. **不可控变量**。手工逐题作答无法保证 baseline 与 IR 两个条件用的是同一套采样参数，条件间对比就失效了。
3. **规模不现实**。200 题 × 2 条件 = 400 次作答，手工方式没有可行的质量保证手段。
4. **判定者与被判定者同一**。让生成答案的系统自己判定 $\nu$ 和 $\kappa$，恰恰是本文批判的做法。$\nu$、$\kappa$ 必须由外部检查器给出——这也是为什么脚本里这两个量一律由本地 `parse_ir` / `check_ir` 决定，模型说了不算。

---

## 三、本轮实际产出

**1. 数据**
- `experiments/data/gsm8k_test.jsonl`：GSM8K test 全量 1319 题

**2. 可执行实验管线** `experiments/run_experiment.py`
- 两条件：`baseline`（自由 CoT，`####` 标记答案）/ `ir`（结构化 Typed IR JSON）
- 本地检查器：`parse_ir` 做良构性判定 → 输出 $\nu$；`check_ir` 求值并比对 → 输出 $\kappa$
- 失败分类直连论文 §4 的 A/T/R/N 四类：

| 合成输入 | 检查器判定 | 对应类 |
|---|---|---|
| 合法 IR | verified, consistent | — |
| 变量缺 `type` | `T:missing-or-unknown-type` | T 类型省略 |
| `def` 引用尚未声明的变量 | `R:forward-or-unbound-ref:y` | R 指称漂移 |
| 除法未附 `nonzero` 证明 | `T:division-without-nonzero-proof` | T 类型省略 |
| `goal` 引用未声明变量 | `R:goal-refs-undeclared:z` | R 指称漂移 |
| `goal` 求值 ≠ `answer` | verified, **not** consistent | N 不可逆 |
| 非 JSON 输出 | `A:malformed-json` | A 歧义 |

  七条合成用例已实测通过，分类与论文 §4 定义一致。
- 不调 API 也能自检：`python3 run_experiment.py --dry-run`
- 有 key 即跑：`DEEPSEEK_API_KEY=sk-... python3 run_experiment.py --limit 200`
- 产出 `results/<run-id>/{raw.jsonl, summary.md, table.tex}`，其中 `table.tex` 是现成的 LaTeX 表格行，可直接填进 §6 报告模板

**3. 论文 §6 改写**
- 原表述把缺口说成「语料不可达 + 无 API」→ 事实错误
- 现表述：语料已随文分发、管线已实现并通过合成用例、**缺口精确收敛为一个 model credential**
- 明确写出「we are not claiming that the measurement is infeasible---only that we did not make it」

**4. `.gitignore`**：`experiments/results/` 排除（运行结果不入库，原始数据与脚本入库）

---

## 四、编译与自检

- `tectonic --reruns 2 paper.tex`：EXIT=0，**无 error / overfull / undefined**，仅剩表格窄列 Underfull（无害）
- 引用 12/12 未变动，本轮未新增文献

## 五、下一步

只需一个模型 API 凭据即可把 §6 报告模板填成真实数据。默认配置 DeepSeek（`api.deepseek.com` / `deepseek-chat`），200 题 × 2 条件 ≈ 400 次调用。
