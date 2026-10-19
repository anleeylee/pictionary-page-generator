# Pictionary 内容页批量生成器（Pictionary Page Generator）

> **把词库 JSON 批量生成 SEO 就绪的主题内容页（HTML）——关键词优化的 title/meta、canonical、Open Graph、JSON-LD schema、生成器嵌入、分类样例表、玩法说明、主题 FAQ、站内互链，并自动重写 sitemap.xml。**

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![CLI](https://img.shields.io/badge/CLI-ready-4B8BBE)](page_generator.py)
[![No dependencies](https://img.shields.io/badge/deps-stdlib%20only-blueviolet)](requirements.txt)

---

## 相关链接

- 🎲 **在线工具体验：** [Pictionary Word Generator — 免费 7000+ 画画提示词](https://pictionarywordgenerators.com/)
- 📄 **难词页面：** [Hard Pictionary Words — 有挑战性的画画提示词](https://pictionarywordgenerators.com/hard-pictionary-words)
- 英文版说明：[README.md](README.md)

---

## 这个工具做什么

主题词库只有在能被找到时才有价值。**Pictionary Page Generator** 把一个词库
JSON 文件（与 [Pictionary Wordlist Generator](https://github.com/anleeylee/pictionary-wordlist-generator)
产出的 schema 完全一致）变成一个完整、可直接部署的主题内容页：

- **关键词优化的 `<title>` 与 meta description**（由主题名自动生成，
  如 "Space Pictionary Words — Free List & Generator"）；
- **canonical URL** 指向该主题的规范路径；
- **Open Graph 标签**（og:type / og:site_name / og:title / og:description /
  og:url），让链接在社交媒体上展示美观；
- **JSON-LD schema**——WebPage 节点 + FAQPage 节点（页面内所有问答），
  有资格进入富结果；
- **生成器嵌入块**，回链到在线生成器（[Pictionary Word Generator](https://pictionarywordgenerators.com/)）；
- **分类样例表**（词 / 分类 / 难度），直接来自词库；
- **玩法说明区**，标准 Pictionary 规则；
- **主题 FAQ**（3 个通用 + 2 个主题定制问题，可配置）；
- **站内互链**——一次运行把所有生成的页面加上彼此链接，并链回首页，
  整个主题簇互相关联。

渲染完成后，工具会**自动重写 `sitemap.xml`**，每个生成的页面对应一个
`<url>` 条目（lastmod / changefreq / priority），让新页面立即可被搜索引擎
发现。

## 为什么重要

内容页是 Pictionary 词站针对"hard Pictionary words"、"space Pictionary
words"这类长尾词排名的途径。手写 HTML 又慢又不一致——标题走样、canonical
被漏掉、schema 过时。这个生成器让每个主题页在结构上完全一致、天然
SEO 完整，并自动保持 sitemap 同步。

由于每个页面都链向生成器和其他主题页，每新增一个词库都在壮大站点的内部
链接图，而不是产生一个孤页。

## 安装

```bash
git clone https://github.com/anleeylee/pictionary-page-generator.git
cd pictionary-page-generator

# 无需 pip install —— 仅标准库
python page_generator.py --help
```

## 用法

```bash
# 从词库目录批量生成页面 + sitemap
python page_generator.py --input examples/libs --output pages

# 从单个词库生成
python page_generator.py --input examples/libs/space.json --output pages

# 自定义站点 URL（用于 canonical / OG / sitemap）
python page_generator.py --input examples/libs --output pages \
  --site-url https://pictionarywordgenerators.com

# 跳过 sitemap 重写
python page_generator.py --input examples/libs --output pages --no-sitemap
```

### 参数

| 参数 | 默认 | 说明 |
|---|---|---|
| `--input` | （必填） | 词库 JSON 文件所在目录，或单个 JSON 文件 |
| `--output` | `pages` | 生成的 HTML 页面输出目录 |
| `--site-url` | `https://pictionarywordgenerators.com` | canonical / OG / sitemap 的基础 URL |
| `--no-sitemap` | 关闭 | 不重写 `sitemap.xml` |

## 词库结构约定

```json
{
  "theme": "space",
  "title": "Space",
  "entries": [
    {"prompt": "Moon", "category": "Celestial", "difficulty": "easy"}
  ]
}
```

这正是 [Pictionary Wordlist Generator](https://github.com/anleeylee/pictionary-wordlist-generator)
产出的、并由 [Pictionary Wordlist Auditor](https://github.com/anleeylee/pictionary-wordlist-auditor)
校验的 schema。

## 生成页面结构

```
主题页（如 /space）
├── <title> Space Pictionary Words — Free List & Generator
├── meta description
├── <link rel="canonical" href="https://…/space">
├── Open Graph 标签
├── JSON-LD：WebPage + FAQPage
├── 生成器嵌入块 → 链接到在线生成器
├── 样例词表（词 / 分类 / 难度）
├── 玩法说明区 → 链接到 how-to-play 页
├── 主题 FAQ（5 个问题）
└── 站内互链 → 所有其他生成的主题页 + 首页
```

## 测试

```bash
python -m unittest discover -s tests -v
```

覆盖：slug 规范化、title/meta/canonical/OG 存在性、JSON-LD 结构
（WebPage + FAQPage）、生成器嵌入、样例表、玩法说明、站内互链、FAQ 渲染、
HTML 转义与 sitemap 生成。

## 许可

MIT——可自由使用与扩展，请保留署名。它生成的页面是你网站的内容，工具只是
让它们保持一致且可被抓取。
