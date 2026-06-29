import argparse
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import init_db, get_orders_by_status, get_top_3_clients, get_revenue
from data_export import export_to_json, import_from_json, export_to_xml, import_from_xml
from logger_config import logger

def cmd_report(args):
    print(f"\n--- Отчет за период: {args.period} ---")
    print("Заказы по статусам:")
    for status, count in get_orders_by_status().items():
        print(f"  {status}: {count}")
    
    print("\nТоп-3 клиента:")
    for name, total in get_top_3_clients():
        print(f"  {name}: {total:.2f} руб.")
        
    revenue = get_revenue(args.period)
    print(f"\nОбщая выручка: {revenue:.2f} руб.\n")

def cmd_export(args):
    filepath = args.file
    if filepath.endswith('.json'):
        export_to_json(filepath)
    elif filepath.endswith('.xml'):
        export_to_xml(filepath)
    else:
        print("Ошибка: Файл должен иметь расширение .json или .xml")
        sys.exit(1)
    print(f"Успешно экспортировано в {filepath}")

def cmd_import(args):
    filepath = args.file
    if not os.path.exists(filepath):
        print(f"Ошибка: Файл {filepath} не найден.")
        sys.exit(1)
        
    if filepath.endswith('.json'):
        count = import_from_json(filepath)
    elif filepath.endswith('.xml'):
        count = import_from_xml(filepath)
    else:
        print("Ошибка: Файл должен иметь расширение .json или .xml")
        sys.exit(1)
    print(f"Успешно импортировано {count} заказов.")

def main():
    init_db()
    parser = argparse.ArgumentParser(description="Система управления доставкой 'Быстрая доставка'")
    subparsers = parser.add_subparsers(dest="command", help="Доступные команды")

    # Report
    report_parser = subparsers.add_parser("report", help="Показать отчет")
    report_parser.add_argument("--period", choices=["day", "week", "month", "all"], default="month", help="Период отчета")
    report_parser.set_defaults(func=cmd_report)

    # Export
    export_parser = subparsers.add_parser("export", help="Экспорт заказов")
    export_parser.add_argument("--file", required=True, help="Имя файла для экспорта (.json или .xml)")
    export_parser.set_defaults(func=cmd_export)

    # Import
    import_parser = subparsers.add_parser("import", help="Импорт заказов")
    import_parser.add_argument("--file", required=True, help="Имя файла для импорта (.json или .xml)")
    import_parser.set_defaults(func=cmd_import)

    args = parser.parse_args()
    if args.command:
        args.func(args)
    else:
        parser.print_help()

if __name__ == "__main__":
    main() 
