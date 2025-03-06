import kivy
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.checkbox import CheckBox
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.progressbar import ProgressBar
from kivy.core.window import Window
from openpyxl import Workbook, load_workbook
from datetime import datetime
import os

# Configuración de la ventana
Window.clearcolor = (0.1, 0.1, 0.1, 1)  # Fondo negro
Window.size = (800, 600)

class ContadorApp(App):
    def build(self):
        self.update_title()
        self.root = BoxLayout(orientation='vertical', padding=10, spacing=10)
        Window.bind(on_resize=self.on_window_resize)
        
        # Campo de texto EAN/SKU/ID
        self.ean_sku_id = TextInput(hint_text='EAN/SKU/ID', multiline=False, size_hint=(1, 0.1))
        self.root.add_widget(self.ean_sku_id)
        
        # Campo de texto MARCA/TITULO
        self.marca_titulo = TextInput(hint_text='MARCA/TITULO', multiline=False, size_hint=(1, 0.1))
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
        self.slider = Slider(min=0, max=100, value=0, size_hint=(1, 0.1))
        self.slider_value = TextInput(text='0', multiline=False, size_hint=(None, None), size=(60, 48))
        self.slider.bind(value=self.on_slider_value_change)
        self.slider_value.bind(text=self.on_text_value_change)
        
        slider_layout = BoxLayout(size_hint=(1, 0.1))
        slider_layout.add_widget(Label(text='Cantidad Neta L/ML/GR', color=(1, 1, 1, 1)))
        slider_layout.add_widget(self.slider)
        slider_layout.add_widget(self.slider_value)
        self.root.add_widget(slider_layout)
        
        # Botones
        self.revisado_btn = Button(text='REVISADO', size_hint=(1, 0.1))
        self.revisado_btn.bind(on_press=self.on_revisado)
        self.traducido_btn = Button(text='TRADUCIDO', size_hint=(1, 0.1))
        self.traducido_btn.bind(on_press=self.on_traducido)
        
        button_layout = BoxLayout(size_hint=(1, 0.1))
        button_layout.add_widget(self.revisado_btn)
        button_layout.add_widget(self.traducido_btn)
        self.root.add_widget(button_layout)
        
        # Barra de estado
        self.status_bar = Label(text='Estado: Esperando...', size_hint=(1, 0.1), color=(1, 1, 1, 1))
        self.root.add_widget(self.status_bar)
        
        return self.root

    def update_title(self):
        self.title = f'Contador de Revisiones - {Window.width}x{Window.height}'

    def on_window_resize(self, instance, width, height):
        self.update_title()
        self.status_bar.text = f'Estado: Ventana redimensionada a {width}x{height}'

    def on_slider_value_change(self, instance, value):
        self.slider_value.text = str(int(value))
        self.status_bar.text = f'Estado: Slider movido a {int(value)}'

    def on_text_value_change(self, instance, value):
        if value.isdigit() and 0 <= int(value) <= 100:
            self.slider.value = int(value)
            self.status_bar.text = f'Estado: Valor del campo numérico cambiado a {value}'
        else:
            self.slider_value.text = str(int(self.slider.value))

    def on_revisado(self, instance):
        self.registrar_revision('Solo Revisión')
        self.status_bar.text = 'Estado: Producto revisado'

    def on_traducido(self, instance):
        self.registrar_revision('Revisado y Traducido')
        self.status_bar.text = 'Estado: Producto traducido'

    def registrar_revision(self, estado):
        ean_sku_id = self.ean_sku_id.text
        marca_titulo = self.marca_titulo.text
        tiene_pt = 'Tiene PT' if self.check_pt.active else 'No Tiene PT - TRADUZIDO'
        tiene_es = 'Tiene ES' if self.check_es.active else 'No Tiene ES - TRADUCIDO'
        tiene_it = 'Tiene IT' if self.check_it.active else 'No Tiene IT - TRADOTTO'
        cantidad_neta = self.slider_value.text

        fecha = datetime.now().strftime('%d-%m-%Y')
        archivo = f'REVs/REV-{fecha}.xlsx'
        
        if not os.path.exists('REVs'):
            os.makedirs('REVs')
        
        if os.path.exists(archivo):
            wb = load_workbook(archivo)
            ws = wb.active
        else:
            wb = Workbook()
            ws = wb.active
            ws.append(['EAN/SKU/ID', 'MARCA/TITULO', 'Tiene PT', 'Tiene ES', 'Tiene IT', 'Cantidad Neta', 'Estado'])
        
        ws.append([ean_sku_id, marca_titulo, tiene_pt, tiene_es, tiene_it, cantidad_neta, estado])
        wb.save(archivo)
        
        self.ean_sku_id.text = ''
        self.marca_titulo.text = ''
        self.check_pt.active = False
        self.check_es.active = False
        self.check_it.active = False
        self.slider.value = 0
        self.slider_value.text = '0'
        
        self.log_event(f'Registrado: {ean_sku_id}, {marca_titulo}, {tiene_pt}, {tiene_es}, {tiene_it}, {cantidad_neta}, {estado}')

    def log_event(self, message):
        with open('log.txt', 'a') as log_file:
            log_file.write(f'{datetime.now().strftime("%Y-%m-%d %H:%M:%S")} - {message}\n')

if __name__ == '__main__':
    ContadorApp().run()
