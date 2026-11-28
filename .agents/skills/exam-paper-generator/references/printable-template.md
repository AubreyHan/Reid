# A4 可打印试卷 PDF 排版模板参考

本模板用于生成临时 HTML 中间源，供 `scripts/export_pdf.sh`（无头 Chrome/Edge）渲染为高质量 A4 可打印 PDF。渲染并校验通过后请清理临时 HTML，仅保留最终 `.pdf`。

## 1. 标准 A4 分页 HTML 排版骨架

```html
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<title>【试卷标题】</title>
<style>
  @page {
    size: A4 portrait;
    margin: 12mm 13mm 12mm 13mm;
  }

  * { box-sizing: border-box; }

  body {
    font-family: "Songti SC", "STSong", "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    color: #1a1a1a;
    background: #ffffff;
    margin: 0;
    padding: 0;
    font-size: 12.8px;
    line-height: 1.56;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }

  /* A4 单页内容容器：297mm - 上下各12mm = 273mm，预留 3mm 余量防溢出 */
  .sheet {
    width: auto;
    height: 270mm;
    min-height: 270mm;
    margin: 0;
    padding: 0;
    display: flex;
    flex-direction: column;
    page-break-after: always;
    break-after: page;
  }
  .sheet:last-of-type {
    page-break-after: auto;
    break-after: auto;
  }

  .sheet-content { flex: 1; }

  .page-footer {
    margin-top: auto;
    padding-top: 6px;
    border-top: 1px solid #d4d4d8;
    display: flex;
    justify-content: space-between;
    font-size: 10.8px;
    color: #666;
    font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  }

  /* 防止题目或图表被跨页截断 */
  .q-item, .passage-box, .ans-sec, .analysis-card, .rubric-table, svg {
    break-inside: avoid;
    page-break-inside: avoid;
  }
</style>
</head>
<body>

<!-- ==================== 第一部分：空白试卷 ==================== -->
<div class="sheet part-exam">
  <div class="sheet-content">
    <!-- 卷头、考生信息栏、题分汇总表、（如含听力注明 .mp3 文件名）、试题内容 -->
  </div>
  <div class="page-footer">
    <span>【试卷名称】 · 空白试卷</span>
    <span>第 1 页（共 N 页）</span>
  </div>
</div>

<!-- ==================== 第二部分：参考答案 ==================== -->
<div class="sheet part-answer">
  <div class="sheet-content">
    <!-- 参考答案、采分点、评分细则、参考范文、（如有）听力原文 -->
  </div>
  <div class="page-footer">
    <span>【试卷名称】 · 参考答案</span>
    <span>参考答案 第 1 页</span>
  </div>
</div>

<!-- ==================== 第三部分：题目分析 ==================== -->
<div class="sheet part-analysis">
  <div class="sheet-content">
    <!-- 知识点双向细目表、逐题/重点题考查点、思路、易错点与复习建议 -->
  </div>
  <div class="page-footer">
    <span>【试卷名称】 · 题目分析</span>
    <span>题目分析 第 1 页</span>
  </div>
</div>

</body>
</html>
```

## 2. PDF 排版注意事项

1. **高度控制防溢出**：A4 纸高 `297mm`，上下页边距各 `12mm` 时，单页可用高度为 `273mm`。将 `.sheet` 控制在 `270mm` 以内可避免单页轻微溢出导致多出空白页。
2. **局部导出（如需拆分为独立 PDF）**：若用户要求单独输出空白试卷、参考答案或题目分析的 PDF，可通过临时 CSS 隐藏其余部分（如 `.part-answer, .part-analysis { display: none; }`），并给最后一个可见 `.sheet` 加上 `break-after: auto`，分别调用 `scripts/export_pdf.sh` 导出即可。
3. **学科专用字体与组件**：
   - **语文**：正文优先宋体（`"Songti SC", "STSong"`），作文区使用标准方格阵（每行 20 格，标注字数刻度如 300/400/500 字）。
   - **数学**：分数/公式排版清晰，几何图形使用内联 SVG 矢量图保证打印锐利，解答题留足 `50mm`～`75mm` 演算空白。
   - **英语**：英文优先无衬线体（`"Helvetica Neue", Arial`），书写题与作文区使用双实线+虚线模拟英文书写行或四线三格。
4. **黑白打印友好**：所有边框、表格线、重点强调在黑白激光打印下均须清晰可辨，避免依赖浅色背景色区分关键信息。
5. **渲染验收**：PDF 导出后建议核查总页数与每一页的实际排版（确保无溢出空白页、无元素被截断）。
