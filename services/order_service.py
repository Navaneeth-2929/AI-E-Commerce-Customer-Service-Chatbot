import json
import random
import string
from pathlib import Path
from threading import Lock


class OrderService:
    def __init__(self, orders_path: Path):
        self.orders_path = Path(orders_path)
        self._lock = Lock()

    def _load_orders(self) -> list[dict]:
        with self.orders_path.open("r", encoding="utf-8") as handle:
            return json.load(handle)

    def _save_orders(self, orders: list[dict]) -> None:
        with self.orders_path.open("w", encoding="utf-8") as handle:
            json.dump(orders, handle, indent=2)

    def track_order(self, order_id: str) -> dict | None:
        order_id = order_id.upper()
        orders = self._load_orders()
        return next((order for order in orders if order["order_id"] == order_id), None)

    def cancel_order(self, order_id: str) -> dict:
        order_id = order_id.upper()
        with self._lock:
            orders = self._load_orders()
            for order in orders:
                if order["order_id"] != order_id:
                    continue
                if order["status"] in {"delivered", "cancelled"}:
                    return {
                        "success": False,
                        "message": f"Order {order_id} cannot be cancelled because it is {order['status']}.",
                    }
                order["status"] = "cancelled"
                self._save_orders(orders)
                return {
                    "success": True,
                    "message": f"Order {order_id} has been cancelled successfully.",
                    "order": order,
                }
        return {"success": False, "message": f"Order {order_id} was not found."}

    def create_order(self, product_name: str, price: float | None = None) -> dict:
        with self._lock:
            orders = self._load_orders()
            order = {
                "order_id": self._generate_order_id(orders),
                "product_name": product_name.title(),
                "status": "processing",
                "price": round(price if price is not None else random.uniform(19.99, 499.99), 2),
            }
            orders.append(order)
            self._save_orders(orders)
            return order

    def _generate_order_id(self, orders: list[dict]) -> str:
        existing_ids = {order["order_id"] for order in orders}
        while True:
            candidate = "ORD" + "".join(random.choices(string.digits, k=6))
            if candidate not in existing_ids:
                return candidate
