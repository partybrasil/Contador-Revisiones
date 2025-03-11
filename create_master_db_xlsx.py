from openpyxl import Workbook

# Crear un nuevo libro de trabajo y una hoja activa
wb = Workbook()
ws = wb.active

# Agregar encabezados
ws.append(['SKU', 'Título', 'EANs'])

# Agregar un ejemplo de producto
ws.append(['123456', 'Producto de Ejemplo', '1234567890123,2345678901234'])

# Guardar el archivo
wb.save('c:\\Users\\usuario\\Proyectos\\Contador-Revisiones\\db.xlsx')
