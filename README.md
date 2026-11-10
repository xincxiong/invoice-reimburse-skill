# 发票报销助手（WorkBuddy Skill）

把发票照片或 PDF 丢进一个文件夹，助手自动识别成 Excel 表格；核对一遍后，让助手把发票信息逐张填进学校报销网站，自己只需要在最后点提交。

## 安装（只需一次）

1. 在本页右侧 Releases 下载 `invoice-reimburse.zip`（也可以在仓库 `dist/` 目录里下载同一个文件）
2. 双击解压，得到 `invoice-reimburse` 文件夹
3. 打开“终端”，粘贴下面这行并回车：

```bash
mkdir -p ~/.workbuddy/skills && mv ~/Downloads/invoice-reimburse ~/.workbuddy/skills/
```

4. 重启 WorkBuddy

如果不想敲命令，也可以在 WorkBuddy 里把 zip 直接拖进对话，说“帮我安装这个 skill”。

## 使用

**首次**：在 WorkBuddy 里说「初始化发票报销」。助手会建好工作目录并安装依赖，需要联网，约 1-2 分钟。如果电脑提示安装“命令行开发者工具”，按提示装完再说一次。

**日常**：

| 想做的事 | 在 WorkBuddy 里说 |
|---------|------------------|
| 识别发票 | 把发票图片/PDF 发给助手，或放进 `~/invoice-reimburse/inbox/`，说「处理发票」 |
| 核对 | 打开 `~/invoice-reimburse/out/reimburse.xlsx`，核对金额，把「复核状态」改成「通过」 |
| 填报 | 说「把发票填到报销网站」，在弹出的 Chrome 里登录，之后助手逐张填入并暂存 |
| 提交 | 自己在报销网站上检查后点提交（助手不会替你提交） |

**首次填报前**：告诉 WorkBuddy「帮我校准报销网站填报」，按提示打开发票录入页、把输入框信息发给它，配置一次即可长期用。

## 前提

- Mac 电脑，装有 Chrome 和 python3
- 报销网站能用 Chrome 打开
- 首次初始化需要联网

## 说明

- 识别在本地完成，发票图片不上传任何服务
- 二维码增值税发票和电子发票 PDF 是零误差解析；火车票、出租车票等需要可选 OCR 组件
- 复核状态、报销网站配置、Chrome 登录态在升级 skill 时不会丢失
- 仓库里 `scripts/` 是全部代码，`references/calibration.md` 是网站选择器校准说明

## 更新

重新下载新版 zip 覆盖 `~/.workbuddy/skills/invoice-reimburse/`，回到 `~/invoice-reimburse/` 目录再跑一次 `bash ~/.workbuddy/skills/invoice-reimburse/scripts/setup.sh` 即可；已核对过的数据和网站配置都会保留。
