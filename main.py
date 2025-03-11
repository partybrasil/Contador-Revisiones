import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.core.window import Window
import sqlite3
from datetime import datetime
import os
from openpyxl import load_workbook, Workbook
from kivy.uix.switch import Switch
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle

# Configuración de la ventana
Window.clearcolor = (0.1, 0.1, 0.1, 1)  # Fondo negro
Window.size = (500, 400)  # Tamaño inicial de la ventana

class CustomSwitch(Switch):
    def __init__(self, **kwargs):
        super(CustomSwitch, self).__init__(**kwargs)
        self.bind(active=self.on_active)
        self.bind(pos=self.on_pos)
        self.bind(size=self.on_size)

    def on_active(self, instance, value):
        if self.canvas is not None:
            self.canvas.before.clear()
            with self.canvas.before:
                Color(0, 1, 0, 1) if value else Color(1, 0, 0, 1)
                Rectangle(pos=self.pos, size=self.size)

    def on_size(self, *args):
        self.on_active(self, self.active)

    def on_pos(self, *args):
        self.on_active(self, self.active)

class ContadorApp(App):
    def build(self):
        self.title = 'Contador de Revisiones'
        self.root = BoxLayout(orientation='vertical', padding=10, spacing=10)
        Window.bind(on_resize=self.on_window_resize)
        self.init_db()
        
        # Checkboxes para Regalo ZZ, LOTE, Consumo
        self.check_regalo = CheckBox(size_hint=(None, None), size=(48, 48))
        self.check_lote = CheckBox(size_hint=(None, None), size=(48, 48))
        self.check_consumo = CheckBox(size_hint=(None, None), size=(48, 48))
        
        self.check_regalo.bind(active=self.on_special_checkbox_active)
        self.check_lote.bind(active=self.on_special_checkbox_active)
        self.check_consumo.bind(active=self.on_special_checkbox_active)
        
        special_checkbox_layout = BoxLayout(size_hint=(1, 0.1))
        special_checkbox_layout.add_widget(Label(text='Regalo ZZ', color=(1, 1, 1, 1)))
        special_checkbox_layout.add_widget(self.check_regalo)
        special_checkbox_layout.add_widget(Label(text='LOTE', color=(1, 1, 1, 1)))
        special_checkbox_layout.add_widget(self.check_lote)
        special_checkbox_layout.add_widget(Label(text='Consumo', color=(1, 1, 1, 1)))
        special_checkbox_layout.add_widget(self.check_consumo)
        self.root.add_widget(special_checkbox_layout)
        
        # Campo de texto EAN/SKU/ID
        self.ean_sku_id = TextInput(hint_text='EAN/SKU/ID', multiline=False, size_hint=(1, 0.1))
        self.ean_sku_id.bind(on_text_validate=self.on_ean_enter)
        self.root.add_widget(self.ean_sku_id)
        
        # Campo de texto MARCA/TITULO
        self.marca_titulo = TextInput(hint_text='MARCA/TITULO', multiline=False, size_hint=(1, 0.1))
        self.marca_titulo.bind(on_text_validate=self.focus_next)
        self.root.add_widget(self.marca_titulo)
        
        # Checkboxes
        self.check_pt = CheckBox(size_hint=(None, None), size=(48, 48))
        self.check_es = CheckBox(size_hint=(None, None), size=(48, 48))
        self.check_it = CheckBox(size_hint=(None, None), size=(48, 48))
        
        checkbox_layout = BoxLayout(size_hint=(1, 0.1))
        checkbox_layout.add_widget(Label(text='Tiene PT', color=(1, 1, 1, 1)))
        checkbox_layout.add_widget(self.check_pt)
        checkbox_layout.add_widget(Label(text='Tiene ES', color=(1, 1, 1, 1)))
        checkbox_layout.add_widget(self.check_es)
        checkbox_layout.add_widget(Label(text='Tiene IT', color=(1, 1, 1, 1)))
        checkbox_layout.add_widget(self.check_it)
        self.root.add_widget(checkbox_layout)
        
        # Barra deslizante y campo numérico
        self.slider = Slider(min=0, max=1000, value=1, size_hint=(1, 0.1))  # Valor inicial cambiado a 1
        self.slider_value = TextInput(text='1', multiline=False, size_hint=(None, None), size=(60, 48))  # Valor inicial cambiado a 1
        self.slider.bind(value=self.on_slider_value_change)
        self.slider_value.bind(on_text_validate=self.on_text_value_change)
        
        slider_layout = BoxLayout(size_hint=(1, 0.1))
        slider_layout.add_widget(Label(text='Cantidad Neta', color=(1, 1, 1, 1)))
        slider_layout.add_widget(self.slider)
        slider_layout.add_widget(self.slider_value)
        self.root.add_widget(slider_layout)
        
        # Checkboxes para UND, ML, GR
        self.check_und = CheckBox(size_hint=(None, None), size=(48, 48))
        self.check_ml = CheckBox(size_hint=(None, None), size=(48, 48))
        self.check_gr = CheckBox(size_hint=(None, None), size=(48, 48))
        
        self.check_und.bind(active=self.on_unit_checkbox_active)
        self.check_ml.bind(active=self.on_unit_checkbox_active)
        self.check_gr.bind(active=self.on_unit_checkbox_active)
        
        unit_checkbox_layout = BoxLayout(size_hint=(1, 0.1))
        unit_checkbox_layout.add_widget(Label(text='UND', color=(1, 1, 1, 1)))
        unit_checkbox_layout.add_widget(self.check_und)
        unit_checkbox_layout.add_widget(Label(text='ML', color=(1, 1, 1, 1)))
        unit_checkbox_layout.add_widget(self.check_ml)
        unit_checkbox_layout.add_widget(Label(text='GR', color=(1, 1, 1, 1)))
        unit_checkbox_layout.add_widget(self.check_gr)
        self.root.add_widget(unit_checkbox_layout)
        
        # Botones
        self.revisado_btn = Button(text='REVISADO', size_hint=(1, 1))
        self.revisado_btn.bind(on_press=self.on_revisado)
        self.traducir_btn = Button(text='TRADUCIR', size_hint=(1, 1))
        self.traducir_btn.bind(on_press=self.on_traducir)
        self.traducido_btn = Button(text='TRADUCIDO', size_hint=(1, 1))
        self.traducido_btn.bind(on_press=self.on_traducido)
        
        button_layout = BoxLayout(size_hint=(1, 0.1))
        button_layout.add_widget(self.revisado_btn)
        button_layout.add_widget(self.traducir_btn)
        button_layout.add_widget(self.traducido_btn)
        self.root.add_widget(button_layout)
        
        # Barra de estado
        self.status_bar = Label(text='Estado: Esperando...', size_hint=(1, 0.1), color=(1, 1, 1, 1))
        self.root.add_widget(self.status_bar)
        
        self.descripcion = ''
        self.modo_empleo = ''
        self.precauciones = ''
        self.mas_informaciones = ''
        self.traduccion_tipo = ''
        
        return self.root

    def init_db(self):
        self.conn = sqlite3.connect('db.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                sku TEXT PRIMARY KEY,
                titulo TEXT,
                eans TEXT
            )
        ''')
        self.conn.commit()

    def on_window_resize(self, instance, width, height):
        self.status_bar.text = f'Estado: Ventana redimensionada a {width}x{height}'

    def focus_next(self, instance):
        next_widget = instance.get_focus_next()
        if next_widget:
            next_widget.focus = True

    def on_slider_value_change(self, instance, value):
        self.slider_value.text = str(int(value))
        self.status_bar.text = f'Estado: Slider movido a {int(value)}'

    def on_text_value_change(self, instance):
        value = self.slider_value.text
        if value.isdigit() and 0 <= int(value) <= 1000:
            self.slider.value = int(value)
            self.status_bar.text = f'Estado: Valor del campo numérico cambiado a {value}'
        else:
            self.slider_value.text = str(int(self.slider.value))

    def on_ean_enter(self, instance):
        ean = self.ean_sku_id.text.strip()
        if not ean:
            self.show_warning_popup('El campo EAN/SKU/ID\nno puede estar vacío.')
            return

        self.show_loading_popup('Espere, cargando...')
        self.root.do_layout()
        found, sku, title = self.search_product_in_db(ean)
        self.loading_popup.dismiss()
        if found:
            self.ean_sku_id.text = sku
            self.marca_titulo.text = title
            self.show_info_popup('Producto encontrado', f'SKU: {sku}\nTítulo: {title}')
        else:
            self.show_add_product_popup(ean)

    def search_product_in_db(self, ean):
        self.cursor.execute('SELECT sku, titulo FROM productos WHERE eans LIKE ?', ('%' + ean + '%',))
        result = self.cursor.fetchone()
        if result:
            return True, result[0], result[1]
        return False, '', ''

    def show_loading_popup(self, message):
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text=message, text_size=(280, None), halign='center'))
        self.loading_popup = Popup(title='Cargando',
                                   content=content,
                                   size_hint=(0.6, 0.4),
                                   auto_dismiss=False)
        self.loading_popup.open()

    def show_info_popup(self, title, message):
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text=message, text_size=(280, None), halign='center'))
        popup = Popup(title=title,
                      content=content,
                      size_hint=(0.6, 0.4))
        popup.open()

    def show_add_product_popup(self, ean):
        content = BoxLayout(orientation='vertical', padding=10)
        content.add_widget(Label(text=f'El producto con EAN {ean} no se encontró.'))
        content.add_widget(Label(text='¿Desea agregarlo a la base de datos?'))
        button_layout = BoxLayout(size_hint=(1, 0.2))
        continue_button = Button(text='Continuar')
        continue_button.bind(on_press=lambda x: self.continue_without_adding(ean))
        add_button = Button(text='Añadir a DB')
        add_button.bind(on_press=lambda x: self.show_add_to_db_popup(ean))
        button_layout.add_widget(continue_button)
        button_layout.add_widget(add_button)
        content.add_widget(button_layout)
        self.add_product_popup = Popup(title='Agregar Producto',
                                       content=content,
                                       size_hint=(0.8, 0.4))
        self.add_product_popup.open()

    def continue_without_adding(self, ean):
        self.add_product_popup.dismiss()
        self.ean_sku_id.text = ean

    def show_add_to_db_popup(self, ean):
        self.add_product_popup.dismiss()
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        self.sku_input = TextInput(hint_text='SKU (Codigo ID Unico)', multiline=False)
        self.title_input = TextInput(hint_text='Titulo (Marca y Descripción)', multiline=False)
        self.eans_input = TextInput(hint_text='EANs (separados por coma si hay varios)', multiline=False)
        add_button = Button(text='Añadir')
        add_button.bind(on_press=self.add_product_to_db)
        content.add_widget(self.sku_input)
        content.add_widget(self.title_input)
        content.add_widget(self.eans_input)
        content.add_widget(add_button)
        self.add_to_db_popup = Popup(title='Añadir a la Base de Datos',
                                     content=content,
                                     size_hint=(0.8, 0.6))
        self.add_to_db_popup.open()

    def add_product_to_db(self, instance):
        sku = self.sku_input.text.strip()
        title = self.title_input.text.strip()
        eans = self.eans_input.text.strip()
        if sku and title and eans:
            self.show_loading_popup('Añadiendo a la base de datos...')
            self.root.do_layout()
            self.cursor.execute('INSERT INTO productos (sku, titulo, eans) VALUES (?, ?, ?)', (sku, title, eans))
            self.conn.commit()
            self.loading_popup.dismiss()
            self.add_to_db_popup.dismiss()
            self.ean_sku_id.text = sku
            self.marca_titulo.text = title
        else:
            self.show_warning_popup('Todos los campos son obligatorios.')

    def on_special_checkbox_active(self, checkbox, value):
        if value:
            if checkbox == self.check_regalo:
                self.check_lote.active = False
                self.check_consumo.active = False
            elif checkbox == self.check_lote:
                self.check_regalo.active = False
                self.check_consumo.active = False
                self.show_lote_popup()
            elif checkbox == self.check_consumo:
                self.check_regalo.active = False
                self.check_lote.active = False

    def show_lote_popup(self):
        self.lote_popup = Popup(title='Composición de Lote',
                                content=BoxLayout(orientation='vertical'),
                                size_hint=(0.8, 0.5))
        self.lote_text_input = TextInput(hint_text='EANs separados por líneas', multiline=True)
        next_button = Button(text='Siguiente', size_hint=(1, 0.2))
        next_button.bind(on_press=self.on_next_lote)
        accept_button = Button(text='Aceptar', size_hint=(1, 0.2))
        accept_button.bind(on_press=self.on_accept_lote)
        
        self.lote_popup.content.add_widget(self.lote_text_input)
        self.lote_popup.content.add_widget(next_button)
        self.lote_popup.content.add_widget(accept_button)
        self.lote_popup.open()

    def on_next_lote(self, instance):
        self.lote_text_input.text += '\n'

    def on_accept_lote(self, instance):
        eans = self.lote_text_input.text.strip().split('\n')
        self.lote_composition = ','.join([f'"{ean.strip()}"' for ean in eans if ean.strip()])
        self.lote_popup.dismiss()

    def on_unit_checkbox_active(self, checkbox, value):
        if value:
            if checkbox == self.check_und:
                self.check_ml.active = False
                self.check_gr.active = False
            elif checkbox == self.check_ml:
                self.check_und.active = False
                self.check_gr.active = False
            elif checkbox == self.check_gr:
                self.check_und.active = False
                self.check_ml.active = False

    def show_warning_popup(self, message):
        content = BoxLayout(orientation='vertical', padding=10)
        label = Label(text=message, text_size=(280, None), halign='center', valign='middle', size_hint_y=None)
        label.bind(texture_size=label.setter('size'))
        content.add_widget(label)
        popup = Popup(title='Advertencia',
                      content=content,
                      size_hint=(0.6, 0.4))
        popup.open()

    def on_revisado(self, instance):
        if not self.ean_sku_id.text.strip():
            self.show_warning_popup('El campo EAN/SKU/ID\nno puede estar vacío.')
        else:
            self.registrar_revision('Solo Revisión')
            self.status_bar.text = 'Estado: Producto revisado'
            self.slider.value = 1  # Volver a 1 después de revisar
            self.slider_value.text = '1'  # Volver a 1 después de revisar

    def on_traducir(self, instance):
        self.traducir_popup = Popup(title='Traducciones',
                                    content=BoxLayout(orientation='vertical', spacing=10, padding=10),
                                    size_hint=(0.8, 0.8))
        
        self.switch_traduccion = CustomSwitch(active=False, size_hint=(None, None), size=(100, 48))
        switch_layout = BoxLayout(size_hint=(1, 0.1), spacing=10)
        switch_layout.add_widget(Label(text='PT', color=(1, 1, 1, 1)))
        switch_layout.add_widget(self.switch_traduccion)
        switch_layout.add_widget(Label(text='IT', color=(1, 1, 1, 1)))
        
        self.descripcion_input = TextInput(hint_text='Descripcion', multiline=True, size_hint=(1, 0.2))
        self.modo_empleo_input = TextInput(hint_text='Modo de Empleo', multiline=True, size_hint=(1, 0.2))
        self.precauciones_input = TextInput(hint_text='Precauciones', multiline=True, size_hint=(1, 0.2))
        self.mas_informaciones_input = TextInput(hint_text='Más Informaciones', multiline=True, size_hint=(1, 0.2))
        
        grabar_button = Button(text='Grabar y Volver', size_hint=(1, 0.2))
        grabar_button.bind(on_press=self.on_grabar_traducciones)
        
        self.traducir_popup.content.add_widget(switch_layout)
        self.traducir_popup.content.add_widget(self.descripcion_input)
        self.traducir_popup.content.add_widget(self.modo_empleo_input)
        self.traducir_popup.content.add_widget(self.precauciones_input)
        self.traducir_popup.content.add_widget(self.mas_informaciones_input)
        self.traducir_popup.content.add_widget(grabar_button)
        self.traducir_popup.open()

    def on_grabar_traducciones(self, instance):
        traduccion_tipo = 'IT' if self.switch_traduccion.active else 'PT'
        self.descripcion = self.descripcion_input.text
        self.modo_empleo = self.modo_empleo_input.text
        self.precauciones = self.precauciones_input.text
        self.mas_informaciones = self.mas_informaciones_input.text
        self.traduccion_tipo = traduccion_tipo
        self.traducir_popup.dismiss()
        self.slider.value = 1  # Volver a 1 después de traducir
        self.slider_value.text = '1'  # Volver a 1 después de traducir

    def on_traducido(self, instance):
        if not self.ean_sku_id.text.strip():
            self.show_warning_popup('El campo EAN/SKU/ID\nno puede estar vacío.')
        else:
            self.registrar_revision('Revisado y Traducido')
            self.status_bar.text = 'Estado: Producto traducido'
            self.slider.value = 1  # Volver a 1 después de traducir
            self.slider_value.text = '1'  # Volver a 1 después de traducir

    def registrar_revision(self, estado):
        ean_sku_id = self.ean_sku_id.text
        marca_titulo = self.marca_titulo.text
        tipo = 'Regalo ZZ' if self.check_regalo.active else 'LOTE' if self.check_lote.active else 'Consumo' if self.check_consumo.active else ''
        tiene_pt = 'Tiene PT' if self.check_pt.active else 'No Tiene PT - TRADUZIDO'
        tiene_es = 'Tiene ES' if self.check_es.active else 'No Tiene ES - TRADUCIDO'
        tiene_it = 'Tiene IT' if self.check_it.active else 'No Tiene IT - TRADOTTO'
        cantidad_neta = self.slider_value.text
        unidad = 'UND' if self.check_und.active else 'ML' if self.check_ml.active else 'GR' if self.check_gr.active else ''
        composicion_lote = self.lote_composition if self.check_lote.active else ''
        
        fecha = datetime.now().strftime('%d-%m-%Y')
        archivo = f'REVs/REV-{fecha}.xlsx'
        
        descripcion_col = f'Descripcion{self.traduccion_tipo}' if self.traduccion_tipo else ''
        modo_empleo_col = f'Modo de Empleo{self.traduccion_tipo}' if self.traduccion_tipo else ''
        precauciones_col = f'Precauciones{self.traduccion_tipo}' if self.traduccion_tipo else ''
        mas_informaciones_col = f'Más Informaciones{self.traduccion_tipo}' if self.traduccion_tipo else ''
        
        if not os.path.exists('REVs'):
            os.makedirs('REVs')
        
        if os.path.exists(archivo):
            wb = load_workbook(archivo)
            ws = wb.active
        else:
            wb = Workbook()
            ws = wb.active
            ws.append(['EAN/SKU/ID', 'MARCA/TITULO', 'Tipo', 'Tiene PT', 'Tiene ES', 'Tiene IT', 'Cantidad Neta', 'UND/ML/GR', 'Composición de Lote', 'Estado', 'DescripcionPT', 'Modo de EmpleoPT', 'PrecaucionesPT', 'Más InformacionesPT', 'DescripcionIT', 'Modo de EmpleoIT', 'PrecaucionesIT', 'Más InformacionesIT'])
        
        ws.append([ean_sku_id, marca_titulo, tipo, tiene_pt, tiene_es, tiene_it, cantidad_neta, unidad, composicion_lote, estado, self.descripcion if self.traduccion_tipo == 'PT' else '', self.modo_empleo if self.traduccion_tipo == 'PT' else '', self.precauciones if self.traduccion_tipo == 'PT' else '', self.mas_informaciones if self.traduccion_tipo == 'PT' else '', self.descripcion if self.traduccion_tipo == 'IT' else '', self.modo_empleo if self.traduccion_tipo == 'IT' else '', self.precauciones if self.traduccion_tipo == 'IT' else '', self.mas_informaciones if self.traduccion_tipo == 'IT' else ''])
        wb.save(archivo)
        
        self.ean_sku_id.text = ''
        self.marca_titulo.text = ''
        self.check_regalo.active = False
        self.check_lote.active = False
        self.check_consumo.active = False
        self.check_pt.active = False
        self.check_es.active = False
        self.check_it.active = False
        self.slider.value = 1  # Volver a 1 después de resetear la interfaz
        self.slider_value.text = '1'  # Volver a 1 después de resetear la interfaz
        self.check_und.active = False
        self.check_ml.active = False
        self.check_gr.active = False
        self.lote_composition = ''
        self.descripcion = ''
        self.modo_empleo = ''
        self.precauciones = ''
        self.mas_informaciones = ''
        self.traduccion_tipo = ''

if __name__ == '__main__':
    ContadorApp().run()
