import time
import pandas as pd
import unicodedata
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

URL = "https://www.smartprix.com/laptops"
timestamp = time.strftime("%Y%m%d-%H%M%S")
OUTPUT_CSV = f"data/smartprix_laptops_{timestamp}.csv"

def get_driver():
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1200, 800)
    return driver

def wait_for_first_page(driver):
    try:
        WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.sm-product"))
        )
        return True
    except TimeoutException:
        print("❌ Timeout: First product cards did not load.")
        return False

def manual_captcha_workaround(driver):
    print("⚠️ CAPTCHA likely not triggered yet.")
    print("👉 Opening first laptop in new tab. Solve CAPTCHA if prompted.")
    original_window = driver.current_window_handle

    try:
        first_link = driver.find_element(By.CSS_SELECTOR, "a.name")
        href = first_link.get_attribute("href")
        driver.execute_script(f"window.open('{href}', '_blank');")
        time.sleep(5)
        input("✅ After solving the CAPTCHA in the new tab, press [Enter] to continue scraping...\n")
        driver.switch_to.window(original_window)
    except Exception as e:
        print(f"⚠️ Could not trigger CAPTCHA workaround: {e}")

def load_all_products(driver, max_clicks=200, max_stale_attempts=5, max_runtime_sec=3600):
    print("🔁 Clicking 'Load More' until all laptops are loaded or timeout is reached...")
    previous_count = 0
    stale_attempts = 0
    start_time = time.time()

    for i in range(max_clicks):
        elapsed = time.time() - start_time
        if elapsed > max_runtime_sec:
            print(f"⏳ Runtime exceeded {max_runtime_sec//60} minutes. Stopping.")
            break

        product_cards = driver.find_elements(By.CSS_SELECTOR, "div.sm-product")
        current_count = len(product_cards)

        if current_count == previous_count:
            stale_attempts += 1
            print(f"⚠️ No new laptops after click #{i+1}. Attempt {stale_attempts}/{max_stale_attempts}.")
            if stale_attempts >= max_stale_attempts:
                print("🚫 Max no-change attempts reached. Saving snapshot before exit.")
                timestamp = time.strftime("%Y%m%d-%H%M%S")
                driver.save_screenshot(f"data/loadmore_fail_{timestamp}.png")
                break
        else:
            stale_attempts = 0
            previous_count = current_count

        try:
            load_more_btn = driver.find_element(By.CSS_SELECTOR, "div.sm-load-more")
            if not load_more_btn.is_displayed():
                print("✅ 'Load More' button hidden. End of products.")
                break

            print(f"⬇️ Clicking Load More ({i+1}) | Total loaded: {current_count}")
            time.sleep(3)
            driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", load_more_btn)
            time.sleep(2.5)
            load_more_btn.click()

            WebDriverWait(driver, 10).until(
                lambda d: len(d.find_elements(By.CSS_SELECTOR, "div.sm-product")) > current_count
            )
            time.sleep(2)

        except TimeoutException:
            print("❌ Timeout waiting after click. Saving snapshot.")
            timestamp = time.strftime("%Y%m%d-%H%M%S")
            driver.save_screenshot(f"data/loadmore_timeout_{timestamp}.png")
            break
        except (NoSuchElementException, ElementClickInterceptedException):
            print("⚠️ 'Load More' not clickable or missing. Scrolling up slightly...")
            driver.execute_script("window.scrollBy(0, -100);")
            time.sleep(2)
        # Ask user if they want to stop loading more
        user_input = input("🔄 Press [Enter] to load more or type 'stop' to end and start scraping: ")
        if user_input.strip().lower() == 'stop':
            print("🛑 Manual stop triggered. Proceeding to scrape loaded laptops...\n")
            break

# 👇 Paste this ABOVE extract_laptops()
import re

