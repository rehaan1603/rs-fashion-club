import os
from datetime import timedelta
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import (
    JWTManager, create_access_token, jwt_required, get_jwt_identity
)
from werkzeug.security import generate_password_hash, check_password_hash
import stripe

app = Flask(__name__)
CORS(app)

basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", f"sqlite:///{os.path.join(basedir, 'efashion.db')}"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["JWT_SECRET_KEY"] = os.environ.get("JWT_SECRET_KEY", "dev-secret-change-me")
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(days=7)

db = SQLAlchemy(app)
jwt = JWTManager(app)

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")
FRONTEND_URL = os.environ.get("FRONTEND_URL", "http://localhost:5173")

# ---------------- Models ----------------

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(120), nullable=False)

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    brand = db.Column(db.String(80), nullable=False, default="MAISON")
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    original_price = db.Column(db.Float, nullable=True)  # if set and > price, shows as strikethrough discount
    rating = db.Column(db.Float, nullable=False, default=4.0)
    rating_count = db.Column(db.Integer, nullable=False, default=100)
    category = db.Column(db.String(80), nullable=False)
    gender = db.Column(db.String(20), nullable=False, default="Unisex")  # Men / Women / Kids / Unisex
    tags = db.Column(db.String(300), nullable=False, default="")  # comma-separated
    sizes = db.Column(db.String(100), nullable=False, default="S,M,L,XL")
    color = db.Column(db.String(40), nullable=False, default="Multi")
    image_url = db.Column(db.String(400), nullable=False)
    stock = db.Column(db.Integer, nullable=False, default=25)

    def to_dict(self):
        discount_pct = None
        if self.original_price and self.original_price > self.price:
            discount_pct = round((1 - self.price / self.original_price) * 100)
        return {
            "id": self.id,
            "name": self.name,
            "brand": self.brand,
            "description": self.description,
            "price": self.price,
            "original_price": self.original_price,
            "discount_pct": discount_pct,
            "rating": self.rating,
            "rating_count": self.rating_count,
            "category": self.category,
            "gender": self.gender,
            "tags": [t for t in self.tags.split(",") if t],
            "sizes": [s for s in self.sizes.split(",") if s],
            "color": self.color,
            "image_url": self.image_url,
            "stock": self.stock,
        }

class Wishlist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    total = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(40), nullable=False, default="pending")
    stripe_session_id = db.Column(db.String(200))
    payment_method = db.Column(db.String(20), nullable=False, default="card")  # card / upi / netbanking / cod
    items_json = db.Column(db.Text, nullable=False)  # snapshot of items at purchase time

# ---------------- Auth ----------------

@app.post("/api/auth/signup")
def signup():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""
    name = (data.get("name") or "").strip()

    if not email or not password or not name:
        return jsonify({"error": "name, email and password are required"}), 400
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "an account with this email already exists"}), 409
    if len(password) < 6:
        return jsonify({"error": "password must be at least 6 characters"}), 400

    user = User(email=email, name=name, password_hash=generate_password_hash(password))
    db.session.add(user)
    db.session.commit()

    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": {"id": user.id, "email": user.email, "name": user.name}}), 201

@app.post("/api/auth/login")
def login():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = User.query.filter_by(email=email).first()
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({"error": "invalid email or password"}), 401

    token = create_access_token(identity=str(user.id))
    return jsonify({"token": token, "user": {"id": user.id, "email": user.email, "name": user.name}})

@app.get("/api/auth/me")
@jwt_required()
def me():
    user = User.query.get(int(get_jwt_identity()))
    if not user:
        return jsonify({"error": "not found"}), 404
    return jsonify({"id": user.id, "email": user.email, "name": user.name})

# ---------------- Products ----------------

