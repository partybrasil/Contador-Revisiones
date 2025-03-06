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
from openpyxl import Workbook, load_workbook
from datetime import datetime
import os

# Configuración de la ventana
Window.clearcolor = (0.1, 0.1, 0.1, 1)  # Fondo negro
Window.size = (390, 360)  # Tamaño inicial de la ventana

class ContadorApp(App):
    def build(self):
        self.title = 'Contador de Revisiones'
        self.root = BoxLayout(orientation='vertical', padding=10, spacing=10)
        Window.bind(on_resize=self.on_window_resize)
        
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
        self.ean_sku_id.bind(on_text_validate=self.focus_next)
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
        self.slider = Slider(min=0, max=1000, value=0, size_hint=(1, 0.1))
        self.slider_value = TextInput(text='0', multiline=False, size_hint=(None, None), size=(60, 48))
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

    def focus_next(self, instance):
        next_widget = instance.get_focus_next()
        if next_widget:
            next_widget.focus = True

    def on_window_resize(self, instance, width, height):
        self.status_bar.text = f'Estado: Ventana redimensionada a {width}x{height}'

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

    def on_revisado(self, instance):
        self.registrar_revision('Solo Revisión')
        self.status_bar.text = 'Estado: Producto revisado'

    def on_traducido(self, instance):
        self.registrar_revision('Revisado y Traducido')
        self.status_bar.text = 'Estado: Producto traducido'

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
        
        if not os.path.exists('REVs'):
            os.makedirs('REVs')
        
        if os.path.exists(archivo):
            wb = load_workbook(archivo)
            ws = wb.active
        else:
            wb = Workbook()
            ws = wb.active
            ws.append(['EAN/SKU/ID', 'MARCA/TITULO', 'Tipo', 'Tiene PT', 'Tiene ES', 'Tiene IT', 'Cantidad Neta', 'UND/ML/GR', 'Composición de Lote', 'Estado'])
        
        ws.append([ean_sku_id, marca_titulo, tipo, tiene_pt, tiene_es, tiene_it, cantidad_neta, unidad, composicion_lote, estado])
        wb.save(archivo)
        
        self.ean_sku_id.text = ''
        self.marca_titulo.text = ''
        self.check_regalo.active = False
        self.check_lote.active = False
        self.check_consumo.active = False
        self.check_pt.active = False
        self.check_es.active = False
        self.check_it.active = False
        self.slider.value = 0
        self.slider_value.text = '0'
        self.check_und.active = False
        self.check_ml.active = False
        self.check_gr.active = False
        self.lote_composition = ''

if __name__ == '__main__':
    ContadorApp().run()
