import os
os.environ['KIVY_NO_ARGS'] = '1'
from kivy.config import Config
Config.set('graphics', 'window', 'auto')
Config.set('graphics', 'resizable', True)
Config.set('input', 'mouse', 'mouse,disable_multitouch')
# Раскомментируйте одну из строк ниже для исправления вставки текста
# Config.set('kivy', 'clipboard', 'xclip')
Config.set('kivy', 'clipboard', 'xsel')
# Config.set('kivy', 'clipboard', 'gtk')
# Config.set('kivy', 'clipboard', 'qt')
# Config.set('kivy', 'clipboard', 'sdl2')

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.image import Image
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView

import threading
import webbrowser
from urllib.parse import urlparse, urljoin
import requests
from bs4 import BeautifulSoup

API_URL = "http://83.217.28.113:5000/patients"

# ---------- Парсер на BeautifulSoup ----------
class Bs4Parser:
    def __init__(self, start_urls, keywords, max_pages=30, max_depth=2):
        self.start_urls = start_urls
        self.keywords = [kw.strip().lower() for kw in keywords]
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.visited_urls = set()
        self.pages_parsed = 0
        self.allowed_domains = [urlparse(url).netloc for url in start_urls]
        self.callback = None

    def normalize_url(self, url):
        parsed = urlparse(url)
        return parsed._replace(fragment='').geturl()

    def fetch_page(self, url):
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.status_code == 200:
                return resp.text
        except:
            return None

    def parse_page(self, url, depth):
        norm_url = self.normalize_url(url)
        if norm_url in self.visited_urls or self.pages_parsed >= self.max_pages:
            return []
        self.visited_urls.add(norm_url)
        self.pages_parsed += 1

        html = self.fetch_page(url)
        if not html:
            return []

        soup = BeautifulSoup(html, 'html.parser')
        page_text = soup.get_text().lower()

        found = [kw for kw in self.keywords if kw in page_text]
        if found:
            first_kw = found[0]
            pos = page_text.find(first_kw)
            start = max(0, pos - 100)
            end = min(len(page_text), pos + 100)
            snippet = page_text[start:end].replace('\n', ' ').strip()
            result = {
                'url': url,
                'keywords': ', '.join(found),
                'snippet': snippet[:200] + ('...' if len(snippet) > 200 else '')
            }
            if self.callback:
                self.callback(result)

        links = []
        if depth < self.max_depth:
            for a in soup.find_all('a', href=True):
                next_url = urljoin(url, a['href'])
                parsed = urlparse(next_url)
                if parsed.netloc in self.allowed_domains:
                    links.append(self.normalize_url(next_url))
        return links

    def start(self, callback):
        self.callback = callback
        queue = list(self.start_urls)
        depth_map = {url: 0 for url in queue}

        while queue and self.pages_parsed < self.max_pages:
            url = queue.pop(0)
            depth = depth_map.get(url, 0)
            new_links = self.parse_page(url, depth)
            for link in new_links:
                if link not in self.visited_urls and link not in depth_map:
                    depth_map[link] = depth + 1
                    queue.append(link)

        if self.callback:
            self.callback(None, finished=True)

# ---------- Менеджер тем ----------
class ThemeManager:
    light_theme = {
        'window_bg': (1, 1, 1, 1),
        'label_fg': (0, 0, 0, 1),
        'input_bg': (1, 1, 1, 1),
        'input_fg': (0, 0, 0, 1),
        'header_bg': (0.19, 0.55, 0.87, 1),
        'button_primary': (0.8, 0.25, 0.2, 1),
        'button_secondary': (0.2, 0.6, 0.4, 1),
        'button_neutral': (0.5, 0.5, 0.5, 1),
        'result_bg1': (0.95, 0.95, 0.95, 1),
        'result_bg2': (0.9, 0.9, 0.9, 1),
        'result_fg': (0, 0, 0, 1),
    }

    dark_theme = {
        'window_bg': (0.1, 0.1, 0.1, 1),
        'label_fg': (1, 1, 1, 1),
        'input_bg': (0.2, 0.2, 0.2, 1),
        'input_fg': (1, 1, 1, 1),
        'header_bg': (0.1, 0.3, 0.5, 1),
        'button_primary': (0.6, 0.2, 0.15, 1),
        'button_secondary': (0.15, 0.45, 0.3, 1),
        'button_neutral': (0.3, 0.3, 0.3, 1),
        'result_bg1': (0.25, 0.25, 0.25, 1),
        'result_bg2': (0.2, 0.2, 0.2, 1),
        'result_fg': (1, 1, 1, 1),
    }

    def __init__(self):
        self.current_theme = 'light'
        self.colors = self.light_theme

    def toggle(self):
        if self.current_theme == 'light':
            self.current_theme = 'dark'
            self.colors = self.dark_theme
        else:
            self.current_theme = 'light'
            self.colors = self.light_theme
        return self.colors

