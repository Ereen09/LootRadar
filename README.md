# 🎯 LootRadar — Modular Steam Deal & Price History Tracker

**LootRadar**, Steam mağazasındaki indirimli oyunları dinamik olarak tarayan, zaman içindeki fiyat değişimlerini geçmişe dönük saklayan ve bütçe/indirim oranı bazlı fırsat analizleri sunan nesne yönelimli (OOP) bir yerel masaüstü CLI uygulamasıdır.

Harici ağır veri işleme kütüphanelerine (Pandas, NumPy vb.) bağımlı kalmadan, **saf Python veri yapıları (`dict`, `list`)**, **katmanlı mimari** ve **Selenium WebDriver** kullanılarak geliştirilmiştir.

---

## 🏗️ Mimari ve Tasarım Kararları

Proje, sorumlulukların ayrılması (*Separation of Concerns*) ilkesine göre 4 bağımsız çekirdek katmana ayrılmıştır:

```text
LootRadar/
├── models/
│   └── game.py              # PriceRecord ve Game veri modelleri (Composition & Validation)
├── storage/
│   └── json_repository.py   # O(1) bellek içi dict yönetimi ve UTF-8 JSON kalıcılığı
├── scrapers/
│   └── steam_scraper.py     # Context Manager destekli Selenium kazıyıcı ve Regex ayrıştırıcı
├── core/
│   └── radar_engine.py      # Veri senkronizasyonu ve fırsat filtreleme iş mantığı
├── data/
│   └── .gitkeep             # Yerel JSON veritabanı dizini
├── main.py                  # Etkileşimli CLI giriş noktası (Composition Root)
├── requirements.txt         # Proje bağımlılıkları
└── .gitignore               # Git hariç tutma kuralları