def parse_specs(specs):
    parsed = {
        "Processor": None,
        "RAM Size (GB)": None,
        "RAM Type": None,
        "Storage SSD (GB)": None,
        "Storage HDD (GB)": None,
        "Storage Type": None,
        "GPU": None,
        "VRAM (GB)": None,
        "OS": None,
        "Display Size (inch)": None
    }

    if not specs or specs == "N/A":
        return parsed

    if match := re.search(r"(Intel|AMD|Apple|M1|M2|M3|M4)[^/|,]+", specs, re.IGNORECASE):
        parsed["Processor"] = match.group().strip()

    if match := re.search(r"(\d+)\s?GB\s?(?:DDR\d|LPDDR\d)?\s?RAM", specs, re.IGNORECASE):
        parsed["RAM Size (GB)"] = int(match.group(1))

    if match := re.search(r"(DDR[345]|LPDDR[45])", specs, re.IGNORECASE):
        parsed["RAM Type"] = match.group().strip()

    if match := re.search(r"(\d+)\s?TB\s?SSD", specs, re.IGNORECASE):
        parsed["Storage SSD (GB)"] = int(match.group(1)) * 1024
    elif match := re.search(r"(\d+)\s?GB\s?SSD", specs, re.IGNORECASE):
        parsed["Storage SSD (GB)"] = int(match.group(1))

    if match := re.search(r"(\d+)\s?TB\s?HDD", specs, re.IGNORECASE):
        parsed["Storage HDD (GB)"] = int(match.group(1)) * 1024
    elif match := re.search(r"(\d+)\s?GB\s?HDD", specs, re.IGNORECASE):
        parsed["Storage HDD (GB)"] = int(match.group(1))

    if "SSD" in specs:
        parsed["Storage Type"] = "SSD"
    elif "HDD" in specs:
        parsed["Storage Type"] = "HDD"
    elif "eMMC" in specs:
        parsed["Storage Type"] = "eMMC"

    if match := re.search(r"(RTX\s?\d{3,4}|GTX\s?\d{3,4}|Intel Iris Xe|Radeon\s?\w+|Graphics\s\d+)", specs, re.IGNORECASE):
        parsed["GPU"] = match.group().strip()

    if match := re.search(r"(\d+)\s?GB\s?(VRAM|Graphics|Graph|RTX|GTX)", specs, re.IGNORECASE):
        parsed["VRAM (GB)"] = int(match.group(1))

    if match := re.search(r"(Windows\s?\d+|Win11|Win10|Mac\s?OS|MacOS|DOS|Linux|Ubuntu)", specs, re.IGNORECASE):
        parsed["OS"] = match.group().replace("Win11", "Windows 11").replace("Win10", "Windows 10").strip()

    if match := re.search(r"(\d{2,3}\.?\d?)\s?-?\s?inch", specs, re.IGNORECASE):
        parsed["Display Size (inch)"] = float(match.group(1))

    return parsed

def extract_laptops(driver):
    print("🔍 Extracting laptop details...")
    laptops = []
    product_cards = driver.find_elements(By.CSS_SELECTOR, "div.sm-product")

    for card in product_cards:
        try:
            name = card.find_element(By.CSS_SELECTOR, "a.name").text.strip()
        except:
            name = "N/A"
        try:
            specs_raw = card.find_element(By.CSS_SELECTOR, ".specs").text.strip()
            specs = unicodedata.normalize("NFKC", specs_raw).replace("\u2009", " ")
        except:
            specs = "N/A"
        try:
            price = card.find_element(By.CSS_SELECTOR, ".price").text.strip()
        except:
            price = "N/A"

        details = parse_specs(specs)

        laptop = {
            "Name": name,
            "Specs": specs,
            "Price": price,
            **details
        }

        laptops.append(laptop)

    return laptops

def main():
    driver = get_driver()
    print(f"🌐 Opening: {URL}")
    driver.get(URL)

    if not wait_for_first_page(driver):
        driver.quit()
        return

    manual_captcha_workaround(driver)

    laptops = []

    try:
        load_all_products(driver)
    except KeyboardInterrupt:
        print("\n🛑 Manual interrupt during loading. Proceeding with what’s visible...")

    try:
        laptops = extract_laptops(driver)
    except Exception as e:
        print(f"\n⚠️ Could not extract laptops after interruption: {e}")
        laptops = []

    driver.quit()

    if laptops:
        df = pd.DataFrame(laptops)
        df.to_csv(OUTPUT_CSV, index=False)
        print(f"✅ Saved {len(df)} laptops to {OUTPUT_CSV}")
    else:
        print("⚠️ No laptops collected. Nothing saved.")

if __name__ == "__main__":
    main()
