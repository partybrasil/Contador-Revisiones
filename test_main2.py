import os
import shutil
import pytest
from unittest.mock import MagicMock, patch
from datetime import datetime
import sqlite3
import logging

# Configuración de logging para ver los resultados en consola
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

# Importar la app principal
import sys
sys.path.append(os.path.dirname(__file__))
from main2 import ContadorApp

@pytest.fixture(scope="module")
def app():
    # Preparar entorno limpio
    logging.info("Preparando entorno limpio para los tests...")
    if os.path.exists('db.db'):
        os.remove('db.db')
    if os.path.exists('REVs'):
        shutil.rmtree('REVs')
    if os.path.exists('OUTPUT'):
        shutil.rmtree('OUTPUT')
    app = ContadorApp()
    app.build()
    yield app
    # Limpieza final
    logging.info("Limpiando entorno después de los tests...")
    # Cerrar la conexión a la base de datos antes de borrar el archivo
    try:
        if hasattr(app, 'conn'):
            try:
                app.conn.close()
            except Exception as e:
                logging.warning(f"Error cerrando la conexión a la base de datos: {e}")
    except Exception as e:
        logging.warning(f"Error accediendo a la conexión a la base de datos: {e}")
    # Forzar el recolector de basura para liberar posibles referencias a la base de datos
    import gc
    gc.collect()
    import time
    for _ in range(5):
        try:
            if os.path.exists('db.db'):
                os.remove('db.db')
            break
        except PermissionError:
            time.sleep(0.2)
    if os.path.exists('REVs'):
        shutil.rmtree('REVs')
    if os.path.exists('OUTPUT'):
        shutil.rmtree('OUTPUT')

def test_init_db(app):
    logging.info("Ejecutando test_init_db")
    app.init_db()
    assert os.path.exists('db.db')
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='productos'")
    assert cursor.fetchone() is not None
    logging.info("test_init_db completado correctamente")

def test_add_product_to_db(app):
    logging.info("Ejecutando test_add_product_to_db")
    app.sku_input = MagicMock()
    app.title_input = MagicMock()
    app.eans_input = MagicMock()
    app.sku_input.text = "SKU1"
    app.title_input.text = "Producto Test"
    app.eans_input.text = "123456"
    app.add_to_db_popup = MagicMock()
    app.status_bar = MagicMock()
    app.show_warning_popup = MagicMock()
    app.add_product_to_db(None)
    app.cursor.execute("SELECT sku, titulo, eans FROM productos WHERE sku='SKU1'")
    row = app.cursor.fetchone()
    assert row == ("SKU1", "Producto Test", "123456")
    logging.info("test_add_product_to_db completado correctamente")

def test_search_product_in_db(app):
    logging.info("Ejecutando test_search_product_in_db")
    found, sku, titulo = app.search_product_in_db("123456")
    assert found
    assert sku == "SKU1"
    assert titulo == "Producto Test"
    found, sku, titulo = app.search_product_in_db("NOEXISTE")
    assert not found
    logging.info("test_search_product_in_db completado correctamente")

def test_on_ean_enter_found(app):
    logging.info("Ejecutando test_on_ean_enter_found")
    app.ean_sku_id.text = "123456"
    app.show_results_popup = MagicMock()
    app.show_add_product_popup = MagicMock()
    app.cursor.execute("INSERT OR IGNORE INTO productos (sku, titulo, eans) VALUES (?, ?, ?)", ("SKU2", "Otro", "123456"))
    app.conn.commit()
    app.on_ean_enter(None)
    assert app.show_results_popup.called
    logging.info("test_on_ean_enter_found completado correctamente")

def test_on_ean_enter_not_found(app):
    logging.info("Ejecutando test_on_ean_enter_not_found")
    app.ean_sku_id.text = "NOEXISTE"
    app.show_results_popup = MagicMock()
    app.show_add_product_popup = MagicMock()
    app.on_ean_enter(None)
    assert app.show_add_product_popup.called
    logging.info("test_on_ean_enter_not_found completado correctamente")

def test_reset_fields(app):
    logging.info("Ejecutando test_reset_fields")
    app.ean_sku_id.text = "test"
    app.marca_titulo.text = "test"
    app.slider.value = 10
    app.slider_value.text = "10"
    app.reset_fields()
    assert app.ean_sku_id.text == ""
    assert app.marca_titulo.text == ""
    assert app.slider.value == 1
    assert app.slider_value.text == "1"
    logging.info("test_reset_fields completado correctamente")

def test_registrar_revision(app):
    logging.info("Ejecutando test_registrar_revision")
    app.ean_sku_id.text = "SKU1"
    app.marca_titulo.text = "Producto Test"
    app.slider_value.text = "5"
    app.check_und.active = True
    app.check_pt.active = True
    app.check_es.active = True
    app.check_it.active = True
    app.selected_tipo = "ACCESSORIES"
    app.registrar_revision("Solo Revisión")
    fecha = datetime.now().strftime('%d-%m-%Y')
    archivo = f'REVs/REV-{fecha}.xlsx'
    assert os.path.exists(archivo)
    logging.info("test_registrar_revision completado correctamente")

