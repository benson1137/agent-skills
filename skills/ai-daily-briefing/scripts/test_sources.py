#!/usr/bin/env python3
"""
测试12个待测试新闻源的实际可用性
"""

import feedparser
import requests
from datetime import datetime
from playwright.sync_api import sync_playwright
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}

# 待测试的12个源
TEST_SOURCES = {
    # 商业财经 - 3个网页源
    "财经网": {"url": "https://www.caijing.com.cn/", "type": "web"},
    "第一财经": {"url": "https://www.yicai.com/", "type": "web"},
    "界面新闻": {"url": "https://www.jiemian.com/", "type": "web"},
    
    # 政策与产业 - 8个政府网站
    "国务院": {"url": "http://www.gov.cn/zhengce/", "type": "web"},
    "工信部": {"url": "http://www.miit.gov.cn/", "type": "web"},
    "发改委": {"url": "http://www.ndrc.gov.cn/", "type": "web"},
    "网信办": {"url": "http://www.cac.gov.cn/", "type": "web"},
    "上海市政府": {"url": "http://www.shanghai.gov.cn/", "type": "web"},
    "广东省政府": {"url": "http://www.gd.gov.cn/", "type": "web"},
    "深圳市政府": {"url": "http://www.sz.gov.cn/", "type": "web"},
    "武汉市政府": {"url": "http://www.wuhan.gov.cn/", "type": "web"},
    
    # 商业财经 - 1个RSS源
    "Forbes": {"url": "https://www.forbes.com/feed/", "type": "rss"},
}


def test_rss_source(name, url):
    """测试RSS源"""
    try:
        print(f"\n[{name}] 测试RSS...", end=" ")
        feed = feedparser.parse(url)
        
        if feed.bozo and hasattr(feed, 'bozo_exception'):
            print(f"⚠️ 解析警告: {str(feed.bozo_exception)[:50]}")
        
        if feed.entries:
            print(f"✅ 可用 - {len(feed.entries)} 条")
            return True, len(feed.entries)
        else:
            print(f"⚠️ 无内容")
            return False, 0
            
    except Exception as e:
        print(f"❌ 失败: {str(e)[:60]}")
        return False, 0


def test_web_source(name, url):
    """测试网页源（使用Playwright）"""
    try:
        print(f"\n[{name}] 测试网页...", end=" ")
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent=HEADERS['User-Agent'],
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = context.new_page()
            
            # 设置超时
            response = page.goto(url, wait_until='domcontentloaded', timeout=30000)
            
            if response:
                status = response.status
                if status >= 400:
                    print(f"❌ HTTP {status}")
                    browser.close()
                    return False, status
                
                # 等待页面加载
                page.wait_for_timeout(5000)
                
                # 获取页面标题
                title = page.title()
                
                # 检查是否有内容
                content = page.content()
                has_content = len(content) > 1000
                
                browser.close()
                
                if has_content:
                    print(f"✅ 可用 - 标题: {title[:30]}...")
                    return True, status
                else:
                    print(f"⚠️ 页面内容过少")
                    return False, status
            else:
                print(f"❌ 无响应")
                browser.close()
                return False, 0
                
    except Exception as e:
        print(f"❌ 失败: {str(e)[:60]}")
        return False, str(e)[:50]


def main():
    """主函数"""
    print("="*70)
    print("测试12个待测试新闻源")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    results = {}
    
    for name, config in TEST_SOURCES.items():
        if config['type'] == 'rss':
            success, info = test_rss_source(name, config['url'])
        else:
            success, info = test_web_source(name, config['url'])
        
        results[name] = {
            'success': success,
            'info': info,
            'type': config['type']
        }
        
        time.sleep(1)  # 避免请求过快
    
    # 打印总结
    print("\n" + "="*70)
    print("测试结果总结")
    print("="*70)
    
    working = []
    failed = []
    
    for name, result in results.items():
        if result['success']:
            working.append(name)
            print(f"✅ {name}: 可用")
        else:
            failed.append(name)
            print(f"❌ {name}: 失败 ({result['info']})")
    
    print("\n" + "="*70)
    print(f"总计: {len(working)} 个可用, {len(failed)} 个失败")
    print("="*70)
    
    if failed:
        print("\n失败的源:")
        for name in failed:
            print(f"  - {name}")
    
    return results


if __name__ == "__main__":
    results = main()
