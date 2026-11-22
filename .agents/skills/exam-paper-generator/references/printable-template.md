# A4 可打印试卷 HTML 模板与排版参考

生成可打印试卷 HTML 时，请以本模板为基础并根据科目特点（语文作文格、数学公式与几何 SVG、英语四线三格/音频条）扩展样式。

## 1. 标准 HTML 结构骨架

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
    background: #eef1f5;
    margin: 0;
    padding: 18px 0 40px 0;
    font-size: 12.8px;
    line-height: 1.56;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }

  /* 顶部打印工具栏（打印时自动隐藏） */
  .no-print-banner {
    width: 210mm;
    margin: 0 auto 14px auto;
    background: #ffffff;
    border: 1px solid #cbd5e1;
    border-left: 4px solid #1d4ed8;
    border-radius: 8px;
    padding: 12px 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 12px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
  }
  .banner-info { font-size: 12.5px; color: #334155; }
  .banner-info strong { color: #0f172a; font-size: 14px; }
  .banner-actions { display: flex; flex-wrap: wrap; gap: 6px; justify-content: flex-end; }
  .btn {
    border: none;
    padding: 6px 11px;
    font-size: 12px;
    border-radius: 6px;
    cursor: pointer;
    font-weight: 500;
    font-family: inherit;
  }
  .btn-primary { background: #1d4ed8; color: #fff; }
  .btn-primary:hover { background: #1e40af; }
  .btn-secondary { background: #f1f5f9; color: #1e293b; border: 1px solid #cbd5e1; }
  .btn-secondary:hover { background: #e2e8f0; }

  /* 音频播放条（仅屏幕可见，打印自动隐藏） */
  .audio-bar {
    width: 210mm;
    margin: 0 auto 14px auto;
    background: #f8fafc;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 10px 16px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 12px;
    font-family: "PingFang SC", "Microsoft YaHei", sans-serif;
    font-size: 12.5px;
  }
  .audio-bar audio { flex: 1; height: 34px; }

  /* A4 纸张容器 */
  .sheet {
    width: 210mm;
    min-height: 297mm;
    margin: 0 auto 18px auto;
    background: #ffffff;
    padding: 12mm 13mm 11mm 13mm;
    box-shadow: 0 2px 12px rgba(0,0,0,0.1);
    display: flex;
    flex-direction: column;
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

  /* 分模块打印模式 */
  body.print-exam-only .part-answer,
  body.print-exam-only .part-analysis { display: none !important; }

  body.print-answer-only .part-exam,
  body.print-answer-only .part-analysis { display: none !important; }

  body.print-analysis-only .part-exam,
  body.print-analysis-only .part-answer { display: none !important; }

  body.print-answer-analysis .part-exam { display: none !important; }

  @media print {
    body {
      background: #fff;
      padding: 0;
      margin: 0;
    }
    .no-print,
    .no-print-banner,
    .audio-bar {
      display: none !important;
    }
    .sheet {
      width: auto;
      height: 273mm;
      min-height: 273mm;
      margin: 0;
      padding: 0;
      box-shadow: none;
      page-break-after: always;
      break-after: page;
    }
    .sheet:last-of-type {
      page-break-after: auto;
      break-after: auto;
    }
  }
</style>
</head>
<body>

<div class="no-print-banner">
  <div class="banner-info">
    <strong>【试卷名称】（A4 可打印版）</strong><br>
    包含：空白试卷 / 参考答案 / 题目分析（三部分独立起页，可按需单打）
  </div>
  <div class="banner-actions">
    <button class="btn btn-primary" onclick="printMode('all')">打印完整版</button>
    <button class="btn btn-secondary" onclick="printMode('exam')">仅打印空白试卷</button>
    <button class="btn btn-secondary" onclick="printMode('answer')">仅打印参考答案</button>
    <button class="btn btn-secondary" onclick="printMode('analysis')">仅打印题目分析</button>
    <button class="btn btn-secondary" onclick="printMode('answer-analysis')">仅打印答案与分析</button>
  </div>
</div>

<!-- 可选：当试卷含音频时保留此块，src 使用同目录相对路径 -->
<!--
<div class="audio-bar no-print">
  <span><strong>听力音频：</strong>./【音频文件名】.mp3</span>
  <audio controls preload="metadata" src="./【音频文件名】.mp3"></audio>
</div>
-->

<!-- ==================== 第一部分：空白试卷 ==================== -->
<div class="sheet part-exam">
  <div class="sheet-content">
    <!-- 卷头、考生信息栏、题分汇总表、试题内容 -->
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

<script>
  const PRINT_CLASSES = [
    'print-exam-only',
    'print-answer-only',
    'print-analysis-only',
    'print-answer-analysis'
  ];
  function printMode(mode) {
    document.body.classList.remove(...PRINT_CLASSES);
    if (mode === 'exam') document.body.classList.add('print-exam-only');
    if (mode === 'answer') document.body.classList.add('print-answer-only');
    if (mode === 'analysis') document.body.classList.add('print-analysis-only');
    if (mode === 'answer-analysis') document.body.classList.add('print-answer-analysis');
    window.print();
    setTimeout(() => document.body.classList.remove(...PRINT_CLASSES), 300);
  }
</script>
</body>
</html>
```

## 2. 排版注意事项

1. **高度控制防溢出**：A4 纸高 `297mm`，上下页边距各 `12mm` 时，单页可用高度为 `273mm`（建议控制在 `268mm`～`270mm` 以留出安全余量，避免一页内容被浏览器多拆出一个近乎空白的尾页）。
2. **仅打印局部时的最后一页处理**：当使用 `print-exam-only` 等模式隐藏后续 `.sheet` 时，浏览器可能仍对被显示部分的最后一个 `.sheet` 触发 `page-break-after: always`（因为 DOM 中它不是 `:last-of-type`）。如需消除局部打印时的多余空白页，可在 `printMode` 中动态给最后一个可见 `.sheet` 临时加一个 `.is-last-visible` 类，在 `@media print` 中设 `.sheet.is-last-visible { page-break-after: auto; break-after: auto; }`。
3. **学科专用字体与组件**：
   - **语文**：正文优先宋体（`"Songti SC", "STSong"`），作文区使用标准方格阵（每行 20 格，标注字数刻度如 300/400/500 字）。
   - **数学**：分数/公式排版清晰，几何图形使用内联 SVG 矢量图保证打印锐利，解答题留足 `50mm`～`75mm` 演算空白。
   - **英语**：英文优先无衬线体（`"Helvetica Neue", Arial`），书写题与作文区使用双实线+虚线模拟英文书写行或四线三格。
4. **黑白打印友好**：所有边框、表格线、重点强调在黑白激光打印下均须清晰可辨，避免依赖浅色背景色区分关键信息。
