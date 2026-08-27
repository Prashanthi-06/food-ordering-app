# QuickBite — Food Ordering App (Flask + MySQL)

A simple food ordering platform where **customers order food items directly**
(pizza, biryani, burgers, etc.) — there is no restaurant-selection step.

## Features
- Browse food menu by category, each item with name, price, and image
- Add to cart / update quantity / remove items (session-based cart)
- Checkout with delivery address & payment method
- Order confirmation with a unique order number
- Order tracking (pending → confirmed → preparing → out for delivery → delivered)
- Order history ("My Orders")
- User registration / login / logout (Flask-Login + bcrypt password hashing)
- Simple admin page to add new food items

## Tech Stack
- Flask 3.x, Flask-SQLAlchemy, Flask-Login, Flask-Bcrypt
- MySQL 8.x (schema in `database.sql`)
- Bootstrap 5 for styling

## Setup

1. Create and activate a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up MySQL:
   ```sql
   CREATE DATABASE food_ordering_db CHARACTER SET utf8mb4;
   CREATE USER 'food_user'@'localhost' IDENTIFIED BY 'your_password';
   GRANT ALL PRIVILEGES ON food_ordering_db.* TO 'food_user'@'localhost';
   ```
   Or simply import the schema: `mysql -u root -p < database.sql`

4. Set environment variables (or edit `config.py` directly):
   ```
   export MYSQL_USER=food_user
   export MYSQL_PASSWORD=your_password
   export MYSQL_HOST=localhost
   export MYSQL_DB=food_ordering_db
   ```

   To try it quickly without MySQL, set `USE_SQLITE=1` instead — it will use
   a local `food_ordering.db` SQLite file.

5. Create tables and seed sample food items:
   ```
   flask --app app seed
   ```
   This creates an admin login: `admin@fooddelivery.com` / `admin123`,
   plus ~12 sample food items (pizzas, biryani, burgers, curries, desserts).

6. Run the app:
   ```
   python app.py
   ```
   Visit http://localhost:5000

## Project Structure
```
food_ordering_app/
├── app.py              # Routes: menu, cart, checkout, orders, auth
├── models.py           # User, FoodItem, Order, OrderItem
├── config.py           # MySQL / SQLite configuration
├── database.sql        # MySQL schema
├── requirements.txt
├── templates/
│   ├── base.html, index.html, cart.html, checkout.html
│   ├── orders.html, order_detail.html
│   ├── login.html, register.html, add_food.html
└── static/css/style.css
```

## Learning Outcomes
- Designing a relational schema without a restaurant/multi-vendor layer
- Session-based cart management in Flask
- Order lifecycle & status tracking
- Authentication with Flask-Login + Flask-Bcrypt
- Rendering dynamic data with Jinja2 + Bootstrap
