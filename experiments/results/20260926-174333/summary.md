# run 20260926-174333

- dataset: math-prealgebra
- problems: 170 (offset 0)
- model: deepseek-chat @ https://api.deepseek.com
- dry-run: False   workers: 8
- baseline: call errors = 0
- ir: call errors = 0

| condition | a | nu | kappa | alpha |
|---|---|---|---|---|
| baseline | 0.959 | 0.000 | 0.000 | 0.000 |
| ir | 0.500 | 0.618 | 0.848 | 0.435 |
