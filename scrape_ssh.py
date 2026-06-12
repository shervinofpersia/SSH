from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
import re
import time
import os

BASE_URL = "https://www.vpnjantit.com"
COUNTRIES = [
    "united-states", "germany", "united-kingdom",
    "finland", "netherlands", "india", "france",
]

def get_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")  # headless جدید
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=chrome_options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def scrape_country(driver, slug):
    url = f"{BASE_URL}/free-ssh?server={slug}"
    print(f"🌐 {url}")
    try:
        driver.get(url)
        # صبر برای لود کامل و گذر از Cloudflare
        time.sleep(5)
        html = driver.page_source
    except Exception as e:
        print(f"  ❌ خطا در بارگذاری: {e}")
        return []

    soup = BeautifulSoup(html, "html.parser")
    servers = []

    # یافتن کارت‌ها
    for block in soup.select(".col-lg-3 .block-7, .col-md-6 .block-7"):
        heading = block.select_one(".heading strong, .heading b strong, .heading font strong")
        if not heading:
            continue
        name = heading.get_text(strip=True)

        host_match = re.search(r"([a-zA-Z0-9.-]+\.vpnjantit\.com)", block.get_text())
        host = host_match.group(1) if host_match else ""

        ports = []
        for li in block.find_all("li"):
            text = li.get_text()
            if "Port" in text and "UDP CUSTOM" not in text:
                ports += re.findall(r"\b(\d{2,5})\b", text)

        features = []
        for li in block.find_all("li"):
            text = li.get_text()
            if "WebSocket CDN" in text: features.append("WebSocket CDN")
            if "SlowDNS" in text: features.append("SlowDNS")
            if "BADVPN UDPGW" in text:
                m = re.search(r"(\d{1,5},\d{1,5})\s*BADVPN", text)
                if m: features.append(f"BADVPN: {m.group(1)}")
            if "UDP CUSTOM" in text: features.append("UDP Custom")

        status_tag = block.select_one('font[size="5"]')
        is_avail = status_tag and "available" in status_tag.get_text(strip=True).lower()

        img = block.select_one(".heading img")
        flag = ""
        if img:
            src = img["src"]
            flag = f"{BASE_URL}{src}" if src.startswith('/') else src
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

    print(f"  ✅ {len(servers)} سرور")
    return servers

def main():
    driver = get_driver()
    all_servers = []
    try:
        for slug in COUNTRIES:
            all_servers += scrape_country(driver, slug)
            time.sleep(1)  # فاصله بین درخواست‌ها
    finally:
        driver.quit()

    # حذف تکراری
    unique, seen = [], set()
    for s in all_servers:
        key = s["host"]
        if key and key not in seen:
            seen.add(key)
            unique.append(s)
        elif not key:
            unique.append(s)

    out_path = "ssh_configs.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)

    print(f"\n🎯 {len(unique)} سرور یکتا در {out_path} ذخیره شد.")

if __name__ == "__main__":
    main()
