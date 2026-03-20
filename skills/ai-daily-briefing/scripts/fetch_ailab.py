#!/usr/bin/env python3
"""
新智元新闻抓取脚本
使用playwright浏览器
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}


def fetch_with_playwright():
    """使用playwright浏览器抓取"""
    print("[新智元] 使用 Playwright 浏览器抓取...")
    
    try:
        from playwright.sync_api import sync_playwright
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=HEADERS['User-Agent'],
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = context.new_page()
            
            # 访问页面
            print("  正在加载页面...")
            page.goto("https://ailab.cn/", wait_until='networkidle', timeout=30000)
            
            # 等待内容加载
            print("  等待内容加载...")
            page.wait_for_timeout(3000)
            
            # 获取页面内容
            content = page.content()
            browser.close()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        articles = []
        
        # 使用正确的选择器
        items = soup.select('.ul_zt li')
        print(f"  ✓ 找到 {len(items)} 个文章项")
        
        for item in items[:10]:
            # 提取标题
            title_elem = item.select_one('.title')
            if title_elem:
                title = title_elem.get_text(strip=True)
                
                # 提取链接
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
                    })
        
        if articles:
            print(f"  ✓ 成功获取 {len(articles)} 条")
            return articles
        else:
            print("  ✗ 未提取到文章")
            return None
            
    except ImportError:
        print("  ✗ Playwright 未安装")
        print("    安装命令: pip install playwright && playwright install chromium")
        return None
    except Exception as e:
        print(f"  ✗ Playwright 失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def main():
    """主函数"""
    print("="*60)
    print("新智元新闻抓取")
    print("="*60)
    
    # 使用playwright抓取
    articles = fetch_with_playwright()
    
    # 输出结果
    if articles:
        print(f"\n✓ 总计获取 {len(articles)} 条新闻")
        print("\n最新文章:")
        for i, article in enumerate(articles[:5], 1):
            print(f"{i}. {article['title']}")
            print(f"   {article['link']}")
        
        # 保存结果
        output_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                   'output', 'ailab_latest.json')
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        print(f"\n已保存到: {output_file}")
        
        return articles
    else:
        print("\n✗ 抓取失败")
        return []


if __name__ == '__main__':
    main()
