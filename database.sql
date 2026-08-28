```sql
-- Food Ordering App - MySQL schema
-- Run: mysql -u root -p < database.sql

CREATE DATABASE IF NOT EXISTS food_delivery_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

USE food_delivery_db;


-- =====================================================
-- USER TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password VARCHAR(200) NOT NULL,
    phone VARCHAR(15),
    address TEXT,
    role VARCHAR(20) DEFAULT 'customer',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);


-- =====================================================
-- FOOD ITEM TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS food_item (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price FLOAT NOT NULL,
    category VARCHAR(50),
    image_url VARCHAR(300),
    is_available BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);


-- =====================================================
-- ORDER TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS `order` (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_number VARCHAR(20) UNIQUE NOT NULL,
    customer_id INT NOT NULL,
    total_amount FLOAT NOT NULL,
    delivery_address TEXT NOT NULL,
    delivery_instructions TEXT,
    payment_method VARCHAR(50) DEFAULT 'cash_on_delivery',
    status VARCHAR(20) DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (customer_id)
        REFERENCES user(id)
);


-- =====================================================
-- ORDER ITEM TABLE
-- =====================================================

CREATE TABLE IF NOT EXISTS order_item (
    id INT AUTO_INCREMENT PRIMARY KEY,

    order_id INT NOT NULL,

    -- This column matches the current Flask/SQLAlchemy model
    menu_item_id INT DEFAULT NULL,

    quantity INT NOT NULL DEFAULT 1,

    price FLOAT NOT NULL,

    special_instructions TEXT,

    FOREIGN KEY (order_id)
        REFERENCES `order`(id)
        ON DELETE CASCADE,

    -- IMPORTANT:
    -- menu_item_id points to food_item.id
    FOREIGN KEY (menu_item_id)
        REFERENCES food_item(id)
);


-- =====================================================
-- END OF DATABASE SCHEMA
-- =====================================================
```
