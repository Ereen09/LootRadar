import re
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from models.game import Game, PriceRecord

class SteamScraper:
    BASE_URL = "https://store.steampowered.com/search/?specials=1"
    def __init__(self, headless: bool = True, timeout: int = 10) -> None:
        self.timeout = timeout
        self.options = Options()

        if headless:
            self.options.add_argument("--headless=new")

        self.options.add_argument("--window-size=1920,1080")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument("--no-sandbox")
        self.options.add_argument(
            "user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
        )
        self.driver: webdriver.Chrome | None = None

    def __enter__(self) -> "SteamScraper":
       
        self.driver = webdriver.Chrome(options=self.options)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        
        if self.driver is not None:
            self.driver.quit()
            self.driver = None
    def _parse_price(self, raw_text: str) -> float:
        
        if not raw_text:
            return 0.0

        cleaned_text = raw_text.strip().lower()
        if "free" in cleaned_text or "ücretsiz" in cleaned_text:
            return 0.0

        
        normalized = cleaned_text.replace(",", ".")

       
        match = re.search(r"\d+(?:\.\d+)?", normalized)
        if not match:
            raise ValueError(f"Geçersiz fiyat metni ayrıştırılamadı: '{raw_text}'")

        return float(match.group())

    def _parse_discount(self, raw_text: str) -> int:
        
        if not raw_text:
            return 0

        
        match = re.search(r"\d+", raw_text)
        if not match:
            return 0

        return int(match.group())       
    def _scroll_page(self,scroll_count: int = 3, pause_seconds: float = 2.0) -> None:
        
        if self.driver is None:
            return

        for _ in range(scroll_count):
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(pause_seconds)
    def fetch_specials(self,  scroll_count: int = 3) :
        if self.driver is None:
            raise RuntimeError("WebDriver is not initialized. Use 'with' statement to manage the context.")
        self.driver.get(self.BASE_URL)
        wait = WebDriverWait(self.driver, self.timeout)
        try:
            wait.until(EC.presence_of_element_located((By.CLASS_NAME, "search_result_row")))
        except TimeoutException:
            print("Timeout: No search results found.")
            return []
        self._scroll_page(scroll_count=scroll_count)
        rows = self.driver.find_elements(By.CLASS_NAME, "search_result_row")
        scraped_games: list[Game] = [] 
        for row in rows:
            try:
                app_id = row.get_attribute("data-ds-appid")
                
                if not app_id or "," in app_id:
                    continue

                title = row.find_element(By.CSS_SELECTOR, "span.title").text
                raw_url = row.get_attribute("href") or ""
                clean_url = raw_url.split("?")[0]  #
               
                discount_el = row.find_element(By.CSS_SELECTOR, "div.discount_pct")
                original_price_el = row.find_element(By.CSS_SELECTOR, "div.discount_original_price")
                final_price_el = row.find_element(By.CSS_SELECTOR, "div.discount_final_price")

                
                discount_percent = self._parse_discount(discount_el.text)
                normal_price = self._parse_price(original_price_el.text)
                sale_price = self._parse_price(final_price_el.text)

                
                price_record = PriceRecord(
                    normal_price=normal_price,
                    sale_price=sale_price,
                    discount_percent=discount_percent,
                )
                game = Game(app_id=app_id, title=title, url=clean_url)
                game.add_price_record(price_record)

                scraped_games.append(game)

            except (NoSuchElementException, ValueError):
                
                continue

        return scraped_games
             
          