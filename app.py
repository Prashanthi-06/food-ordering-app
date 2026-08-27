import random
import string
from datetime import datetime

from flask import Flask, render_template, redirect, url_for, flash, request, session
from flask_login import (
    LoginManager, login_user, login_required, logout_user, current_user
)
from flask_bcrypt import Bcrypt

from config import Config
from models import db, User, FoodItem, Order, OrderItem

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt = Bcrypt(app)

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def get_cart():
    """Cart is stored in the session as {food_item_id(str): quantity}."""
    return session.setdefault("cart", {})


def cart_details():
    cart = get_cart()
    items = []
    total = 0.0
    for food_id_str, qty in cart.items():
        food = FoodItem.query.get(int(food_id_str))
        if not food:
            continue
        subtotal = food.price * qty
        total += subtotal
        items.append({"food": food, "qty": qty, "subtotal": subtotal})
    return items, total


def generate_order_number():
    return "ORD" + "".join(random.choices(string.digits, k=8))


# ---------------------------------------------------------------------
# Food menu (home page) — customers browse & order food directly
# ---------------------------------------------------------------------

@app.route("/")
def index():
    category = request.args.get("category")
    query = FoodItem.query.filter_by(is_available=True)
    if category:
        query = query.filter_by(category=category)
    foods = query.order_by(FoodItem.category, FoodItem.name).all()

    categories = [
        c[0] for c in db.session.query(FoodItem.category).distinct().all() if c[0]
    ]
    cart_count = sum(get_cart().values())
    return render_template(
        "index.html", foods=foods, categories=categories,
        selected_category=category, cart_count=cart_count
    )


# ---------------------------------------------------------------------
# Cart
# ---------------------------------------------------------------------

@app.route("/cart/add/<int:food_id>", methods=["POST"])
def add_to_cart(food_id):
    food = FoodItem.query.get_or_404(food_id)
    cart = get_cart()
    key = str(food_id)
    cart[key] = cart.get(key, 0) + 1
    session.modified = True
    flash(f"Added {food.name} to your cart.", "success")
    return redirect(request.referrer or url_for("index"))


@app.route("/cart")
def view_cart():
    items, total = cart_details()
    return render_template("cart.html", items=items, total=total)


@app.route("/cart/update/<int:food_id>", methods=["POST"])
def update_cart(food_id):
    qty = int(request.form.get("quantity", 1))
    cart = get_cart()
    key = str(food_id)
    if qty <= 0:
        cart.pop(key, None)
    else:
        cart[key] = qty
    session.modified = True
    return redirect(url_for("view_cart"))


@app.route("/cart/remove/<int:food_id>", methods=["POST"])
def remove_from_cart(food_id):
    cart = get_cart()
    cart.pop(str(food_id), None)
    session.modified = True
    return redirect(url_for("view_cart"))


# ---------------------------------------------------------------------
# Checkout & Orders
# ---------------------------------------------------------------------

@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    items, total = cart_details()
    if not items:
        flash("Your cart is empty.", "warning")
        return redirect(url_for("index"))

    if request.method == "POST":
        address = request.form.get("address", "").strip()
        instructions = request.form.get("instructions", "").strip()
        payment_method = request.form.get("payment_method", "cash_on_delivery")

        if not address:
            flash("Delivery address is required.", "danger")
            return redirect(url_for("checkout"))

        order = Order(
            order_number=generate_order_number(),
            customer_id=current_user.id,
            total_amount=total,
            delivery_address=address,
            delivery_instructions=instructions,
            payment_method=payment_method,
            status="pending",
        )
        db.session.add(order)
        db.session.flush()  # get order.id before commit

        for entry in items:
            db.session.add(OrderItem(
                order_id=order.id,
                food_item_id=entry["food"].id,
                food_name=entry["food"].name,
                quantity=entry["qty"],
                price=entry["food"].price,
            ))

        db.session.commit()
        session["cart"] = {}
        flash(f"Order {order.order_number} placed successfully!", "success")
        return redirect(url_for("order_detail", order_id=order.id))

    return render_template("checkout.html", items=items, total=total)