# ---------- Универсальная шапка ----------
class Header(BoxLayout):
    def __init__(self, right_button_text="Парсер", right_button_action=None, **kwargs):
        super().__init__(
            orientation='horizontal',
            size_hint_y=None,
            height=dp(100),
            padding=[dp(20), 0],
            spacing=dp(10),
            **kwargs
        )

        self.theme_manager = App.get_running_app().theme_manager

        with self.canvas.before:
            Color(*self.theme_manager.colors['header_bg'])
            self.bg = Rectangle(pos=self.pos, size=self.size)

        self.bind(pos=self.update_bg, size=self.update_bg)

        self.logo = Image(
            source="assets/logo.png",
            size_hint=(None, None),
            size=(dp(60), dp(60)),
            pos_hint={'center_y': 0.5}
        )

        self.title = Label(
            text="Duplex",
            font_size="28sp",
            bold=True,
            color=(1, 1, 1, 1),
            size_hint=(None, None),
            size=(dp(200), dp(60)),
            halign="left",
            valign="middle"
        )
        self.title.bind(size=self.title.setter('text_size'))
        self.title.pos_hint = {'center_y': 0.5}

        self.add_widget(self.logo)
        self.add_widget(self.title)

        self.add_widget(Widget())

        self.theme_btn = Button(
            text="☾" if self.theme_manager.current_theme == 'light' else "☀",
            size_hint=(None, None),
            size=(dp(50), dp(50)),
            background_normal='',
            background_color=(1, 1, 1, 0.3),
            color=(1, 1, 1, 1),
            pos_hint={'center_y': 0.5}
        )
        self.theme_btn.bind(on_release=self.toggle_theme)
        self.add_widget(self.theme_btn)

        self.right_btn = Button(
            text=right_button_text,
            size_hint=(None, None),
            size=(dp(120), dp(50)),
            background_normal='',
            background_color=self.theme_manager.colors['button_secondary'],
            color=(1, 1, 1, 1),
            pos_hint={'center_y': 0.5}
        )
        if right_button_action:
            self.right_btn.bind(on_release=right_button_action)
        self.add_widget(self.right_btn)

    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def apply_theme(self, colors):
        self.canvas.before.clear()
        with self.canvas.before:
            Color(*colors['header_bg'])
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.theme_btn.text = "☀" if colors == self.theme_manager.dark_theme else "☾"
        self.right_btn.background_color = colors['button_secondary']

    def toggle_theme(self, *args):
        app = App.get_running_app()
        app.toggle_theme()

# ---------- Виджет одного результата (текст + кнопка "Открыть") ----------
class ResultWidget(BoxLayout):
    def __init__(self, index, keywords, url, snippet, bg_color, text_color, **kwargs):
        super().__init__(orientation='horizontal', size_hint_y=None, height=dp(120), spacing=dp(10), padding=dp(5), **kwargs)
        self.url = url
        self.bg_color = bg_color

        with self.canvas.before:
            Color(*bg_color)
            self.bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self.update_bg, size=self.update_bg)

        # Текстовая часть (с переносом)
        text_label = Label(
            text=f"[b]{index}. {keywords}[/b] – {url}\n…{snippet}…",
            markup=True,
            color=text_color,
            size_hint_x=0.8,
            halign='left',
            valign='top',
            text_size=(None, None)
        )
        text_label.bind(size=text_label.setter('text_size'))
        self.add_widget(text_label)

        # Кнопка "Открыть"
        open_btn = Button(
            text="Открыть",
            size_hint_x=0.2,
            background_normal='',
            background_color=(0.2, 0.6, 0.4, 1) if bg_color == (0.95,0.95,0.95,1) else (0.15,0.45,0.3,1),
            color=(1,1,1,1)
        )
        open_btn.bind(on_release=self.open_url)
        self.add_widget(open_btn)

    def update_bg(self, *args):
        self.bg.pos = self.pos
        self.bg.size = self.size

    def open_url(self, instance):
        if self.url:
            webbrowser.open(self.url)

