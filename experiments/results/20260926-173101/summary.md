# run 20260926-173101

- dataset: math-prealgebra
- problems: 170 (offset 0)
- model: deepseek-chat @ https://api.deepseek.com
- dry-run: False   workers: 8
- baseline: call errors = 0
- ir: call errors = 0

| condition | a | nu | kappa | alpha |
|---|---|---|---|---|
| baseline | 0.947 | 0.000 | 0.000 | 0.000 |
| ir | 0.512 | 0.641 | 0.881 | 0.453 |
