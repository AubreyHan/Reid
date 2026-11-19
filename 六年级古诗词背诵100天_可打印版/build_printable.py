#!/usr/bin/env python3
"""
小学六年级古诗词背诵 100 天（可打印全套系统）构建与校验脚本

读取 data/vol01.json ~ data/vol10.json 共 100 首诗词数据，
执行严格的数据完整性、审音字形及唯一性校验，
并生成零外部依赖、直接支持 file:// 打开和 A4 精准分页打印的全套 HTML 文件：
  - index.html（百日背诵总导航主页 + 100首实时搜索索引）
  - 第01-10天_山川清音.html ~ 第91-100天_风雅巅峰.html（10 个分册打印版）
  - 全套100天合集打印版.html（全套 100 篇单文件打印版）
  - 百日背诵打卡总表与名句默写卷.html（100 天墙贴打卡表 + 50 题理解性默写自测卷及答案）
"""

from __future__ import annotations

import html
import json
import re
from pathlib import Path
from typing import Any

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"

VOLUMES = [
    {
        "volume": 1,
        "file": "第01-10天_山川清音.html",
        "name": "卷一 · 山川清音",
        "subtitle": "四时风物与写景炼字",
        "days": "Day 01 – 10",
        "desc": "以钱塘风雪、江南烟雨、西湖晓春、建德江月为线，体悟写景诗“景中含情、炼字传神”的审美密码。",
    },
    {
        "volume": 2,
        "file": "第11-20天_田园哲思.html",
        "name": "卷二 · 田园哲思",
        "subtitle": "田园闲适与生活哲思",
        "days": "Day 11 – 20",
        "desc": "走进孟浩然、陶渊明、辛弃疾与朱熹笔下的村居野趣，从朴素生活里品读豁达人生与哲理意趣。",
    },
    {
        "volume": 3,
        "file": "第21-30天_托物言志.html",
        "name": "卷三 · 托物言志",
        "subtitle": "托物言志与风骨铮铮",
        "days": "Day 21 – 30",
        "desc": "借骏马、石灰、青竹、寒梅、秋菊、高蝉写人格风骨，是六年级“以物喻人”立意与作文素材的黄金库。",
    },
    {
        "volume": 4,
        "file": "第31-40天_送别知己.html",
        "name": "卷四 · 送别知己",
        "subtitle": "送别情深与天涯知己",
        "days": "Day 31 – 40",
        "desc": "从阳关折柳到海内存知己、千里共婵娟，感受古人重情守诺、豁达劝慰与跨越山海的深厚情谊。",
    },
    {
        "volume": 5,
        "file": "第41-50天_边塞家国.html",
        "name": "卷五 · 边塞家国",
        "subtitle": "边塞烽火与家国壮志",
        "days": "Day 41 – 50",
        "desc": "大漠孤烟、铁马冰河、飞雪千树、八百里麾下炙，培养孩子胸怀天下的壮阔格局与英雄气概。",
    },
    {
        "volume": 6,
        "file": "第51-60天_岁时乡愁.html",
        "name": "卷六 · 岁时乡愁",
        "subtitle": "羁旅乡愁与节俗雅韵",
        "days": "Day 51 – 60",
        "desc": "寒食、七夕、中秋、元夕与秋暮天涯，紧扣统编六年级传统节日与羁旅思乡主题，文化底蕴拉满。",
    },
    {
        "volume": 7,
        "file": "第61-70天_登临怀古.html",
        "name": "卷七 · 登临怀古",
        "subtitle": "登临怀古与沧桑兴替",
        "days": "Day 61 – 70",
        "desc": "登泰山、望飞来峰、临潼关古道、吊赤壁秦淮，学会在历史沧桑与天地苍茫中思考人生志向。",
    },
    {
        "volume": 8,
        "file": "第71-80天_逆境昂扬.html",
        "name": "卷八 · 逆境昂扬",
        "subtitle": "逆境突围与生命昂扬",
        "days": "Day 71 – 80",
        "desc": "病树前头万木春、长风破浪济沧海、化作春泥更护花，用千古强音锻造面对挫折的坚韧心志。",
    },
    {
        "volume": 9,
        "file": "第81-90天_唐宋风华.html",
        "name": "卷九 · 唐宋风华",
        "subtitle": "唐宋风华与婉约豪放",
        "days": "Day 81 – 90",
        "desc": "纵览诗圣杜甫的悲喜春秋与唐宋词婉约深情、九万里风鹏豪情，拓展文学审美的深度与广度。",
    },
    {
        "volume": 10,
        "file": "第91-100天_风雅巅峰.html",
        "name": "卷十 · 风雅巅峰",
        "subtitle": "风雅源流与意境巅峰",
        "days": "Day 91 – 100",
        "desc": "溯源《诗经》风雅重章叠咏，收官李煜、辛弃疾与《沁园春·雪》的巅峰气象，圆满完成百日积淀。",
    },
]

REQUIRED_FIELDS = [
    "day",
    "volume",
    "volume_file",
    "volume_name",
    "volume_subtitle",
    "category",
    "genre",
    "title",
    "dynasty",
    "author",
    "preface",
    "lines",
    "pinyin_notes",
    "word_notes",
    "translation",
    "analysis",
    "golden_quote",
    "application_tip",
    "dictation_prompt",
    "dictation_answer",
]

VALID_CATEGORIES = {"六年级核心", "高段核心", "初中衔接", "课外拓展"}


def esc(text: Any) -> str:
    return html.escape(str(text), quote=True)


def load_and_validate() -> list[dict[str, Any]]:
    all_poems: list[dict[str, Any]] = []
    vol_map = {v["volume"]: v for v in VOLUMES}

    for vol_idx in range(1, 11):
        path = DATA_DIR / f"vol{vol_idx:02d}.json"
        if not path.exists():
            raise FileNotFoundError(f"缺少数据文件: {path}")
        with path.open("r", encoding="utf-8") as f:
            items = json.load(f)
        if not isinstance(items, list) or len(items) != 10:
            raise ValueError(f"{path.name} 必须包含恰好 10 条数据，实际为 {len(items) if isinstance(items, list) else type(items)}")
        for item in items:
            for field in REQUIRED_FIELDS:
                if field not in item:
                    raise ValueError(f"{path.name} Day {item.get('day')} 缺少字段: {field}")
                if field != "preface":
                    val = item[field]
                    if val is None or (isinstance(val, str) and not val.strip()) or (isinstance(val, list) and len(val) == 0):
                        raise ValueError(f"{path.name} Day {item.get('day')} 字段 {field} 为空")
            if item["volume"] != vol_idx:
                raise ValueError(f"{path.name} Day {item['day']} volume={item['volume']} 与文件卷号 {vol_idx} 不符")
            if item["volume_file"] != vol_map[vol_idx]["file"]:
                raise ValueError(f"{path.name} Day {item['day']} volume_file={item['volume_file']} 应为 {vol_map[vol_idx]['file']}")
            if item["category"] not in VALID_CATEGORIES:
                raise ValueError(f"{path.name} Day {item['day']} 非法分类: {item['category']}")
            if not isinstance(item["lines"], list) or any(not str(line).strip() for line in item["lines"]):
                raise ValueError(f"{path.name} Day {item['day']} lines 格式无效")
            # 检查是否存在 TODO 或省略号占位
            blob = json.dumps(item, ensure_ascii=False)
            if "TODO" in blob or "待补充" in blob or "……" in item["translation"] or "..." in item["translation"]:
                raise ValueError(f"{path.name} Day {item['day']} 存在疑似占位或省略号")
            all_poems.append(item)

    all_poems.sort(key=lambda x: x["day"])
    days = [p["day"] for p in all_poems]
    if days != list(range(1, 101)):
        raise ValueError(f"Day 编号未覆盖 1..100：{days}")

    titles = [p["title"] for p in all_poems]
    if len(set(titles)) != 100:
        dups = [t for t in titles if titles.count(t) > 1]
        raise ValueError(f"篇名存在重复（去重后 {len(set(titles))} 篇）：{set(dups)}")

    # 统编版关键易错点硬校验
    day_map = {p["day"]: p for p in all_poems}
    assert "浑不怕" in "".join(day_map[22]["lines"]), "Day 22《石灰吟》必须为‘粉骨碎身浑不怕’"
    assert "亡赖" in "".join(day_map[17]["lines"]), "Day 17《清平乐·村居》必须为‘亡赖’"
    assert "政入" in "".join(day_map[19]["lines"]), "Day 19《过松源晨炊漆公店》必须为‘政入’"
    assert "都寂" in "".join(day_map[85]["lines"]), "Day 85《题破山寺后禅院》必须为‘万籁此都寂’"
    assert "蜡象" in "".join(day_map[100]["lines"]), "Day 100《沁园春·雪》必须为‘原驰蜡象’"

    return all_poems


def format_tagged_blocks(text: str) -> str:
    """将含【标签】的段落文本格式化为带小徽章/粗体引导的结构化 HTML。"""
    escaped = esc(text.strip())
    # 在第二个及之后的【xxx】前插入换行分隔（如【意境赏析】【写作运用】）
    escaped = re.sub(r"(?<!^)(【[^】]+】)", r"<br>\1", escaped)
    escaped = re.sub(r"(【[^】]+】)", r'<strong class="inline-tag">\1</strong>', escaped)
    return escaped


def category_badge_class(category: str) -> str:
    mapping = {
        "六年级核心": "cat-core",
        "高段核心": "cat-upper",
        "初中衔接": "cat-junior",
        "课外拓展": "cat-extra",
    }
    return mapping.get(category, "cat-core")


def sheet_length_class(poem: dict[str, Any]) -> str:
    lines = poem["lines"]
    total_chars = sum(len(x) for x in lines) + len(poem.get("preface", ""))
    detail_chars = (
        len(poem["word_notes"])
        + len(poem["translation"])
        + len(poem["analysis"])
        + len(poem["application_tip"])
    )
    if len(lines) >= 8 or total_chars >= 115 or detail_chars >= 520:
        return "poem-sheet--xlong"
    if len(lines) >= 6 or total_chars >= 76 or detail_chars >= 440:
        return "poem-sheet--long"
    return ""


