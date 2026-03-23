import logging
from pathlib import Path

from flask import Flask

from app.routes import api_bp
from services.chat_service import ChatService
from services.order_service import OrderService
from services.session_service import SessionService


def create_app() -> Flask:
    base_dir = Path(__file__).resolve().parent.parent
    app = Flask(
        __name__,
        template_folder=str(base_dir / "templates"),
        static_folder=str(base_dir / "static"),
    )
    app.config["SECRET_KEY"] = "dev-secret-key"
    app.config["BASE_DIR"] = base_dir
    app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )

    data_dir = base_dir / "data"
    order_service = OrderService(data_dir / "orders.json")
    session_service = SessionService()
    chat_service = ChatService(
        intents_path=data_dir / "intents.json",
        responses_path=data_dir / "responses.json",
        catalog_path=data_dir / "catalog.json",
        order_service=order_service,
        session_service=session_service,
    )
    app.extensions["order_service"] = order_service
    app.extensions["chat_service"] = chat_service

    app.register_blueprint(api_bp)
    return app
