from models.game import Game
from storage.json_repository import JsonRepository

class RadarEngine:
    def __init__(self, repository: JsonRepository) -> None:
        self.repository = repository

    def sync_games(self, fetched_games: list[Game]) -> dict[str, int]:
        
        updated_or_new_count = 0

        for game in fetched_games:
            is_changed = self.repository.upsert_game(game)
            if is_changed:
                updated_or_new_count += 1

        self.repository.save()

        return {
            "scanned_count": len(fetched_games),
            "changed_count": updated_or_new_count,
            "total_stored": len(self.repository.get_all_games()),
        }
    def get_top_discounts(self, min_discount: int = 50) -> list[Game]:
        
        filtered = [
            game for game in self.repository.get_all_games()
            if game.current_price is not None and game.current_price.discount_percent >= min_discount
        ]
        # İndirim yüzdesine göre büyükten küçüğe (reverse=True) sırala
        return sorted(filtered, key=lambda g: g.current_price.discount_percent, reverse=True)

    def get_deals_under_price(self, max_price: float) -> list[Game]:
        
        filtered = [
            game for game in self.repository.get_all_games()
            if game.current_price is not None and game.current_price.sale_price <= max_price
        ]
        
        return sorted(filtered, key=lambda g: g.current_price.sale_price)

    def search_by_title(self, keyword: str) -> list[Game]:
       
        clean_keyword = keyword.strip().lower()
        if not clean_keyword:
            return []

        return [
            game for game in self.repository.get_all_games()
            if clean_keyword in game.title.lower()
        ]