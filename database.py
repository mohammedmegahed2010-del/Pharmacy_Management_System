import sqlite3

connection = sqlite3.connect('pharmacy.db', check_same_thread=False)
cr = connection.cursor()

cr.execute('''
CREATE TABLE IF NOT EXISTS Medicine(
    name TEXT UNIQUE, 
    ingredient TEXT, 
    price REAL, 
    quantity INTEGER, 
    category TEXT
)''')

cr.execute('''
CREATE TABLE IF NOT EXISTS Sales(
    sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
    medicine_name TEXT,
    quantity_sold INTEGER,
    total_price REAL,
    sale_date TEXT
)''')

connection.commit()

def add_medicine(name, ingredient, price, quantity, category="UnKnown"):
    try:
        cr.execute('INSERT INTO Medicine VALUES(?, ?, ?, ?, ?)', [name, ingredient, price, quantity, category])
        connection.commit()
        return "تمت الإضافة بنجاح"
    except sqlite3.IntegrityError:
        return f"الصنف {name} موجود بالفعل"

def delete_medicine(name):
    cr.execute('DELETE FROM Medicine WHERE name = ?', (name,))
    connection.commit()
    if cr.rowcount > 0:
        return "تم الحذف بنجاح"
    return "هذا الصنف غير موجود"

def update_stock(medicine_name, new_total_quantity):
    try:
        cr.execute('UPDATE Medicine SET quantity = ? WHERE name = ?', (new_total_quantity, medicine_name))
        if cr.rowcount == 0:
            return "الصنف غير موجود"
        connection.commit()
        return "تم تعديل الكمية بنجاح"
    except sqlite3.Error:
        return "حدث خطأ أثناء تعديل الكمية"

def get_low_stock(threshold=5):
    cr.execute('SELECT * FROM Medicine WHERE quantity <= ?', (threshold,))
    return cr.fetchall()

def search_by(search_by, search_keyword):
    if search_by in ["name", "ingredient", "category"]:
        cr.execute(f'SELECT * FROM Medicine WHERE {search_by} LIKE ?', (f'%{search_keyword}%',))
        return cr.fetchall()
    return []

def get_all_medicines():
    cr.execute('SELECT * FROM Medicine ORDER BY name')
    return cr.fetchall()

def get_total_inventory_value():
    cr.execute('SELECT SUM(price * quantity) FROM Medicine')
    result = cr.fetchone()[0]
    return result if result is not None else 0

def count_distinct(column_name):
    if column_name in ["name", "ingredient", "price", "quantity", "category"]:
        cr.execute(f'SELECT DISTINCT {column_name} FROM Medicine')
        return cr.fetchall()
    return f"لا يوجد عمود بهذا الاسم: {column_name}"

def update_medicine_info(name, new_ingredient, new_price, new_quantity, new_category):
    cr.execute('''
        UPDATE Medicine 
        SET ingredient = ?, price = ?, quantity = ?, category = ?
        WHERE name = ?
    ''', (new_ingredient, new_price, new_quantity, new_category, name))

    connection.commit()

    if cr.rowcount == 0:
        return "الصنف غير موجود"

    return "تم تحديث بيانات الصنف"

def record_sale(medicine_name, quantity_sold):
    cr.execute('SELECT quantity, price FROM Medicine WHERE name = ?', (medicine_name,))
    item = cr.fetchone()
    if item and item[0] >= quantity_sold:
        new_qty = item[0] - quantity_sold
        total_price = item[1] * quantity_sold
        cr.execute('UPDATE Medicine SET quantity = ? WHERE name = ?', (new_qty, medicine_name))
        from datetime import datetime
        current_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cr.execute('INSERT INTO Sales (medicine_name, quantity_sold, total_price, sale_date) VALUES(?, ?, ?, ?)',
                   (medicine_name, quantity_sold, total_price, current_date))
        connection.commit()
        return f"تمت البيعة بنجاح! الإجمالي: {total_price} ج.م"
    elif item is None:
        return "الصنف غير موجود"
    else:
        return "الكمية غير كافية"
    
def close_connection():
    connection.close()