from flask import Blueprint, current_app, jsonify, render_template, request


api_bp = Blueprint("api", __name__)


def _build_services():
    return current_app.extensions["chat_service"], current_app.extensions["order_service"]


@api_bp.get("/")
def index():
    base_dir = current_app.config["BASE_DIR"]
    css_version = int((base_dir / "static" / "styles.css").stat().st_mtime)
    js_version = int((base_dir / "static" / "app.js").stat().st_mtime)
    return render_template("index.html", css_version=css_version, js_version=js_version)


@api_bp.post("/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    message = (payload.get("message") or "").strip()
    session_id = payload.get("session_id")

    if not message:
        return jsonify({"error": "Message is required."}), 400

    chat_service, _ = _build_services()
    response = chat_service.process_message(message=message, session_id=session_id)
    return jsonify(response)


@api_bp.post("/order/track")
def track_order():
    payload = request.get_json(silent=True) or {}
    order_id = (payload.get("order_id") or "").strip()
    if not order_id:
        return jsonify({"error": "order_id is required."}), 400

    _, order_service = _build_services()
    order = order_service.track_order(order_id)
    if not order:
        return jsonify({"error": f"Order {order_id} was not found."}), 404
    return jsonify({"order": order})


@api_bp.post("/order/cancel")
def cancel_order():
    payload = request.get_json(silent=True) or {}
    order_id = (payload.get("order_id") or "").strip()
    if not order_id:
        return jsonify({"error": "order_id is required."}), 400

    _, order_service = _build_services()
    result = order_service.cancel_order(order_id)
    status_code = 200 if result["success"] else 400
    return jsonify(result), status_code


@api_bp.post("/order/create")
def create_order():
    payload = request.get_json(silent=True) or {}
    product_name = (payload.get("product_name") or "").strip()
    if not product_name:
        return jsonify({"error": "product_name is required."}), 400

    _, order_service = _build_services()
    order = order_service.create_order(product_name)
    return jsonify({"order": order}), 201