# ---------- Главный экран ----------
class MainUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation="vertical", spacing=dp(15), padding=dp(15), **kwargs)
        self.app = App.get_running_app()
        self.theme_manager = self.app.theme_manager
        self.manager = None

        self.header = Header(
            right_button_text="Парсер",
            right_button_action=self.go_to_parser
        )
        self.add_widget(self.header)

        controls = BoxLayout(size_hint_y=None, height=dp(90), spacing=dp(15))

        type_box = BoxLayout(orientation="vertical")
        type_box.add_widget(Label(text="Тип ошибки (пусто = все)", size_hint_y=None, height=dp(25)))
        self.type_input = TextInput(hint_text="Тип ошибки", multiline=False)
        type_box.add_widget(self.type_input)

        code_box = BoxLayout(orientation="vertical")
        code_box.add_widget(Label(text="Код ошибки (точное совпадение)", size_hint_y=None, height=dp(25)))
        self.code_input = TextInput(hint_text="Код ошибки", multiline=False)
        code_box.add_widget(self.code_input)

        self.start_btn = Button(
            text="Начать",
            size_hint_x=None,
            width=dp(170),
            background_normal="",
            background_color=self.theme_manager.colors['button_primary'],
            color=(1, 1, 1, 1)
        )
        self.start_btn.bind(on_release=self.load_data)

        controls.add_widget(type_box)
        controls.add_widget(code_box)
        controls.add_widget(self.start_btn)

        self.add_widget(controls)

        self.output = TextInput(
            text="Нажмите 'Начать' для загрузки данных...",
            readonly=True,
            multiline=True,
            halign="left"
        )
        self.add_widget(self.output)

        self.apply_theme()

    def set_manager(self, manager):
        self.manager = manager

    def go_to_parser(self, *args):
        if self.manager:
            self.manager.current = 'parser'

    def apply_theme(self):
        colors = self.theme_manager.colors
        Window.clearcolor = colors['window_bg']
        self.type_input.background_color = colors['input_bg']
        self.type_input.foreground_color = colors['input_fg']
        self.code_input.background_color = colors['input_bg']
        self.code_input.foreground_color = colors['input_fg']
        self.output.background_color = colors['input_bg']
        self.output.foreground_color = colors['input_fg']
        self.start_btn.background_color = colors['button_primary']
        for child in self.walk(restrict=True):
            if isinstance(child, Label):
                child.color = colors['label_fg']
        self.header.apply_theme(colors)

    def load_data(self, *args):
        import requests
        self.output.text = "Загрузка данных..."
        try:
            response = requests.get(API_URL, timeout=5)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            self.output.text = f"Ошибка подключения к API:\n{e}"
            return

        type_filter = self.type_input.text.strip()
        code_filter = self.code_input.text.strip()
        results = []

        for record in data:
            errors = record.get("errors", {})
            error_value = errors.get("error", "")
            code_value = errors.get("error_code", "")

            if not error_value or not error_value.strip():
                continue
            if type_filter and type_filter.lower() not in error_value.lower():
                continue
            if code_filter and str(code_value).strip() != code_filter:
                continue

            personal = record.get("personal_info", {})
            fio = f"{personal.get('last_name', '')} {personal.get('first_name', '')} {personal.get('middle_name', '')}".strip()
            block = (f"ID: {record.get('patient_id')}\nФИО: {fio}\nОшибка: {error_value}\nКод ошибки: {code_value}\n{'-'*60}")
            results.append(block)

        if not results:
            self.output.text = "Записи, соответствующие фильтрам, не найдены."
        else:
            self.output.text = "\n".join(results)
            self.output.scroll_y = 1