@app.route("/orders")
@login_required
def my_orders():
    orders = (
        Order.query.filter_by(customer_id=current_user.id)
        .order_by(Order.created_at.desc())
        .all()
    )
    return render_template("orders.html", orders=orders)


@app.route("/orders/<int:order_id>")
@login_required
def order_detail(order_id):
    order = Order.query.get_or_404(order_id)
    if order.customer_id != current_user.id and current_user.role != "admin":
        flash("You cannot view this order.", "danger")
        return redirect(url_for("my_orders"))
    return render_template("order_detail.html", order=order)


# ---------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        address = request.form.get("address", "").strip()
        password = request.form.get("password", "")

        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash("Username or email already registered.", "danger")
            return redirect(url_for("register"))

        hashed_pw = bcrypt.generate_password_hash(password).decode("utf-8")
        user = User(
            username=username, email=email, phone=phone,
            address=address, password=hashed_pw,
        )
        db.session.add(user)
        db.session.commit()
        flash("Account created. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            flash("Logged in successfully.", "success")
            return redirect(url_for("index"))
        flash("Invalid email or password.", "danger")
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("index"))


# ---------------------------------------------------------------------
# Minimal admin route to add food items (role must be 'admin')
# ---------------------------------------------------------------------

@app.route("/admin/food/add", methods=["GET", "POST"])
@login_required
def add_food():
    if current_user.role != "admin":
        flash("Admins only.", "danger")
        return redirect(url_for("index"))

    if request.method == "POST":
        food = FoodItem(
            name=request.form.get("name", "").strip(),
            description=request.form.get("description", "").strip(),
            price=float(request.form.get("price", 0)),
            category=request.form.get("category", "").strip(),
            image_url=request.form.get("image_url", "").strip(),
            is_available=True,
        )
        db.session.add(food)
        db.session.commit()
        flash(f"{food.name} added to menu.", "success")
        return redirect(url_for("index"))

    return render_template("add_food.html")


# ---------------------------------------------------------------------
# CLI helper: seed the database with sample food items
# ---------------------------------------------------------------------

@app.cli.command("seed")
def seed():
    """Run with: flask --app app seed"""
    db.create_all()

    if not User.query.filter_by(email="admin@fooddelivery.com").first():
        db.session.add(User(
            username="admin", email="admin@fooddelivery.com",
            password=bcrypt.generate_password_hash("admin123").decode("utf-8"),
            phone="0000000000", role="admin",
        ))

    sample_foods = [
        ("Margherita Pizza", "Classic pizza with mozzarella & basil", 249, "Pizza"),
        ("Pepperoni Pizza", "Loaded with pepperoni & cheese", 299, "Pizza"),
        ("Chicken Biryani", "Fragrant basmati rice with spiced chicken", 219, "Biryani"),
        ("Veg Biryani", "Basmati rice with mixed vegetables & spices", 179, "Biryani"),
        ("Cheese Burger", "Grilled patty with cheese, lettuce & tomato", 149, "Burgers"),
        ("Veggie Burger", "Crispy veggie patty with fresh toppings", 129, "Burgers"),
        ("Butter Chicken", "Creamy tomato curry with tender chicken", 259, "Curries"),
        ("Paneer Tikka Masala", "Grilled paneer in spiced tomato gravy", 219, "Curries"),
        ("Chocolate Brownie", "Warm fudgy brownie with chocolate sauce", 99, "Desserts"),
        ("Gulab Jamun (2 pcs)", "Soft milk dumplings in sugar syrup", 69, "Desserts"),
        ("French Fries", "Crispy salted fries", 89, "Sides"),
        ("Coke (500ml)", "Chilled soft drink", 49, "Beverages"),
    ]

    for name, desc, price, category in sample_foods:
        if not FoodItem.query.filter_by(name=name).first():
            img = "https://placehold.co/400x300?text=" + name.replace(" ", "+")
            db.session.add(FoodItem(
                name=name, description=desc, price=price,
                category=category, image_url=img, is_available=True,
            ))

    db.session.commit()
    print("Database seeded with admin user (admin@fooddelivery.com / admin123) and sample food items.")


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
