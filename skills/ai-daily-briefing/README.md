# 📰 AI 每日简报系统

自动化 AI 领域新闻收集与简报生成工具。

---

## 📁 目录结构

```
daily-ai-briefing/
├── README.md                 # 项目说明
├── config/                   # 配置文件
│   └── news_sources.yaml     # 新闻源配置（38个源）
├── scripts/                  # 脚本文件
│   ├── fetch_all.py         # 完整抓取脚本
│   ├── fetch_jiqizhixin.py  # 机器之心专用
│   └── fetch_ailab.py       # 新智元专用
├── output/                   # 生成的简报
│   ├── ai_briefing_YYYY-MM-DD.md
│   ├── news_YYYY-MM-DD.json
│   ├── jiqizhixin_latest.json
│   └── ailab_latest.json
├── archive/                  # 历史简报归档
└── logs/                     # 运行日志
```

---

## 🚀 快速开始

### 1. 手动运行

```bash
# 抓取新闻并生成简报
cd /root/.openclaw/workspace/daily-ai-briefing
python3 scripts/fetch_all.py
```

### 2. 查看简报

```bash
# 查看最新简报
cat output/ai_briefing_$(date +%Y-%m-%d).md
```

---

## 🌐 代理配置（可选）

脚本支持自动检测常见代理端口（7890, 17890, 1080 等），无需手动配置即可使用。

### 手动指定代理

如需手动指定代理，使用以下任一环境变量：

```bash
# 方式1：专用变量（推荐）
export AI_BRIEFING_PROXY="http://127.0.0.1:17890"
python3 scripts/fetch_all.py

# 方式2：标准变量（兼容其他工具）
export HTTP_PROXY="http://127.0.0.1:17890"
export HTTPS_PROXY="http://127.0.0.1:17890"
python3 scripts/fetch_all.py

# 方式3：临时指定（单次运行）
AI_BRIEFING_PROXY="http://127.0.0.1:17890" python3 scripts/fetch_all.py
```

### 优先级说明

代理配置优先级（从高到低）：
1. `AI_BRIEFING_PROXY` - 专用环境变量
2. `HTTP_PROXY` / `http_proxy` / `HTTPS_PROXY` / `https_proxy` - 标准环境变量
3. 自动检测 - 检测常见代理端口（7890, 17890, 1080, 10808, 8080, 7897, 9090）
4. 直接连接 - 不使用代理

### 不同启动方式的配置

**Systemd 服务** (`/etc/systemd/system/openclaw.service`)：
```ini
[Service]
Environment="AI_BRIEFING_PROXY=http://127.0.0.1:17890"
```

**PM2** (`ecosystem.config.js`)：
```javascript
module.exports = {
  apps: [{
    name: 'openclaw',
    script: './dist/index.js',
    env: {
      AI_BRIEFING_PROXY: 'http://127.0.0.1:17890'
    }
  }]
}
```

**Docker** (`docker-compose.yml`)：
```yaml
services:
  openclaw:
    environment:
      - AI_BRIEFING_PROXY=http://host:17890
```

**Cron 定时任务** (`crontab -e`)：
```bash
# 方式1：在 crontab 中设置变量
AI_BRIEFING_PROXY=http://127.0.0.1:17890
0 8 * * * cd /path/to/daily-ai-briefing && python3 scripts/fetch_all.py

# 方式2：在命令中内联设置
0 8 * * * export AI_BRIEFING_PROXY=http://127.0.0.1:17890; cd /path/to/daily-ai-briefing && python3 scripts/fetch_all.py
```

---

## 📊 四板块新闻源架构

### 板块1: AI科技 (14个源)

| 来源 | 类型 | 状态 |
|------|------|------|
| TechCrunch AI | RSS | ✅ |
| The Verge AI | RSS | ✅ |
| Ars Technica AI | RSS | ✅ |
| OpenAI News | RSS | ✅ |
| Google Developers | RSS | ✅ |
| GitHub Blog | RSS | ✅ |
| Papers With Code | RSS | ✅ |
| 量子位 | RSS | ✅ |
| 机器之心 | Playwright | ✅ |
| 新智元 | Playwright | ✅ |
| 36氪 | RSS | ✅ |
| 雷锋网 | RSS | ✅ |
| InfoQ | RSS | ✅ |
| Hacker News | RSS | ✅ |

### 板块2: 商业财经 (10个源)

| 来源 | 类型 | 状态 |
|------|------|------|
| CNBC Finance | RSS | ✅ |
| Business Insider | RSS | ✅ |
| Fortune | RSS | ✅ |
| VentureBeat | RSS | ✅ |
| The Guardian Tech | RSS | ✅ |
| BBC Technology | RSS | ✅ |
| 财经网 | Playwright | ✅ |
| 第一财经 | Playwright | ✅ |
| 界面新闻 | Playwright | ✅ |
| Forbes | RSS | ❌ |

### 板块3: 学术研究 (5个源)

| 来源 | 类型 | 状态 |
|------|------|------|
| arXiv AI | RSS | ✅ |
| arXiv NLP | RSS | ✅ |
| arXiv ML | RSS | ✅ |
| arXiv CV | RSS | ✅ |
| Google AI Blog | RSS | ✅ |

### 板块4: 政策与产业 (17个源)

| 来源 | 类型 | 状态 |
|------|------|------|
| 199IT | RSS | ✅ |
| 国务院 | Playwright | ✅ |
| 工信部 | Playwright | ⚠️ |
| 发改委 | Playwright | ✅ |
| 网信办 | Playwright | ✅ |
| 上海市政府 | Playwright | ✅ |
| 广东省政府 | Playwright | ✅ |
| 深圳市政府 | Playwright | ✅ |
| 武汉市政府 | Playwright | ✅ |
| 湖北省政府 | Playwright | ⚠️ |
| 武汉市发改委 | Playwright | ✅ |
| 武汉市经信局 | Playwright | ✅ |
| 武汉市科技局 | Playwright | ✅ |
| 武汉市数据局 | Playwright | ✅ |
| 武汉市人社局 | Playwright | ✅ |
| 武汉市商务局 | Playwright | ✅ |
| 武汉市卫健委 | Playwright | ✅ |

---

## 📈 统计

- **总计**: 46个新闻源
- ✅ **可用**: 43个
- ⚠️ **有限制**: 2个 (工信部403, 湖北省政府412)
- ❌ **不可用**: 1个 (Forbes RSS空)

---

## ⚙️ 配置说明

编辑 `config/news_sources.yaml` 来：
- 添加/删除新闻源
- 调整抓取优先级
- 设置时间窗口
- 配置输出格式

---

## 📝 简报格式

每日简报包含四个板块：
- 🤖 **AI科技** - 最新技术动态、产品发布
- 💼 **商业财经** - 融资、市场、经济趋势
- 🎓 **学术研究** - 最新论文、研究成果
- 📜 **政策与产业** - 政府政策、产业规划

---

## ⏰ 自动化设置

### 定时任务（Cron）

```bash
# 每天早上 8:00 自动生成简报
0 8 * * * cd /root/.openclaw/workspace/daily-ai-briefing && python3 scripts/fetch_all.py
```

---

## 📈 更新日志

- **2026-03-19** - 项目初始化，完成四板块架构
  - AI科技板块: 14个源
  - 商业财经板块: 10个源
  - 学术研究板块: 5个源
  - 政策与产业板块: 9个源
- **2026-03-19** - 添加湖北省及武汉市各部门
  - 新增: 湖北省政府、武汉市发改委、经信局、科技局、数据局、人社局、商务局、卫健委
  - 政策与产业板块扩展至17个源

---

*Created by Lewis for Ben*
