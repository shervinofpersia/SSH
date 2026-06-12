import requests
from bs4 import BeautifulSoup
import json
import re
import os
from urllib.parse import urljoin
import time

BASE_URL = "https://www.vpnjantit.com"

# کشورهای هدف
COUNTRIES = [
    "united-states",
    "germany",
    "united-kingdom",
    "finland",
    "netherlands",
    "india",
    "france",
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

def scrape_country(country_slug):
    url = f"{BASE_URL}/free-ssh?server={country_slug}"
    print(f"🌐 دریافت: {url}")
    try:
        resp = requests.get(url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception as e:
        print(f"  ❌ خطا در دریافت {country_slug}: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    servers = []

    # هر سرور در یک div با کلاس col-lg-3 و block-7
    blocks = soup.select(".col-lg-3 .block-7")
    print(f"  📦 تعداد بلاک‌های پیدا شده: {len(blocks)}")

    for block in blocks:
        # نام سرور
        heading_tag = block.select_one(".heading strong, .heading b strong, .heading font strong")
        if not heading_tag:
            continue
        name = heading_tag.get_text(strip=True)

        # هاست
        host_text = block.get_text(separator=" ", strip=True)
        host_match = re.search(r"([a-zA-Z0-9.-]+\.vpnjantit\.com)", host_text)
        host = host_match.group(1) if host_match else ""

        # پورت‌ها
        ports = []
        for li in block.find_all("li"):
            text = li.get_text()
            if "Port" in text and "UDP CUSTOM" not in text:
                ports += re.findall(r"\b(\d{2,5})\b", text)

        # ویژگی‌ها
        features = []
        for li in block.find_all("li"):
            text = li.get_text()
            if "WebSocket CDN" in text:
                features.append("WebSocket CDN")
            if "SlowDNS" in text:
                features.append("SlowDNS")
            if "BADVPN UDPGW" in text:
                m = re.search(r"(\d{1,5},\d{1,5})\s*BADVPN", text)
                if m:
                    features.append(f"BADVPN: {m.group(1)}")
            if "UDP CUSTOM" in text:
                features.append("UDP Custom")

        # وضعیت
        status_tag = block.select_one('font[size="5"]')
        status_text = status_tag.get_text(strip=True) if status_tag else ""
        is_available = "available" in status_text.lower()

        # پرچم
        img_tag = block.select_one(".heading img")
        flag_src = img_tag["src"] if img_tag else ""
        flag_url = urljoin(BASE_URL, flag_src) if flag_src else ""

        # نام کشور
        country_name = (
            img_tag["alt"].strip() if (img_tag and img_tag.get("alt"))
            else country_slug.replace("-", " ").title()
        )

        servers.append({
            "name": name,
            "host": host,
            "ports": sorted(set(ports), key=int),
            "features": list(set(features)),
            "status": "Available" if is_available else "Full",
            "country": country_name,
            "flag": flag_url,
        })

    print(f"  ✅ {len(servers)} سرور استخراج شد.")
    return servers


def main():
    all_servers = []
    for slug in COUNTRIES:
        all_servers.extend(scrape_country(slug))
        time.sleep(0.5)  # فاصله‌ی کوتاه برای جلوگیری از فشار

    # حذف تکراری (بر اساس host)
    unique = []
    seen = set()
    for s in all_servers:
        key = s["host"]
        if key and key not in seen:
            seen.add(key)
            unique.append(s)
        elif not key:
            unique.append(s)   # موارد بدون هاست (تبلیغاتی) هم حفظ شوند

    output_path = os.path.join(os.path.dirname(__file__), "ssh_configs.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)

    print(f"\n🎯 مجموع سرورهای یکتا: {len(unique)} → {output_path}")

if __name__ == "__main__":
    main()
