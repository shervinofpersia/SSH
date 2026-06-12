# ☬SHΞN™ SSH Tunnel Hub

<p align="center">
  <img src="https://img.shields.io/github/actions/workflow/status/shervinofpersia/SSH/scrape_ssh.yml?label=Scrape%20Status&style=for-the-badge" alt="Scraper Status">
  <img src="https://img.shields.io/github/last-commit/shervinofpersia/SSH?style=for-the-badge" alt="Last Commit">
  <img src="https://img.shields.io/badge/license-MIT-blue?style=for-the-badge" alt="License">
</p>

<p align="center">
  <b>Automated SSH Tunnel Configs Aggregator + Live Filterable Dashboard</b><br>
  <em>Freshly scraped every 3 hours from vpnjantit.com — curated for Psiphon & general use.</em>
</p>

---

## 🧠 How It Works

1. **Python scraper** (powered by Selenium + BeautifulSoup) pulls live SSH server info from vpnjantit.com across **7 major countries**:
   - 🇺🇸 United States
   - 🇩🇪 Germany
   - 🇫🇮 Finland
   - 🇬🇧 United Kingdom
   - 🇳🇱 Netherlands
   - 🇮🇳 India
   - 🇫🇷 France

2. A **GitHub Action** runs the scraper every 3 hours and commits the collected data into a single `ssh_configs.json` file.

3. The **web dashboard** (hosted via GitHub Pages) fetches that JSON in real time and displays all configs in a beautiful glass‑morphism UI with:
   - One‑click copy for hosts & ports
   - Country circle filters
   - Availability status badges
   - Fully responsive (desktop table + mobile cards)

---

## ⚡ Live Demo

👉 **[Launch Dashboard](https://shervinofpersia.github.io/SSH/)**  

*(Enable GitHub Pages from `main` branch, root directory.)*

---

## 🎯 Features

- ✅ **Zero manual work** – everything is automated.
- 🌍 **Multi‑country** – filter by nation flag.
- 📋 **Clipboard magic** – tap any host/port to copy instantly.
- 🧩 **Clean UI** – Tailwind CSS + glass‑morphism, inspired by hacker‑terminal aesthetic.
- 📲 **Mobile friendly** – dedicated card layout for small screens.
- ⏰ **Always fresh** – updated every 3 hours, round the clock.
‍ ‍
``` ☬ SHΞЯVIN™
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⠉⠉⠉⠉⠉⠉⠉⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⡿⠟⠋⢀⣤⣾⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⠉⠀⠀⠚⠛⠛⠛⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣶⣶⣶⣶⣶⣶⣶⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣀⣀⣀⣀⣀⣀⣀⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⠀⠉⠛⠿⠿⣿⣿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣷⣶⣤⠤⠀⠉⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⠉⠉⢀⣀⣤⣶⣾⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⠒⠛⠛⠛⠛⠛⠛⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⠀⣶⣶⠀⢰⣶⣶⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⡀⠙⠋⢀⡀⠈⠛⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⠿⣶⡶⠿⣿⣿⠶⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⠀⣿⡇⠀⣿⣿⠀⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⠀⣿⣇⣀⣿⣿⠀⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⠛⠛⠛⠛⠛⠛⠛⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣶⣶⣶⠀⣶⣶⣶⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⠿⠿⠿⠀⠿⠿⠿⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣤⣤⣤⣤⣤⣤⣤⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⠋⢀⣿⠋⢀⡀⠙⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣇⠀⢿⡏⢀⣾⡿⠀⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣤⣀⣀⣼⣇⣀⣰⣿⣿⣿⣿⣿
⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿
☬  Exclusive  SHΞN™   made
```
