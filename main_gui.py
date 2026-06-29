import tkinter as tk
from tkinter import ttk, messagebox
from database import init_db, get_customers, add_customer, delete_customer, get_orders, add_order, update_order, delete_order
from models import OrderItem
from datetime import datetime

class DeliveryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Быстрая доставка")
        self.root.geometry("900x600")
        
        init_db()
        
        self.create_main_window()
        self.load_orders()
        self.load_customers()

    def create_main_window(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(top_frame, text="Добавить заказ", command=self.open_add_order, 
                  bg="#90EE90", width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="Редактировать заказ", command=self.open_edit_order, 
                  width=15).pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="Удалить заказ", command=self.delete_order, 
                  bg="#FFB6C1", width=15).pack(side=tk.LEFT, padx=5)
        
        tk.Button(top_frame, text="Добавить клиента", command=self.open_add_customer, 
                  bg="#87CEEB", width=15).pack(side=tk.RIGHT, padx=5)
        tk.Button(top_frame, text="Показать отчет", command=self.show_report, 
                  bg="#DDA0DD", width=15).pack(side=tk.RIGHT, padx=5)
        
        columns = ("id", "date", "customer", "status", "total")
        self.tree = ttk.Treeview(self.root, columns=columns, show="headings", height=20)
        
        self.tree.heading("id", text="ID")
        self.tree.heading("date", text="Дата")
        self.tree.heading("customer", text="Клиент")
        self.tree.heading("status", text="Статус")
        self.tree.heading("total", text="Сумма (руб)")
        
        self.tree.column("id", width=50)
        self.tree.column("date", width=100)
        self.tree.column("customer", width=200)
        self.tree.column("status", width=100)
        self.tree.column("total", width=100)
        
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def load_orders(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        orders = get_orders()
        customers = get_customers()
        
        customers_dict = {c.id: c.name for c in customers}
        
        for order in orders:
            customer_name = customers_dict.get(order.customer_id, "Неизвестно")
            self.tree.insert("", tk.END, values=(
                order.id,
                order.order_date,
                customer_name,
                order.status,
                f"{order.total:.2f}"
            ))

    def load_customers(self):
        self.customers_list = get_customers()

    def get_selected_order(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Внимание", "Выберите заказ!")
            return None
        
        item = self.tree.item(selected[0])
        order_id = item["values"][0]
        
        orders = get_orders()
        for order in orders:
            if order.id == order_id:
                return order
        return None

    def open_add_order(self):
        self.load_customers()
        
        if not self.customers_list:
            messagebox.showerror("Ошибка", "Сначала добавьте клиента!")
            return
        
        self.order_dialog(None)

    def open_edit_order(self):
        order = self.get_selected_order()
        if order:
            self.load_customers()
            self.order_dialog(order)

    def order_dialog(self, order):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить заказ" if not order else "Редактировать заказ")
        dialog.geometry("400x300")
        
        tk.Label(dialog, text="Клиент:").pack(pady=5)
        
        customer_names = [f"{c.id} - {c.name}" for c in self.customers_list]
        self.customer_var = tk.StringVar()
        
        customer_combo = ttk.Combobox(dialog, textvariable=self.customer_var, 
                                       values=customer_names, state="readonly", width=35)
        customer_combo.pack(pady=5)
        
        if order:
            for i, c in enumerate(self.customers_list):
                if c.id == order.customer_id:
                    customer_combo.current(i)
                    break
        else:
            customer_combo.current(0)
        
        tk.Label(dialog, text="Дата (ГГГГ-ММ-ДД):").pack(pady=5)
        self.date_var = tk.StringVar(value=order.order_date if order else datetime.now().strftime("%Y-%m-%d"))
        tk.Entry(dialog, textvariable=self.date_var, width=20).pack(pady=5)
        
        tk.Label(dialog, text="Статус:").pack(pady=5)
        self.status_var = tk.StringVar(value=order.status if order else "новый")
        status_combo = ttk.Combobox(dialog, textvariable=self.status_var,
                                     values=["новый", "в доставке", "выполнен", "отменён"],
                                     state="readonly", width=18)
        status_combo.pack(pady=5)
        
        tk.Label(dialog, text="Сумма (руб):").pack(pady=5)
        self.total_var = tk.DoubleVar(value=order.total if order else 0.0)
        tk.Entry(dialog, textvariable=self.total_var, width=20).pack(pady=5)
        
        def save():
            try:
                selected_customer = self.customer_var.get()
                customer_id = int(selected_customer.split(" - ")[0])
                
                items = [OrderItem(None, None, "Товар", 1, self.total_var.get())]
                
                if order:
                    order.customer_id = customer_id
                    order.order_date = self.date_var.get()
                    order.status = self.status_var.get()
                    order.total = self.total_var.get()
                    update_order(order)
                    messagebox.showinfo("Успех", "Заказ обновлен!")
                else:
                    add_order(customer_id, self.date_var.get(), self.status_var.get(), 
                             self.total_var.get(), items)
                    messagebox.showinfo("Успех", "Заказ создан!")
                
                dialog.destroy()
                self.load_orders()
                
            except Exception as e:
                messagebox.showerror("Ошибка", f"Ошибка: {str(e)}")
        
        tk.Button(dialog, text="Сохранить", command=save, 
                  bg="#90EE90", width=15).pack(pady=20)

    def delete_order(self):
        order = self.get_selected_order()
        if order:
            if messagebox.askyesno("Подтверждение", f"Удалить заказ №{order.id}?"):
                delete_order(order.id)
                messagebox.showinfo("Успех", "Заказ удален!")
                self.load_orders()

    def open_add_customer(self):
        dialog = tk.Toplevel(self.root)
        dialog.title("Добавить клиента")
        dialog.geometry("400x250")
        
        tk.Label(dialog, text="Имя:").pack(pady=5)
        name_var = tk.StringVar()
        tk.Entry(dialog, textvariable=name_var, width=40).pack(pady=5)
        
        tk.Label(dialog, text="Телефон:").pack(pady=5)
        phone_var = tk.StringVar()
        tk.Entry(dialog, textvariable=phone_var, width=40).pack(pady=5)
        
        tk.Label(dialog, text="Адрес:").pack(pady=5)
        address_var = tk.StringVar()
        tk.Entry(dialog, textvariable=address_var, width=40).pack(pady=5)
        
        def save():
            if not name_var.get():
                messagebox.showerror("Ошибка", "Введите имя!")
                return
            
            add_customer(name_var.get(), phone_var.get(), address_var.get())
            messagebox.showinfo("Успех", "Клиент добавлен!")
            dialog.destroy()
            self.load_customers()
        
        tk.Button(dialog, text="Сохранить", command=save,
                  bg="#90EE90", width=15).pack(pady=20)

    def show_report(self):
        from database import get_orders_by_status, get_top_3_clients, get_revenue
        
        report_window = tk.Toplevel(self.root)
        report_window.title("Отчет")
        report_window.geometry("500x400")
        
        revenue = get_revenue("month")
        tk.Label(report_window, text=f"💰 Выручка за месяц: {revenue:.2f} руб",
                font=("Arial", 12, "bold")).pack(pady=10)
        
        tk.Label(report_window, text="\n📦 Заказы по статусам:",
                font=("Arial", 11, "bold")).pack(pady=5)
        
        status_text = tk.Text(report_window, height=8, width=50)
        status_text.pack(pady=5)
        
        stats = get_orders_by_status()
        for status, count in stats.items():
            status_text.insert(tk.END, f"{status}: {count}\n")
        status_text.config(state=tk.DISABLED)
        
        tk.Label(report_window, text="\n🏆 Топ-3 клиента:",
                font=("Arial", 11, "bold")).pack(pady=5)
        
        top_text = tk.Text(report_window, height=6, width=50)
        top_text.pack(pady=5)
        
        top_clients = get_top_3_clients()
        for i, (name, total) in enumerate(top_clients, 1):
            top_text.insert(tk.END, f"{i}. {name}: {total:.2f} руб\n")
        top_text.config(state=tk.DISABLED)
        
        tk.Button(report_window, text="Закрыть", command=report_window.destroy).pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = DeliveryApp(root)
    root.mainloop()