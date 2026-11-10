---
name: invoice-reimburse
description: 高校财务报销发票自动化。本地识别增值税发票(二维码/PDF文本/OCR兜底)汇总成Excel供人工复核,再用Playwright驱动Chrome把复核通过的发票自动填入报销网站(只填入并暂存,不自动提交)。当用户提到 发票、报销、识别发票、处理发票、发票录入、填报销单、报销网站、批量录发票 等场景时使用此技能。
agent_created: true
---

# 发票报销自动化

## 概述

把报销人从"对着发票逐张往网站里抄"中解放出来:发票(照片/PDF)投放到本地文件夹,机器识别成结构化字段,人工复核一次,再由浏览器自动化逐张填入报销网站并暂存。提交永远由人工完成。

## 工作目录

所有数据在 `~/invoice-reimburse/`:

```
~/invoice-reimburse/
├── inbox/          发票投放目录(图片/PDF/HEIC)
├── out/            reimburse.xlsx 结果 + 填报错误截图
├── chrome-profile/ Chrome 登录态(首次人工登录后持久化)
├── extract.py      识别入口
├── fill.py         自动填报入口
└── selectors.yaml  报销网站选择器(校准一次后长期有效)
```

## 流程决策树

1. `~/invoice-reimburse/` 不存在 → 执行【首次初始化】
2. 用户要求识别/处理发票 → 执行【识别与复核】
3. 用户要求填报/录入到报销网站 → 先确认 selectors.yaml 已校准,再执行【自动填报】
4. 用户报告网站改版/填报失败 → 按脚本目录旁 `references/calibration.md` 重新校准

## 首次初始化

前置条件:macOS、已装 Chrome、有 python3(含 venv 模块)。

```bash
bash <skill目录>/scripts/setup.sh
```

setup.sh 会把代码装到 `~/invoice-reimburse/` 并创建 Python 虚拟环境(约 1-2 分钟,需联网装依赖)。OCR 兜底(火车票/出租车票等无二维码票种)为可选:`~/invoice-reimburse/.venv/bin/pip install paddlepaddle paddleocr`。

## 识别与复核

1. 把发票文件放入 `~/invoice-reimburse/inbox/`。用户在会话里直接发来的发票图片/PDF 附件,先保存到该目录。
2. 运行:

```bash
cd ~/invoice-reimburse && .venv/bin/python extract.py
```

3. 用 pandas 读 `out/reimburse.xlsx` 向用户汇报结果表格:机器识别 N 条(二维码/PDF 文本,字段零误差)、待人工 M 条及原因。重跑幂等,复核状态按发票号码保留。
4. 引导复核:请用户打开 Excel 核对每行金额与票面一致,把"复核状态"下拉改为"通过"。也可让用户口头确认后由助手代改(逐条读给用户确认再写)。

已知边界:
- 二维码只含不含税金额,价税合计/税额空的格子需人工补或 OCR 补
- HEIC 照片自动经 sips 转 JPEG,无需预处理
- pandas 读回显示科学计数法是显示问题,单元格实际是文本且前导零完好

## 自动填报

前置:`selectors.yaml` 已按用户报销网站校准(校准方法见脚本目录旁 `references/calibration.md`)。

1. 确认 Excel 中有"复核状态=通过"的行
2. 运行:

```bash
cd ~/invoice-reimburse && .venv/bin/python fill.py
```

3. 首次会弹出 Chrome:指导用户登录报销网站(统一认证/短信均可),登录完成回终端按回车。之后登录态自动复用。
4. 机器逐张填入并点"暂存";某张失败会截图到 `out/error_N.png`,读截图定位问题。
5. 全部填完后,明确提醒用户:去网站逐张核对并人工提交。

## 安全边界(必须遵守)

- 只自动填入和暂存,禁止配置或点击"提交"类按钮
- 只填报复核状态为"通过"的行
- Chrome 登录态目录 `chrome-profile/` 属于敏感数据,不读取、不外传、不打包

## 脚本清单(scripts/)

| 文件 | 用途 |
|------|------|
| setup.sh | 初始化/升级工作目录,配置与登录态不覆盖 |
| extract.py | 识别入口:inbox → out/reimburse.xlsx |
| fill.py | Playwright 填报(channel=chrome,持久化登录态) |
| watch.py | 可选:后台监控 inbox 自动重扫 |
| reimburse/ | 识别库:QR/PDF/OCR/字段/Excel 输出 |
| selectors.yaml | 选择器模板(校准后生效) |
