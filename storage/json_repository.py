import json
import os
from models.game import Game


class JsonRepository:
    """Oyun verilerini bellekte dict olarak yönetir ve JSON dosyasına kaydeder."""

    def __init__(self, file_path: str = "data/lootradar_db.json") -> None:
        self.file_path = file_path
        self._games: dict[str, Game] = {}
        self._ensure_directory()
        self.load()

    def _ensure_directory(self) -> None:
        """Hedef JSON dosyasının bulunacağı klasör yoksa otomatik oluşturur."""
        directory = os.path.dirname(self.file_path)
        if directory:
            os.makedirs(directory, exist_ok=True)

    def load(self) -> None:
        """JSON dosyasındaki verileri okur ve canlı Game nesnelerine dönüştürerek belleğe alır."""
        if not os.path.exists(self.file_path):
            self._games = {}
            return

        try:
            with open(self.file_path, "r", encoding="utf-8") as file:
                raw_data = json.load(file)
                self._games = {
                    app_id: Game.from_dict(game_data)
                    for app_id, game_data in raw_data.items()
                }
        except (json.JSONDecodeError, KeyError, ValueError):
            self._games = {}

    def save(self) -> None:
        """Bellekteki tüm Game nesnelerini serileştirip JSON dosyasına yazar."""
        serialized_data = {
            app_id: game.to_dict()
            for app_id, game in self._games.items()
        }

        with open(self.file_path, "w", encoding="utf-8") as file:
            json.dump(serialized_data, file, ensure_ascii=False, indent=4)

    def upsert_game(self, game: Game) -> bool:
        """Oyun depoda varsa yeni fiyat kaydını ekler, yoksa yeni oyun olarak kaydeder."""
        existing_game = self._games.get(game.app_id)

        if existing_game is not None:
            if game.current_price is not None:
                return existing_game.add_price_record(game.current_price)
            return False

        self._games[game.app_id] = game
        return True

    def get_all_games(self) -> list[Game]:
        """Bellekteki tüm Game nesnelerini liste olarak döndürür."""
        return list(self._games.values())

    def get_game_by_id(self, app_id: str) -> Game | None:
        """Verilen app_id değerine sahip oyunu O(1) hızında bulup döndürür."""
        return self._games.get(str(app_id).strip())
                