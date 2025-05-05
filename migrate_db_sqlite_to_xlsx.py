import sqlite3
from openpyxl import Workbook

# Conectar a la base de datos SQLite
conn = sqlite3.connect('db.db')
cursor = conn.cursor()

# Crear un nuevo archivo Excel
wb = Workbook()
ws = wb.active

# Escribir los encabezados en la primera fila
ws.append(['SKU', 'Titulo', 'EANs'])  # Encabezados de las columnas

# Obtener todos los productos de la base de datos
cursor.execute('SELECT sku, titulo, eans FROM productos')
productos = cursor.fetchall()

# Contar el número total de productos para mostrar el progreso
total_productos = len(productos)
print(f'Iniciando la migración de {total_productos} productos...')

# Escribir los datos de los productos en el archivo Excel
for idx, producto in enumerate(productos, start=1):
    ws.append(producto)  # Agregar cada producto como una fila
    print(f'Progreso: {idx}/{total_productos} productos migrados')

# Guardar el archivo Excel
wb.save('db.xlsx')

# Cerrar la conexión a la base de datos
conn.close()

print('Migración completada de SQLite a Excel.')
