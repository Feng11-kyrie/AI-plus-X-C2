# run 20260926-175151

- dataset: math-prealgebra
- problems: 170 (offset 0)
- model: deepseek-chat @ https://api.deepseek.com
- prompt-style: plain   dry-run: False   workers: 8
- baseline: call errors = 0
- ir: call errors = 0

| condition | a | nu | kappa | alpha |
|---|---|---|---|---|
| baseline | 0.971 | 0.000 | 0.000 | 0.000 |
| ir | 0.500 | 0.647 | 0.845 | 0.447 |
