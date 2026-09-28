# run 20260926-174718

- dataset: gsm8k
- problems: 200 (offset 0)
- model: deepseek-chat @ https://api.deepseek.com
- dry-run: False   workers: 8
- baseline: call errors = 0
- ir: call errors = 0

| condition | a | nu | kappa | alpha |
|---|---|---|---|---|
| baseline | 0.975 | 0.000 | 0.000 | 0.000 |
| ir | 0.665 | 0.800 | 0.824 | 0.640 |