@app.get("/api/products")
def list_products():
    category = request.args.get("category")
    gender = request.args.get("gender")
    q = request.args.get("q")
    brand = request.args.get("brand")
    min_price = request.args.get("min_price", type=float)
    max_price = request.args.get("max_price", type=float)
    min_discount = request.args.get("min_discount", type=float)
    sort = request.args.get("sort")

    query = Product.query
    if category and category != "all":
        query = query.filter_by(category=category)
    if gender and gender != "all":
        query = query.filter_by(gender=gender)
    if q:
        query = query.filter(Product.name.ilike(f"%{q}%"))
    if brand and brand != "all":
        query = query.filter_by(brand=brand)
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    if max_price is not None:
        query = query.filter(Product.price <= max_price)

    if sort == "price_asc":
        query = query.order_by(Product.price.asc())
    elif sort == "price_desc":
        query = query.order_by(Product.price.desc())
    elif sort == "rating":
        query = query.order_by(Product.rating.desc())
    elif sort == "newest":
        query = query.order_by(Product.id.desc())

    products = query.all()
    results = [p.to_dict() for p in products]
    if min_discount is not None:
        results = [r for r in results if r["discount_pct"] >= min_discount]
    return jsonify(results)

@app.get("/api/brands")
def brands():
    vals = db.session.query(Product.brand).distinct().all()
    return jsonify(sorted([v[0] for v in vals]))

@app.get("/api/genders")
def genders():
    vals = db.session.query(Product.gender).distinct().all()
    return jsonify(sorted([v[0] for v in vals]))

@app.get("/api/products/<int:product_id>")
def get_product(product_id):
    p = Product.query.get_or_404(product_id)
    return jsonify(p.to_dict())

@app.get("/api/products/<int:product_id>/recommendations")
def recommend(product_id):
    """Content-based recommendations: score other products by shared category + tag overlap."""
    target = Product.query.get_or_404(product_id)
    target_tags = set(target.tags.split(","))

    others = Product.query.filter(Product.id != product_id).all()
    scored = []
    for p in others:
        score = 0
        if p.category == target.category:
            score += 2
        overlap = len(target_tags.intersection(set(p.tags.split(","))))
        score += overlap
        if score > 0:
            scored.append((score, p))

    scored.sort(key=lambda x: x[0], reverse=True)
    top = [p.to_dict() for _, p in scored[:4]]
    return jsonify(top)

@app.get("/api/categories")
def categories():
    cats = db.session.query(Product.category).distinct().all()
    return jsonify(sorted([c[0] for c in cats]))

# ---------------- Cart ----------------

@app.get("/api/cart")
@jwt_required()
def get_cart():
    user_id = int(get_jwt_identity())
    items = CartItem.query.filter_by(user_id=user_id).all()
    result = []
    for item in items:
        product = Product.query.get(item.product_id)
        if product:
            result.append({
                "id": item.id,
                "quantity": item.quantity,
                "product": product.to_dict(),
            })
    return jsonify(result)

@app.post("/api/cart")
@jwt_required()
def add_to_cart():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    product_id = data.get("product_id")
    quantity = int(data.get("quantity", 1))

    product = Product.query.get(product_id)
    if not product:
        return jsonify({"error": "product not found"}), 404

    existing = CartItem.query.filter_by(user_id=user_id, product_id=product_id).first()
    if existing:
        existing.quantity += quantity
    else:
        existing = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
        db.session.add(existing)
    db.session.commit()
    return jsonify({"message": "added to cart"}), 201

@app.patch("/api/cart/<int:item_id>")
@jwt_required()
def update_cart_item(item_id):
    user_id = int(get_jwt_identity())
    item = CartItem.query.filter_by(id=item_id, user_id=user_id).first_or_404()
    data = request.get_json() or {}
    quantity = int(data.get("quantity", item.quantity))
    if quantity <= 0:
        db.session.delete(item)
    else:
        item.quantity = quantity
    db.session.commit()
    return jsonify({"message": "updated"})

@app.delete("/api/cart/<int:item_id>")
@jwt_required()
def delete_cart_item(item_id):
    user_id = int(get_jwt_identity())
    item = CartItem.query.filter_by(id=item_id, user_id=user_id).first_or_404()
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "removed"})

# ---------------- Wishlist ----------------

@app.get("/api/wishlist")
@jwt_required()
def get_wishlist():
    user_id = int(get_jwt_identity())
    items = Wishlist.query.filter_by(user_id=user_id).all()
    result = []
    for item in items:
        product = Product.query.get(item.product_id)
        if product:
            result.append({"id": item.id, "product": product.to_dict()})
    return jsonify(result)

