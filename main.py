from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.camera import Camera
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy.graphics import Color, Rectangle
from pyzbar.pyzbar import decode
from kivy.clock import Clock
import numpy as np
from io import BytesIO
from PIL import Image
import requests_cache
from pydub import AudioSegment
from pydub.playback import play
# from kivy.uix.image import Image
from kivy.clock import Clock
from googleapiclient.discovery import build
from google.oauth2 import service_account
from googlesearch import search
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from pyzbar.pyzbar import decode
import cv2
import numpy as np
from kivy.uix.popup import Popup
from kivy.uix.label import Label
import threading
import time
import re
import requests
from kivy.lang import Builder
from kivy.uix.behaviors import ButtonBehavior
from kivy.core.window import Window

Builder.load_string("""
<CustomButton>:
    background_normal: ''
    canvas.before:
        Color:
            rgba: [0.18, 0.58, 0.74, 1] if self.state == 'normal' else [0.067, 0.22, 0.278, 1]
        RoundedRectangle:
            pos: self.pos
            size: self.size
            radius: [15,]
""")

class CustomButton(ButtonBehavior, Label):
    pass


class LoadingPopup(Popup):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = 'Carregando...'
        self.content = Label(text='Pesquisando no Google, aguarde...')
        self.auto_dismiss = False

class ListScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        keyfile = 'secretes.json'
        scope = ['https://www.googleapis.com/auth/spreadsheets']
        credentials = service_account.Credentials.from_service_account_file(keyfile, scopes=scope)
        self.service = build('sheets', 'v4', credentials=credentials)
        self.spreadsheet_id = '1bPyum8hlQddBfn4yloaBDt6OrTinjLTGwOot-hV6OJ0'
        self.sheet_name = 'Estoque'
        options = Options()
        options.headless = True
        self.driver = webdriver.Chrome(options=options)
        largura, altura = Window.size

        print(f"Largura da tela: {largura}px")
        print(f"Altura da tela: {altura}px")
        layout = BoxLayout(orientation='vertical', spacing=10)
        layout.size = [largura, altura]
        
        with layout.canvas.before:
            Color(1, 1, 1, 1)  # Define a cor de fundo como branco
            self.rect = Rectangle(pos=layout.pos, size=layout.size)

        self.list_send = []
        # Criar uma instância do popup de loading
        self.loading_popup = LoadingPopup()

        self.label = Label(text='[color=#2e94bc][b]Lista[/b]\n[/color]', 
                      markup=True, size_hint=(1, 0.2))
        button_back = CustomButton(text='Voltar para a Tela Principal', size_hint=(1, 0.2))
        button_back.bind(on_release=self.switch_to_main_screen)

        button_send = CustomButton(text='Enviar para Planilha', size_hint=(1, 0.2))
        button_send.bind(on_release=self.start_send)  # Modificamos aqui para chamar o método start_send()

        layout.add_widget(self.label)
        layout.add_widget(button_send)
        layout.add_widget(button_back)

        self.add_widget(layout)

    def start_send(self, instance):
        # Mostrar o popup de loading durante a pesquisa no Google
        self.loading_popup.title = "Carregando..."
        self.loading_popup.content.text = 'Pesquisando no Google, aguarde...'
        self.loading_popup.open()

        # Realizar a pesquisa no Google em segundo plano (em uma thread separada)
        threading.Thread(target=self.send, daemon=True).start()

    def send(self):
         # Variável para garantir que a pesquisa no Google seja executada apenas uma vez
        searched_google = False

        for barcode in self.list_send:
            if not searched_google:
                # Fazer a pesquisa no Google apenas uma vez
                # searched_google = True
                # self.label.text = f"Pesquisando {barcode} - Não feche o app"
                print("Aqui")
                self.update_spreadsheet(barcode)

        self.list_send = []

    def search_google(self, query):
        saved_url = ""
        price = 0
        qnt = 0
        i = 1
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:77.0) Gecko/20100101 Firefox/77.0'}
        num_results = 5
        lang = "pt"
        search_results = []
         # Configurar o cache para armazenar em disco por 1 hora
        requests_cache.install_cache('google_search_cache', expire_after=0)



        while i < num_results:
            google_search = requests.get(f"https://www.google.com/search?q={query}&start={i}&num={num_results}&hl={lang}", headers=headers)
            soup = BeautifulSoup(google_search.text, 'html.parser')
            searched = soup.select('.tF2Cxc')
            print("TO AQ")
            if saved_url:
                break
        
            for result in searched:
                print("Aqui qui aqui")
                link = result.select_one('a')
                if link:
                    search_results.append(link['href'])

                    if("amazon" in link):
                        saved_url = link['href']
                        break

            i += num_results

        saved_url = search_results[-1]        
        print("Iniciando pesquisa")
       
        self.driver.get(saved_url)
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')
        if (soup.title):
            title = soup.title.string
        else:
            title = "Não encontrou título"
        qnt += 1

        if "amazon" in saved_url:
            price_element = soup.find('span', id='listPrice')
            if price_element:
                price = price_element.text.strip()
            else:
                price = 'Não foi possível encontrar o preço do produto.'

        text = f"Registrando {title}, na planilha com preço {price} ..."
        print(text)
        # self.loading_popup.content = Label(text=text)
        # driver.quit()
        return title, price, qnt

    def update_spreadsheet(self, query):
       

        result = self.service.spreadsheets().values().get(spreadsheetId=self.spreadsheet_id, range=self.sheet_name).execute()
        records = result.get('values', [])
        num_rows = len(records)

        exists = False
        update_range = ''
        body = {}

        for i, record in enumerate(records):
            if i == 0:
                continue
            if len(record) >= 2:
                if query in record[0]:
                    exists = True
                    qnt = int(records[i][1])
                    qnt += 1
                    records[i][1] = qnt
                    update_range = f'{self.sheet_name}!B{i+1}'
                    body = {
                        'values': [[records[i][1]]]
                    }

        if not exists:
            print("Not exists")
            title, price, qnt = self.search_google(query)
            new_record = [str(query), qnt, title, price]
            range_to_update = f'{self.sheet_name}!A{num_rows + 1}:D{num_rows + 1}'
            request_body = {
                'values': [new_record]
            }
            request = self.service.spreadsheets().values().update(spreadsheetId=self.spreadsheet_id, range=range_to_update,
                                                            valueInputOption='RAW', body=request_body)
            response = request.execute()
            print(response)
            self.label.text = "Sucesso - Registro adicionado!"
        else:
            print("Exists")
            update_request = self.service.spreadsheets().values().update(
                spreadsheetId=self.spreadsheet_id, range=update_range,
                valueInputOption='RAW', body=body)
            update_response = update_request.execute()
            self.label.text = "Sucesso - Linhas atualizadas!"

        self.loading_popup.dismiss()



    def on_pos(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

    def switch_to_main_screen(self, instance):
        app = App.get_running_app()
        app.root.current = 'main'

class CameraScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        largura, altura = Window.size
        print(f"Largura da tela: {largura}px")
        print(f"Altura da tela: {altura}px")
        layout.size = [largura, altura]

        with layout.canvas.before:
            Color(1, 1, 1, 1)  # Define a cor de fundo como branco
            self.rect = Rectangle(pos=layout.pos, size=layout.size)
        

        self.camera = Camera(resolution=(640, 480), size_hint=(1, 1), play=True)

        self.label = Label(text='[color=#2e94bc]Ler Código de Barras [/color]', markup=True, size_hint=(1, 0.2))
        button_back = CustomButton(text='Voltar para a Tela Principal', size_hint=(1, 0.2))
        button_back.bind(on_release=self.switch_to_main_screen)

        layout.add_widget(self.label)
        layout.add_widget(self.camera)
        layout.add_widget(button_back)

        self.add_widget(layout)

        # Inicia a atualização do processamento dos frames
        Clock.schedule_interval(self.process_frame, 1)

    def on_pos(self, *args):
        # Atualiza a posição e tamanho do retângulo quando a posição da tela da câmera é alterada
        self.rect.pos = self.pos
        self.rect.size = self.size

    def switch_to_main_screen(self, instance):
        app = App.get_running_app()
        app.root.current = 'main'
        # self.camera.play = False

    def play_sound(self):
        # Carrega o arquivo de som "beep.wav"
        sound = AudioSegment.from_wav("beep.wav")
        # Reproduz o som
        play(sound)

    def process_frame(self, dt):
        app = App.get_running_app()
        frame = self.camera.texture
        if frame is None:
            return

        # Convertemos o frame da câmera para uma imagem no formato aceito pelo decode
        image = Image.frombytes(mode='RGBA', size=frame.size, data=frame.pixels)
        image = image.convert('L')

        # Decodifica os códigos de barras presentes na imagem
        barcodes = decode(image)

        if barcodes:
            barcode_data = barcodes[0].data.decode('utf-8')
            self.label.text = f'[color=#2e94bc]Código de Barras:[b] {barcode_data}[/b] [/color]'
            app.list_screen.list_send.append(barcode_data)
            text_list = str(app.list_screen.list_send).replace(',','\n').replace('[','').replace(']','')
            app.list_screen.label.text = f'[color=#2e94bc][b]Lista[/b]\n \n {text_list} [/color]'
            # Reproduz o som de beep quando um código de barras é lido
            self.play_sound()
        # else:
        #     self.label.text = 'Tela da Câmera'

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        largura, altura = Window.size

        print(f"Largura da tela: {largura}px")
        print(f"Altura da tela: {altura}px")
        layout = BoxLayout(orientation='vertical', spacing=10)
        layout.size = [largura, altura]
        
        with layout.canvas.before:
            Color(1, 1, 1, 1)  # Define a cor de fundo como branco
            self.rect = Rectangle(pos=layout.pos, size=layout.size)

        button_camera = CustomButton(text='Abrir Câmera', size_hint=(1, 0.2))
        button_camera.bind(on_release=self.switch_to_camera_screen)

        button_list = CustomButton(text='Ver Lista', size_hint=(1, 0.2))
        button_list.bind(on_release=self.switch_to_list_screen)

        layout.add_widget(button_camera)
        layout.add_widget(button_list)

        self.add_widget(layout)

    def switch_to_camera_screen(self, instance):
        app = App.get_running_app()
        app.root.current = 'camera'

    def switch_to_list_screen(self, instance):
        app = App.get_running_app()
        app.root.current = 'list'

class MyScreenManager(ScreenManager):
    pass

class MyKivyApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def build(self):
        self.screen_manager = MyScreenManager()
        self.main_screen = MainScreen(name='main')
        self.camera_screen = CameraScreen(name='camera')
        self.list_screen = ListScreen(name='list')
        self.screen_manager.add_widget(self.main_screen)
        self.screen_manager.add_widget(self.camera_screen)
        self.screen_manager.add_widget(self.list_screen)
        return self.screen_manager

if __name__ == '__main__':
    MyKivyApp().run()
