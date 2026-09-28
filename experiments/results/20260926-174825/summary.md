# run 20260926-174825

- dataset: gsm8k
- problems: 200 (offset 0)
- model: deepseek-chat @ https://api.deepseek.com
- dry-run: False   workers: 8
- baseline: call errors = 0
- ir: call errors = 0

| condition | a | nu | kappa | alpha |
|---|---|---|---|---|
| baseline | 0.975 | 0.000 | 0.000 | 0.000 |
| ir | 0.680 | 0.810 | 0.857 | 0.660 |
