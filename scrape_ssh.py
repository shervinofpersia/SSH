import requests
from bs4 import BeautifulSoup
import json
import re
import os
from urllib.parse import urljoin
import time

BASE_URL = "https://www.vpnjantit.com"
COUNTRIES = [
    "united-states", "germany", "united-kingdom",
    "finland", "netherlands", "india", "france"
]
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

def scrape_country(slug):
    url = f"{BASE_URL}/free-ssh?server={slug}"
    print(f"🌐 {url}")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        print(f"  ❌ خطا: {e}")
        return []
    soup = BeautifulSoup(resp.text, "html.parser")
    servers = []
    for block in soup.select(".col-lg-3 .block-7"):
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
        status_text = block.select_one('font[size="5"]')
        is_avail = status_text and "available" in status_text.get_text(strip=True).lower()
        img = block.select_one(".heading img")
        flag = urljoin(BASE_URL, img["src"]) if img else ""
        country = img.get("alt") if img else slug.replace("-", " ").title()
        servers.append({
            "name": name, "host": host,
            "ports": sorted(set(ports), key=int),
            "features": list(set(features)),
            "status": "Available" if is_avail else "Full",
            "country": country, "flag": flag
        })
    print(f"  ✅ {len(servers)} server(s)")
    return servers

def main():
    all_servers = []
    for slug in COUNTRIES:
        all_servers += scrape_country(slug)
        time.sleep(0.3)
    # حذف تکراری بر اساس host
    uniq, seen = [], set()
    for s in all_servers:
        key = s["host"]
        if key and key not in seen:
            seen.add(key)
            uniq.append(s)
        elif not key:
            uniq.append(s)
    # ذخیره در ریشه‌ی ریپازیتوری
    out = "ssh_configs.json"
    with open(out, "w", encoding="utf-8") as f:
        json.dump(uniq, f, ensure_ascii=False, indent=2)
    print(f"\n✅ ذخیره شد: {out} ({len(uniq)} سرور)")

if __name__ == "__main__":
    main()
