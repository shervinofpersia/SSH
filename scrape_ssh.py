from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import json
import re
import time

# لیست کشورها ← مستقیماً آدرس کامل
URLS = {
    "Germany":       "https://www.vpnjantit.com/free-ssh-germany",
    "Finland":       "https://www.vpnjantit.com/free-ssh-finland",
    "United Kingdom":"https://www.vpnjantit.com/free-ssh-united-kingdom",
    "Netherlands":   "https://www.vpnjantit.com/free-ssh-netherlands",
    "India":         "https://www.vpnjantit.com/free-ssh-india",
    "France":        "https://www.vpnjantit.com/free-ssh-france",
    "United States": "https://www.vpnjantit.com/free-ssh-united-states"
}

def get_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def scrape_page(driver, country_name, url):
    print(f"🌐 {country_name}: {url}")
    try:
        driver.get(url)
        time.sleep(5)  # صبر برای لود کامل
        soup = BeautifulSoup(driver.page_source, "html.parser")
    except Exception as e:
        print(f"  ❌ خطا: {e}")
        return []

    servers = []
    for block in soup.select(".col-lg-3 .block-7, .col-md-6 .block-7"):
        heading = block.select_one(".heading strong, .heading b strong")
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
            flag = f"https://www.vpnjantit.com{src}" if src.startswith('/') else src

        servers.append({
            "name": name,
            "host": host,
            "ports": sorted(set(ports), key=int),
            "features": list(set(features)),
            "status": "Available" if is_avail else "Full",
            "country": country_name,
            "flag": flag,
        })

    print(f"  ✅ {len(servers)} سرور")
    return servers

def main():
    driver = get_driver()
    all_servers = []
    try:
        for country, url in URLS.items():
            all_servers += scrape_page(driver, country, url)
            time.sleep(1)
    finally:
        driver.quit()

    # حذف تکراری بر اساس host
    unique, seen = [], set()
    for s in all_servers:
        key = s["host"]
        if key and key not in seen:
            seen.add(key)
            unique.append(s)
        elif not key:
            unique.append(s)

    with open("ssh_configs.json", "w", encoding="utf-8") as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)

    print(f"\n🎯 مجموع: {len(unique)} سرور")

if __name__ == "__main__":
    main()
