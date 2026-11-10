# 报销网站选择器校准指南

首次填报前必须完成一次。之后网站改版才需要重做。

## 前置信息

需要用户提供:
1. 报销网站的发票录入页 URL(登录后浏览器地址栏复制)
2. 录入页各输入框的 HTML(教用户操作:在录入页右键任一输入框 → 检查,把高亮的那行 HTML 复制出来)

## 校准步骤

1. 编辑 `~/invoice-reimburse/selectors.yaml`,把 URL 填入 `invoice_page_url`
2. 对每个字段,从 HTML 推导 selector,优先级:
   - `<input id="invoiceNo">` → `#invoiceNo`
   - `<input name="fpNo">` → `input[name='fpNo']`
   - 带稳定 class:`input.fp-num`
   - 禁止用自动生成的 class(如 `el-input-4f2a`,每次渲染会变)和位置路径(`div > div > input`)
3. 填入 `selectors:` 对应字段,删掉页面上不存在的字段(如网站不要填校验码,就删掉 `check_code` 行)
4. 确认 `save_button` 对应"暂存/保存"按钮,**永远不要配置提交按钮**

## 常见控件处理

| 控件类型 | 处理方法 |
|---------|---------|
| 原生 `<select>` 下拉 | fill.py 的 fill() 会生效;若失败,在 selectors.yaml 加 `<字段>_click` 和 `<字段>_option` 序列 |
| Element-UI/AntD 等组件下拉 | 用 click 序列:点开下拉,再点 `li[data-value='xx']` |
| readonly 日期控件 | fill.py 已用键盘输入绕过;仍失败则改 click + 日历面板选项序列 |
| iframe 内嵌表单 | 在 fill.py 的 fill_page 中进入 frame: `page.frame_locator("iframe的selector")` |

## 验证

用 1-2 张已复核"通过"的发票跑 `fill.py`,观察填写过程;失败时看 `out/error_N.png` 截图定位是哪个字段没填上,对应修正 selector 后重跑(已暂存的发票在网站上删除重填,或人工改)。