def render_poem_sheet(poem: dict[str, Any]) -> str:
    day = poem["day"]
    cat_cls = category_badge_class(poem["category"])
    len_cls = sheet_length_class(poem)
    lines_html = "\n          ".join(f'<div class="poem-line">{esc(line)}</div>' for line in poem["lines"])
    preface_html = (
        f'<div class="poem-preface">〔序〕{esc(poem["preface"])}</div>'
        if poem.get("preface", "").strip()
        else ""
    )
    author_line = f'〔{esc(poem["dynasty"])}〕{esc(poem["author"])}'
    analysis_html = format_tagged_blocks(poem["analysis"])
    tip_html = format_tagged_blocks(poem["application_tip"])

    return f"""
<article class="poem-sheet {len_cls}" id="day-{day}" data-day="{day}" data-volume="{poem["volume"]}">
  <!-- 顶部页眉 -->
  <header class="sheet-header">
    <div class="header-left">
      <span class="day-pill">第 {day:02d} 天 / 100</span>
      <span class="vol-label">{esc(poem["volume_name"])}</span>
    </div>
    <div class="header-right">
      <span class="genre-badge">{esc(poem["genre"])}</span>
      <span class="cat-badge {cat_cls}">{esc(poem["category"])}</span>
      <div class="compact-mini-check" aria-hidden="true">
        <span>□读</span><span>□解</span><span>□背</span><span>□默</span>
      </div>
    </div>
  </header>

  <!-- 主体内容区（精讲模式纵向流动；省纸双拼模式自动转为左右双栏） -->
  <div class="sheet-body">
    <!-- 左/上核心原文区 -->
    <section class="poem-core-panel">
      <div class="poem-title-block">
        <h2 class="poem-title">{esc(poem["title"])}</h2>
        <div class="poem-author">{author_line}</div>
      </div>
      {preface_html}
      <div class="poem-verses">
          {lines_html}
      </div>
      <div class="notes-card">
        <div class="note-row"><span class="note-label">字音点拨</span><span class="note-text">{esc(poem["pinyin_notes"])}</span></div>
        <div class="note-row"><span class="note-label">重点字词</span><span class="note-text">{esc(poem["word_notes"])}</span></div>
      </div>
    </section>

    <!-- 右/下深度讲解区 -->
    <section class="poem-study-panel">
      <div class="study-box translation-box">
        <div class="box-title"><span class="box-dot"></span>白话译文 · 画面还原</div>
        <div class="box-content">{esc(poem["translation"])}</div>
      </div>

      <div class="study-box analysis-box">
        <div class="box-title"><span class="box-dot"></span>内容精讲与赏析</div>
        <div class="box-content">{analysis_html}</div>
      </div>

      <div class="study-grid-bottom">
        <div class="study-box quote-box">
          <div class="box-title"><span class="box-dot"></span>千古名句点睛</div>
          <div class="quote-text">“{esc(poem["golden_quote"])}”</div>
        </div>
        <div class="study-box tip-box">
          <div class="box-title"><span class="box-dot"></span>背诵抓手与写作运用</div>
          <div class="box-content">{tip_html}</div>
        </div>
      </div>
    </section>
  </div>

  <!-- 理解性默写微测（可通过顶部开关控制，省纸模式默认隐藏） -->
  <section class="dictation-strip">
    <div class="dictation-head">
      <span class="dictation-badge">小升初 · 理解性默写微测</span>
      <span class="dictation-ans-ref">参考答案：{esc(poem["dictation_answer"])}</span>
    </div>
    <div class="dictation-q">{esc(poem["dictation_prompt"])}</div>
  </section>

  <!-- 底部每日四步打卡栏 -->
  <footer class="sheet-footer">
    <div class="check-steps">
      <label class="step-item"><span class="print-box"></span> 朗读三遍（正音停顿）</label>
      <label class="step-item"><span class="print-box"></span> 理解释义（画面复述）</label>
      <label class="step-item"><span class="print-box"></span> 脱口背诵（流利无误）</label>
      <label class="step-item"><span class="print-box"></span> 过关默写（零错别字）</label>
    </div>
    <div class="sign-fields">
      <span>日期：<i class="sign-line"></i></span>
      <span>家长签字：<i class="sign-line"></i></span>
    </div>
  </footer>
</article>
""".strip()


SHARED_SHEET_CSS = r"""
  @page {
    size: A4 portrait;
    margin: 9mm 11mm 9mm 11mm;
  }
  * {
    box-sizing: border-box;
  }
  :root {
    --ink: #1e242b;
    --ink-soft: #4a5562;
    --ink-muted: #6e7781;
    --brand: #1f3a52;
    --accent: #9e2a2b;
    --gold: #8c6218;
    --paper-bg: #f6f4ef;
    --card-bg: #ffffff;
    --soft-tint: #f8f9fb;
    --warm-tint: #fcf9f2;
    --border: #d8dee6;
  }
  body {
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    color: var(--ink);
    background: var(--paper-bg);
    margin: 0;
    padding: 18px 14px 40px 14px;
    font-size: 13px;
    line-height: 1.5;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }

  /* 顶部控制栏（不打印） */
  .no-print-bar {
    max-width: 210mm;
    margin: 0 auto 16px auto;
    background: #fff;
    border: 1px solid #d0d7de;
    border-radius: 10px;
    padding: 12px 16px;
    box-shadow: 0 3px 12px rgba(24, 39, 75, 0.06);
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
    position: sticky;
    top: 10px;
    z-index: 100;
  }
  .bar-title-group {
    display: flex;
    flex-direction: column;
    gap: 2px;
  }
  .bar-title {
    font-size: 15px;
    font-weight: 700;
    color: var(--brand);
  }
  .bar-subtitle {
    font-size: 12px;
    color: var(--ink-muted);
  }
  .bar-controls {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 8px;
  }
  .btn {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 12.5px;
    font-weight: 600;
    cursor: pointer;
    text-decoration: none;
    border: 1px solid #d0d7de;
    background: #fff;
    color: var(--ink);
    transition: all 0.15s ease;
  }
  .btn:hover {
    background: #f3f6f9;
    border-color: #9aa7b4;
  }
  .btn.active {
    background: var(--brand);
    color: #fff;
    border-color: var(--brand);
  }
  .btn-print {
    background: var(--accent);
    color: #fff;
    border-color: var(--accent);
    padding: 6px 15px;
  }
  .btn-print:hover {
    background: #7f2021;
    border-color: #7f2021;
  }
  .day-select {
    padding: 5px 10px;
    border-radius: 6px;
    border: 1px solid #d0d7de;
    font-size: 12.5px;
    color: var(--ink);
    background: #fff;
  }
  .toggle-check {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 12px;
    color: var(--ink-soft);
    cursor: pointer;
    user-select: none;
    padding: 4px 8px;
    border: 1px solid #e2e7ed;
    border-radius: 6px;
    background: #fafbfc;
  }

  /* 印刷卡片：屏幕端 A4 纸张模拟 */
  .sheets-wrap {
    max-width: 210mm;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 18px;
  }
  .poem-sheet {
    width: 100%;
    background: var(--card-bg);
    border: 1px solid #cfd6df;
    border-radius: 6px;
    box-shadow: 0 4px 14px rgba(20, 30, 45, 0.07);
    padding: 10mm 11mm 8mm 11mm;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    gap: 10px;
    min-height: 268mm;
  }
  .poem-sheet.hidden-by-filter {
    display: none !important;
  }

  /* 页眉 */
  .sheet-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 2px solid var(--brand);
    padding-bottom: 6px;
  }
  .header-left, .header-right {
    display: flex;
    align-items: center;
    gap: 8px;
  }
  .day-pill {
    background: var(--brand);
    color: #fff;
    font-size: 12px;
    font-weight: 700;
    padding: 2px 10px;
    border-radius: 4px;
    letter-spacing: 0.5px;
  }
  .vol-label {
    font-size: 12.5px;
    font-weight: 600;
    color: var(--ink-soft);
  }
  .genre-badge {
    font-size: 11.5px;
    padding: 1.5px 8px;
    border-radius: 4px;
    background: #f0f3f7;
    color: var(--ink-soft);
    border: 1px solid #d5dce4;
  }
  .cat-badge {
    font-size: 11.5px;
    font-weight: 600;
    padding: 1.5px 8px;
    border-radius: 4px;
  }
  .cat-core { background: #e8f3ee; color: #166534; border: 1px solid #b7dfc9; }
  .cat-upper { background: #e6f2fa; color: #0c548a; border: 1px solid #b8daf2; }
  .cat-junior { background: #fdf3e1; color: #92400e; border: 1px solid #f2d59c; }
  .cat-extra { background: #f4effa; color: #6b21a8; border: 1px solid #d8c2f0; }

  .compact-mini-check {
    display: none;
    font-size: 10px;
    color: var(--ink-soft);
    gap: 6px;
    margin-left: 4px;
  }

  /* 主体 */
  .sheet-body {
    display: flex;
    flex-direction: column;
    gap: 10px;
    flex: 1 1 auto;
  }

  /* 原文核心区 */
  .poem-core-panel {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .poem-title-block {
    text-align: center;
    padding-top: 2px;
  }
  .poem-title {
    margin: 0;
    font-family: "Songti SC", "STSong", "Noto Serif SC", "SimSun", serif;
    font-size: 24px;
    font-weight: 700;
    color: #111827;
    letter-spacing: 1.5px;
  }
  .poem-author {
    margin-top: 4px;
    font-family: "Songti SC", "STSong", "KaiTi", serif;
    font-size: 14px;
    color: var(--accent);
    font-weight: 600;
    letter-spacing: 1px;
  }
  .poem-preface {
    text-align: center;
    font-size: 12px;
    color: var(--ink-soft);
    font-style: italic;
    margin: -2px auto 0 auto;
    max-width: 92%;
  }
  .poem-verses {
    background: var(--warm-tint);
    border: 1px solid #e6decb;
    border-left: 4px solid var(--accent);
    border-radius: 6px;
    padding: 12px 16px;
    text-align: center;
    font-family: "Songti SC", "STSong", "STKaiti", "Kaiti SC", serif;
    font-size: 19px;
    line-height: 1.85;
    color: #14171a;
    letter-spacing: 1px;
  }
  .poem-line {
    white-space: normal;
  }

  /* 字音字词条 */
  .notes-card {
    background: #f7f9fb;
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 8px 12px;
    display: flex;
    flex-direction: column;
    gap: 4px;
    font-size: 12.2px;
    line-height: 1.55;
  }
  .note-row {
    display: flex;
    align-items: baseline;
    gap: 8px;
  }
  .note-label {
    flex-shrink: 0;
    font-weight: 700;
    color: var(--brand);
    background: #e6eef5;
    padding: 1px 6px;
    border-radius: 3px;
    font-size: 11px;
  }
  .note-text {
    color: var(--ink);
  }

  /* 讲解各卡片 */
  .poem-study-panel {
    display: flex;
    flex-direction: column;
    gap: 8px;
  }
  .study-box {
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 8px 12px;
    background: #fff;
  }
  .box-title {
    font-size: 12.5px;
    font-weight: 700;
    color: var(--brand);
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    gap: 6px;
  }
  .box-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: var(--accent);
    display: inline-block;
  }
  .box-content {
    font-size: 12.6px;
    line-height: 1.62;
    color: #24292f;
    text-align: justify;
  }
  .inline-tag {
    color: var(--accent);
    font-weight: 700;
  }
  .study-grid-bottom {
    display: grid;
    grid-template-columns: 36% 1fr;
    gap: 8px;
  }
  .quote-box {
    background: #fdfaf3;
    border-color: #e6d8b5;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  .quote-text {
    font-family: "Songti SC", "STSong", "KaiTi", serif;
    font-size: 14.5px;
    font-weight: 700;
    color: var(--accent);
    line-height: 1.55;
    text-align: center;
    padding: 2px 0;
  }
  .tip-box {
    background: #f8fafc;
  }

  /* 理解性默写条 */
  .dictation-strip {
    border: 1px dashed #8b9bb0;
    border-radius: 6px;
    padding: 7px 12px;
    background: #fafbfd;
  }
  body.hide-dictation .dictation-strip {
    display: none !important;
  }
  .dictation-head {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 3px;
  }
  .dictation-badge {
    font-size: 11px;
    font-weight: 700;
    color: var(--brand);
  }
  .dictation-ans-ref {
    font-size: 10.5px;
    color: #8c959f;
  }
  .dictation-q {
    font-size: 12.2px;
    color: #1f2328;
    line-height: 1.55;
  }

  /* 底部打卡签章 */
  .sheet-footer {
    border-top: 1.5px solid #c9d2dc;
    padding-top: 7px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 11.5px;
    color: var(--ink-soft);
    gap: 8px;
  }
  .check-steps {
    display: flex;
    flex-wrap: wrap;
    gap: 11px;
  }
  .step-item {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    cursor: pointer;
  }
  .print-box {
    display: inline-block;
    width: 11px;
    height: 11px;
    border: 1.3px solid var(--brand);
    border-radius: 2px;
    background: #fff;
  }
  .step-item.checked .print-box {
    background: var(--brand);
    box-shadow: inset 0 0 0 2px #fff;
  }
  .sign-fields {
    display: flex;
    gap: 10px;
    white-space: nowrap;
  }
  .sign-line {
    display: inline-block;
    width: 58px;
    border-bottom: 1px solid #6e7781;
    height: 12px;
  }

  /* 长诗微调（保证单页 A4 绝对不溢出） */
  .poem-sheet--long {
    gap: 7px;
    padding: 8mm 10mm 7mm 10mm;
  }
  .poem-sheet--long .poem-title { font-size: 21px; }
  .poem-sheet--long .poem-verses {
    font-size: 16.5px;
    line-height: 1.62;
    padding: 9px 12px;
  }
  .poem-sheet--long .notes-card { padding: 6px 10px; font-size: 11.6px; }
  .poem-sheet--long .study-box { padding: 6px 10px; }
  .poem-sheet--long .box-content { font-size: 12px; line-height: 1.54; }
  .poem-sheet--long .dictation-strip { padding: 5px 10px; }

  .poem-sheet--xlong {
    gap: 5px;
    padding: 6.5mm 10mm 6mm 10mm;
  }
  .poem-sheet--xlong .poem-title { font-size: 19.5px; }
  .poem-sheet--xlong .poem-author { font-size: 13px; margin-top: 2px; }
  .poem-sheet--xlong .poem-verses {
    font-size: 15px;
    line-height: 1.5;
    padding: 7px 10px;
  }
  .poem-sheet--xlong .notes-card { padding: 5px 10px; font-size: 11.2px; line-height: 1.45; }
  .poem-sheet--xlong .study-box { padding: 5px 10px; }
  .poem-sheet--xlong .box-title { font-size: 11.8px; margin-bottom: 2px; }
  .poem-sheet--xlong .box-content { font-size: 11.5px; line-height: 1.48; }
  .poem-sheet--xlong .quote-text { font-size: 13px; }
  .poem-sheet--xlong .dictation-strip { padding: 4px 10px; }
  .poem-sheet--xlong .dictation-q { font-size: 11.5px; }
  .poem-sheet--xlong .sheet-footer { padding-top: 5px; font-size: 11px; }

  /* =========================================================
     省纸双拼版（1 页 A4 = 2 天，左右双栏卡片）
     ========================================================= */
  body.mode-compact .sheets-wrap {
    gap: 10px;
  }
  body.mode-compact .poem-sheet {
    min-height: 128mm;
    padding: 4.5mm 6mm 4.5mm 6mm;
    gap: 6px;
    border: 1px solid #b9c3cf;
  }
  body.mode-compact .sheet-header {
    padding-bottom: 4px;
    border-bottom-width: 1.5px;
  }
  body.mode-compact .day-pill { font-size: 11px; padding: 1px 7px; }
  body.mode-compact .vol-label { font-size: 11px; }
  body.mode-compact .genre-badge,
  body.mode-compact .cat-badge { font-size: 10.5px; padding: 1px 6px; }
  body.mode-compact .compact-mini-check { display: inline-flex; }
  body.mode-compact .sheet-footer { display: none; }

  body.mode-compact .sheet-body {
    display: grid;
    grid-template-columns: 39% 1fr;
    gap: 8px;
    align-items: stretch;
  }
  body.mode-compact .poem-core-panel {
    gap: 5px;
    justify-content: space-between;
  }
  body.mode-compact .poem-title-block { padding-top: 0; }
  body.mode-compact .poem-title { font-size: 16.5px; letter-spacing: 0.5px; }
  body.mode-compact .poem-author { font-size: 11.5px; margin-top: 1px; }
  body.mode-compact .poem-preface { font-size: 10.2px; }
  body.mode-compact .poem-verses {
    font-size: 13px;
    line-height: 1.48;
    padding: 6px 8px;
    letter-spacing: 0.3px;
    flex: 1 1 auto;
    display: flex;
    flex-direction: column;
    justify-content: center;
  }
  body.mode-compact .poem-sheet--xlong .poem-verses {
    font-size: 11.4px;
    line-height: 1.38;
    padding: 5px 6px;
  }
  body.mode-compact .notes-card {
    padding: 4.5px 7px;
    font-size: 10px;
    line-height: 1.38;
    gap: 2px;
  }
  body.mode-compact .note-label { font-size: 9.5px; padding: 0 4px; }

  body.mode-compact .poem-study-panel {
    gap: 5px;
    justify-content: space-between;
  }
  body.mode-compact .study-box {
    padding: 4.5px 8px;
  }
  body.mode-compact .box-title {
    font-size: 10.8px;
    margin-bottom: 2px;
  }
  body.mode-compact .box-content {
    font-size: 10.4px;
    line-height: 1.4;
  }
  body.mode-compact .poem-sheet--xlong .box-content {
    font-size: 9.8px;
    line-height: 1.35;
  }
  body.mode-compact .study-grid-bottom {
    grid-template-columns: 35% 1fr;
    gap: 5px;
  }
  body.mode-compact .quote-text {
    font-size: 11.2px;
    line-height: 1.35;
  }
  body.mode-compact .dictation-strip {
    padding: 3px 8px;
  }
  body.mode-compact .dictation-badge,
  body.mode-compact .dictation-ans-ref { font-size: 9.5px; }
  body.mode-compact .dictation-q { font-size: 10.2px; line-height: 1.35; }

  /* 打印专用样式 */
  @media print {
    body {
      background: #fff !important;
      padding: 0 !important;
      margin: 0 !important;
    }
    .no-print-bar {
      display: none !important;
    }
    .sheets-wrap {
      max-width: 100% !important;
      width: 100% !important;
      gap: 0 !important;
      display: block !important;
    }
    .poem-sheet {
      border: 1px solid #bcc6d1 !important;
      box-shadow: none !important;
      border-radius: 4px !important;
      width: 100% !important;
      min-height: 266mm;
      margin: 0 !important;
      page-break-inside: avoid !important;
      break-inside: avoid !important;
    }
    body.mode-compact .poem-sheet {
      min-height: 129mm !important;
      margin-bottom: 4.5mm !important;
      border: 1px solid #adb7c2 !important;
    }
    body.mode-compact .poem-sheet.compact-row-end {
      margin-bottom: 0 !important;
    }
    .poem-sheet.break-after-page {
      page-break-after: always !important;
      break-after: page !important;
    }
    .poem-sheet:not(.break-after-page) {
      page-break-after: auto !important;
      break-after: auto !important;
    }
    /* 打印时清除屏幕上点击的蓝色勾选，保持干净方框让孩子用笔手写打卡 */
    .step-item.checked .print-box {
      background: #fff !important;
      box-shadow: none !important;
    }
  }
""".strip()


