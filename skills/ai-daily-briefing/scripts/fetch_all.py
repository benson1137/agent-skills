#!/usr/bin/env python3
"""
完整的新闻抓取脚本
- RSS源使用feedparser
- 网页源使用Playwright
"""

import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from playwright.sync_api import sync_playwright
import json
import os
import sys
import time
import yaml
import socket

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


def get_proxy():
    """
    获取代理设置，优先级：
    1. 环境变量 AI_BRIEFING_PROXY
    2. 环境变量 HTTP_PROXY / http_proxy / HTTPS_PROXY / https_proxy
    3. 自动检测常见代理端口
    
    Returns:
        dict: {'http': proxy_url, 'https': proxy_url} 或 None
    """
    # 1. 专用环境变量（最高优先级）
    if proxy := os.getenv('AI_BRIEFING_PROXY'):
        print(f"[代理] 使用 AI_BRIEFING_PROXY: {proxy}")
        return {'http': proxy, 'https': proxy}
    
    # 2. 标准环境变量
    for env_var in ['HTTP_PROXY', 'http_proxy', 'HTTPS_PROXY', 'https_proxy']:
        if proxy := os.getenv(env_var):
            print(f"[代理] 使用 {env_var}: {proxy}")
            return {'http': proxy, 'https': proxy}
    
    # 3. 自动检测常见代理端口
    common_ports = [7890, 17890, 1080, 10808, 8080, 7897, 9090]
    for port in common_ports:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.3)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            if result == 0:
                proxy_url = f"http://127.0.0.1:{port}"
                # 快速验证是否真的是代理
                if test_proxy_quick(proxy_url):
                    print(f"[代理] 自动检测到代理: {proxy_url}")
                    return {'http': proxy_url, 'https': proxy_url}
        except:
            continue
    
    print("[代理] 未配置代理，直接连接")
    return None


def test_proxy_quick(proxy_url):
    """快速测试代理是否可用（不阻塞主流程）"""
    try:
        import urllib.request
        proxy_handler = urllib.request.ProxyHandler({'http': proxy_url, 'https': proxy_url})
        opener = urllib.request.build_opener(proxy_handler)
        opener.addheaders = [('User-Agent', HEADERS['User-Agent'])]
        urllib.request.install_opener(opener)
        # 尝试连接，3秒超时
        req = urllib.request.Request('https://www.google.com', method='HEAD')
        with urllib.request.urlopen(req, timeout=3) as response:
            return response.status == 200
    except:
        return False


# 全局代理配置（在 main() 中初始化）
PROXY_CONFIG = None

# RSS源配置 - 板块1: AI科技
RSS_SOURCES_AI = {
    "TechCrunch AI": "https://techcrunch.com/category/artificial-intelligence/feed/",
    "The Verge AI": "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml",
    "Ars Technica AI": "https://arstechnica.com/tag/artificial-intelligence/feed/",
    "OpenAI News": "https://openai.com/news/rss",
    "Google Developers": "https://developers.googleblog.com/feed/",
    "GitHub Blog": "https://github.blog/feed/",
    "Papers With Code": "https://paperswithcode.com/rss",
    "量子位": "https://www.qbitai.com/feed",
    "36氪": "https://36kr.com/feed",
    "雷锋网": "https://www.leiphone.com/feed",
    "InfoQ": "https://www.infoq.cn/feed",
    "Hacker News": "https://news.ycombinator.com/rss",
}

# RSS源配置 - 板块2: 商业财经
RSS_SOURCES_BUSINESS = {
    "CNBC Finance": "https://www.cnbc.com/id/10000664/device/rss/rss.html",
    "Business Insider": "https://www.businessinsider.com/rss",
    "Fortune": "https://fortune.com/feed/",
    "VentureBeat": "https://venturebeat.com/feed/",
    "The Guardian Tech": "https://www.theguardian.com/technology/rss",
    "BBC Technology": "https://feeds.bbci.co.uk/news/technology/rss.xml",
}

# RSS源配置 - 板块3: 学术研究
RSS_SOURCES_ACADEMIC = {
    "arXiv AI": "https://arxiv.org/rss/cs.AI",
    "arXiv NLP": "https://arxiv.org/rss/cs.CL",
    "arXiv ML": "https://arxiv.org/rss/cs.LG",
    "arXiv CV": "https://arxiv.org/rss/cs.CV",
    "Google AI Blog": "https://blog.google/technology/ai/rss/",
}

# RSS源配置 - 板块4: 政策与产业
RSS_SOURCES_POLICY = {
    "199IT": "https://www.199it.com/feed",
}

# 合并所有RSS源
ALL_RSS_SOURCES = {}
ALL_RSS_SOURCES.update(RSS_SOURCES_AI)
ALL_RSS_SOURCES.update(RSS_SOURCES_BUSINESS)
ALL_RSS_SOURCES.update(RSS_SOURCES_ACADEMIC)
ALL_RSS_SOURCES.update(RSS_SOURCES_POLICY)


