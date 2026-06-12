import cloudscraper
from bs4 import BeautifulSoup
import json
import re
import os
import time

BASE_URL = "https://www.vpnjantit.com"
COUNTRIES = [
    "united-states", "germany", "united-kingdom",
    "finland", "netherlands", "india", "france"
]

scraper = cloudscraper.create_scraper(
    browser={'custom': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
)

def scrape_country(slug):
    url = f"{BASE_URL}/free-ssh?server={slug}"
    print(f"\n🌐 {url}")
    try:
        resp = scraper.get(url, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        print(f"  ❌ خطا در دریافت: {e}")
        return []

    soup = BeautifulSoup(resp.text, 'html.parser')
    
    # سلکتورهای مختلف برای پیدا کردن کارت سرورها
    possible_selectors = [
        ".col-lg-3 .block-7",
        ".col-md-6 .block-7",
        ".col-lg-4 .block-7",
        ".services.border",                     # کلاس قدیمی
        "div[class*='col'] .block-7",           # هر col همراه با block-7
    ]
    
    blocks = []
    for sel in possible_selectors:
        blocks = soup.select(sel)
        if blocks:
            print(f"  🔍 با سلکتور '{sel}' → {len(blocks)} بلاک پیدا شد")
            break
    
    if not blocks:
        # چاپ بخشی از HTML برای اشکال‌زدایی
        body = soup.body
        if body:
            sample = body.get_text(separator=' ', strip=True)[:500]
            print(f"  ⚠️ هیچ بلاکی پیدا نشد. نمونه متن:\n{sample}")
        return []

    servers = []
    for block in blocks:
        # نام سرور
        heading = block.select_one(
            ".heading strong, .heading b, .heading font strong, h2 strong, h3 strong"
        )
        if not heading:
            continue
        name = heading.get_text(strip=True)

        # هاست (دامنه)
        text_all = block.get_text(separator=' ', strip=True)
        host_match = re.search(r"([a-zA-Z0-9.-]+\.vpnjantit\.com)", text_all)
        host = host_match.group(1) if host_match else ""

        # پورت‌ها
        ports = []
        for li in block.find_all("li"):
            t = li.get_text()
            if "Port" in t and "UDP CUSTOM" not in t:
                ports += re.findall(r"\b(\d{2,5})\b", t)

        # ویژگی‌ها
        features = []
        for li in block.find_all("li"):
            t = li.get_text()
            if "WebSocket CDN" in t: features.append("WebSocket CDN")
            if "SlowDNS" in t: features.append("SlowDNS")
            if "BADVPN UDPGW" in t:
                m = re.search(r"(\d{1,5},\d{1,5})\s*BADVPN", t)
                if m: features.append(f"BADVPN: {m.group(1)}")
            if "UDP CUSTOM" in t: features.append("UDP Custom")

        # وضعیت
        status_tag = block.select_one('font[size="5"]')
        is_avail = status_tag and "available" in status_tag.get_text(strip=True).lower()

        # پرچم و کشور
        img = block.select_one("img[src*='bendera'], .heading img")
        flag_src = img["src"] if img else ""
        flag = f"https://www.vpnjantit.com{flag_src}" if flag_src.startswith('/') else flag_src
        country = img.get("alt") if img else slug.replace("-", " ").title()

        servers.append({
            "name": name,
            "host": host,
            "ports": sorted(set(ports), key=int),
            "features": list(set(features)),
            "status": "Available" if is_avail else "Full",
            "country": country,
            "flag": flag,
        })

    print(f"  ✅ {len(servers)} سرور استخراج شد")
    return servers

def main():
    all_servers = []
    for slug in COUNTRIES:
        servers = scrape_country(slug)
        all_servers.extend(servers)
        time.sleep(0.5)

    # حذف تکراری بر اساس host
    unique, seen = [], set()
    for s in all_servers:
        key = s["host"]
        if key and key not in seen:
            seen.add(key)
            unique.append(s)
        elif not key:
            unique.append(s)

    out = "ssh_configs.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)

    print(f"\n🎯 مجموع سرورهای یکتا: {len(unique)} → {out}")

if __name__ == "__main__":
    main()
