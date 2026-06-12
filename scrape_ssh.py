import requests
from bs4 import BeautifulSoup
import json
import re
import os
from urllib.parse import urljoin

BASE_URL = "https://www.vpnjantit.com"
# لیست کشورها - می‌توانید اضافه یا کم کنید
COUNTRIES = [
    "united-states",
    "germany",
    "united-kingdom",
    "finland",
    "netherlands",
    "india",
    "france",
    # سایر کشورهای قوی: "sweden", "canada", "japan", "singapore" ...
]

def scrape_country(country_slug):
    url = f"{BASE_URL}/free-ssh?server={country_slug}"
    print(f"🌐 دریافت اطلاعات از: {url}")
    resp = requests.get(url)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    servers = []

    # هر سرور در یک div با کلاس col-lg-3 و block-7 قرار دارد
    for block in soup.select(".col-lg-3 .block-7"):
        # نام سرور
        heading_tag = block.select_one(".heading strong")
        if not heading_tag:
            continue
        name = heading_tag.get_text(strip=True)

        # هاست (دامنه‌ای که به vpnjantit.com ختم می‌شود)
        host_text = block.get_text()
        host_match = re.search(r"([a-zA-Z0-9.-]+\.vpnjantit\.com)", host_text)
        host = host_match.group(1) if host_match else ""

        # استخراج پورت‌ها (همه‌ی اعداد در خطوط حاوی Port به جز UDP CUSTOM)
        ports = []
        for li in block.find_all("li"):
            text = li.get_text()
            if "Port" in text and "UDP CUSTOM" not in text:
                ports += re.findall(r"\b(\d{1,5})\b", text)

        # ویژگی‌های خاص
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

        # وضعیت (Available/Full)
        status_tag = block.select_one('font[size="5"]')
        status_text = status_tag.get_text(strip=True) if status_tag else ""
        is_available = "available" in status_text.lower()

        # دریافت تصویر پرچم از داخل heading
        img_tag = block.select_one(".heading img")
        flag_src = img_tag["src"] if img_tag else ""
        flag_url = urljoin(BASE_URL, flag_src) if flag_src else ""

        # نام کشور از alt تصویر، یا از slug
        country_name = (
            img_tag["alt"] if (img_tag and img_tag.has_attr("alt"))
            else country_slug.replace("-", " ").title()
        )

        servers.append({
            "name": name,
            "host": host,
            "ports": sorted(set(ports), key=int),  # حذف تکراری و مرتب‌سازی عددی
            "features": list(set(features)),
            "status": "Available" if is_available else "Full",
            "country": country_name,
            "flag": flag_url
        })

    print(f"  ✅ {len(servers)} سرور استخراج شد.")
    return servers


def main():
    all_servers = []

    for slug in COUNTRIES:
        try:
            all_servers.extend(scrape_country(slug))
        except Exception as e:
            print(f"  ❌ خطا در دریافت {slug}: {e}")

    # حذف سرورهای تکراری بر اساس host
    unique = []
    seen = set()
    for s in all_servers:
        key = s["host"]
        if key and key not in seen:
            seen.add(key)
            unique.append(s)
        elif not key:  # اگر host خالی بود (مثلاً تبلیغ) باز هم نگه می‌داریم
            unique.append(s)

    # ذخیره‌سازی
    output_path = os.path.join(os.path.dirname(__file__), "ssh_configs.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(unique, f, ensure_ascii=False, indent=2)

    print(f"\n🎯 مجموع سرورهای یکتا: {len(unique)} → ذخیره در {output_path}")


if __name__ == "__main__":
    main()