SHARED_SHEET_JS = r"""
(function() {
  const body = document.body;
  const btnStandard = document.getElementById('btn-mode-standard');
  const btnCompact = document.getElementById('btn-mode-compact');
  const daySelect = document.getElementById('day-filter-select');
  const chkDictation = document.getElementById('toggle-dictation');
  const sheets = Array.from(document.querySelectorAll('.poem-sheet'));

  function refreshPagination() {
    const isCompact = body.classList.contains('mode-compact');
    const visibleSheets = sheets.filter(el => !el.classList.contains('hidden-by-filter'));
    sheets.forEach(el => {
      el.classList.remove('break-after-page', 'compact-row-end');
    });

    visibleSheets.forEach((el, idx) => {
      const isLast = idx === visibleSheets.length - 1;
      if (isCompact) {
        if (idx % 2 === 1) {
          el.classList.add('compact-row-end');
          if (!isLast) el.classList.add('break-after-page');
        }
      } else {
        if (!isLast) {
          el.classList.add('break-after-page');
        }
      }
    });
  }

  function setMode(mode) {
    if (mode === 'compact') {
      body.classList.add('mode-compact');
      btnCompact.classList.add('active');
      btnStandard.classList.remove('active');
      if (chkDictation && !chkDictation.dataset.userTouched) {
        chkDictation.checked = false;
        body.classList.add('hide-dictation');
      }
    } else {
      body.classList.remove('mode-compact');
      btnStandard.classList.add('active');
      btnCompact.classList.remove('active');
      if (chkDictation && !chkDictation.dataset.userTouched) {
        chkDictation.checked = true;
        body.classList.remove('hide-dictation');
      }
    }
    refreshPagination();
  }

  function setDayFilter(val) {
    sheets.forEach(el => {
      if (val === 'all' || el.dataset.day === val) {
        el.classList.remove('hidden-by-filter');
      } else {
        el.classList.add('hidden-by-filter');
      }
    });
    refreshPagination();
  }

  if (btnStandard) {
    btnStandard.addEventListener('click', () => setMode('standard'));
  }
  if (btnCompact) {
    btnCompact.addEventListener('click', () => setMode('compact'));
  }
  if (daySelect) {
    daySelect.addEventListener('change', (e) => setDayFilter(e.target.value));
  }
  if (chkDictation) {
    chkDictation.addEventListener('change', (e) => {
      chkDictation.dataset.userTouched = '1';
      if (e.target.checked) {
        body.classList.remove('hide-dictation');
      } else {
        body.classList.add('hide-dictation');
      }
    });
  }

  // 屏幕端点击打卡记录互动
  document.querySelectorAll('.step-item').forEach(label => {
    label.addEventListener('click', () => label.classList.toggle('checked'));
  });

  // 支持 URL 查询参数: ?mode=compact & ?day=5 & ?autoprint=1
  const params = new URLSearchParams(window.location.search);
  const qDay = params.get('day');
  const qMode = params.get('mode');
  if (qDay && daySelect) {
    const optExists = Array.from(daySelect.options).some(o => o.value === qDay);
    if (optExists) {
      daySelect.value = qDay;
      setDayFilter(qDay);
    }
  }
  if (qMode === 'compact') {
    setMode('compact');
  } else {
    setMode('standard');
  }

  if (params.get('autoprint') === '1') {
    setTimeout(() => window.print(), 250);
  }
})();
""".strip()