# ---------- Экран парсера (с динамическими виджетами) ----------
class ParserScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = App.get_running_app()
        self.theme_manager = self.app.theme_manager
        self.is_parsing = False
        self.result_counter = 0

        layout = BoxLayout(orientation='vertical', spacing=dp(15), padding=dp(15))

        self.header = Header(
            right_button_text="На главную",
            right_button_action=self.go_to_main
        )
        layout.add_widget(self.header)

        layout.add_widget(Label(
            text="Ресурсы (каждый URL с новой строки):",
            size_hint_y=None,
            height=dp(30),
            halign='left',
            color=self.theme_manager.colors['label_fg']
        ))
        self.resources_input = TextInput(
            hint_text="https://example.com\nhttps://another.com",
            multiline=True,
            size_hint_y=None,
            height=dp(100)
        )
        layout.add_widget(self.resources_input)

        layout.add_widget(Label(
            text="Ключевые слова (через запятую):",
            size_hint_y=None,
            height=dp(30),
            halign='left',
            color=self.theme_manager.colors['label_fg']
        ))
        self.keywords_input = TextInput(
            hint_text="ноутбук, смартфон, apple",
            multiline=False,
            size_hint_y=None,
            height=dp(40)
        )
        layout.add_widget(self.keywords_input)

        self.parse_btn = Button(
            text="Начать парсинг",
            size_hint_y=None,
            height=dp(50),
            background_normal='',
            background_color=self.theme_manager.colors['button_secondary'],
            color=(1, 1, 1, 1)
        )
        self.parse_btn.bind(on_release=self.start_parsing)
        layout.add_widget(self.parse_btn)

        # ScrollView для результатов
        self.scroll = ScrollView(size_hint=(1, 1))
        self.results_container = BoxLayout(orientation='vertical', size_hint_y=None, spacing=dp(5))
        self.results_container.bind(minimum_height=self.results_container.setter('height'))
        self.scroll.add_widget(self.results_container)
        layout.add_widget(self.scroll)

        self.add_widget(layout)
        self.apply_theme()

    def go_to_main(self, *args):
        self.manager.current = 'main'

    def apply_theme(self):
        colors = self.theme_manager.colors
        self.header.apply_theme(colors)
        for child in self.walk(restrict=True):
            if isinstance(child, Label):
                child.color = colors['label_fg']
            elif isinstance(child, TextInput):
                child.background_color = colors['input_bg']
                child.foreground_color = colors['input_fg']
        self.parse_btn.background_color = colors['button_secondary']

    def start_parsing(self, *args):
        if self.is_parsing:
            return

        urls_text = self.resources_input.text.strip()
        keywords_text = self.keywords_input.text.strip()

        if not urls_text:
            self.show_message("Введите хотя бы один URL")
            return
        if not keywords_text:
            self.show_message("Введите ключевые слова")
            return

        urls = [line.strip() for line in urls_text.splitlines() if line.strip()]
        keywords = [kw.strip() for kw in keywords_text.split(',') if kw.strip()]

        self.parse_btn.text = "Парсинг..."
        self.parse_btn.disabled = True
        self.is_parsing = True
        self.result_counter = 0

        # Очищаем предыдущие результаты
        self.results_container.clear_widgets()

        def thread_target():
            def safe_callback(item, finished=False):
                Clock.schedule_once(lambda dt: self.on_result(item, finished))
            parser = Bs4Parser(urls, keywords)
            parser.start(safe_callback)

        thread = threading.Thread(target=thread_target, daemon=True)
        thread.start()

    def on_result(self, item, finished=False):
        if finished:
            self.parse_btn.text = "Начать парсинг"
            self.parse_btn.disabled = False
            self.is_parsing = False
            if self.result_counter == 0:
                self.show_message("Парсинг завершён. Результатов не найдено.")
        else:
            self.result_counter += 1
            colors = self.theme_manager.colors
            bg = colors['result_bg1'] if self.result_counter % 2 == 0 else colors['result_bg2']
            # Создаём виджет результата
            result_widget = ResultWidget(
                index=self.result_counter,
                keywords=item['keywords'],
                url=item['url'],
                snippet=item['snippet'],
                bg_color=bg,
                text_color=colors['result_fg']
            )
            self.results_container.add_widget(result_widget)

    def show_message(self, msg):
        # Добавляем временное сообщение в контейнер
        msg_label = Label(
            text=msg,
            size_hint_y=None,
            height=dp(50),
            color=self.theme_manager.colors['result_fg']
        )
        self.results_container.add_widget(msg_label)

# ---------- Обёртка главного экрана ----------
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.ui = MainUI()
        self.ui.set_manager(self.manager)
        self.add_widget(self.ui)

    def on_enter(self, *args):
        self.ui.set_manager(self.manager)

    def apply_theme(self):
        self.ui.apply_theme()

# ---------- Приложение ----------
class DuplexApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.theme_manager = ThemeManager()

    def build(self):
        self.title = "Duplex"
        self.icon = "assets/logo.png"
        Window.clearcolor = self.theme_manager.colors['window_bg']

        sm = ScreenManager()
        main_screen = MainScreen(name='main')
        parser_screen = ParserScreen(name='parser')
        sm.add_widget(main_screen)
        sm.add_widget(parser_screen)
        return sm

    def toggle_theme(self):
        self.theme_manager.toggle()
        Window.clearcolor = self.theme_manager.colors['window_bg']
        for screen in self.root.screens:
            if hasattr(screen, 'apply_theme'):
                screen.apply_theme()

if __name__ == "__main__":
    DuplexApp().run()