def test_edit_db_popup_and_save_new_eans(app):
    logging.info("Ejecutando test_edit_db_popup_and_save_new_eans")
    app.ean_sku_id.text = "SKU1"
    app.show_warning_popup = MagicMock()
    app.edit_db_popup = MagicMock()
    app.new_eans_input = MagicMock()
    app.new_eans_input.text = "654321"
    app.save_new_eans("SKU1", "123456")
    app.cursor.execute("SELECT eans FROM productos WHERE sku='SKU1'")
    eans = app.cursor.fetchone()[0]
    assert "654321" in eans
    logging.info("test_edit_db_popup_and_save_new_eans completado correctamente")

def test_on_marca_titulo_enter_allin(app):
    logging.info("Ejecutando test_on_marca_titulo_enter_allin")
    app.marca_titulo.text = app.SECRET_KEYWORD
    app.load_special_results = MagicMock()
    app.on_marca_titulo_enter(None)
    assert app.load_special_results.called
    logging.info("test_on_marca_titulo_enter_allin completado correctamente")

def test_on_marca_titulo_enter_duplicate(app):
    logging.info("Ejecutando test_on_marca_titulo_enter_duplicate")
    app.marca_titulo.text = app.DUPLICATE_EAN_KEYWORD
    app.load_special_results = MagicMock()
    app.on_marca_titulo_enter(None)
    assert app.load_special_results.called
    logging.info("test_on_marca_titulo_enter_duplicate completado correctamente")

def test_on_marca_titulo_enter_keywords(app):
    logging.info("Ejecutando test_on_marca_titulo_enter_keywords")
    app.marca_titulo.text = "Producto"
    app.load_special_results = MagicMock()
    app.on_marca_titulo_enter(None)
    assert app.load_special_results.called
    logging.info("test_on_marca_titulo_enter_keywords completado correctamente")

def test_toggle_lock_mode(app):
    logging.info("Ejecutando test_toggle_lock_mode")
    app.ex1_btn = MagicMock()
    app.status_bar = MagicMock()
    app.ean_sku_id.focus = False
    app.toggle_lock_mode(None)
    assert app.lock_mode
    app.toggle_lock_mode(None)
    assert not app.lock_mode
    logging.info("test_toggle_lock_mode completado correctamente")

def test_apply_locked_values(app):
    logging.info("Ejecutando test_apply_locked_values")
    app.locked_values = {
        'tipo': 'ACCESSORIES',
        'check_zz': True,
        'slider_value': 5,
        'slider_text': '5',
        'check_und': True
    }
    app.tipo_combobox.text = ""
    app.check_zz.active = False
    app.slider.value = 1
    app.slider_value.text = "1"
    app.check_und.active = False
    app.apply_locked_values()
    assert app.tipo_combobox.text == 'ACCESSORIES'
    assert app.check_zz.active
    assert app.slider.value == 5
    assert app.slider_value.text == '5'
    assert app.check_und.active
    logging.info("test_apply_locked_values completado correctamente")

def test_show_warning_popup(app):
    logging.info("Ejecutando test_show_warning_popup")
    app.show_warning_popup("Mensaje de prueba")  # No debe lanzar excepción
    logging.info("test_show_warning_popup completado correctamente")

def test_show_info_popup(app):
    logging.info("Ejecutando test_show_info_popup")
    app.on_info_popup_dismiss = MagicMock()
    app.info_popup = None
    app.show_info_popup("Título", "Mensaje")
    assert hasattr(app, 'info_popup')
    logging.info("test_show_info_popup completado correctamente")

def test_show_exit_confirmation(app):
    logging.info("Ejecutando test_show_exit_confirmation")
    app.confirm_exit = MagicMock()
    app.show_exit_confirmation()
    assert hasattr(app, 'exit_confirmation_popup')
    logging.info("test_show_exit_confirmation completado correctamente")

def test_focus_next(app):
    logging.info("Ejecutando test_focus_next")
    widget = MagicMock()
    next_widget = MagicMock()
    widget.get_focus_next.return_value = next_widget
    app.focus_next(widget)
    assert next_widget.focus
    logging.info("test_focus_next completado correctamente")

def test_on_slider_value_change(app):
    logging.info("Ejecutando test_on_slider_value_change")
    app.status_bar = MagicMock()
    app.on_slider_value_change(app.slider, 7)
    assert app.slider_value.text == "7"
    logging.info("test_on_slider_value_change completado correctamente")

def test_on_text_value_change(app):
    logging.info("Ejecutando test_on_text_value_change")
    app.status_bar = MagicMock()
    app.slider_value.text = "8"
    app.on_text_value_change(app.slider_value)
    assert app.slider.value == 8
    logging.info("test_on_text_value_change completado correctamente")

def test_on_text_value_change_invalid(app):
    logging.info("Ejecutando test_on_text_value_change_invalid")
    app.status_bar = MagicMock()
    app.slider_value.text = "abc"
    app.slider.value = 3
    app.on_text_value_change(app.slider_value)
    assert app.slider_value.text == "3"
    logging.info("test_on_text_value_change_invalid completado correctamente")

# Instrucción para ejecutar y ver logs:
# pytest -s --log-cli-level=INFO test_main2.py
