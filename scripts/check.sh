#!/usr/bin/env bash
# 论文自检：编译 + 引用完整性 + 交付物齐全性
# 用法：bash scripts/check.sh
set -uo pipefail

cd "$(dirname "$0")/.." || exit 1
ROOT="$(pwd)"
FAIL=0

echo "=== [1/4] 编译检查 ==="
TECT=""
for c in "$HOME/.workbuddy/binaries/tectonic/tectonic" "$(command -v tectonic 2>/dev/null)"; do
  [ -x "$c" ] && TECT="$c" && break
done
if [ -n "$TECT" ]; then
  echo "  引擎: tectonic ($TECT)"
  cd "$ROOT/paper" || exit 1
  if "$TECT" --reruns 2 paper.tex >/tmp/tectonic.log 2>&1; then
    [ -f paper.pdf ] && echo "  OK: paper.pdf 生成成功 ($(wc -c < paper.pdf | tr -d ' ') bytes)" || { echo "  FAIL: 未生成 PDF"; FAIL=1; }
  else
    echo "  FAIL: tectonic 报错，查看 /tmp/tectonic.log"; tail -25 /tmp/tectonic.log; FAIL=1
  fi
  cd "$ROOT" || exit 1
elif command -v pdflatex >/dev/null 2>&1; then
  cd "$ROOT/paper" || exit 1
  pdflatex -interaction=nonstopmode -halt-on-error paper.tex >/tmp/tex1.log 2>&1
  if [ $? -eq 0 ]; then
    bibtex paper >/tmp/bib.log 2>&1 || echo "  ! bibtex 有告警，查看 /tmp/bib.log"
    pdflatex -interaction=nonstopmode paper.tex >/tmp/tex2.log 2>&1
    pdflatex -interaction=nonstopmode paper.tex >/tmp/tex3.log 2>&1
    [ -f paper.pdf ] && echo "  OK: paper.pdf 生成成功" || { echo "  FAIL: 未生成 PDF"; FAIL=1; }
    grep -c "Citation .* undefined" /tmp/tex3.log 2>/dev/null | grep -q "^0$" || echo "  ! 存在未定义引用"
    grep -c "There were undefined references" /tmp/tex3.log >/dev/null 2>&1 && echo "  ! 存在未解析引用"
  else
    echo "  FAIL: pdflatex 报错，查看 /tmp/tex1.log"; FAIL=1
  fi
  cd "$ROOT" || exit 1
else
  echo "  SKIP: 本机无 LaTeX。用 Overleaf 导入 paper/ 验证，或装自包含版 tectonic："
  echo "        curl -sL -o t.tar.gz https://github.com/tectonic-typesetting/tectonic/releases/download/tectonic%400.17.0/tectonic-0.17.0-aarch64-apple-darwin.tar.gz"
  echo "        tar xzf t.tar.gz && xattr -d com.apple.quarantine tectonic && chmod +x tectonic"
fi

echo ""
echo "=== [2/4] 引用完整性（正文引用的 key 必须在 bib 中存在）==="
cd "$ROOT/paper" || exit 1
MISSING=0
for k in $(grep -oE '\\cite\{[^}]*\}' paper.tex | sed 's/\\cite{//;s/}//' | tr ',' '\n' | sed 's/ //g' | sort -u); do
  if ! grep -q "^@[a-zA-Z]*{$(echo "$k" | sed 's/[.*[\^$]/\\&/g')," references.bib; then
    echo "  MISSING in bib: $k"; MISSING=$((MISSING+1)); FAIL=1
  fi
done
[ $MISSING -eq 0 ] && echo "  OK: 所有 \\cite 均能在 references.bib 中找到"
echo "  bib 条目总数: $(grep -c '^@' references.bib)  (要求 >= 8)"
[ "$(grep -c '^@' references.bib)" -ge 8 ] || { echo "  FAIL: 引用不足 8 篇"; FAIL=1; }

echo ""
echo "=== [3/4] 交付物齐全性 ==="
cd "$ROOT" || exit 1
check() { [ -e "$1" ] && echo "  OK  : $1" || { echo "  MISS: $1"; FAIL=1; }; }
check "paper/paper.tex"
check "paper/references.bib"
ls logs/AI日志-Day*.md >/dev/null 2>&1 && echo "  OK  : logs/AI日志-Day*.md ($(ls logs/AI日志-Day*.md | wc -l | tr -d ' ') 份)" || { echo "  MISS: AI 日志"; FAIL=1; }
check "aar/AAR.md"

echo ""
echo "=== [4/4] 红线自查 ==="
echo "  [ ] references.bib 中每一条都在 docs/02-文献核验记录.md 登记并核验过？"
echo "  [ ] paper.tex 实机编译通过（未编译 = 技术实现 <= 5 分）？"
echo "  [ ] AI 日志覆盖了每一天（无日志 = 复盘 <= 5 分）？"

echo ""
[ $FAIL -eq 0 ] && echo "=== 全部检查通过 ===" || echo "=== 存在 $FAIL 项问题，见上方 ==="
exit $FAIL