def fetch_rss_sources(sources_dict, category_name):
    """抓取RSS源"""
    print(f"\n{'='*60}")
    print(f"抓取 {category_name} RSS 源")
    print('='*60)
    
    time_window = datetime.now() - timedelta(hours=24)
    all_articles = []
    
    for name, url in sources_dict.items():
        try:
            print(f"\n[{name}] 抓取中...", end=" ")
            # 使用代理配置
            feed = feedparser.parse(url, proxy=PROXY_CONFIG)
            count = 0
            
            for entry in feed.entries[:10]:
                published = entry.get('published_parsed') or entry.get('updated_parsed')
                if published:
                    pub_date = datetime(*published[:6])
                    if pub_date > time_window:
                        summary = entry.get('summary', '')
                        all_articles.append({
                            'source': name,
                            'title': entry.get('title', 'No title'),
                            'link': entry.get('link', ''),
                            'published': pub_date.isoformat(),
                            'summary': summary[:200] + '...' if len(summary) > 200 else summary,
                            'category': category_name
                        })
                        count += 1
            
            print(f"✓ {count} 条")
            time.sleep(0.3)
            
        except Exception as e:
            print(f"✗ 失败: {str(e)[:50]}")
    
    return all_articles


def fetch_jiqizhixin():
    """抓取机器之心"""
    print("\n" + "="*60)
    print("抓取机器之心 (Playwright)")
    print("="*60)
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=HEADERS['User-Agent'],
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = context.new_page()
            page.goto("https://www.jiqizhixin.com/articles", wait_until='networkidle', timeout=30000)
            page.wait_for_timeout(3000)
            
            content = page.content()
            browser.close()
        
        soup = BeautifulSoup(content, 'html.parser')
        articles = []
        
        items = soup.select('.article-card')
        print(f"找到 {len(items)} 个文章卡片")
        
        for item in items[:10]:
            title_elem = item.select_one('.article-card__title')
            if title_elem:
                title = title_elem.get_text(strip=True)
                link_elem = item.select_one('a')
                href = link_elem.get('href', '') if link_elem else ''
                
                if title and len(title) > 5:
                    if href and not href.startswith('http'):
                        href = f"https://www.jiqizhixin.com{href}"
                    
                    articles.append({
                        'source': '机器之心',
                        'title': title,
                        'link': href or 'https://www.jiqizhixin.com/articles',
                        'published': datetime.now().isoformat(),
                        'summary': '',
                        'category': 'AI科技'
                    })
        
        print(f"✓ 成功获取 {len(articles)} 条")
        return articles
        
    except Exception as e:
        print(f"✗ 失败: {e}")
        return []


def fetch_ailab():
    """抓取新智元"""
    print("\n" + "="*60)
    print("抓取新智元 (Playwright)")
    print("="*60)
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=HEADERS['User-Agent'],
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = context.new_page()
            page.goto("https://ailab.cn/", wait_until='networkidle', timeout=30000)
            page.wait_for_timeout(3000)
            
            content = page.content()
            browser.close()
        
        soup = BeautifulSoup(content, 'html.parser')
        articles = []
        
        items = soup.select('.ul_zt li')
        print(f"找到 {len(items)} 个文章项")
        
        for item in items[:10]:
            title_elem = item.select_one('.title')
            if title_elem:
                title = title_elem.get_text(strip=True)
                link_elem = item.select_one('a')
                href = link_elem.get('href', '') if link_elem else ''
                
                if title and len(title) > 5 and href:
                    if not href.startswith('http'):
                        href = f"https://ailab.cn{href}"
                    
                    articles.append({
                        'source': '新智元',
                        'title': title,
                        'link': href,
                        'published': datetime.now().isoformat(),
                        'summary': '',
                        'category': 'AI科技'
                    })
        
        print(f"✓ 成功获取 {len(articles)} 条")
        return articles
        
    except Exception as e:
        print(f"✗ 失败: {e}")
        return []


def fetch_web_source(name, url, selector, category, title_selector=None, link_selector=None):
    """通用网页抓取函数"""
    print(f"\n[{name}] 抓取中...", end=" ")
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=HEADERS['User-Agent'],
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = context.new_page()
            response = page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            if response and response.status >= 400:
                print(f"✗ HTTP {response.status}")
                browser.close()
                return []
            
            page.wait_for_timeout(5000)
            content = page.content()
            browser.close()
        
        soup = BeautifulSoup(content, 'html.parser')
        articles = []
        
        items = soup.select(selector)
        
        for item in items[:10]:
            if title_selector:
                title_elem = item.select_one(title_selector)
            else:
                title_elem = item
            
            if title_elem:
                title = title_elem.get_text(strip=True)
                
                if link_selector:
                    link_elem = item.select_one(link_selector)
                else:
                    link_elem = item if item.name == 'a' else item.find('a')
                
                href = link_elem.get('href', '') if link_elem else ''
                
                if title and len(title) > 5:
                    if href and not href.startswith('http'):
                        href = f"{url.rstrip('/')}{href}"
                    
                    articles.append({
                        'source': name,
                        'title': title,
                        'link': href or url,
                        'published': datetime.now().isoformat(),
                        'summary': '',
                        'category': category
                    })
        
        print(f"✓ {len(articles)} 条")
        return articles
        
    except Exception as e:
        print(f"✗ 失败: {str(e)[:50]}")
        return []


