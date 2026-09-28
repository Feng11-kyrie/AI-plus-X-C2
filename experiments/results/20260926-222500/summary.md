# run 20260926-222500

- dataset: gsm8k
- problems: 200 (offset 0)
- model: deepseek-v4-pro @ https://api.deepseek.com
- prompt-style: plain   dry-run: False   workers: 8
- baseline: call errors = 0
- ir: call errors = 75

| condition | a | nu | kappa | alpha |
|---|---|---|---|---|
| baseline | 0.925 | 0.000 | 0.000 | 0.000 |
| ir | 0.610 | 0.625 | 1.000 | 0.610 |
