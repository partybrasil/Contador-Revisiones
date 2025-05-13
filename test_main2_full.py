import os
import shutil
import pytest
from unittest.mock import MagicMock
from datetime import datetime
import sqlite3
import logging
from kivy.clock import Clock
from main2 import ContadorApp

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')

@pytest.fixture(scope="module")
def app():
    # Preparar entorno limpio
    if os.path.exists('db.db'):
        os.remove('db.db')
    if os.path.exists('REVs'):
        shutil.rmtree('REVs')
    if os.path.exists('OUTPUT'):
        shutil.rmtree('OUTPUT')
    app = ContadorApp()
    root = app.build()
    yield app, root
    # Limpieza final
    try:
        if hasattr(app, 'conn'):
            try:
                app.conn.close()
            except Exception as e:
                logging.warning(f"Error cerrando la conexión a la base de datos: {e}")
    except Exception as e:
        logging.warning(f"Error accediendo a la conexión a la base de datos: {e}")
    import gc, time
    gc.collect()
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

# --- TESTS DE LÓGICA Y DB ---
def test_init_db(app):
    app, _ = app
    app.init_db()
    assert os.path.exists('db.db')
    conn = sqlite3.connect('db.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='productos'")
    assert cursor.fetchone() is not None

def test_add_product_to_db(app):
    app, _ = app
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

def test_search_product_in_db(app):
    app, _ = app
    found, sku, titulo = app.search_product_in_db("123456")
    assert found
    assert sku == "SKU1"
    assert titulo == "Producto Test"
    found, sku, titulo = app.search_product_in_db("NOEXISTE")
    assert not found

def test_on_ean_enter_found(app):
    app, _ = app
    app.ean_sku_id.text = "123456"
    app.show_results_popup = MagicMock()
    app.show_add_product_popup = MagicMock()
    app.cursor.execute("INSERT OR IGNORE INTO productos (sku, titulo, eans) VALUES (?, ?, ?)", ("SKU2", "Otro", "123456"))
    app.conn.commit()
    app.on_ean_enter(None)
    assert app.show_results_popup.called

def test_on_ean_enter_not_found(app):
    app, _ = app
    app.ean_sku_id.text = "NOEXISTE"
    app.show_results_popup = MagicMock()
    app.show_add_product_popup = MagicMock()
    app.on_ean_enter(None)
    assert app.show_add_product_popup.called

def test_reset_fields(app):
    app, _ = app
    app.ean_sku_id.text = "test"
    app.marca_titulo.text = "test"
    app.slider.value = 10
    app.slider_value.text = "10"
    app.reset_fields()
    assert app.ean_sku_id.text == ""
    assert app.marca_titulo.text == ""
    assert app.slider.value == 1
    assert app.slider_value.text == "1"

def test_registrar_revision(app):
    app, _ = app
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

def test_edit_db_popup_and_save_new_eans(app):
    app, _ = app
    app.ean_sku_id.text = "SKU1"
    app.show_warning_popup = MagicMock()
    app.edit_db_popup = MagicMock()
    app.new_eans_input = MagicMock()
    app.new_eans_input.text = "654321"
    app.save_new_eans("SKU1", "123456")
    app.cursor.execute("SELECT eans FROM productos WHERE sku='SKU1'")
    eans = app.cursor.fetchone()[0]
    assert "654321" in eans

def test_on_marca_titulo_enter_allin(app):
    app, _ = app
    app.marca_titulo.text = app.SECRET_KEYWORD
    app.load_special_results = MagicMock()
    app.on_marca_titulo_enter(None)
    assert app.load_special_results.called

def test_on_marca_titulo_enter_duplicate(app):
    app, _ = app
    app.marca_titulo.text = app.DUPLICATE_EAN_KEYWORD
    app.load_special_results = MagicMock()
    app.on_marca_titulo_enter(None)
    assert app.load_special_results.called

def test_on_marca_titulo_enter_keywords(app):
    app, _ = app
    app.marca_titulo.text = "Producto"
    app.load_special_results = MagicMock()
    app.on_marca_titulo_enter(None)
    assert app.load_special_results.called

def test_toggle_lock_mode(app):
    app, _ = app
    app.ex1_btn = MagicMock()
    app.status_bar = MagicMock()
    app.ean_sku_id.focus = False
    app.toggle_lock_mode(None)
    assert app.lock_mode
    app.toggle_lock_mode(None)
    assert not app.lock_mode

def test_apply_locked_values(app):
    app, _ = app
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

def test_show_warning_popup(app):
    app, _ = app
    app.show_warning_popup("Mensaje de prueba")  # No debe lanzar excepción

def test_show_info_popup(app):
    app, _ = app
    app.on_info_popup_dismiss = MagicMock()
    app.info_popup = None
    app.show_info_popup("Título", "Mensaje")
    assert hasattr(app, 'info_popup')

def test_show_exit_confirmation(app):
    app, _ = app
    app.confirm_exit = MagicMock()
    app.show_exit_confirmation()
    assert hasattr(app, 'exit_confirmation_popup')

def test_focus_next(app):
    app, _ = app
    widget = MagicMock()
    next_widget = MagicMock()
    widget.get_focus_next.return_value = next_widget
    app.focus_next(widget)
    assert next_widget.focus

def test_on_slider_value_change(app):
    app, _ = app
    app.status_bar = MagicMock()
    app.on_slider_value_change(app.slider, 7)
    assert app.slider_value.text == "7"

def test_on_text_value_change(app):
    app, _ = app
    app.status_bar = MagicMock()
    app.slider_value.text = "8"
    app.on_text_value_change(app.slider_value)
    assert app.slider.value == 8

def test_on_text_value_change_invalid(app):
    app, _ = app
    app.status_bar = MagicMock()
    app.slider_value.text = "abc"
    app.slider.value = 3
    app.on_text_value_change(app.slider_value)
    assert app.slider_value.text == "3"

# --- TESTS DE UI VISUAL ---
def test_main_screen_widgets_exist(app):
    app, _ = app
    assert hasattr(app, 'ean_sku_id')
    assert hasattr(app, 'marca_titulo')
    assert hasattr(app, 'slider')
    assert hasattr(app, 'slider_value')
    assert hasattr(app, 'tipo_combobox')
    assert hasattr(app, 'revisado_btn')
    assert hasattr(app, 'traducir_btn')
    assert hasattr(app, 'traducido_btn')
    assert hasattr(app, 'status_bar')

def test_focus_and_textinput_ui(app):
    app, _ = app
    app.ean_sku_id.text = "123456"
    app.ean_sku_id.focus = True
    assert app.ean_sku_id.focus
    app.marca_titulo.text = "Marca test"
    app.marca_titulo.focus = True
    assert app.marca_titulo.focus

def test_slider_interaction_ui(app):
    app, _ = app
    app.slider.value = 42
    Clock.tick()
    assert app.slider_value.text == "42"

def test_button_press_ui(app):
    app, _ = app
    called = {"pressed": False}
    def fake_on_revisado(instance):
        called["pressed"] = True
    app.revisado_btn.unbind(on_press=None)
    app.revisado_btn.bind(on_press=fake_on_revisado)
    app.revisado_btn.trigger_action(duration=0.1)
    Clock.tick()
    assert called["pressed"]

def test_checkbox_toggle_ui(app):
    app, _ = app
    app.check_pt.active = False
    app.check_pt.active = True
    assert app.check_pt.active
    app.check_pt.active = False
    assert not app.check_pt.active

def test_open_traducir_popup_ui(app):
    app, _ = app
    app.on_traducir(None)
    assert hasattr(app, 'traducir_popup')
    assert hasattr(app, 'descripcion_input_pt')
    assert hasattr(app, 'descripcion_input_it')
    app.traducir_popup.dismiss()

def test_historial_popup_ui(app):
    app, _ = app
    app.on_historial(None)
    assert hasattr(app, 'historial_popup')
    app.historial_popup.dismiss()

def test_reset_button_ui(app):
    app, _ = app
    app.reset_btn.trigger_action(duration=0.1)
    Clock.tick()
    # Solo se comprueba que no lanza excepción

# NOTA: Ejecuta con: pytest -s test_main2_full.py
# NOTA: Requiere entorno gráfico o pytest-xvfb en Linux.

# NOTA: Para ejecutar todos los tests (lógica y UI) usa el siguiente comando en la terminal:

# pytest -s test_main2_full.py

# Si usas Linux sin entorno gráfico, instala pytest-xvfb y ejecuta:
# pytest -s --xvfb test_main2_full.py

# En Windows, solo asegúrate de tener la ventana activa o ejecuta en modo normal.
