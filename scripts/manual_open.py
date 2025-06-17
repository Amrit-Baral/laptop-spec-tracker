from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

URL = "https://www.smartprix.com/laptops"

def main():
    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # Optional: disable headless for manual interaction
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1200, 800)

    print("🌐 Opening Smartprix manually — click 'Load More' yourself.")
    driver.get(URL)

    # Let you interact manually
    print("🕒 You now have full control. Close the browser window to end.")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        driver.quit()
        print("✅ Browser closed.")

if __name__ == "__main__":
    main()
