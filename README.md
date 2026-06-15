# Быстрая доставка — Система управления заказами

## Описание
Внутреннее приложение для учёта заказов компании «Быстрая доставка».
Позволяет управлять клиентами и заказами, строить отчёты, экспортировать и импортировать данные.

## Функционал
- Управление клиентами (добавление, просмотр, редактирование, удаление)
- Управление заказами (создание, редактирование, удаление, фильтрация)
- Отчёты и статистика (выручка, топ клиентов, заказы по статусам)
- Экспорт/импорт данных (JSON, XML)
- CLI и GUI интерфейсы
- Логирование действий
- Тестирование (pytest)

## Технологии
- Python 3.8+
- SQLite
- Tkinter 
- pytest 
- argparse 
- logging 

## Установка и запуск(надо распоковать установленную папку и дальше следовать инструкциям)

### 1. Откройте командную строку и перейдите в папку проекта

```cmd
cd путь_к_папке\delivery_system
```

**Пример:**
```cmd
cd C:\Users\Amir\delivery_system
```

### 2. Установите зависимости

```cmd
pip install -r requirements.txt
```
### 2.1 Может потребоваться доп установка для pytest
```cmd
pip install pytest
```
### 3. Запустите приложение

**Графический интерфейс (GUI):**
```cmd
python main_gui.py
```

**Консольный интерфейс (CLI):**
```cmd
python main_cli.py report --period month
python main_cli.py export --file orders.json
python main_cli.py import --file orders.json
```

### 4. Запустите тесты

```cmd
python -m pytest tests/ -v
```


## Структура проекта

```text
delivery_system/
├── main_cli.py            # CLI-точка входа (argparse)
├── main_gui.py            # GUI-точка входа (Tkinter)
├── database.py            # Работа с БД (SQLite)
├── models.py              # Классы Customer, Order
├── data_export.py         # Экспорт/импорт XML/JSON(сделал оба варианта)
├── logger_config.py       # Настройка логирования
├── requirements.txt       # Зависимости (pytest, tinydb)
├── README.md              # Инструкция по установке и запуску
├── tests/                 # Тесты (pytest)
│   ├── test_database.py
│   ├── test_models.py
│   └── test_export.py
── logs/                  # Папка для логов (создаётся автоматически)
└── data/                  # Папка для БД (создаётся автоматически)
```
```Пример(у меня в директории)
delivery_system/
├── main_cli.py # CLI-интерфейс (argparse)
├── main_gui.py # GUI-интерфейс (Tkinter)
├── database.py # Работа с SQLite
├── models.py # Классы данных (Customer, Order)
├── data_export.py # Экспорт/импорт JSON и XML
├── logger_config.py # Настройка логирования
├── requirements.txt # Зависимости (pytest, tinydb)
├── README.md # Документация
├── .gitignore # Исключения для Git
│
├── tests/ # Тесты (pytest)
│ ├── test_database.py
│ ├── test_models.py
│ └── test_export.py
│
├── data/ # База данных SQLite
│ └── delivery.db
│
├── logs/ # Логи приложения
│ └── app.log
│
└── [тестовые файлы]
├── orders.json
├── test.json
└── test_orders.json
```
