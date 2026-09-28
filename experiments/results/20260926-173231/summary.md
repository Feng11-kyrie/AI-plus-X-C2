# run 20260926-173231

- dataset: math-number-theory
- problems: 195 (offset 0)
- model: deepseek-chat @ https://api.deepseek.com
- dry-run: False   workers: 8
- baseline: call errors = 0
- ir: call errors = 0

| condition | a | nu | kappa | alpha |
|---|---|---|---|---|
| baseline | 0.908 | 0.000 | 0.000 | 0.000 |
| ir | 0.338 | 0.579 | 0.557 | 0.108 |