def build_poem_collection_html(
    page_title: str,
    bar_title: str,
    bar_subtitle: str,
    poems: list[dict[str, Any]],
) -> str:
    options_html = ['<option value="all">全部篇目（共 %d 天）</option>' % len(poems)]
    for p in poems:
        options_html.append(
            f'<option value="{p["day"]}">第 {p["day"]:02d} 天 · 《{esc(p["title"])}》</option>'
        )
    sheets_html = "\n\n".join(render_poem_sheet(p) for p in poems)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{esc(page_title)}</title>
<style>
{SHARED_SHEET_CSS}
</style>
</head>
<body>

<div class="no-print-bar">
  <div class="bar-title-group">
    <div class="bar-title">{esc(bar_title)}</div>
    <div class="bar-subtitle">{esc(bar_subtitle)}</div>
  </div>
  <div class="bar-controls">
    <a href="index.html" class="btn">← 返回总目录</a>
    <a href="百日背诵打卡总表与名句默写卷.html" class="btn">📋 打卡总表</a>
    <button type="button" id="btn-mode-standard" class="btn active" title="每天独占1张A4纸，大字精讲">📄 1页1篇·精讲版</button>
    <button type="button" id="btn-mode-compact" class="btn" title="每页2篇双栏排版，节省一半纸张">📑 1页2篇·省纸版</button>
    <select id="day-filter-select" class="day-select" aria-label="按天筛选">
      {"".join(options_html)}
    </select>
    <label class="toggle-check">
      <input type="checkbox" id="toggle-dictation" checked> 显示默写微测
    </label>
    <button type="button" class="btn btn-print" onclick="window.print()">🖨️ 立即打印</button>
  </div>
</div>

<main class="sheets-wrap">
{sheets_html}
</main>

