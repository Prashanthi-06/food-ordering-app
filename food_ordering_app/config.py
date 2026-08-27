import os


class Config:
    SECRET_KEY = os.environ.get(
        "SECRET_KEY",
        "change-this-secret-key"
    )

    # ---- MySQL configuration ----
    MYSQL_USER = "food_user"
    MYSQL_PASSWORD = "FoodUser123"
    MYSQL_HOST = "localhost"
    MYSQL_DB = "food_delivery_db"

    # ---- Database configuration ----
    if os.environ.get("USE_SQLITE") == "1":
        SQLALCHEMY_DATABASE_URI = "sqlite:///food_ordering.db"
    else:
        SQLALCHEMY_DATABASE_URI = (
            f"mysql://{MYSQL_USER}:{MYSQL_PASSWORD}"
            f"@{MYSQL_HOST}/{MYSQL_DB}"
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False