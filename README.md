# 💻 Realtime Laptop Spec Tracker 🚀

![Python](https://img.shields.io/badge/python-3.11-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A cross-platform laptop specification tracker and validator that scrapes multiple sources, merges them into a unified format, and prepares for filtering, benchmarking, and spec-based analytics.

---

## 🚀 Features

- Manual CAPTCHA bypass via guided prompt  
- Auto-clicks **"Load More"** until all laptops are visible  
- Option to **manually stop loading** at any point  
- Extracts product name, raw specs, price, and **parsed fields** like:
  - Processor
  - RAM size & type
  - Storage (SSD / HDD)
  - GPU & VRAM
  - OS and display size  
- Saves all data to a timestamped CSV (e.g. `data/smartprix_laptops_20250619-145531.csv`)

---

## 🧰 Requirements

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate    # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

This script uses:
- `selenium` for browser automation
- `pandas` for data handling
- `chromedriver` must be installed and in your PATH

---

## ⚙️ Usage

```bash
python scripts/smartprix_scraper.py
```

1. The script opens the Smartprix laptop page in Chrome  
2. It prompts you to open and solve any CAPTCHA manually  
3. It begins clicking "Load More" in a loop  
4. After each load, you can press:
   - **Enter** to load more
   - Type `'stop'` to end scrolling and begin scraping  
5. Extracted laptops are saved to a CSV inside the `data/` folder

---

## 🧠 Structure

- `get_driver()` — Chrome WebDriver configuration  
- `load_all_products()` — Handles scrolling + manual termination  
- `parse_specs()` — Cleans and parses spec strings into structured fields  
- `extract_laptops()` — Gathers all laptop cards and enriches with parsed data  
- `main()` — Orchestrates everything start to finish  

---

## 📁 Output Example

| Name           | Price     | Processor         | RAM Size (GB) | Storage SSD (GB) |
|----------------|-----------|-------------------|----------------|-------------------|
| Acer Aspire 7  | ₹54,990   | AMD Ryzen 5 7530U | 16             | 512               |

---

## 🙌 Credits

Built by [Amrit](https://github.com/your-username)  
MIT License · For educational and portfolio purposes