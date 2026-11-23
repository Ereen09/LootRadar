from models.game import Game
from storage.json_repository import JsonRepository
from scrapers.steam_scraper import SteamScraper
from core.radar_engine import RadarEngine


def display_games(games: list[Game], limit: int = 15) -> None:
    
    if not games:
        print("\n[!] Kriterlere uygun oyun bulunamadı.")
        return

    print(f"\nToplam {len(games)} oyun bulundu (İlk {min(len(games), limit)} gösteriliyor):")
    print("-" * 75)
    print(f"{'Oyun Adı':<40} | {'İndirim':<8} | {'Eski':<8} | {'Yeni':<8}")
    print("-" * 75)

    for game in games[:limit]:
        price = game.current_price
        if price is None:
            continue

       
        short_title = (game.title[:37] + "...") if len(game.title) > 40 else game.title
        print(
            f"{short_title:<40} | "
            f"%-{price.discount_percent:<6} | "
            f"${price.normal_price:<7.2f} | "
            f"${price.sale_price:<7.2f}"
        )
    print("-" * 75)
def main() -> None:
    
    repository = JsonRepository("data/lootradar_db.json")
    engine = RadarEngine(repository)

    print("=== LootRadar: Steam İndirim Takip Motoru ===")

    while True:
        print("\nLütfen bir işlem seçin:")
        print("1. Steam İndirimlerini Tara ve Güncelle")
        print("2. En Yüksek İndirimli Oyunları Listele (%50+)")
        print("3. Bütçeye Göre Fırsat Ara (Maksimum Fiyat)")
        print("4. İsimle Oyun Ara")
        print("0. Çıkış")

        choice = input("\nSeçiminiz: ").strip()

        if choice == "1":
            try:
                scroll_input = input("Sayfa kaydırma sayısı (Varsayılan 3): ").strip()
                scroll_count = int(scroll_input) if scroll_input else 3
                if scroll_count < 1:
                    raise ValueError
            except ValueError:
                print("[!] Geçersiz sayı girdiniz, varsayılan (3) kullanılıyor.")
                scroll_count = 3

            print("\n[*] Steam mağazası taranıyor, lütfen bekleyin...")
            with SteamScraper(headless=True) as scraper:
                fetched_games = scraper.fetch_specials(scroll_count=scroll_count)

            stats = engine.sync_games(fetched_games)
            print(
                f"[+] Tarama tamamlandı! Taranan: {stats['scanned_count']} | "
                f"Yeni/Değişen: {stats['changed_count']} | "
                f"Toplam Kayıtlı: {stats['total_stored']}"
            )

        elif choice == "2":
            try:
                min_disc_input = input("Minimum indirim yüzdesi (Varsayılan 50): ").strip()
                min_discount = int(min_disc_input) if min_disc_input else 50
            except ValueError:
                print("[!] Geçersiz oran, varsayılan (%50) kullanılıyor.")
                min_discount = 50

            deals = engine.get_top_discounts(min_discount=min_discount)
            display_games(deals)

        elif choice == "3":
            try:
                max_price = float(input("Maksimum fiyat ($ cinsinden, örn: 5.0): ").strip())
                deals = engine.get_deals_under_price(max_price=max_price)
                display_games(deals)
            except ValueError:
                print("[!] Lütfen geçerli bir sayısal fiyat girin (Örn: 4.99).")

        elif choice == "4":
            keyword = input("Aranacak oyun adı: ").strip()
            results = engine.search_by_title(keyword)
            display_games(results)

        elif choice == "0":
            print("\nLootRadar kapatılıyor. İyi oyunlar!")
            break

        else:
            print("\n[!] Geçersiz seçim, lütfen 0-4 arası bir değer girin.")


if __name__ == "__main__":
    main()    