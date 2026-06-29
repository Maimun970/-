import sqlite3
import os
from typing import List, Optional, Tuple
from models import Customer, Order, OrderItem
from logger_config import logger

DB_PATH = "data/delivery.db"

def get_connection():
    os.makedirs("data", exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.executescript("""
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            address TEXT
        );
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_id INTEGER REFERENCES customers(id) ON DELETE RESTRICT,
            order_date TEXT NOT NULL,
            status TEXT CHECK(status IN ('новый','в доставке','выполнен','отменён')),
            total REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER REFERENCES orders(id) ON DELETE CASCADE,
            product_name TEXT,
            quantity INTEGER,
            price REAL
        );
    """)
    conn.commit()
    conn.close()
    logger.info("База данных инициализирована.")

# --- Customers ---
def add_customer(name: str, phone: str, address: str) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO customers (name, phone, address) VALUES (?, ?, ?)", (name, phone, address))
    conn.commit()
    cid = cursor.lastrowid
    conn.close()
    logger.info(f"Добавлен клиент: {name} (ID: {cid})")
    return cid

def get_customers() -> List[Customer]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM customers")
    rows = cursor.fetchall()
    conn.close()
    return [Customer(row['id'], row['name'], row['phone'], row['address']) for row in rows]

def delete_customer(customer_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM orders WHERE customer_id = ?", (customer_id,))
    if cursor.fetchone()[0] > 0:
        conn.close()
        logger.warning(f"Невозможно удалить клиента {customer_id}: существуют заказы.")
        return False
    
    cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
    conn.commit()
    conn.close()
    logger.info(f"Удален клиент ID: {customer_id}")
    return True

# --- Orders ---
def add_order(customer_id: int, order_date: str, status: str, total: float, items: List[OrderItem]) -> int:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO orders (customer_id, order_date, status, total) VALUES (?, ?, ?, ?)",
                   (customer_id, order_date, status, total))
    order_id = cursor.lastrowid
    
    for item in items:
        cursor.execute("INSERT INTO order_items (order_id, product_name, quantity, price) VALUES (?, ?, ?, ?)",
                       (order_id, item.product_name, item.quantity, item.price))
    conn.commit()
    conn.close()
    logger.info(f"Создан заказ ID: {order_id}")
    return order_id

def get_orders(status_filter: Optional[str] = None, date_from: Optional[str] = None, date_to: Optional[str] = None) -> List[Order]:
    conn = get_connection()
    cursor = conn.cursor()
    query = "SELECT * FROM orders WHERE 1=1"
    params = []
    
    if status_filter:
        query += " AND status = ?"
        params.append(status_filter)
    if date_from:
        query += " AND order_date >= ?"
        params.append(date_from)
    if date_to:
        query += " AND order_date <= ?"
        params.append(date_to)
        
    cursor.execute(query, params)
    rows = cursor.fetchall()
    
    orders = []
    for row in rows:
        cursor.execute("SELECT * FROM order_items WHERE order_id = ?", (row['id'],))
        item_rows = cursor.fetchall()
        items = [OrderItem(ir['id'], ir['order_id'], ir['product_name'], ir['quantity'], ir['price']) for ir in item_rows]
        orders.append(Order(row['id'], row['customer_id'], row['order_date'], row['status'], row['total'], items))
    
    conn.close()
    return orders

def update_order(order: Order):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE orders SET customer_id=?, order_date=?, status=?, total=? WHERE id=?",
                   (order.customer_id, order.order_date, order.status, order.total, order.id))
    
    cursor.execute("DELETE FROM order_items WHERE order_id = ?", (order.id,))
    for item in order.items:
        cursor.execute("INSERT INTO order_items (order_id, product_name, quantity, price) VALUES (?, ?, ?, ?)",
                       (order.id, item.product_name, item.quantity, item.price))
    conn.commit()
    conn.close()
    logger.info(f"Обновлен заказ ID: {order.id}")

def delete_order(order_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM orders WHERE id = ?", (order_id,))
    conn.commit()
    conn.close()
    logger.info(f"Удален заказ ID: {order_id}")

# --- Analytics ---
def get_orders_by_status() -> dict:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT status, COUNT(*) as count FROM orders GROUP BY status")
    res = {row['status']: row['count'] for row in cursor.fetchall()}
    conn.close()
    return res

def get_top_3_clients() -> List[Tuple[str, float]]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT c.name, SUM(o.total) as total_sum 
        FROM orders o 
        JOIN customers c ON o.customer_id = c.id 
        WHERE o.status != 'отменён'
        GROUP BY c.id 
        ORDER BY total_sum DESC 
        LIMIT 3
    """)
    res = [(row['name'], row['total_sum']) for row in cursor.fetchall()]
    conn.close()
    return res

def get_revenue(period: str) -> float:
    import datetime
    conn = get_connection()
    cursor = conn.cursor()
    
    today = datetime.date.today()
    if period == 'day':
        start_date = today.strftime("%Y-%m-%d")
        end_date = start_date
    elif period == 'week':
        start_date = (today - datetime.timedelta(days=today.weekday())).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
    elif period == 'month':
        start_date = today.replace(day=1).strftime("%Y-%m-%d")
        end_date = today.strftime("%Y-%m-%d")
    else:
        start_date = "2000-01-01"
        end_date = "2099-12-31"

    cursor.execute("""
        SELECT SUM(total) as revenue FROM orders 
        WHERE order_date BETWEEN ? AND ? AND status != 'отменён'
    """, (start_date, end_date))
    
    res = cursor.fetchone()['revenue']
    conn.close()
    return res if res else 0.0
