# Agent Skills

OpenClaw Agent 技能集合

## Skills

### ai-daily-briefing

AI每日简报系统 - 自动化收集AI领域新闻并生成简报。

**功能特点：**
- 覆盖AI科技、商业财经、学术研究、政策与产业四大板块
- 支持RSS和网页抓取
- 自动代理检测（支持Clash/Mihomo等）
- 生成Markdown简报和JSON数据

**快速开始：**
```bash
cd skills/ai-daily-briefing
python3 scripts/fetch_all.py
```

**代理配置（可选）：**
```bash
export AI_BRIEFING_PROXY="http://127.0.0.1:17890"
python3 scripts/fetch_all.py
```

详见 [skills/ai-daily-briefing/README.md](skills/ai-daily-briefing/README.md)

## 安装

将技能目录复制到 OpenClaw skills 目录：
```bash
cp -r skills/ai-daily-briefing ~/.openclaw/skills/
```

## 依赖

```bash
pip install feedparser beautifulsoup4 playwright
playwright install chromium
```

## License

MIT
