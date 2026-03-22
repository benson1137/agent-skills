---
name: ai-daily-briefing
description: AI每日简报系统 - 自动化收集AI领域新闻并生成简报。支持RSS和网页抓取，覆盖AI科技、商业财经、学术研究、政策与产业四大板块。当用户需要获取AI新闻、生成每日简报、或管理新闻源时使用此技能。
---

# AI 每日简报系统

自动化收集AI领域新闻并生成每日简报的工具。

## 快速开始

### 运行简报生成

```bash
cd /root/.openclaw/workspace/daily-ai-briefing
python3 scripts/fetch_all.py
```

### 查看最新简报

```bash
cat output/ai_briefing_$(date +%Y-%m-%d).md
```

## 新闻源架构

系统覆盖四大板块，共46个新闻源：

### 板块1: AI科技 (14个源)
- 国际科技媒体: TechCrunch, The Verge, Ars Technica
- AI公司官方: OpenAI, Google Developers, GitHub
- 国内AI媒体: 机器之心, 新智元, 量子位
- 开发者社区: Hacker News

### 板块2: 商业财经 (10个源)
- 国际商业媒体: CNBC, Business Insider, Fortune
- 科技投资: VentureBeat
- 主流媒体: The Guardian, BBC

### 板块3: 学术研究 (5个源)
- arXiv论文: AI, NLP, ML, CV
- 研究博客: Google AI Blog

### 板块4: 政策与产业 (17个源)
- 中央政府: 国务院, 发改委, 网信办
- 地方政府: 上海, 广东, 深圳, 武汉
- 武汉本地: 发改委, 经信局, 科技局, 数据局等

## 实现状态

| 板块 | 总数 | 自动抓取 | 待实现 | 覆盖率 |
|------|------|----------|--------|--------|
| AI科技 | 14 | 14 | 0 | 100% |
| 商业财经 | 10 | 9 | 1 | 90% |
| 学术研究 | 5 | 5 | 0 | 100% |
| 政策与产业 | 17 | 1 | 16 | 6% |
| **总计** | **46** | **29** | **17** | 63% |

**详细实现状态**: 参见 [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md)

**新闻源获取指南**: 参见 [SOURCES_GUIDE.md](SOURCES_GUIDE.md)

**可用源列表**: 参见 [AVAILABLE_SOURCES.md](AVAILABLE_SOURCES.md)

**项目结构说明**: 参见 [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md)

## 技术实现

### RSS抓取
使用 `feedparser` 库抓取RSS/Atom feed，支持24小时时间窗口过滤。

### 网页抓取
使用 `Playwright` 浏览器渲染抓取动态网页内容。

### 输出格式
- JSON: 结构化数据，便于后续处理
- Markdown: 人类可读的简报格式
- 飞书卡片: 用于推送到飞书

## 配置文件

新闻源配置: `/root/.openclaw/workspace/daily-ai-briefing/config/news_sources.yaml`

## 脚本文件

| 脚本 | 功能 |
|------|------|
| `fetch_all.py` | 主抓取脚本，覆盖29个源 |
| `fetch_jiqizhixin.py` | 机器之心专用（已整合到主脚本） |
| `fetch_ailab.py` | 新智元专用（已整合到主脚本） |
| `test_sources.py` | 新闻源测试脚本 |

## 定时任务

```bash
# 每天早上 8:00 自动生成简报
0 8 * * * cd /root/.openclaw/workspace/daily-ai-briefing && python3 scripts/fetch_all.py
```

## 文档索引

| 文档 | 说明 |
|------|------|
| [SKILL.md](SKILL.md) | 本文件 - 技能主文档 |
| [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md) | 详细实现状态报告 |
| [SOURCES_GUIDE.md](SOURCES_GUIDE.md) | 新闻源获取指南 |
| [AVAILABLE_SOURCES.md](AVAILABLE_SOURCES.md) | 可用源列表 |
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | 项目结构说明 |
| [README.md](README.md) | 项目主文档 |

## 待实现功能

### 高优先级 (政府网站)
- 国务院、发改委、网信办网页抓取
- 工信部: HTTP 403，需研究绕过方案

### 中优先级 (地方政府)
- 各省级市政府网站（上海、广东、深圳）
- 武汉市政府及各部门网站

### 特殊处理
- 湖北省政府: HTTP 412，需处理预检限制
- Forbes: RSS空内容，已有其他商业媒体替代

## 目录结构

```
daily-ai-briefing/
├── config/
│   └── news_sources.yaml      # 46个新闻源配置
├── scripts/
│   ├── fetch_all.py          # 主抓取脚本
│   ├── fetch_jiqizhixin.py   # 机器之心
│   └── fetch_ailab.py        # 新智元
├── output/                   # 生成的简报
├── archive/                  # 历史归档
└── logs/                     # 运行日志
```

## 依赖

```bash
pip install feedparser beautifulsoup4 playwright
```

Playwright浏览器:
```bash
playwright install chromium
```
