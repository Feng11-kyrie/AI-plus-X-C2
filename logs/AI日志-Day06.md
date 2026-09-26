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

## 五、追问：「现在用的这个大模型不行吗」

用户反问能否直接用会话中的 AI 当被测模型。本机探测结果：**无任何本地模型端点**
（8080 是用户自己的微信群管理应用；ollama 未安装；无 ccSwitch 本地端口）。
所以「用现在的模型」只有一条实现路径——由我逐题作答，脚本判定。

### 结论：不建议。三条理由，按严重程度排序

1. **我知道实验假设与检查器规则（致命）**。我在上一轮刚写完 `parse_ir` / `check_ir`，
   清楚知道合法 IR 的每一条判据、知道论文预测「IR 条件 ν>0、baseline ν=0」。
   我作为被测者会有意识地迎合检查器 → 系统性偏倚（demand characteristics）。
   **而本文的全部论点押在 ν 上**：$a$ 我无法迎合（看不到参考答案，由脚本持有），
   但 ν 与 κ 我能迎合。核心假设检验因此失效。
2. **被测系统匿名**。论文必须说明被测模型是什么。会话中模型的身份与版本由平台决定
   且不固定，无法写出可辩护的模型名/版本，评审无法判断结果说明什么。
3. 规模受限：400 次作答在一次会话中不可行；30–50 题的 pilot 可行但效力不足。

### 对上一轮论证的自我修正

上一轮我把「不可复现」列为理由 1，说得太绝对。事实上 LLM 实验的复现本就是**程度问题**
（模型权重静默更新、temperature=0 不保证逐位确定性），即便有 API 也只是近似可复现。
所以「我不可复现」相对 API 是程度差异，不是有无差异。
**真正致命的是上面的第 1、2 条**，不是复现性。此处更正记录，避免论证被夸大理由支撑。

### 可行的替代：免费且模型身份明确的端点

无需信用卡、OpenAI 兼容、可在论文中写明模型名与版本：

| 平台 | base_url | 免费模型举例 | 额度 |
|---|---|---|---|
| 硅基流动 | `https://api.siliconflow.cn/v1` | `Qwen/Qwen2.5-7B-Instruct`、`deepseek-ai/DeepSeek-R1-Distill-Qwen-7B` | 注册送 2000 万 token，9B 以下永久免费 |
| 智谱 | `https://open.bigmodel.cn/api/paas/v4` | `glm-4-flash` | 免费模型不限量调用 |
| 阿里云百炼 | 兼容 OpenAI | 通义千问系列 | 每模型 100 万 token（90 天） |

拿到任意一个 key 即可直接跑现有管线，`--base-url` 与 `--model` 均为命令行参数，无需改代码。

## 六、实验已执行（用户授权后实跑）

### 执行参数
- 模型 `deepseek-v4-flash` @ `https://api.deepseek.com`，temperature 0
- GSM8K test 前 200 题 × 2 条件 = 400 次 completion，8 并发，耗时 5 分 16 秒
- **call errors = 0**（无一次调用失败）
- 密钥从 ccSwitch 配置读取，仅经环境变量传递，**未写入任何文件**；`.gitignore` 已挡 `.env*`
- 原始输出留档：`experiments/results/20260926-170715/raw.jsonl`（400 条）

### 结果

| 条件 | $a$ | $\nu$ | $\kappa$ | $\alpha$ |
|---|---|---|---|---|
| Baseline（自由 CoT） | **0.985** | 0.000 | -- | 0.000 |
| IR + 完整清单 | **0.975** | 0.995 | 0.995 | 0.975 |

失败分类：IR 条件 200 条中 199 条被检查器接受；1 条 **R 类**（变量绑定到尚未声明的名字 `max`）；
1 条 **N 类**（goal 求值 ≠ 模型自述 answer）。baseline 200 条全部 `A:no-structured-object`（协议定义，非测量）。

### 关键发现：实验抓出了我自己论文里的一个定义 bug

首轮跑完出现 α=0.990 > a=0.975，与 §3.2 的恒等式 $a = \alpha + (1-\nu)u$ **直接矛盾**。

- **AI/我的初始定义**：α = verifiable ∧ verified ∧ consistent（不含 correct）
- 核验：用已跑数据重算，检验恒等式
  - 旧定义：α + (1−ν)u = 0.990 ≠ a = 0.975 → **恒等式不成立**
  - 新定义（α 追加 correct）：α = 0.975，α + (1−ν)u = 0.975 = a → **残差 0，精确成立**
- 处置：① `score()` 中 α 加 `and r["correct"]` 并写明原因注释；② §6 指标表 α 定义补上 "and correct"；
  ③ 新增 `--rescore` 模式从已有 `raw.jsonl` 重算（不重复消耗调用）
- **教训：这个 bug 靠读代码/读论文都没发现，是跑出来才暴露的**。形式化定义与操作化实现之间的一致性，
  只有真实数据能检验

### 统计检验（避免过读）
- McNemar 精确检验：不一致对 4 个（baseline 错 IR 对 1 个，baseline 对 IR 错 3 个），**p ≈ 0.63，不显著**
- 因此文中**不声称**「IR 降低了准确率」，只声称「IR 未提高准确率」——这正是可证伪条件 (iii) 的要求
- 可证伪条件 (i)(ii) 也未触发 → 三条全部未触发，假设未被推翻

### 诚实写入文中的三条局限
1. **baseline 的 ν=0 是定义使然，不是测出来的**（协议要求自由输出，本就没有可检查对象）
2. **GSM8K 太简单**，不足以压测 Layer 2；高 ν 只能读作「在最易任务上取得的上界」
3. **κ 在此设计下近乎空洞**——它比对 IR 渲染与模型自述答案，二者同源，必然一致（κ=0.995）。
   要让 κ 真正咬合语义保真，需要独立撰写的题意渲染，本文未做

## 七、下一步

§6 报告模板已填为真实数据，实验缺口关闭。剩余可选：
- 换更难的数据集（MATH / miniF2F）复跑，检验 ν 是否随语义复杂度下降（这是 taxonomy 的真正预测）
- 引入独立渲染以让 κ 具备判别力
- 按 CICM 2027 的 LNCS 模板重排