def save_results(all_articles):
    """保存结果"""
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    # 按来源分组
    from collections import defaultdict
    by_source = defaultdict(list)
    for article in all_articles:
        by_source[article['source']].append(article)
    
    # 按分类分组
    by_category = defaultdict(list)
    for article in all_articles:
        by_category[article.get('category', '未分类')].append(article)
    
    # 保存JSON
    today = datetime.now().strftime('%Y-%m-%d')
    json_file = os.path.join(output_dir, f'news_{today}.json')
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump({
            'date': today,
            'total': len(all_articles),
            'by_source': dict(by_source),
            'by_category': dict(by_category)
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n✓ 已保存到: {json_file}")
    return json_file


def generate_markdown(all_articles):
    """生成Markdown简报"""
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'output')
    os.makedirs(output_dir, exist_ok=True)
    
    today = datetime.now().strftime('%Y-%m-%d')
    md_file = os.path.join(output_dir, f'ai_briefing_{today}.md')
    
    # 按分类分组
    from collections import defaultdict
    by_category = defaultdict(list)
    for article in all_articles:
        by_category[article.get('category', '未分类')].append(article)
    
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(f"# 🤖 AI 每日简报 - {today}\n\n")
        f.write(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"共收集 {len(all_articles)} 条新闻\n\n")
        f.write("---\n\n")
        
        # 分类输出
        category_icons = {
            'AI科技': '🤖',
            '商业财经': '💼',
            '学术研究': '🎓',
            '政策与产业': '📜'
        }
        
        for category in ['AI科技', '商业财经', '学术研究', '政策与产业']:
            if category in by_category:
                icon = category_icons.get(category, '📰')
                f.write(f"## {icon} {category}\n\n")
                
                # 按来源分组显示
                by_source = defaultdict(list)
                for article in by_category[category]:
                    by_source[article['source']].append(article)
                
                for source, articles in by_source.items():
                    f.write(f"### {source}\n\n")
                    for article in articles[:5]:  # 每个源最多显示5条
                        f.write(f"- [{article['title']}]({article['link']})\n")
                    f.write("\n")
    
    print(f"✓ Markdown简报已生成: {md_file}")
    return md_file


def main():
    """主函数"""
    global PROXY_CONFIG
    
    print("="*60)
    print("AI 新闻抓取系统")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # 初始化代理配置
    PROXY_CONFIG = get_proxy()
    
    all_articles = []
    
    # 抓取板块1: AI科技 RSS
    rss_ai = fetch_rss_sources(RSS_SOURCES_AI, "AI科技")
    all_articles.extend(rss_ai)
    
    # 抓取板块1: AI科技 网页源
    jiqizhixin_articles = fetch_jiqizhixin()
    all_articles.extend(jiqizhixin_articles)
    
    ailab_articles = fetch_ailab()
    all_articles.extend(ailab_articles)
    
    # 抓取板块2: 商业财经
    rss_business = fetch_rss_sources(RSS_SOURCES_BUSINESS, "商业财经")
    all_articles.extend(rss_business)
    
    # 抓取板块3: 学术研究
    rss_academic = fetch_rss_sources(RSS_SOURCES_ACADEMIC, "学术研究")
    all_articles.extend(rss_academic)
    
    # 抓取板块4: 政策与产业
    rss_policy = fetch_rss_sources(RSS_SOURCES_POLICY, "政策与产业")
    all_articles.extend(rss_policy)
    
    # 保存结果
    print("\n" + "="*60)
    print("保存结果")
    print("="*60)
    
    json_file = save_results(all_articles)
    md_file = generate_markdown(all_articles)
    
    # 打印统计
    print("\n" + "="*60)
    print("抓取统计")
    print("="*60)
    
    from collections import defaultdict
    by_category = defaultdict(int)
    by_source = defaultdict(int)
    
    for article in all_articles:
        by_category[article.get('category', '未分类')] += 1
        by_source[article['source']] += 1
    
    print(f"\n总计: {len(all_articles)} 条")
    print("\n按分类:")
    for category, count in by_category.items():
        print(f"  {category}: {count} 条")
    
    print("\n按来源 (Top 10):")
    for source, count in sorted(by_source.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {source}: {count} 条")
    
    print("\n" + "="*60)
    print("完成!")
    print("="*60)


if __name__ == "__main__":
    main()
