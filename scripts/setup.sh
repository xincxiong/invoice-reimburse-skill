#!/bin/bash
# 初始化报销工作目录(代码与数据都在 TARGET,默认 ~/invoice-reimburse)
# 用法: bash setup.sh [目标目录]
set -euo pipefail

SRC_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET="${1:-$HOME/invoice-reimburse}"

mkdir -p "$TARGET/inbox" "$TARGET/out" "$TARGET/chrome-profile"

# 代码:每次覆盖(升级识别逻辑)
rm -rf "$TARGET/reimburse"
cp -R "$SRC_DIR/reimburse" "$TARGET/"
rm -rf "$TARGET/reimburse/__pycache__"
cp "$SRC_DIR/extract.py" "$SRC_DIR/fill.py" "$SRC_DIR/watch.py" "$SRC_DIR/requirements.txt" "$TARGET/"

# 用户配置:仅首次生成,后续不覆盖(保留 selectors 校准成果)
for f in config.yaml selectors.yaml; do
  if [ ! -f "$TARGET/$f" ]; then
    cp "$SRC_DIR/$f" "$TARGET/$f"
    echo "已生成 $TARGET/$f"
  fi
done

# Python 环境:仅首次创建
if [ ! -d "$TARGET/.venv" ]; then
  python3 -m venv "$TARGET/.venv"
fi
"$TARGET/.venv/bin/pip" install -q -r "$TARGET/requirements.txt"

echo "初始化完成: $TARGET"
echo "  投放发票:  $TARGET/inbox/"
echo "  结果文件:  $TARGET/out/reimburse.xlsx"
echo "  登录态:    $TARGET/chrome-profile/"
