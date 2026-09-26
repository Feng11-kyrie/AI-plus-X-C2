# 实验结果

## 执行参数

| 项 | 值 |
|---|---|
| 模型 | `deepseek-v4-flash` @ `https://api.deepseek.com` |
| 采样 | temperature 0 |
| 数据 | GSM8K test split 前 200 题（全量 1319 题见 `data/gsm8k_test.jsonl`） |
| 条件 | baseline（自由 CoT）与 ir（Typed IR + 完整清单），各 200 次 |
| 调用 | 400 次 completion，8 并发，耗时 5 分 16 秒，**失败 0 次** |
| 运行 ID | `20260926-170715` |

密钥经环境变量传入，未写入任何文件；`.gitignore` 已排除 `.env*` 与 `results/`。

## 结果

| 条件 | $a$ | $\nu$ | $\kappa$ | $\alpha$ |
|---|---|---|---|---|
| Baseline（自由 CoT） | 0.985 | 0.000 | -- | 0.000 |
| IR + 完整清单 | 0.975 | 0.995 | 0.995 | 0.975 |

$a$ 准确率 / $\nu$ 可验证率 / $\kappa$ 一致性 / $\alpha$ 可认证准确率（定义见论文 §6）。

**核心读数**：两个系统在报告准确率上只差 1 个百分点（197 vs 195 正确），
在可认证准确率上差 97.5 个百分点。只报 $a$ 的基准会把 baseline 判为更好的系统。

## 失败分类（IR 条件，200 条）

- 199 条被检查器接受
- 1 条 **R 类**：`R:forward-or-unbound-ref:max`（变量绑定到尚未声明的名字）
- 1 条 **N 类**：`N:goal!=answer`（goal 求值 ≠ 模型自述答案），属已验证但不一致

Baseline 200 条全部为 `A:no-structured-object`——这是**协议定义**使然（baseline 不产出结构化对象），
不是测量发现。

## 统计检验

McNemar 精确检验（不一致对 4 个：baseline 错 IR 对 1 个，baseline 对 IR 错 3 个）：
**p ≈ 0.63，不显著**。

因此文中只声称「IR 未提高准确率」，**不声称**「IR 降低了准确率」。

## 已知局限（论文 §6 已写明）

1. baseline 的 $\nu=0$ 是定义性的，不是测出来的
2. GSM8K 过于简单，不足以压测 Layer 2；此处的 $\nu$ 只能读作最易任务上的上界
3. $\kappa$ 在此设计下近乎空洞——它比对 IR 渲染与模型自述答案，二者同源，必然一致

## 复现

```bash
export DEEPSEEK_API_KEY=sk-...
python3 experiments/run_experiment.py --model deepseek-v4-flash --limit 200 --workers 8
```

已有结果可在不调用模型的前提下重算（α 定义修正后即采用此方式）：

```bash
python3 experiments/run_experiment.py --rescore experiments/results/<run-id>/raw.jsonl
```