<script>
{SHARED_SHEET_JS}
</script>
</body>
</html>
"""


TRACKER_QUIZ_CSS = r"""
  .pages-wrap {
    max-width: 210mm;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 18px;
  }
  .a4-page {
    background: #fff;
    border: 1px solid #cfd6df;
    border-radius: 6px;
    padding: 7mm 10mm;
    min-height: 262mm;
    font-size: 12px;
    line-height: 1.45;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    box-shadow: 0 4px 14px rgba(20, 30, 45, 0.07);
    page-break-inside: avoid;
    break-inside: avoid;
    page-break-after: always;
    break-after: page;
  }
  .a4-page.last-page {
    page-break-after: auto;
    break-after: auto;
  }
  .page-head {
    border-bottom: 2px solid #1f3a52;
    padding-bottom: 4px;
    margin-bottom: 5px;
    display: flex;
    justify-content: space-between;
    align-items: flex-end;
    gap: 8px;
  }
  .page-head h2 {
    margin: 0;
    font-size: 16px;
    color: #1f3a52;
  }
  .page-head .sub {
    margin: 2px 0 0 0;
    font-size: 10.5px;
    color: #6e7781;
  }
  .student-meta {
    font-size: 11px;
    color: #4a5562;
    white-space: nowrap;
  }
  .tracker-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 9.3px;
    line-height: 1.16;
  }
  .tracker-table th, .tracker-table td {
    border: 1px solid #d0d7de;
    padding: 1px 4px;
    text-align: left;
    white-space: nowrap;
  }
  .tracker-table th {
    background: #f0f4f8;
    color: #1f3a52;
    font-weight: 700;
    text-align: center;
  }
  .tracker-table tbody tr:nth-child(even) { background: #fafbfc; }
  .col-day { width: 56px; font-weight: 700; color: #1f3a52; text-align: center !important; }
  .col-title { font-weight: 600; }
  .col-author { width: 108px; color: #4a5562; }
  .col-cat { width: 76px; text-align: center !important; }
  .col-chk { width: 38px; text-align: center !important; font-size: 10px; }
  .col-sign { width: 88px; }

  .quiz-list {
    flex: 1 1 auto;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    gap: 3px;
  }
  .quiz-item {
    border-bottom: 1px dashed #d8dee6;
    padding-bottom: 3.5px;
  }
  .quiz-q {
    font-size: 11.2px;
    line-height: 1.36;
    color: #1e242b;
  }
  .q-idx { font-weight: 700; color: #1f3a52; }
  .q-src { font-size: 10px; color: #8c959f; }
  .quiz-write-line {
    margin-top: 8px;
    border-bottom: 1px solid #9aa7b4;
    height: 3px;
  }

  .ans-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    flex: 1 1 auto;
    align-content: start;
  }
  .ans-col {
    border: 1px solid #d8dee6;
    border-radius: 6px;
    padding: 6px 9px;
    background: #fafbfd;
  }
  .ans-col h3 {
    margin: 0 0 5px 0;
    font-size: 12.5px;
    color: #1f3a52;
    border-bottom: 1px solid #d8dee6;
    padding-bottom: 3px;
  }
  .ans-row {
    font-size: 10.8px;
    line-height: 1.4;
    padding: 1.6px 0;
    border-bottom: 1px dashed #e6ebf1;
  }
  .ans-row:last-child { border-bottom: none; }

  .page-foot {
    border-top: 1px solid #d8dee6;
    padding-top: 4px;
    margin-top: 4px;
    font-size: 10px;
    color: #6e7781;
    display: flex;
    justify-content: space-between;
  }

  @media print {
    .pages-wrap { max-width: 100% !important; gap: 0 !important; display: block !important; }
    .a4-page {
      border: none !important;
      box-shadow: none !important;
      padding: 0 !important;
      min-height: 262mm;
      margin: 0 !important;
    }
  }
""".strip()


def render_tracker_pages_html(poems: list[dict[str, Any]], mark_second_last: bool = False) -> str:
    def render_table_rows(subset: list[dict[str, Any]]) -> str:
        rows = []
        for p in subset:
            cat_cls = category_badge_class(p["category"])
            author_disp = f'〔{esc(p["dynasty"])}〕{esc(p["author"])}'
            rows.append(
                f"""<tr>
                  <td class="col-day">Day {p["day"]:02d}</td>
                  <td class="col-title">《{esc(p["title"])}》</td>
                  <td class="col-author">{author_disp}</td>
                  <td class="col-cat"><span class="cat-badge {cat_cls}">{esc(p["category"])}</span></td>
                  <td class="col-chk">□</td>
                  <td class="col-chk">□</td>
                  <td class="col-sign"></td>
                </tr>"""
            )
        return "\n".join(rows)

    second_cls = "a4-page last-page" if mark_second_last else "a4-page"
    return f"""
  <!-- 第 1 页：Day 01-50 打卡表 -->
  <section class="a4-page">
    <div>
      <header class="page-head">
        <div>
          <h2>小学六年级古诗词背诵 100 天 · 进度打卡墙贴表（上篇：Day 01 – 50）</h2>
          <p class="sub">建议贴在书桌前，每天完成“朗读 → 精讲理解 → 脱口背诵 → 零错字默写”后打钩签字</p>
        </div>
        <div class="student-meta">姓名：________ &nbsp; 目标：100 天通关</div>
      </header>
      <table class="tracker-table">
        <thead>
          <tr><th>天数</th><th>诗词篇目</th><th>朝代 · 作者</th><th>板块定位</th><th>背诵</th><th>默写</th><th>日期 / 签字</th></tr>
        </thead>
        <tbody>
          {render_table_rows(poems[:50])}
        </tbody>
      </table>
    </div>
    <footer class="page-foot">
      <span>卷一至卷五（山川 · 田园 · 托物 · 送别 · 边塞）</span>
      <span>第 1 / 2 页（打卡总表）</span>
    </footer>
  </section>

  <!-- 第 2 页：Day 51-100 打卡表 -->
  <section class="{second_cls}">
    <div>
      <header class="page-head">
        <div>
          <h2>小学六年级古诗词背诵 100 天 · 进度打卡墙贴表（下篇：Day 51 – 100）</h2>
          <p class="sub">坚持到第 100 天，你将完整积累 100 篇中华经典诗词与小升初高频名句库</p>
        </div>
        <div class="student-meta">阶段奖励：____________________</div>
      </header>
      <table class="tracker-table">
        <thead>
          <tr><th>天数</th><th>诗词篇目</th><th>朝代 · 作者</th><th>板块定位</th><th>背诵</th><th>默写</th><th>日期 / 签字</th></tr>
        </thead>
        <tbody>
          {render_table_rows(poems[50:])}
        </tbody>
      </table>
    </div>
    <footer class="page-foot">
      <span>卷六至卷十（乡愁 · 怀古 · 昂扬 · 唐宋 · 风雅）</span>
      <span>第 2 / 2 页（打卡总表）</span>
    </footer>
  </section>
""".strip()


def render_quiz_and_answer_pages_html(poems: list[dict[str, Any]]) -> str:
    # 精选 50 道理解性默写题（每 2 天抽 1 道，完整覆盖 1..100 天各主题）
    quiz_poems = [poems[i] for i in range(0, 100, 2)]
    assert len(quiz_poems) == 50

    quiz_pages_html = []
    slices = [
        ("小升初古诗词理解性默写通关卷（一）：第 1 – 13 题", quiz_poems[0:13], 1),
        ("小升初古诗词理解性默写通关卷（一）：第 14 – 25 题", quiz_poems[13:25], 14),
        ("小升初古诗词理解性默写通关卷（二）：第 26 – 38 题", quiz_poems[25:38], 26),
        ("小升初古诗词理解性默写通关卷（二）：第 39 – 50 题", quiz_poems[38:50], 39),
    ]
    for title_str, subset, start_num in slices:
        q_items = []
        for offset, p in enumerate(subset):
            q_num = start_num + offset
            q_items.append(
                f"""<div class="quiz-item">
                  <div class="quiz-q"><span class="q-idx">{q_num:02d}.</span> {esc(p["dictation_prompt"])} <span class="q-src">（Day {p["day"]:02d}）</span></div>
                  <div class="quiz-write-line"></div>
                </div>"""
            )
        quiz_pages_html.append(
            f"""<section class="a4-page">
              <header class="page-head">
                <div>
                  <h2>{esc(title_str)}</h2>
                  <p class="sub">满分 100 分（每题 2 分，共 50 题）· 要求：字迹工整，不错字、不漏字、不添字</p>
                </div>
                <div class="student-meta">姓名：________ &nbsp; 用时：____分 &nbsp; 得分：____</div>
              </header>
              <div class="quiz-list">
                {"".join(q_items)}
              </div>
              <footer class="page-foot">
                <span>小学六年级古诗词背诵 100 天 · 阶段过关检测卷</span>
                <span>请对照本套卷末《参考答案页》批改订正</span>
              </footer>
            </section>"""
        )

    ans_items_left = []
    ans_items_right = []
    for idx, p in enumerate(quiz_poems, start=1):
        row = f'<div class="ans-row"><strong>{idx:02d}.</strong> 《{esc(p["title"])}》：{esc(p["dictation_answer"])}</div>'
        if idx <= 25:
            ans_items_left.append(row)
        else:
            ans_items_right.append(row)

    return f"""
  {"".join(quiz_pages_html)}

  <!-- 第 5 页：50 题参考答案 -->
  <section class="a4-page last-page">
    <div style="display:flex; flex-direction:column; height:100%;">
      <header class="page-head">
        <div>
          <h2>小升初古诗词理解性默写通关卷（50 题）· 参考答案</h2>
          <p class="sub">批改提示：重点核查通假字（见/亡/政/曾）、形近字（汗青/蜡象/喑/摧）及字序（粉骨碎身）</p>
        </div>
        <div class="student-meta">家长批改参考专用</div>
      </header>
      <div class="ans-grid">
        <div class="ans-col">
          <h3>第 01 – 25 题答案</h3>
          {"".join(ans_items_left)}
        </div>
        <div class="ans-col">
          <h3>第 26 – 50 题答案</h3>
          {"".join(ans_items_right)}
        </div>
      </div>
    </div>
    <footer class="page-foot">
      <span>错题请回到对应“第 XX 天”精讲单页重新巩固字词与背景</span>
      <span>全卷完</span>
    </footer>
  </section>
""".strip()


def build_tracker_and_quiz_html(poems: list[dict[str, Any]]) -> str:
    tracker_pages = render_tracker_pages_html(poems, mark_second_last=False)
    quiz_pages = render_quiz_and_answer_pages_html(poems)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>百日背诵打卡总表与理解性默写过关卷（可打印A4版）</title>
<style>
  @page {{
    size: A4 portrait;
    margin: 9mm 11mm 9mm 11mm;
  }}
  * {{ box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    background: #f6f4ef;
    color: #1e242b;
    margin: 0;
    padding: 18px 14px 36px 14px;
    font-size: 12px;
    line-height: 1.45;
    -webkit-print-color-adjust: exact;
    print-color-adjust: exact;
  }}
  .no-print-bar {{
    max-width: 210mm;
    margin: 0 auto 16px auto;
    background: #fff;
    border: 1px solid #d0d7de;
    border-radius: 10px;
    padding: 12px 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
    box-shadow: 0 3px 12px rgba(24, 39, 75, 0.06);
  }}
  .btn {{
    display: inline-flex;
    align-items: center;
    padding: 6px 12px;
    border-radius: 6px;
    font-size: 12.5px;
    font-weight: 600;
    text-decoration: none;
    border: 1px solid #d0d7de;
    background: #fff;
    color: #1e242b;
    cursor: pointer;
  }}
  .btn-print {{ background: #9e2a2b; color: #fff; border-color: #9e2a2b; }}
  .cat-badge {{ font-size: 9px; padding: 0 4px; border-radius: 3px; font-weight: 600; }}
  .cat-core {{ background: #e8f3ee; color: #166534; }}
  .cat-upper {{ background: #e6f2fa; color: #0c548a; }}
  .cat-junior {{ background: #fdf3e1; color: #92400e; }}
  .cat-extra {{ background: #f4effa; color: #6b21a8; }}
  {TRACKER_QUIZ_CSS}
  @media print {{
    body {{ background: #fff !important; padding: 0 !important; }}
    .no-print-bar {{ display: none !important; }}
  }}
</style>
</head>
<body>

<div class="no-print-bar">
  <div>
    <strong style="font-size:15px; color:#1f3a52;">📋 百日背诵墙贴打卡总表 &amp; 小升初 50 题默写通关卷</strong>
    <div style="font-size:12px; color:#6e7781;">第1-2页：100天墙贴打卡表 ｜ 第3-6页：50题理解性默写卷 ｜ 第7页：参考答案</div>
  </div>
  <div style="display:flex; gap:8px;">
    <a href="index.html" class="btn">← 返回总目录</a>
    <a href="全套100天合集打印版.html" class="btn">📚 100天合集</a>
    <button class="btn btn-print" onclick="window.print()">🖨️ 打印打卡表与默写卷 (7页A4)</button>
  </div>
</div>

<main class="pages-wrap">
{tracker_pages}
{quiz_pages}
</main>

</body>
</html>
"""


def build_index_html(poems: list[dict[str, Any]]) -> str:
    vol_cards = []
    for v in VOLUMES:
        v_poems = [p for p in poems if p["volume"] == v["volume"]]
        preview = "、".join(f"《{p['title']}》" for p in v_poems[:4]) + " 等 10 篇"
        vol_cards.append(
            f"""<div class="vol-card">
              <div class="vol-head">
                <div>
                  <span class="vol-days">{esc(v["days"])}</span>
                  <h3>{esc(v["name"])}</h3>
                </div>
                <span class="vol-sub">{esc(v["subtitle"])}</span>
              </div>
              <p class="vol-desc">{esc(v["desc"])}</p>
              <div class="vol-preview">代表篇目：{esc(preview)}</div>
              <div class="vol-actions">
                <a href="{esc(v["file"])}" class="btn btn-primary" target="_blank">📄 精讲打印 (10页)</a>
                <a href="{esc(v["file"])}?mode=compact" class="btn btn-secondary" target="_blank">📑 省纸双拼 (5页)</a>
              </div>
            </div>"""
        )

    cat_counts = {cat: sum(1 for p in poems if p["category"] == cat) for cat in ["六年级核心", "高段核心", "初中衔接", "课外拓展"]}

    table_rows = []
    for p in poems:
        cat_cls = category_badge_class(p["category"])
        search_blob = f"{p['day']} {p['title']} {p['author']} {p['dynasty']} {p['category']} {p['golden_quote']} {p['volume_name']}"
        table_rows.append(
            f"""<tr class="poem-row" data-cat="{esc(p['category'])}" data-search="{esc(search_blob.lower())}">
              <td class="td-day">Day {p["day"]:02d}</td>
              <td class="td-title">《{esc(p["title"])}》</td>
              <td class="td-author">〔{esc(p["dynasty"])}〕{esc(p["author"])}</td>
              <td class="td-genre">{esc(p["genre"])}</td>
              <td class="td-cat"><span class="cat-badge {cat_cls}">{esc(p["category"])}</span></td>
              <td class="td-quote">{esc(p["golden_quote"])}</td>
              <td class="td-link"><a href="{esc(p["volume_file"])}?day={p["day"]}" target="_blank">单页直达 →</a></td>
            </tr>"""
        )

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>小学六年级古诗词背诵 100 天（每日精讲 · A4可打印全套）</title>
<style>
  * {{ box-sizing: border-box; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
    background: #f6f4ef;
    color: #1e242b;
    margin: 0;
    padding: 26px 18px 50px 18px;
    line-height: 1.55;
  }}
  .wrap {{
    max-width: 1040px;
    margin: 0 auto;
  }}
  .hero {{
    background: linear-gradient(135deg, #1f3a52 0%, #2c4e6b 100%);
    color: #fff;
    border-radius: 12px;
    padding: 26px 30px;
    margin-bottom: 22px;
    box-shadow: 0 8px 24px rgba(31, 58, 82, 0.16);
  }}
  .hero h1 {{
    margin: 0 0 8px 0;
    font-family: "Songti SC", "STSong", "Noto Serif SC", serif;
    font-size: 26px;
    letter-spacing: 1px;
  }}
  .hero p {{
    margin: 0 0 14px 0;
    font-size: 14px;
    color: #e2eaf1;
    max-width: 820px;
  }}
  .stats-row {{
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
  }}
  .stat-pill {{
    background: rgba(255, 255, 255, 0.14);
    border: 1px solid rgba(255, 255, 255, 0.25);
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 12.5px;
    color: #fff;
  }}

  /* 快捷打印通道 */
  .quick-bar {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 16px;
    margin-bottom: 24px;
  }}
  .quick-card {{
    background: #fff;
    border: 1px solid #d5dce4;
    border-radius: 10px;
    padding: 18px 22px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 14px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
  }}
  .quick-card h3 {{ margin: 0 0 4px 0; font-size: 16px; color: #1f3a52; }}
  .quick-card p {{ margin: 0; font-size: 12.5px; color: #57606a; }}
  .quick-btns {{ display: flex; flex-direction: column; gap: 6px; flex-shrink: 0; }}

  .section-title {{
    font-size: 18px;
    font-weight: 700;
    color: #1f3a52;
    margin: 26px 0 12px 0;
    padding-left: 10px;
    border-left: 4px solid #9e2a2b;
  }}

  .vol-grid {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 14px;
  }}
  .vol-card {{
    background: #fff;
    border: 1px solid #d5dce4;
    border-radius: 10px;
    padding: 16px 20px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    gap: 8px;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
    transition: transform 0.15s ease, border-color 0.15s ease;
  }}
  .vol-card:hover {{
    border-color: #1f3a52;
    transform: translateY(-2px);
  }}
  .vol-head {{
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 8px;
  }}
  .vol-days {{
    display: inline-block;
    font-size: 11px;
    font-weight: 700;
    color: #9e2a2b;
    background: #fdf2f2;
    padding: 1px 8px;
    border-radius: 4px;
    margin-bottom: 4px;
  }}
  .vol-head h3 {{ margin: 0; font-size: 16px; color: #1e242b; }}
  .vol-sub {{ font-size: 12px; color: #6e7781; font-weight: 500; }}
  .vol-desc {{ margin: 0; font-size: 12.5px; color: #4a5562; }}
  .vol-preview {{ font-size: 11.8px; color: #6e7781; background: #f8f9fb; padding: 5px 8px; border-radius: 5px; }}
  .vol-actions {{ display: flex; gap: 8px; margin-top: 4px; }}

  .btn {{
    display: inline-flex;
    align-items: center;
    justify-content: center;
    padding: 6px 13px;
    border-radius: 6px;
    font-size: 12.5px;
    font-weight: 600;
    text-decoration: none;
    cursor: pointer;
    border: 1px solid transparent;
    white-space: nowrap;
  }}
  .btn-primary {{ background: #1f3a52; color: #fff; }}
  .btn-primary:hover {{ background: #162b3d; }}
  .btn-secondary {{ background: #fff; color: #1f3a52; border-color: #b8c4d0; }}
  .btn-secondary:hover {{ background: #f2f5f8; }}
  .btn-accent {{ background: #9e2a2b; color: #fff; }}
  .btn-accent:hover {{ background: #7f2021; }}

  /* 100 首全篇目检索表 */
  .index-panel {{
    background: #fff;
    border: 1px solid #d5dce4;
    border-radius: 10px;
    padding: 18px 20px;
  }}
  .filter-toolbar {{
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
    margin-bottom: 12px;
  }}
  .search-input {{
    flex: 1 1 260px;
    padding: 7px 12px;
    border: 1px solid #cfd6df;
    border-radius: 6px;
    font-size: 13px;
  }}
  .cat-filters {{
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
  }}
  .filter-btn {{
    padding: 5px 11px;
    border-radius: 16px;
    border: 1px solid #d0d7de;
    background: #f8f9fa;
    color: #4a5562;
    font-size: 12px;
    cursor: pointer;
    font-weight: 600;
  }}
  .filter-btn.active {{
    background: #1f3a52;
    color: #fff;
    border-color: #1f3a52;
  }}
  .poem-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 12.8px;
  }}
  .poem-table th, .poem-table td {{
    border-bottom: 1px solid #eaeef2;
    padding: 8px 8px;
    text-align: left;
  }}
  .poem-table th {{
    background: #f6f8fa;
    color: #4a5562;
    font-weight: 700;
  }}
  .poem-table tbody tr:hover {{ background: #fafbfd; }}
  .td-day {{ font-weight: 700; color: #1f3a52; white-space: nowrap; }}
  .td-title {{ font-weight: 600; color: #111; }}
  .td-author {{ color: #4a5562; white-space: nowrap; }}
  .td-genre {{ color: #6e7781; white-space: nowrap; font-size: 12px; }}
  .td-quote {{ color: #57606a; font-family: "Songti SC", "STSong", serif; }}
  .td-link a {{ color: #9e2a2b; font-weight: 600; text-decoration: none; white-space: nowrap; }}
  .td-link a:hover {{ text-decoration: underline; }}

  .cat-badge {{ font-size: 11px; padding: 1.5px 7px; border-radius: 4px; font-weight: 600; white-space: nowrap; }}
  .cat-core {{ background: #e8f3ee; color: #166534; }}
  .cat-upper {{ background: #e6f2fa; color: #0c548a; }}
  .cat-junior {{ background: #fdf3e1; color: #92400e; }}
  .cat-extra {{ background: #f4effa; color: #6b21a8; }}

  @media (max-width: 780px) {{
    .quick-bar, .vol-grid {{ grid-template-columns: 1fr; }}
    .td-genre, .td-quote {{ display: none; }}
  }}
</style>
</head>
<body>
<div class="wrap">
  <section class="hero">
    <h1>📜 小学六年级古诗词背诵 100 天（每日一讲 · A4可打印全套）</h1>
    <p>专为六年级与小升初备考设计：剔除低幼浅白篇目，精选 100 篇横跨唐诗、宋词、元曲与《诗经》的传世名篇。每天 1 篇，包含<strong>权威原文、字音点拨、重点字词、白话译文、深度赏析、背诵抓手与作文运用、理解性默写微测</strong>。</p>
    <div class="stats-row">
      <span class="stat-pill">📚 共 100 天 · 10 大主题分卷</span>
      <span class="stat-pill">🟢 六年级核心 {cat_counts["六年级核心"]} 篇</span>
      <span class="stat-pill">🔵 高段核心 {cat_counts["高段核心"]} 篇</span>
      <span class="stat-pill">🟠 小升初/初中衔接 {cat_counts["初中衔接"]} 篇</span>
      <span class="stat-pill">🟣 课外名篇拓展 {cat_counts["课外拓展"]} 篇</span>
      <span class="stat-pill">🖨️ 支持 1页1篇精讲 / 1页2篇省纸双拼</span>
    </div>
  </section>

  <section class="quick-bar">
    <div class="quick-card">
      <div>
        <h3>📖 全套 100 天完整合集（一次打印全部）</h3>
        <p>适合直接打印装订成册！默认 100 页 A4 精讲版；切换“省纸双拼模式”仅需 50 张纸。</p>
      </div>
      <div class="quick-btns">
        <a href="全套100天合集打印版.html" class="btn btn-accent" target="_blank">📄 打开合集 (100页)</a>
        <a href="全套100天合集打印版.html?mode=compact" class="btn btn-secondary" target="_blank">📑 省纸合集 (50页)</a>
      </div>
    </div>
    <div class="quick-card">
      <div>
        <h3>📋 百日打卡墙贴总表 &amp; 50 题默写卷</h3>
        <p>含 2 页书桌墙贴打卡总表 + 50 道小升初高频理解性默写通关测验 + 独立参考答案。</p>
      </div>
      <div class="quick-btns">
        <a href="百日背诵打卡总表与名句默写卷.html" class="btn btn-primary" target="_blank">🖨️ 打开打卡表与测试卷</a>
      </div>
    </div>
  </section>

  <h2 class="section-title">分卷按旬打印（每 10 天一卷，推荐按旬打印装订）</h2>
  <section class="vol-grid">
    {"".join(vol_cards)}
  </section>

  <h2 class="section-title">100 天完整篇目目录与单篇直达（支持即时搜索）</h2>
  <section class="index-panel">
    <div class="filter-toolbar">
      <input type="text" id="poem-search" class="search-input" placeholder="输入诗名、作者、名句或天数搜索（如：苏轼 / 辛弃疾 / 托物 / 明月）...">
      <div class="cat-filters">
        <button type="button" class="filter-btn active" data-cat="ALL">全部 (100)</button>
        <button type="button" class="filter-btn" data-cat="六年级核心">六年级核心 ({cat_counts["六年级核心"]})</button>
        <button type="button" class="filter-btn" data-cat="高段核心">高段核心 ({cat_counts["高段核心"]})</button>
        <button type="button" class="filter-btn" data-cat="初中衔接">初中衔接 ({cat_counts["初中衔接"]})</button>
        <button type="button" class="filter-btn" data-cat="课外拓展">课外拓展 ({cat_counts["课外拓展"]})</button>
      </div>
    </div>
    <table class="poem-table">
      <thead>
        <tr>
          <th>天数</th>
          <th>诗词题目</th>
          <th>朝代 · 作者</th>
          <th>体裁</th>
          <th>定位</th>
          <th>核心千古名句</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        {"".join(table_rows)}
      </tbody>
    </table>
  </section>
</div>

<script>
(function() {{
  const searchInput = document.getElementById('poem-search');
  const filterBtns = document.querySelectorAll('.filter-btn');
  const rows = document.querySelectorAll('.poem-row');
  let activeCat = 'ALL';

  function applyFilter() {{
    const kw = (searchInput.value || '').trim().toLowerCase();
    rows.forEach(tr => {{
      const matchCat = activeCat === 'ALL' || tr.dataset.cat === activeCat;
      const matchKw = !kw || tr.dataset.search.includes(kw);
      tr.style.display = (matchCat && matchKw) ? '' : 'none';
    }});
  }}

  searchInput.addEventListener('input', applyFilter);
  filterBtns.forEach(btn => {{
    btn.addEventListener('click', () => {{
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeCat = btn.dataset.cat;
      applyFilter();
    }});
  }});
}})();
</script>
</body>
</html>
"""


PORTABLE_EXTRA_CSS = r"""
  .portable-bar {
    flex-direction: column;
    align-items: stretch;
    gap: 8px;
  }
  .portable-top-row {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
  }
  .tab-nav {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    align-items: center;
  }
  .tab-btn {
    padding: 6px 12px;
    border-radius: 6px;
    border: 1px solid #d0d7de;
    background: #f6f8fa;
    color: #24292f;
    font-size: 12.5px;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.15s ease;
  }
  .tab-btn:hover { background: #eaeef2; }
  .tab-btn.active {
    background: #1f3a52;
    color: #fff;
    border-color: #1f3a52;
  }
  .poems-subbar {
    border-top: 1px dashed #d8dee6;
    padding-top: 8px;
    display: flex;
    flex-direction: column;
    gap: 7px;
  }
  .poems-subbar.subbar-hidden { display: none; }
  .vol-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 5px;
  }
  .vol-pill-btn {
    padding: 3.5px 9px;
    border-radius: 14px;
    border: 1px solid #cfd6df;
    background: #fff;
    color: #4a5562;
    font-size: 11.5px;
    font-weight: 600;
    cursor: pointer;
  }
  .vol-pill-btn:hover { border-color: #1f3a52; color: #1f3a52; }
  .vol-pill-btn.active {
    background: #9e2a2b;
    color: #fff;
    border-color: #9e2a2b;
  }
  .poems-action-row {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
  }
  .nav-pager {
    display: flex;
    flex-wrap: wrap;
    align-items: center;
    gap: 6px;
  }
  .view-panel.view-hidden { display: none !important; }

  /* 目录检索视图（单文件内置） */
  .idx-wrap {
    max-width: 210mm;
    margin: 0 auto;
    display: flex;
    flex-direction: column;
    gap: 16px;
  }
  .idx-hero {
    background: linear-gradient(135deg, #1f3a52 0%, #2c4e6b 100%);
    color: #fff;
    border-radius: 10px;
    padding: 20px 24px;
  }
  .idx-hero h1 {
    margin: 0 0 6px 0;
    font-family: "Songti SC", "STSong", "Noto Serif SC", serif;
    font-size: 22px;
  }
  .idx-hero p {
    margin: 0 0 10px 0;
    font-size: 13px;
    color: #e2eaf1;
  }
  .stats-row { display: flex; flex-wrap: wrap; gap: 8px; }
  .stat-pill {
    background: rgba(255, 255, 255, 0.14);
    border: 1px solid rgba(255, 255, 255, 0.25);
    padding: 3px 10px;
    border-radius: 16px;
    font-size: 12px;
    color: #fff;
  }
  .idx-vol-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
  }
  .idx-vol-card {
    background: #fff;
    border: 1px solid #d5dce4;
    border-radius: 8px;
    padding: 14px 16px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    gap: 6px;
  }
  .idx-vol-head {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    gap: 6px;
  }
  .idx-vol-days {
    display: inline-block;
    font-size: 11px;
    font-weight: 700;
    color: #9e2a2b;
    background: #fdf2f2;
    padding: 1px 7px;
    border-radius: 4px;
    margin-bottom: 3px;
  }
  .idx-vol-head h3 { margin: 0; font-size: 15px; color: #1e242b; }
  .idx-vol-sub { font-size: 11.5px; color: #6e7781; }
  .idx-vol-desc { margin: 0; font-size: 12px; color: #4a5562; }
  .idx-vol-preview {
    font-size: 11.2px;
    color: #6e7781;
    background: #f8f9fb;
    padding: 4px 8px;
    border-radius: 4px;
  }
  .idx-panel {
    background: #fff;
    border: 1px solid #d5dce4;
    border-radius: 8px;
    padding: 16px;
  }
  .filter-toolbar {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
    margin-bottom: 10px;
  }
  .search-input {
    flex: 1 1 240px;
    padding: 7px 12px;
    border: 1px solid #cfd6df;
    border-radius: 6px;
    font-size: 13px;
  }
  .cat-filters { display: flex; flex-wrap: wrap; gap: 6px; }
  .filter-btn {
    padding: 4px 10px;
    border-radius: 14px;
    border: 1px solid #d0d7de;
    background: #f8f9fa;
    color: #4a5562;
    font-size: 11.5px;
    cursor: pointer;
    font-weight: 600;
  }
  .filter-btn.active { background: #1f3a52; color: #fff; border-color: #1f3a52; }
  .poem-table { width: 100%; border-collapse: collapse; font-size: 12.2px; }
  .poem-table th, .poem-table td {
    border-bottom: 1px solid #eaeef2;
    padding: 7px 6px;
    text-align: left;
  }
  .poem-table th { background: #f6f8fa; color: #4a5562; font-weight: 700; }
  .poem-table tbody tr:hover { background: #fafbfd; }
  .td-day { font-weight: 700; color: #1f3a52; white-space: nowrap; }
  .td-title { font-weight: 600; color: #111; }
  .td-author { color: #4a5562; white-space: nowrap; }
  .td-genre { color: #6e7781; white-space: nowrap; font-size: 11.5px; }
  .td-quote { color: #57606a; font-family: "Songti SC", "STSong", serif; }
  .td-done { text-align: center !important; width: 46px; }
  .jump-btn {
    background: transparent;
    border: 1px solid #9e2a2b;
    color: #9e2a2b;
    border-radius: 4px;
    padding: 2px 8px;
    font-size: 11.5px;
    font-weight: 600;
    cursor: pointer;
    white-space: nowrap;
  }
  .jump-btn:hover { background: #9e2a2b; color: #fff; }
  .done-chk { width: 15px; height: 15px; cursor: pointer; accent-color: #166534; }
  .portable-foot-note {
    max-width: 210mm;
    margin: 20px auto 0 auto;
    text-align: center;
    font-size: 12px;
    color: #6e7781;
  }

  @media screen and (max-width: 768px) {
    body { padding: 10px 8px 30px 8px; }
    .no-print-bar { position: static; padding: 10px 12px; }
    .poem-sheet { min-height: auto; padding: 14px 12px; }
    .poem-title { font-size: 20px; }
    .poem-verses { font-size: 16.5px; line-height: 1.7; padding: 10px; }
    .study-grid-bottom, .idx-vol-grid, .ans-grid { grid-template-columns: 1fr; }
    .td-genre, .td-quote { display: none; }
    .a4-page { min-height: auto; padding: 12px 10px; }
    .tracker-table { font-size: 10.5px; }
    .tracker-table th, .tracker-table td { white-space: normal; padding: 3px 4px; }
  }
  @media print {
    .no-print { display: none !important; }
    .view-panel.view-hidden { display: none !important; }
  }
""".strip()


PORTABLE_JS = r"""
(function() {
  const body = document.body;
  const tabBtns = Array.from(document.querySelectorAll('.tab-btn'));
  const viewPanels = {
    poems: document.getElementById('view-poems'),
    index: document.getElementById('view-index'),
    tracker: document.getElementById('view-tracker'),
    quiz: document.getElementById('view-quiz'),
  };
  const poemsSubbar = document.getElementById('poems-subbar');
  const btnPrintMain = document.getElementById('btn-print-main');

  const btnStandard = document.getElementById('btn-mode-standard');
  const btnCompact = document.getElementById('btn-mode-compact');
  const daySelect = document.getElementById('day-filter-select');
  const btnPrevDay = document.getElementById('btn-prev-day');
  const btnNextDay = document.getElementById('btn-next-day');
  const btnShowAll = document.getElementById('btn-show-all');
  const chkDictation = document.getElementById('toggle-dictation');
  const volBtns = Array.from(document.querySelectorAll('.vol-pill-btn'));
  const sheets = Array.from(document.querySelectorAll('.poem-sheet'));

  let activeTab = 'poems';
  let currentVol = 'ALL';
  let currentDay = 'all';

  function updatePrintBtnLabel(visibleCount) {
    if (!btnPrintMain) return;
    if (activeTab === 'poems') {
      btnPrintMain.textContent = '🖨️ 打印诗词 (' + visibleCount + '篇)';
    } else if (activeTab === 'tracker') {
      btnPrintMain.textContent = '🖨️ 打印打卡表 (2页A4)';
    } else if (activeTab === 'quiz') {
      btnPrintMain.textContent = '🖨️ 打印默写卷与答案 (5页A4)';
    } else {
      btnPrintMain.textContent = '🖨️ 打印目录表';
    }
  }

  function applyPoemsFilter() {
    let visibleCount = 0;
    sheets.forEach(el => {
      const matchDay = currentDay === 'all' || el.dataset.day === currentDay;
      const matchVol = currentDay !== 'all' || currentVol === 'ALL' || el.dataset.volume === currentVol;
      if (matchDay && matchVol) {
        el.classList.remove('hidden-by-filter');
        visibleCount++;
      } else {
        el.classList.add('hidden-by-filter');
      }
    });

    const isCompact = body.classList.contains('mode-compact');
    const visibleSheets = sheets.filter(el => !el.classList.contains('hidden-by-filter'));
    sheets.forEach(el => el.classList.remove('break-after-page', 'compact-row-end'));
    visibleSheets.forEach((el, idx) => {
      const isLast = idx === visibleSheets.length - 1;
      if (isCompact) {
        if (idx % 2 === 1) {
          el.classList.add('compact-row-end');
          if (!isLast) el.classList.add('break-after-page');
        }
      } else if (!isLast) {
        el.classList.add('break-after-page');
      }
    });
    updatePrintBtnLabel(visibleCount);
  }

  function switchTab(tab) {
    activeTab = viewPanels[tab] ? tab : 'poems';
    tabBtns.forEach(b => b.classList.toggle('active', b.dataset.tab === activeTab));
    Object.keys(viewPanels).forEach(k => {
      if (viewPanels[k]) viewPanels[k].classList.toggle('view-hidden', k !== activeTab);
    });
    if (poemsSubbar) {
      poemsSubbar.classList.toggle('subbar-hidden', activeTab !== 'poems');
    }
    const visibleCount = sheets.filter(el => !el.classList.contains('hidden-by-filter')).length;
    updatePrintBtnLabel(visibleCount);
  }

  function setMode(mode) {
    if (mode === 'compact') {
      body.classList.add('mode-compact');
      btnCompact.classList.add('active');
      btnStandard.classList.remove('active');
      if (chkDictation && !chkDictation.dataset.userTouched) {
        chkDictation.checked = false;
        body.classList.add('hide-dictation');
      }
    } else {
      body.classList.remove('mode-compact');
      btnStandard.classList.add('active');
      btnCompact.classList.remove('active');
      if (chkDictation && !chkDictation.dataset.userTouched) {
        chkDictation.checked = true;
        body.classList.remove('hide-dictation');
      }
    }
    applyPoemsFilter();
  }

  function setVolume(vol) {
    currentVol = String(vol || 'ALL');
    currentDay = 'all';
    if (daySelect) daySelect.value = 'all';
    volBtns.forEach(b => b.classList.toggle('active', b.dataset.vol === currentVol));
    applyPoemsFilter();
  }

  function setDay(dayVal) {
    currentDay = String(dayVal || 'all');
    if (daySelect) daySelect.value = currentDay;
    if (currentDay !== 'all') {
      volBtns.forEach(b => b.classList.remove('active'));
    } else {
      volBtns.forEach(b => b.classList.toggle('active', b.dataset.vol === currentVol));
    }
    applyPoemsFilter();
  }

  tabBtns.forEach(b => b.addEventListener('click', () => {
    switchTab(b.dataset.tab);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }));

  volBtns.forEach(b => b.addEventListener('click', () => setVolume(b.dataset.vol)));
  if (daySelect) daySelect.addEventListener('change', (e) => setDay(e.target.value));
  if (btnPrevDay) {
    btnPrevDay.addEventListener('click', () => {
      const cur = currentDay === 'all' ? 1 : Math.max(1, parseInt(currentDay, 10) - 1);
      setDay(String(cur));
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }
  if (btnNextDay) {
    btnNextDay.addEventListener('click', () => {
      const cur = currentDay === 'all' ? 1 : Math.min(100, parseInt(currentDay, 10) + 1);
      setDay(String(cur));
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }
  if (btnShowAll) {
    btnShowAll.addEventListener('click', () => {
      setVolume('ALL');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  }

  if (btnStandard) btnStandard.addEventListener('click', () => setMode('standard'));
  if (btnCompact) btnCompact.addEventListener('click', () => setMode('compact'));
  if (chkDictation) {
    chkDictation.addEventListener('change', (e) => {
      chkDictation.dataset.userTouched = '1';
      body.classList.toggle('hide-dictation', !e.target.checked);
    });
  }
  if (btnPrintMain) btnPrintMain.addEventListener('click', () => window.print());

  // 打卡步点击
  document.querySelectorAll('.step-item').forEach(label => {
    label.addEventListener('click', () => label.classList.toggle('checked'));
  });

  // 目录检索视图：搜索、分类与页内跳转
  const searchInput = document.getElementById('poem-search');
  const filterBtns = document.querySelectorAll('.filter-btn');
  const rows = document.querySelectorAll('.poem-row');
  let activeCat = 'ALL';

  function applyIndexSearch() {
    const kw = (searchInput ? searchInput.value : '').trim().toLowerCase();
    rows.forEach(tr => {
      const matchCat = activeCat === 'ALL' || tr.dataset.cat === activeCat;
      const matchKw = !kw || tr.dataset.search.includes(kw);
      tr.style.display = (matchCat && matchKw) ? '' : 'none';
    });
  }
  if (searchInput) searchInput.addEventListener('input', applyIndexSearch);
  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      activeCat = btn.dataset.cat;
      applyIndexSearch();
    });
  });

  document.querySelectorAll('[data-jump-day]').forEach(btn => {
    btn.addEventListener('click', () => {
      switchTab('poems');
      setDay(btn.dataset.jumpDay);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  });
  document.querySelectorAll('[data-jump-vol]').forEach(btn => {
    btn.addEventListener('click', () => {
      switchTab('poems');
      setVolume(btn.dataset.jumpVol);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
  });

  // 电子进度记忆（localStorage，隐私模式失败自动忽略）
  const STORAGE_KEY = 'reid_poetry_100_done_v1';
  let doneMap = {};
  try {
    doneMap = JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}') || {};
  } catch (e) { doneMap = {}; }

  const progressText = document.getElementById('done-progress-text');
  function updateDoneSummary() {
    const count = Object.values(doneMap).filter(Boolean).length;
    if (progressText) progressText.textContent = '已完成背诵 ' + count + ' / 100 篇';
  }
  document.querySelectorAll('.done-chk').forEach(chk => {
    const d = chk.dataset.day;
    chk.checked = !!doneMap[d];
    chk.addEventListener('change', () => {
      doneMap[d] = chk.checked;
      try { localStorage.setItem(STORAGE_KEY, JSON.stringify(doneMap)); } catch (e) {}
      updateDoneSummary();
    });
  });
  updateDoneSummary();

  // 解析 URL 参数: ?tab=poems|index|tracker|quiz & ?vol=1..10 & ?day=1..100 & ?mode=compact & ?autoprint=1
  const params = new URLSearchParams(window.location.search);
  const qVol = params.get('vol');
  const qDay = params.get('day');
  const qMode = params.get('mode');
  const qTab = params.get('tab');

  if (qVol && volBtns.some(b => b.dataset.vol === qVol)) {
    setVolume(qVol);
  }
  if (qDay && daySelect && Array.from(daySelect.options).some(o => o.value === qDay)) {
    setDay(qDay);
  }
  setMode(qMode === 'compact' ? 'compact' : 'standard');
  switchTab(qTab || 'poems');

  if (params.get('autoprint') === '1') {
    setTimeout(() => window.print(), 250);
  }
})();
""".strip()


def build_single_portable_html(poems: list[dict[str, Any]]) -> str:
    vol_pills = ['<button type="button" class="vol-pill-btn active" data-vol="ALL">全部 (100天)</button>']
    for v in VOLUMES:
        short_label = v["name"].split(" · ")[0]
        title_label = v["name"].split(" · ")[1]
        vol_pills.append(
            f'<button type="button" class="vol-pill-btn" data-vol="{v["volume"]}">{esc(short_label)} · {esc(title_label)}</button>'
        )

    day_options = ['<option value="all">查看当前所选全部篇目</option>']
    for p in poems:
        day_options.append(f'<option value="{p["day"]}">第 {p["day"]:02d} 天 · 《{esc(p["title"])}》</option>')

    sheets_html = "\n\n".join(render_poem_sheet(p) for p in poems)

    cat_counts = {cat: sum(1 for p in poems if p["category"] == cat) for cat in ["六年级核心", "高段核心", "初中衔接", "课外拓展"]}
    idx_vol_cards = []
    for v in VOLUMES:
        v_poems = [p for p in poems if p["volume"] == v["volume"]]
        preview = "、".join(f"《{p['title']}》" for p in v_poems[:4]) + " 等 10 篇"
        idx_vol_cards.append(
            f"""<div class="idx-vol-card">
              <div class="idx-vol-head">
                <div>
                  <span class="idx-vol-days">{esc(v["days"])}</span>
                  <h3>{esc(v["name"])}</h3>
                </div>
                <span class="idx-vol-sub">{esc(v["subtitle"])}</span>
              </div>
              <p class="idx-vol-desc">{esc(v["desc"])}</p>
              <div class="idx-vol-preview">代表篇目：{esc(preview)}</div>
              <div style="margin-top:4px; display:flex; gap:8px;">
                <button type="button" class="btn active" data-jump-vol="{v["volume"]}">📖 阅读 / 打印本卷 (10篇)</button>
                <button type="button" class="btn" data-jump-day="{v_poems[0]["day"]}">从第 {v_poems[0]["day"]:02d} 天开始 →</button>
              </div>
            </div>"""
        )

    idx_rows = []
    for p in poems:
        cat_cls = category_badge_class(p["category"])
        search_blob = f"{p['day']} {p['title']} {p['author']} {p['dynasty']} {p['category']} {p['golden_quote']} {p['volume_name']}"
        idx_rows.append(
            f"""<tr class="poem-row" data-cat="{esc(p['category'])}" data-search="{esc(search_blob.lower())}">
              <td class="td-done"><input type="checkbox" class="done-chk" data-day="{p['day']}" aria-label="已背标记"></td>
              <td class="td-day">Day {p["day"]:02d}</td>
              <td class="td-title">《{esc(p["title"])}》</td>
              <td class="td-author">〔{esc(p["dynasty"])}〕{esc(p["author"])}</td>
              <td class="td-genre">{esc(p["genre"])}</td>
              <td><span class="cat-badge {cat_cls}">{esc(p["category"])}</span></td>
              <td class="td-quote">{esc(p["golden_quote"])}</td>
              <td><button type="button" class="jump-btn" data-jump-day="{p['day']}">阅读 / 打印 →</button></td>
            </tr>"""
        )

    tracker_only_pages = render_tracker_pages_html(poems, mark_second_last=True)
    quiz_only_pages = render_quiz_and_answer_pages_html(poems)

    return f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>小学六年级古诗词背诵 100 天（单文件便携全能可打印版）</title>
<style>
{SHARED_SHEET_CSS}
{TRACKER_QUIZ_CSS}
{PORTABLE_EXTRA_CSS}
</style>
</head>
<body>

<div class="no-print-bar portable-bar">
  <div class="portable-top-row">
    <div class="bar-title-group">
      <div class="bar-title">📜 小学六年级古诗词背诵 100 天 · 单文件便携全能版</div>
      <div class="bar-subtitle">零外部依赖，可任意拷贝至手机/平板/U盘随时离线阅读或 A4 打印 · <span id="done-progress-text">已完成背诵 0 / 100 篇</span></div>
    </div>
    <div class="tab-nav">
      <button type="button" class="tab-btn active" data-tab="poems">📖 每日精讲 (100篇)</button>
      <button type="button" class="tab-btn" data-tab="index">🔍 目录检索</button>
      <button type="button" class="tab-btn" data-tab="tracker">📋 打卡总表 (2页)</button>
      <button type="button" class="tab-btn" data-tab="quiz">✍️ 50题默写卷 (5页)</button>
      <button type="button" id="btn-print-main" class="btn btn-print">🖨️ 打印诗词 (100篇)</button>
    </div>
  </div>

  <div id="poems-subbar" class="poems-subbar">
    <div class="vol-pills">
      {"".join(vol_pills)}
    </div>
    <div class="poems-action-row">
      <div class="nav-pager">
        <button type="button" id="btn-prev-day" class="btn">◀ 上一天</button>
        <select id="day-filter-select" class="day-select" aria-label="按天选择">
          {"".join(day_options)}
        </select>
        <button type="button" id="btn-next-day" class="btn">下一天 ▶</button>
        <button type="button" id="btn-show-all" class="btn">显示全部</button>
      </div>
      <div class="bar-controls">
        <button type="button" id="btn-mode-standard" class="btn active">📄 1页1篇·精讲版</button>
        <button type="button" id="btn-mode-compact" class="btn">📑 1页2篇·省纸版</button>
        <label class="toggle-check">
          <input type="checkbox" id="toggle-dictation" checked> 显示默写微测
        </label>
      </div>
    </div>
  </div>
</div>

<!-- 视图1：每日诗词精讲（100篇） -->
<section id="view-poems" class="view-panel">
  <main class="sheets-wrap">
{sheets_html}
  </main>
</section>

<!-- 视图2：总目录与即时搜索检索 -->
<section id="view-index" class="view-panel view-hidden">
  <div class="idx-wrap">
    <div class="idx-hero">
      <h1>📜 百日古诗词全篇目导航与进度管理</h1>
      <p>点击下方分卷卡片可整卷阅读/打印；点击目录表任意篇目可立即跳转至该天单篇精讲页；左侧复选框自动在本机浏览器记录已背进度。</p>
      <div class="stats-row">
        <span class="stat-pill">📚 共 100 天 · 10 大主题分卷</span>
        <span class="stat-pill">🟢 六年级核心 {cat_counts["六年级核心"]} 篇</span>
        <span class="stat-pill">🔵 高段核心 {cat_counts["高段核心"]} 篇</span>
        <span class="stat-pill">🟠 初中衔接 {cat_counts["初中衔接"]} 篇</span>
        <span class="stat-pill">🟣 课外拓展 {cat_counts["课外拓展"]} 篇</span>
      </div>
    </div>

    <div class="idx-vol-grid">
      {"".join(idx_vol_cards)}
    </div>

    <div class="idx-panel">
      <div class="filter-toolbar">
        <input type="text" id="poem-search" class="search-input" placeholder="输入诗名、作者、名句或天数搜索（如：苏轼 / 辛弃疾 / 托物 / 明月）...">
        <div class="cat-filters">
          <button type="button" class="filter-btn active" data-cat="ALL">全部 (100)</button>
          <button type="button" class="filter-btn" data-cat="六年级核心">六年级核心 ({cat_counts["六年级核心"]})</button>
          <button type="button" class="filter-btn" data-cat="高段核心">高段核心 ({cat_counts["高段核心"]})</button>
          <button type="button" class="filter-btn" data-cat="初中衔接">初中衔接 ({cat_counts["初中衔接"]})</button>
          <button type="button" class="filter-btn" data-cat="课外拓展">课外拓展 ({cat_counts["课外拓展"]})</button>
        </div>
      </div>
      <table class="poem-table">
        <thead>
          <tr>
            <th class="td-done">已背</th>
            <th>天数</th>
            <th>诗词题目</th>
            <th>朝代 · 作者</th>
            <th>体裁</th>
            <th>定位</th>
            <th>核心千古名句</th>
            <th>直达</th>
          </tr>
        </thead>
        <tbody>
          {"".join(idx_rows)}
        </tbody>
      </table>
    </div>
  </div>
</section>

<!-- 视图3：100天墙贴打卡总表（2页A4） -->
<section id="view-tracker" class="view-panel view-hidden">
  <div class="pages-wrap">
{tracker_only_pages}
  </div>
</section>

<!-- 视图4：50题理解性默写通关卷 + 答案（5页A4） -->
<section id="view-quiz" class="view-panel view-hidden">
  <div class="pages-wrap">
{quiz_only_pages}
  </div>
</section>

<div class="portable-foot-note no-print">
  💡 使用提示：本文件为独立单文件网页，可直接复制到手机、iPad、U盘或任意文件夹离线打开；在浏览器点击右上角红色打印按钮即可按当前选中的视图/分卷精准分页打印 A4 纸张。
</div>

<script>
{PORTABLE_JS}
</script>
</body>
</html>
"""


def main() -> None:
    poems = load_and_validate()
    print(f"[OK] 成功加载并校验全部 {len(poems)} 篇古诗词数据（Day 01..100 连续且篇名 100% 唯一）。")

    # 1. 生成 10 个分卷打印 HTML
    for v in VOLUMES:
        v_poems = [p for p in poems if p["volume"] == v["volume"]]
        out_path = BASE_DIR / v["file"]
        html_str = build_poem_collection_html(
            page_title=f"{v['name']}（{v['days']}）| 小学六年级古诗词背诵100天",
            bar_title=f"{v['name']}（{v['days']} · {v['subtitle']}）",
            bar_subtitle="每天 1 篇 · 含原文、字词、译文、深度精讲、背诵与作文运用及理解性默写",
            poems=v_poems,
        )
        out_path.write_text(html_str, encoding="utf-8")
        print(f"  -> 生成分册: {out_path.name} ({len(v_poems)} 篇)")

    # 2. 生成全套 100 天合集
    all_path = BASE_DIR / "全套100天合集打印版.html"
    all_html = build_poem_collection_html(
        page_title="全套100天合集打印版 | 小学六年级古诗词背诵100天",
        bar_title="小学六年级古诗词背诵 100 天 · 全套完整合集（Day 01 – 100）",
        bar_subtitle="默认 100 页 A4 精讲版；点击“1页2篇·省纸版”仅需 50 张纸即可打完",
        poems=poems,
    )
    all_path.write_text(all_html, encoding="utf-8")
    print(f"  -> 生成全集: {all_path.name} ({len(poems)} 篇)")

    # 3. 生成百日打卡表与 50 题默写卷
    tracker_path = BASE_DIR / "百日背诵打卡总表与名句默写卷.html"
    tracker_path.write_text(build_tracker_and_quiz_html(poems), encoding="utf-8")
    print(f"  -> 生成打卡与测试卷: {tracker_path.name}")

    # 4. 生成总导航主页 index.html
    index_path = BASE_DIR / "index.html"
    index_path.write_text(build_index_html(poems), encoding="utf-8")
    print(f"  -> 生成总导航主页: {index_path.name}")

    # 5. 生成独立单文件便携全能版（放置于 Reid 根目录，便于直接移动分享）
    portable_path = BASE_DIR.parent / "小学六年级古诗词背诵100天(单文件便携可打印版).html"
    portable_path.write_text(build_single_portable_html(poems), encoding="utf-8")
    print(f"  -> 生成单文件便携全能版: {portable_path}")
    print("[DONE] 全部 14 个 HTML 文件构建完成！")


if __name__ == "__main__":
    main()
