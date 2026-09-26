# 实验结果留档

> `results/` 原始产物被 `.gitignore` 排除（体积大、含完整模型输出），本文件是入库留档的摘要。
> 完整原始输出见各 `results/<run-id>/raw_full.jsonl`（未入库，本地保留）。

## 一、配置

| 项 | 值 |
|---|---|
| 模型 | `deepseek-v4-flash` @ `api.deepseek.com` |
| 温度 | 0 |
| 并发 | 8 |
| 总跑批 | 11 次，4,090 次 completion，零调用失败 |
| 判分口径 | 只保留**整数参照答案**（消除循环小数的判分伪影，见下） |
| 取样 | 各测试集前 200 题（不经随机，免 seed） |

### 为什么只取整数答案

参照答案 `1/11` 在 float 中是 `0.09090909090909091`。模型若正确作答写 `0.0909`，
差值为 `9.09e-6`，大于 `1e-6` 容差 → 被判**错**。即"写几位小数"会影响对错，
与数学能力无关。统一取整数参照答案后该伪影消失。

过滤代价：MATH prealgebra 丢弃 14.1%，number theory 丢弃 8.3%（GSM8K 原本全为整数）。

## 二、主表（run 174224 / 174333 / 174449，同一 session）

| 任务 | n | baseline a | IR a | ν | κ | α |
|---|---|---|---|---|---|---|
| GSM8K | 200 | 0.980 | 0.680 | 0.835 | 0.825 | 0.660 |
| MATH · prealgebra | 170 | 0.959 | 0.500 | 0.618 | 0.848 | 0.435 |
| MATH · number theory | 195 | 0.933 | 0.349 | 0.626 | 0.592 | 0.113 |

## 三、配对表（只在 baseline 答对的题上统计）

把题目难度这个最大混淆变量控制掉：子集里每题模型都已答对，
所以 IR 条件的任何失败都不可能是"没找到答案"。

| 任务 | 已解出 | ν\|s | a_IR\|s | α\|s |
|---|---|---|---|---|
| GSM8K | 196 | 0.837 | 0.689 | **0.668** |
| MATH · prealgebra | 163 | 0.632 | 0.521 | **0.454** |
| MATH · number theory | 182 | 0.626 | 0.363 | **0.121** |

**核心读数**：报告准确率跌 4.7 点，可审计比例跌 55 点。

## 四、失败分类（§4 的 A/T/R/N）

| 任务 | 解析失败 | 其中契约(T) | 其中语法外(R) | 解析后失败(N) |
|---|---|---|---|---|
| GSM8K | 33/200 | 26 | 3 | 30 |
| MATH · prealgebra | 65/170 | 24 | 27 | 21 |
| MATH · number theory | 73/195 | 19 | 26 | 77 |

"解析后失败"是重点：对象已合规、已求值，但推出的值与模型自述的答案不符。
NT 上占 39%。

## 五、敏感度分析

| 任务 | ν | 豁免非零证明规则后 | 语法外占比 |
|---|---|---|---|
| GSM8K | 0.835 | 0.965 | 1.5% |
| MATH · prealgebra | 0.618 | 0.759 | 15.9% |
| MATH · number theory | 0.626 | 0.723 | 13.3% |

豁免契约规则后任务间差距依然成立 → 结论不依赖那条规则。
语法外那 13–16% 属 IR 表达力不足，记为设计局限。

## 六、可复现性（ν 不稳定，是结论不是噪声）

| 任务 | 各次跑批的 ν |
|---|---|
| GSM8K | 0.995 / 0.835 / 0.800 / 0.810 / 0.840 |
| MATH · prealgebra | 0.641 / 0.618 / 0.647 |
| MATH · number theory | 0.579 / 0.626 / 0.600 |

首个 0.995 与后四次相差 0.16。已用 `--prompt-style` 做对照实验
（恢复原措辞重跑 → 0.840），**确认不是提示词改动所致**，是服务端随时间漂移。

任务效应（GSM8K 0.80–0.84 vs MATH 0.58–0.65）大于该漂移幅度，且在重复跑中稳定。

## 七、⚠️ 已撤回的一处结论

Day06 基于**单次**跑批写下："两个系统报告准确率只差 1 个百分点（0.985 vs 0.975）"。

重复跑后不成立：

| 轮次 | baseline a | IR a |
|---|---|---|
| 首次（服务状态 A） | 0.985 | 0.975 |
| 后续 4 次（服务状态 B） | 0.980 / 0.975 / 0.975 / 0.975 | 0.680 / 0.665 / 0.680 / 0.675 |

论文 §6 已写明 *We withdraw the earlier claim*，并保留旧数值说明其归属。
McNemar 精确检验：三个任务 p = 2.7e-17 / 6.6e-24 / 4.2e-32。

**教训**：写进正文的实验数字必须来自至少两次独立跑批。

## 八、复现命令

```bash
cd /Users/fengshuo/AI-plus-X-C2
export DEEPSEEK_API_KEY=sk-...

# 单任务
python3 experiments/run_experiment.py --dataset math-number-theory --limit 200

# 三任务批量
for d in gsm8k math-prealgebra math-number-theory; do
  python3 experiments/run_experiment.py --dataset $d --limit 200
done

# 跨任务 + 配对分析
python3 experiments/analyze.py \
  GSM8K=results/<run1>/raw.jsonl \
  MATH-Prealgebra=results/<run2>/raw.jsonl \
  MATH-NumberTheory=results/<run3>/raw.jsonl

# 无 key 自检管线
python3 experiments/run_experiment.py --dry-run
```