@app.post("/api/wishlist")
@jwt_required()
def add_to_wishlist():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    product_id = data.get("product_id")
    if not Product.query.get(product_id):
        return jsonify({"error": "product not found"}), 404
    existing = Wishlist.query.filter_by(user_id=user_id, product_id=product_id).first()
    if not existing:
        db.session.add(Wishlist(user_id=user_id, product_id=product_id))
        db.session.commit()
    return jsonify({"message": "added to wishlist"}), 201

@app.delete("/api/wishlist/<int:product_id>")
@jwt_required()
def remove_from_wishlist(product_id):
    user_id = int(get_jwt_identity())
    item = Wishlist.query.filter_by(user_id=user_id, product_id=product_id).first()
    if item:
        db.session.delete(item)
        db.session.commit()
    return jsonify({"message": "removed"})

# ---------------- Checkout (Stripe test mode) ----------------

@app.post("/api/checkout")
@jwt_required()
def checkout():
    user_id = int(get_jwt_identity())
    data = request.get_json() or {}
    payment_method = data.get("payment_method", "card")
    if payment_method not in ("card", "upi", "netbanking", "cod"):
        return jsonify({"error": "invalid payment method"}), 400

    items = CartItem.query.filter_by(user_id=user_id).all()
    if not items:
        return jsonify({"error": "cart is empty"}), 400

    line_items = []
    snapshot = []
    total = 0.0
    for item in items:
        product = Product.query.get(item.product_id)
        if not product:
            continue
        total += product.price * item.quantity
        snapshot.append({
            "product_id": product.id, "name": product.name,
            "price": product.price, "quantity": item.quantity
        })
        line_items.append({
            "price_data": {
                "currency": "inr",
                "product_data": {"name": product.name},
                "unit_amount": int(round(product.price * 100)),
            },
            "quantity": item.quantity,
        })

    order = Order(user_id=user_id, total=total, status="pending",
                  items_json=str(snapshot), payment_method=payment_method)
    db.session.add(order)
    db.session.commit()

    # Cash on Delivery never touches a payment gateway - confirm immediately.
    if payment_method == "cod":
        order.status = "cod"
        db.session.commit()
        for item in items:
            db.session.delete(item)
        db.session.commit()
        return jsonify({"cod": True, "order_id": order.id, "total": total})

    # UPI / Net Banking / Card all route through the same Stripe test-mode
    # checkout under the hood - there's no real UPI or net banking gateway
    # wired up here, only Stripe's card-based test flow.
    if not stripe.api_key:
        # No Stripe key configured: mark as paid directly so the flow still works end-to-end in a demo.
        order.status = "paid"
        db.session.commit()
        for item in items:
            db.session.delete(item)
        db.session.commit()
        return jsonify({"demo_mode": True, "order_id": order.id, "total": total})

    session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=line_items,
        mode="payment",
        success_url=f"{FRONTEND_URL}/success?order_id={order.id}",
        cancel_url=f"{FRONTEND_URL}/payment",
    )
    order.stripe_session_id = session.id
    db.session.commit()
    return jsonify({"checkout_url": session.url, "order_id": order.id})

@app.post("/api/checkout/confirm/<int:order_id>")
@jwt_required()
def confirm_order(order_id):
    """Called by success page; verifies session with Stripe then clears cart."""
    user_id = int(get_jwt_identity())
    order = Order.query.filter_by(id=order_id, user_id=user_id).first_or_404()
    if order.status != "paid" and order.stripe_session_id:
        session = stripe.checkout.Session.retrieve(order.stripe_session_id)
        if session.payment_status == "paid":
            order.status = "paid"
            CartItem.query.filter_by(user_id=user_id).delete()
            db.session.commit()
    return jsonify({"status": order.status, "total": order.total})

@app.get("/api/orders")
@jwt_required()
def list_orders():
    user_id = int(get_jwt_identity())
    orders = Order.query.filter_by(user_id=user_id).order_by(Order.id.desc()).all()
    return jsonify([{
        "id": o.id, "total": o.total, "status": o.status, "items": o.items_json
    } for o in orders])

@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
