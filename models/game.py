from datetime import datetime
from turtle import title

class PriceRecord:
   def __init__(
        self,
        normal_price: float,
        sale_price: float,
        discount_percent: int,
        recorded_at: str | None = None,
    ) -> None:
       if normal_price < 0 or sale_price < 0:
            raise ValueError("Price values cannot be negative.")
       if not (0 <= discount_percent <= 100):
            raise ValueError("Discount percent must be between 0 and 100.") 
    
       self.normal_price = float (normal_price)
       self.sale_price = float (sale_price)
       self.discount_percent = int (discount_percent)
       self.recorded_at = recorded_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
   def to_dict(self) -> dict:
        return {
            "normal_price": self.normal_price,
            "sale_price": self.sale_price,
            "discount_percent": self.discount_percent,
            "recorded_at": self.recorded_at,
        }    
   def from_dict(cls, data: dict) -> "PriceRecord":
        return cls(
            normal_price=data.get("normal_price", 0.0),
            sale_price=data.get("sale_price", 0.0),
            discount_percent=data.get("discount_percent", 0),
            recorded_at=data.get("recorded_at"),
        )
class Game:
    def __init__(
        self,
        url: str,
        app_id: str, 
        title: str,
        price_history: list[PriceRecord] | None = None,
    ) -> None:
     if not app_id or not title:
        raise ValueError("App ID and title cannot be empty.")   
     self.app_id = str(app_id).strip()
     self.title =(title).strip()
     self.url = (url).strip()
     self.price_history: list[PriceRecord] = price_history if price_history is not None else []            
     
    @property
    def current_price(self) -> PriceRecord | None:
        
        if not self.price_history:
            return None
        return self.price_history[-1]

    def add_price_record(self, record: PriceRecord) -> bool:
        
        latest = self.current_price

        
        if (
            latest is None
            or latest.sale_price != record.sale_price
            or latest.discount_percent != record.discount_percent
        ):
            self.price_history.append(record)
            return True

        return False 
    def to_dict(self) -> dict:
        return {
            "app_id": self.app_id,
            "title": self.title,
            "url": self.url,
            "price_history": [record.to_dict() for record in self.price_history],
        }
    @classmethod
    def from_dict(cls, data: dict) -> "Game":
       
        raw_history = data.get("price_history", [])
        history = [PriceRecord.from_dict(item) for item in raw_history]

        return cls(
            app_id=data["app_id"],
            title=data["title"],
            url=data["url"],
            price_history=history,
        )