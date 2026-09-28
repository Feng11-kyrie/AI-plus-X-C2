# run 20260926-174449

- dataset: math-number-theory
- problems: 195 (offset 0)
- model: deepseek-chat @ https://api.deepseek.com
- dry-run: False   workers: 8
- baseline: call errors = 0
- ir: call errors = 0

| condition | a | nu | kappa | alpha |
|---|---|---|---|---|
| baseline | 0.933 | 0.000 | 0.000 | 0.000 |
| ir | 0.349 | 0.626 | 0.592 | 0.113 |
