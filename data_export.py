import json
import xml.etree.ElementTree as ET
from typing import List
from models import Order, OrderItem
from database import get_orders, add_order
from logger_config import logger

def export_to_json(filepath: str):
    orders = get_orders()
    data = []
    for o in orders:
        data.append({
            "id": o.id,
            "customer_id": o.customer_id,
            "order_date": o.order_date,
            "status": o.status,
            "total": o.total,
            "items": [{"product_name": i.product_name, "quantity": i.quantity, "price": i.price} for i in o.items]
        })
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    logger.info(f"Экспорт в JSON выполнен: {filepath}")

def import_from_json(filepath: str):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    count = 0
    for item in data:
        items = [OrderItem(None, None, i['product_name'], i['quantity'], i['price']) for i in item.get('items', [])]
        add_order(item['customer_id'], item['order_date'], item['status'], item['total'], items)
        count += 1
    logger.info(f"Импорт из JSON выполнен. Добавлено заказов: {count}")
    return count

def export_to_xml(filepath: str):
    orders = get_orders()
    root = ET.Element("orders")
    for o in orders:
        order_elem = ET.SubElement(root, "order", id=str(o.id), customer_id=str(o.customer_id), 
                                   date=o.order_date, status=o.status, total=str(o.total))
        for i in o.items:
            ET.SubElement(order_elem, "item", name=i.product_name, quantity=str(i.quantity), price=str(i.price))
    
    tree = ET.ElementTree(root)
    tree.write(filepath, encoding="utf-8", xml_declaration=True)
    logger.info(f"Экспорт в XML выполнен: {filepath}")

def import_from_xml(filepath: str):
    tree = ET.parse(filepath)
    root = tree.getroot()
    count = 0
    for order_elem in root.findall("order"):
        items = []
        for item_elem in order_elem.findall("item"):
            items.append(OrderItem(None, None, item_elem.get("name"), int(item_elem.get("quantity")), float(item_elem.get("price"))))
        
        add_order(
            int(order_elem.get("customer_id")),
            order_elem.get("date"),
            order_elem.get("status"),
            float(order_elem.get("total")),
            items
        )
        count += 1
    logger.info(f"Импорт из XML выполнен. Добавлено заказов: {count}")
    return count
