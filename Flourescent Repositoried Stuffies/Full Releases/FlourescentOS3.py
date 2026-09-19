import sys, json, smtplib, imaplib, email, wave, ffmpeg, sounddevice as sd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import os, requests, subprocess
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QMessageBox

REPO_URL = "https://api.github.com/repos/aydintepeemlak3867-cloud/FlourescentOS-3Store/contents"
DOWNLOAD_DIR = "DownloadedAppsStuff"

class StoreApp(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("FlourescentOStore")
        self.resize(500, 400)

        layout = QVBoxLayout()
        self.status = QLabel("🔄 Connecting to Store...")
        layout.addWidget(self.status)

        self.app_list = QListWidget()
        layout.addWidget(self.app_list)

        self.install_btn = QPushButton("Install Selected App")
        self.install_btn.clicked.connect(self.install_app)
        layout.addWidget(self.install_btn)

        self.setLayout(layout)
        self.pyapps = {}
        self.load_apps()

    def load_apps(self):
        try:
            response = requests.get(REPO_URL, timeout=5)
            if response.status_code == 200:
                files = response.json()
                pyapps = [f for f in files if f['name'].endswith('.PyApp')]
                if pyapps:
                    self.status.setText("✅ Store Online")
                    for app in pyapps:
                        self.app_list.addItem(app['name'])
                        self.pyapps[app['name']] = app
                else:
                    self.status.setText("❌ No Apps Found")
            else:
                self.status.setText("⚠️ Servers Not Found")
        except requests.exceptions.RequestException:
            self.status.setText("⚠️ No Data found(offline)")

    def install_app(self):
        selected = self.app_list.currentItem()
        if selected:
            app_name = selected.text()
            app_info = self.pyapps[app_name]
            url = app_info['download_url']
            os.makedirs(DOWNLOAD_DIR, exist_ok=True)
            path = os.path.join(DOWNLOAD_DIR, app_name)
            try:
                data = requests.get(url, timeout=10).content
                with open(path, 'wb') as f:
                    f.write(data)
                QMessageBox.information(self, "Install", f"{app_name} installed successfully!")
                # 🔗 Burada Apps uygulaması bu dosyayı çalıştırabilir
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to install {app_name}: {e}")

import os, subprocess
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidget, QPushButton, QMessageBox

DOWNLOAD_DIR = "DownloadedAppsStuff"

class AppRunner(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AppRunner")
        self.resize(500, 400)

        layout = QVBoxLayout()
        self.status = QLabel("🔄 Scanning DownloadedAppsStuff...")
        layout.addWidget(self.status)

        self.app_list = QListWidget()
        layout.addWidget(self.app_list)

        # Çalıştırma butonu
        self.run_btn = QPushButton("▶️ Run Selected App")
        self.run_btn.clicked.connect(self.run_app)
        layout.addWidget(self.run_btn)

        # Kaldırma butonu
        self.remove_btn = QPushButton("🗑️ Remove Selected App")
        self.remove_btn.clicked.connect(self.remove_app)
        layout.addWidget(self.remove_btn)

        # Yenileme butonu
        self.refresh_btn = QPushButton("🔄 Refresh List")
        self.refresh_btn.clicked.connect(self.load_local_apps)
        layout.addWidget(self.refresh_btn)

        self.setLayout(layout)
        self.load_local_apps()

    def load_local_apps(self):
        self.app_list.clear()
        if os.path.exists(DOWNLOAD_DIR):
            files = os.listdir(DOWNLOAD_DIR)
            pyapps = [f for f in files if f.endswith(".PyApp")]
            if pyapps:
                self.status.setText("✅ Apps Found")
                for app in pyapps:
                    self.app_list.addItem(app)
            else:
                self.status.setText("❌ No Apps Found")
        else:
            self.status.setText("⚠️ DownloadedAppsStuff Missing")

    def run_app(self):
        selected = self.app_list.currentItem()
        if selected:
            app_name = selected.text()
            path = os.path.join(DOWNLOAD_DIR, app_name)
            try:
                subprocess.Popen(["python", path])
                QMessageBox.information(self, "Run", f"{app_name} is running!")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to run {app_name}: {e}")

    def remove_app(self):
        selected = self.app_list.currentItem()
        if selected:
            app_name = selected.text()
            path = os.path.join(DOWNLOAD_DIR, app_name)
            try:
                os.remove(path)
                QMessageBox.information(self, "Remove", f"{app_name} removed successfully!")
                self.load_local_apps()
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed to remove {app_name}: {e}")


from PyQt6.QtCore import Qt, QTimer, QDateTime, QUrl, QDir
from PyQt6.QtGui import QColor, QPainter, QPen, QPixmap, QAction
from PyQt6.QtMultimedia import QMediaPlayer, QCamera, QImageCapture, QMediaCaptureSession
from PyQt6.QtMultimediaWidgets import QVideoWidget

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QComboBox
import math

class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculator - Flourescent OS")
        layout = QVBoxLayout()

        self.input = QLineEdit()
        self.input.setPlaceholderText("İşlem gir (örn: 2+2)")
        layout.addWidget(self.input)

        self.mode = QComboBox()
        self.mode.addItems(["Normal", "Bilimsel"])
        layout.addWidget(self.mode)

        btn_calc = QPushButton("Hesapla")
        btn_calc.clicked.connect(self.calculate)
        layout.addWidget(btn_calc)

        self.result_label = QLabel("Sonuç: ")
        layout.addWidget(self.result_label)

        self.setLayout(layout)

    def calculate(self):
        try:
            expr = self.input.text()
            if self.mode.currentText() == "Bilimsel":
                result = eval(expr, {"__builtins__": None}, math.__dict__)
            else:
                result = eval(expr)
            self.result_label.setText(f"Sonuç: {result}")
        except Exception as e:
            self.result_label.setText(f"Hata: {e}")

import json
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel

class Dictionary(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dictionary - Flourescent OS")
        layout = QVBoxLayout()

        self.word_input = QLineEdit()
        self.word_input.setPlaceholderText("Kelime gir")
        layout.addWidget(self.word_input)

        btn_search = QPushButton("Ara")
        btn_search.clicked.connect(self.search_word)
        layout.addWidget(btn_search)

        self.result_label = QLabel("Tanım: ")
        layout.addWidget(self.result_label)

        self.setLayout(layout)

        # Basit JSON sözlük
        self.data = {
            "python": "Yüksek seviyeli programlama dili.",
            "qt": "C++ tabanlı GUI framework.",
            "ai": "Yapay zeka, öğrenen sistemler."
        }

    def search_word(self):
        word = self.word_input.text().lower()
        meaning = self.data.get(word, "Bulunamadı")
        self.result_label.setText(f"Tanım: {meaning}")

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QComboBox

class Translator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Translator - Flourescent OS")
        layout = QVBoxLayout()

        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Çevrilecek metin")
        layout.addWidget(self.text_input)

        self.lang_box = QComboBox()
        self.lang_box.addItems(["English", "Turkish"])
        layout.addWidget(self.lang_box)

        btn_translate = QPushButton("Çevir")
        btn_translate.clicked.connect(self.translate)
        layout.addWidget(btn_translate)

        self.result_label = QLabel("Sonuç: ")
        layout.addWidget(self.result_label)

        self.setLayout(layout)

    def translate(self):
        text = self.text_input.text().lower()
        lang = self.lang_box.currentText()
        # Basit mock çeviri
        translations = {
            "hello": "merhaba",
            "world": "dünya",
            "merhaba": "hello",
            "dünya": "world"
        }
        result = translations.get(text, "Çeviri yok")
        self.result_label.setText(f"Sonuç: {result}")

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel

class Weather(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Weather - Flourescent OS")
        layout = QVBoxLayout()

        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("Şehir gir")
        layout.addWidget(self.city_input)

        btn_check = QPushButton("Hava Durumu")
        btn_check.clicked.connect(self.check_weather)
        layout.addWidget(btn_check)

        self.result_label = QLabel("Durum: ")
        layout.addWidget(self.result_label)

        self.setLayout(layout)

    def check_weather(self):
        city = self.city_input.text().lower()
        mock_data = {
            "istanbul": "Güneşli, 30°C",
            "ankara": "Bulutlu, 25°C",
            "izmir": "Rüzgarlı, 28°C"
        }
        result = mock_data.get(city, "Veri yok")
        self.result_label.setText(f"Durum: {result}")

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QListWidget, QPushButton

class NewsReader(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("News Reader - Flourescent OS")
        layout = QVBoxLayout()

        self.list = QListWidget()
        layout.addWidget(self.list)

        btn_load = QPushButton("Haberleri Yükle")
        btn_load.clicked.connect(self.load_news)
        layout.addWidget(btn_load)

        self.setLayout(layout)

    def load_news(self):
        # Mock haberler
        news = [
            "Yeni teknoloji fuarı İstanbul’da başladı.",
            "Yapay zeka uygulamaları hızla yayılıyor.",
            "Ekonomi gündeminde enflasyon tartışmaları."
        ]
        self.list.clear()
        for n in news:
            self.list.addItem(n)

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton
from PyQt6.QtWebEngineWidgets import QWebEngineView

class Maps(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Maps - Flourescent OS")
        layout = QVBoxLayout()

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Adres gir (örn: İstanbul)")
        layout.addWidget(self.url_input)

        btn_go = QPushButton("Git")
        btn_go.clicked.connect(self.load_map)
        layout.addWidget(btn_go)

        self.browser = QWebEngineView()
        layout.addWidget(self.browser)

        self.setLayout(layout)

    def load_map(self):
        place = self.url_input.text()
        if place:
            url = f"https://www.google.com/maps/search/{place}"
            self.browser.setUrl(url)

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QGridLayout, QMessageBox
import random

class Games(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Minesweeper - Flourescent OS")
        layout = QVBoxLayout()

        self.grid = QGridLayout()
        layout.addLayout(self.grid)

        self.buttons = {}
        self.mines = set(random.sample(range(25), 5))  # 5 mayın

        for i in range(5):
            for j in range(5):
                btn = QPushButton("")
                btn.setFixedSize(40, 40)
                btn.clicked.connect(lambda _, x=i, y=j: self.reveal(x, y))
                self.grid.addWidget(btn, i, j)
                self.buttons[(i, j)] = btn

        self.setLayout(layout)

    def reveal(self, i, j):
        idx = i * 5 + j
        if idx in self.mines:
            QMessageBox.warning(self, "Kaybettin!", "Mayına bastın!")
            for (x, y), btn in self.buttons.items():
                if (x * 5 + y) in self.mines:
                    btn.setText("💣")
        else:
            count = sum(((x * 5 + y) in self.mines) for x in range(max(0, i-1), min(5, i+2))
                        for y in range(max(0, j-1), min(5, j+2)))
            self.buttons[(i, j)].setText(str(count))

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QColorDialog, QFontDialog, QLabel

class Settings(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings - Flourescent OS")
        layout = QVBoxLayout()

        btn_color = QPushButton("Tema Rengi Seç")
        btn_color.clicked.connect(self.choose_color)
        layout.addWidget(btn_color)

        btn_font = QPushButton("Font Seç")
        btn_font.clicked.connect(self.choose_font)
        layout.addWidget(btn_font)

        self.preview = QLabel("Önizleme")
        layout.addWidget(self.preview)

        self.setLayout(layout)

    def choose_color(self):
        color = QColorDialog.getColor()
        if color.isValid():
            self.preview.setStyleSheet(f"color: {color.name()};")

    def choose_font(self):
        font, ok = QFontDialog.getFont()
        if ok:
            self.preview.setFont(font)

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog
from PyQt6.QtPdf import QPdfDocument
from PyQt6.QtPdfWidgets import QPdfView
from PyQt6.QtCore import QUrl

class PDFViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Viewer - Flourescent OS")
        self.resize(800, 600)

        layout = QVBoxLayout()

        # PDF görüntüleyici
        self.viewer = QPdfView()
        layout.addWidget(self.viewer)

        # Aç butonu
        btn_open = QPushButton("PDF Aç")
        btn_open.clicked.connect(self.open_pdf)
        layout.addWidget(btn_open)

        self.setLayout(layout)

        # PDF dokümanı
        self.doc = QPdfDocument(self)

    def open_pdf(self):
        fname, _ = QFileDialog.getOpenFileName(
            self, "PDF Aç", "", "PDF Files (*.pdf)"
        )
        if fname:
            # QUrl ile yükleme
            url = QUrl.fromLocalFile(fname)
            self.doc.load(url)
            self.viewer.setDocument(self.doc)


from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QListWidget, QFileDialog
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtCore import QUrl

class Music(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Music - Flourescent OS")
        layout = QVBoxLayout()

        self.list = QListWidget()
        layout.addWidget(self.list)

        btn_add = QPushButton("Parça Ekle")
        btn_add.clicked.connect(self.add_song)
        layout.addWidget(btn_add)

        btn_play = QPushButton("Oynat")
        btn_play.clicked.connect(self.play_song)
        layout.addWidget(btn_play)

        self.setLayout(layout)
        self.player = QMediaPlayer()

    def add_song(self):
        fnames, _ = QFileDialog.getOpenFileNames(self, "Parça Aç", "", "Audio Files (*.mp3 *.wav *.ogg)")
        for f in fnames:
            self.list.addItem(f)

    def play_song(self):
        row = self.list.currentRow()
        if row >= 0:
            fname = self.list.item(row).text()
            url = QUrl.fromLocalFile(fname)
            self.player.setSource(url)
            self.player.play()



import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QMenuBar, QTableWidget, QTableWidgetItem,
    QPushButton, QFileDialog, QInputDialog
)
from PyQt6.QtGui import QAction

class Calendar(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calendar - Flourescent OS")
        layout = QVBoxLayout()

        # Menü çubuğu
        menubar = QMenuBar()
        file_menu = menubar.addMenu("Dosya")

        new_action = QAction("Yeni", self)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("Aç", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Kaydet", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        layout.setMenuBar(menubar)

        # Takvim tablosu
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Tarih", "Etkinlik"])
        layout.addWidget(self.table)

        # Butonlar
        btn_add = QPushButton("Etkinlik Ekle")
        btn_add.clicked.connect(self.add_event)
        layout.addWidget(btn_add)

        self.setLayout(layout)
        self.current_file = None

    def add_event(self):
        date, ok1 = QInputDialog.getText(self, "Yeni Etkinlik", "Tarih (GG/AA/YYYY):")
        if not ok1 or not date:
            return
        event, ok2 = QInputDialog.getText(self, "Yeni Etkinlik", "Etkinlik:")
        if not ok2 or not event:
            return
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(date))
        self.table.setItem(row, 1, QTableWidgetItem(event))

    def new_file(self):
        self.table.setRowCount(0)
        self.current_file = None

    def open_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Dosya Aç", "", "JSON Files (*.json)")
        if fname:
            with open(fname, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.table.setRowCount(0)
            for ev in data.get("events", []):
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(ev["date"]))
                self.table.setItem(row, 1, QTableWidgetItem(ev["event"]))
            self.current_file = fname

    def save_file(self):
        events = []
        for row in range(self.table.rowCount()):
            date = self.table.item(row, 0).text()
            event = self.table.item(row, 1).text()
            events.append({"date": date, "event": event})
        data = {"events": events}

        if self.current_file:
            fname = self.current_file
        else:
            fname, _ = QFileDialog.getSaveFileName(self, "Dosya Kaydet", "", "JSON Files (*.json)")
            if not fname:
                return
            self.current_file = fname

        with open(fname, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)


class Texter(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Texter - Flourescent OS")
        layout = QVBoxLayout()

        menubar = QMenuBar()
        file_menu = menubar.addMenu("Dosya")

        new_action = QAction("Yeni", self)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("Aç", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Kaydet", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        layout.setMenuBar(menubar)

        self.editor = QTextEdit()
        layout.addWidget(self.editor)

        self.setLayout(layout)
        self.current_file = None

    def new_file(self):
        self.editor.clear()
        self.current_file = None

    def open_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Dosya Aç", "", "Text Files (*.txt)")
        if fname:
            with open(fname, "r", encoding="utf-8") as f:
                self.editor.setText(f.read())
            self.current_file = fname

    def save_file(self):
        if self.current_file:
            with open(self.current_file, "w", encoding="utf-8") as f:
                f.write(self.editor.toPlainText())
        else:
            fname, _ = QFileDialog.getSaveFileName(self, "Dosya Kaydet", "", "Text Files (*.txt)")
            if fname:
                with open(fname, "w", encoding="utf-8") as f:
                    f.write(self.editor.toPlainText())
                self.current_file = fname

import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QMenuBar, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QFileDialog, QInputDialog
)
from PyQt6.QtGui import QAction

class Biller(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Biller - Flourescent OS")
        layout = QVBoxLayout()

        # Menü çubuğu
        menubar = QMenuBar()
        file_menu = menubar.addMenu("Dosya")

        new_action = QAction("Yeni", self)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("Aç", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Kaydet", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        layout.setMenuBar(menubar)

        # Tablo
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Müşteri", "Tutar"])
        layout.addWidget(self.table)

        # Butonlar
        btn_add = QPushButton("Fatura Ekle")
        btn_add.clicked.connect(self.add_invoice)
        btn_total = QPushButton("Toplam Hesapla")
        btn_total.clicked.connect(self.calculate_total)

        layout.addWidget(btn_add)
        layout.addWidget(btn_total)

        # Toplam label
        self.total_label = QLabel("Toplam: 0")
        layout.addWidget(self.total_label)

        self.setLayout(layout)
        self.current_file = None

    def add_invoice(self):
        customer, ok1 = QInputDialog.getText(self, "Yeni Fatura", "Müşteri adı:")
        if not ok1 or not customer:
            return
        amount, ok2 = QInputDialog.getDouble(self, "Yeni Fatura", "Tutar:", 0, 0, 1000000, 2)
        if not ok2:
            return
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row, 0, QTableWidgetItem(customer))
        self.table.setItem(row, 1, QTableWidgetItem(str(amount)))

    def calculate_total(self):
        total = 0
        for row in range(self.table.rowCount()):
            try:
                total += float(self.table.item(row, 1).text())
            except:
                pass
        self.total_label.setText(f"Toplam: {total}")

    def new_file(self):
        self.table.setRowCount(0)
        self.total_label.setText("Toplam: 0")
        self.current_file = None

    def open_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Dosya Aç", "", "JSON Files (*.json)")
        if fname:
            with open(fname, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.table.setRowCount(0)
            for invoice in data.get("invoices", []):
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(invoice["customer"]))
                self.table.setItem(row, 1, QTableWidgetItem(str(invoice["amount"])))
            self.total_label.setText(f"Toplam: {data.get('total', 0)}")
            self.current_file = fname

    def save_file(self):
        invoices = []
        for row in range(self.table.rowCount()):
            customer = self.table.item(row, 0).text()
            amount = float(self.table.item(row, 1).text())
            invoices.append({"customer": customer, "amount": amount})
        total = sum(inv["amount"] for inv in invoices)
        data = {"invoices": invoices, "total": total}

        if self.current_file:
            fname = self.current_file
        else:
            fname, _ = QFileDialog.getSaveFileName(self, "Dosya Kaydet", "", "JSON Files (*.json)")
            if not fname:
                return
            self.current_file = fname

        with open(fname, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QMenuBar, QListWidget,
    QPushButton, QFileDialog, QInputDialog
)
from PyQt6.QtGui import QAction

class Notes(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Notes - Flourescent OS")
        layout = QVBoxLayout()

        # Menü çubuğu
        menubar = QMenuBar()
        file_menu = menubar.addMenu("Dosya")

        new_action = QAction("Yeni", self)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("Aç", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Kaydet", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        layout.setMenuBar(menubar)

        # Not listesi
        self.list = QListWidget()
        layout.addWidget(self.list)

        # Butonlar
        btn_add = QPushButton("Not Ekle")
        btn_add.clicked.connect(self.add_note)
        btn_delete = QPushButton("Seçili Notu Sil")
        btn_delete.clicked.connect(self.delete_note)

        layout.addWidget(btn_add)
        layout.addWidget(btn_delete)

        self.setLayout(layout)
        self.current_file = None

    def add_note(self):
        text, ok = QInputDialog.getText(self, "Yeni Not", "Not içeriği:")
        if ok and text:
            self.list.addItem(text)

    def delete_note(self):
        row = self.list.currentRow()
        if row >= 0:
            self.list.takeItem(row)

    def new_file(self):
        self.list.clear()
        self.current_file = None

    def open_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Dosya Aç", "", "JSON Files (*.json)")
        if fname:
            with open(fname, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.list.clear()
            for note in data.get("notes", []):
                self.list.addItem(note)
            self.current_file = fname

    def save_file(self):
        notes = [self.list.item(i).text() for i in range(self.list.count())]
        data = {"notes": notes}

        if self.current_file:
            fname = self.current_file
        else:
            fname, _ = QFileDialog.getSaveFileName(self, "Dosya Kaydet", "", "JSON Files (*.json)")
            if not fname:
                return
            self.current_file = fname

        with open(fname, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

import smtplib, imaplib, email, json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton, QListWidget,
    QInputDialog, QLabel, QMenuBar, QFileDialog, QMessageBox
)
from PyQt6.QtGui import QAction

class EmailClient(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EmailClient - Flourescent OS")
        layout = QVBoxLayout()

        # Giriş alanları
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("E-posta adresi")
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Şifre / Uygulama Şifresi")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.smtp_input = QLineEdit()
        self.smtp_input.setPlaceholderText("SMTP sunucusu (örn: smtp.gmail.com)")
        self.imap_input = QLineEdit()
        self.imap_input.setPlaceholderText("IMAP sunucusu (örn: imap.gmail.com)")
        self.port_input = QLineEdit()
        self.port_input.setPlaceholderText("SMTP port (örn: 587)")

        btn_login = QPushButton("Hesap Aç")
        btn_login.clicked.connect(self.login)

        layout.addWidget(self.email_input)
        layout.addWidget(self.pass_input)
        layout.addWidget(self.smtp_input)
        layout.addWidget(self.imap_input)
        layout.addWidget(self.port_input)
        layout.addWidget(btn_login)

        # Gelen kutusu
        self.inbox = QListWidget()
        layout.addWidget(self.inbox)

        btn_fetch = QPushButton("Postaları Getir")
        btn_fetch.clicked.connect(self.fetch_mails)
        layout.addWidget(btn_fetch)

        btn_compose = QPushButton("Yeni Mail")
        btn_compose.clicked.connect(self.compose_mail)
        layout.addWidget(btn_compose)

        self.setLayout(layout)

        # Hesap bilgileri
        self.email = None
        self.password = None
        self.smtp_server = None
        self.imap_server = None
        self.smtp_port = None

    def login(self):
        self.email = self.email_input.text()
        self.password = self.pass_input.text()
        self.smtp_server = self.smtp_input.text()
        self.imap_server = self.imap_input.text()
        try:
            self.smtp_port = int(self.port_input.text())
        except:
            self.smtp_port = 587

    def fetch_mails(self):
        try:
            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.email, self.password)
            mail.select("inbox")
            result, data = mail.search(None, "ALL")
            ids = data[0].split()
            self.inbox.clear()
            for i in ids[-5:]:
                res, msg_data = mail.fetch(i, "(RFC822)")
                raw = msg_data[0][1]
                msg = email.message_from_bytes(raw)
                subject = msg["subject"]
                sender = msg["from"]
                self.inbox.addItem(f"{sender}: {subject}")
            mail.logout()
        except Exception as e:
            self.inbox.addItem(f"Hata: {e}")

    def compose_mail(self):
        to, ok1 = QInputDialog.getText(self, "Yeni Mail", "Alıcı:")
        if not ok1 or not to: return
        subject, ok2 = QInputDialog.getText(self, "Yeni Mail", "Konu:")
        if not ok2: return
        body, ok3 = QInputDialog.getText(self, "Yeni Mail", "Mesaj:")
        if not ok3: return

        msg = MIMEMultipart()
        msg["From"] = self.email
        msg["To"] = to
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        try:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email, self.password)
            server.sendmail(self.email, to, msg.as_string())
            server.quit()
        except Exception as e:
            self.inbox.addItem(f"Gönderim hatası: {e}")

import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QMenuBar, QListWidget,
    QPushButton, QFileDialog, QInputDialog
)
from PyQt6.QtGui import QAction

class Presentator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Presentator - Flourescent OS")
        layout = QVBoxLayout()

        # Menü çubuğu
        menubar = QMenuBar()
        file_menu = menubar.addMenu("Dosya")

        new_action = QAction("Yeni", self)
        new_action.triggered.connect(self.new_file)
        file_menu.addAction(new_action)

        open_action = QAction("Aç", self)
        open_action.triggered.connect(self.open_file)
        file_menu.addAction(open_action)

        save_action = QAction("Kaydet", self)
        save_action.triggered.connect(self.save_file)
        file_menu.addAction(save_action)

        layout.setMenuBar(menubar)

        # Slayt listesi
        self.list = QListWidget()
        layout.addWidget(self.list)

        # Butonlar
        btn_add = QPushButton("Slayt Ekle")
        btn_add.clicked.connect(self.add_slide)
        btn_edit = QPushButton("Seçili Slaytı Düzenle")
        btn_edit.clicked.connect(self.edit_slide)
        btn_delete = QPushButton("Seçili Slaytı Sil")
        btn_delete.clicked.connect(self.delete_slide)

        layout.addWidget(btn_add)
        layout.addWidget(btn_edit)
        layout.addWidget(btn_delete)

        self.setLayout(layout)
        self.current_file = None

    def add_slide(self):
        title, ok1 = QInputDialog.getText(self, "Yeni Slayt", "Başlık:")
        if not ok1 or not title:
            return
        content, ok2 = QInputDialog.getText(self, "Yeni Slayt", "İçerik:")
        if not ok2:
            return
        self.list.addItem(f"{title} | {content}")

    def edit_slide(self):
        row = self.list.currentRow()
        if row < 0:
            return
        current = self.list.item(row).text().split(" | ")
        title, ok1 = QInputDialog.getText(self, "Slaytı Düzenle", "Başlık:", text=current[0])
        if not ok1:
            return
        content, ok2 = QInputDialog.getText(self, "Slaytı Düzenle", "İçerik:", text=current[1])
        if not ok2:
            return
        self.list.item(row).setText(f"{title} | {content}")

    def delete_slide(self):
        row = self.list.currentRow()
        if row >= 0:
            self.list.takeItem(row)

    def new_file(self):
        self.list.clear()
        self.current_file = None

    def open_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Dosya Aç", "", "JSON Files (*.json)")
        if fname:
            with open(fname, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.list.clear()
            for slide in data.get("slides", []):
                self.list.addItem(f"{slide['title']} | {slide['content']}")
            self.current_file = fname

    def save_file(self):
        slides = []
        for i in range(self.list.count()):
            title, content = self.list.item(i).text().split(" | ")
            slides.append({"title": title, "content": content})
        data = {"slides": slides}

        if self.current_file:
            fname = self.current_file
        else:
            fname, _ = QFileDialog.getSaveFileName(self, "Dosya Kaydet", "", "JSON Files (*.json)")
            if not fname:
                return
            self.current_file = fname

        with open(fname, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QFileDialog
)
from PyQt6.QtMultimedia import QMediaPlayer
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import QUrl

class MediaPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MediaPlayer - Flourescent OS")
        layout = QVBoxLayout()

        # Video alanı
        self.video = QVideoWidget()
        layout.addWidget(self.video)

        # Player
        self.player = QMediaPlayer()
        self.player.setVideoOutput(self.video)

        # Kontroller
        btn_open = QPushButton("Dosya Aç")
        btn_open.clicked.connect(self.open_file)
        btn_play = QPushButton("Oynat")
        btn_play.clicked.connect(self.player.play)
        btn_pause = QPushButton("Duraklat")
        btn_pause.clicked.connect(self.player.pause)
        btn_stop = QPushButton("Durdur")
        btn_stop.clicked.connect(self.player.stop)

        controls = QHBoxLayout()
        controls.addWidget(btn_open)
        controls.addWidget(btn_play)
        controls.addWidget(btn_pause)
        controls.addWidget(btn_stop)

        layout.addLayout(controls)
        self.setLayout(layout)

    def open_file(self):
        fname, _ = QFileDialog.getOpenFileName(
            self, "Dosya Aç", "", "Media Files (*.mp3 *.mp4 *.wav *.avi)"
        )
        if fname:
            url = QUrl.fromLocalFile(fname)
            self.player.setSource(url)   # 🔥 PyQt6’da setSource kullanılıyor

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, QSlider, QFileDialog
)
from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
from PyQt6.QtCore import QUrl, Qt

class MusicStudio(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MusicStudio - Flourescent OS")
        self.resize(600, 200)

        layout = QVBoxLayout()

        # Player + Audio Output
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)

        # Kontroller
        btn_open = QPushButton("Parça Aç")
        btn_open.clicked.connect(self.open_file)

        btn_play = QPushButton("Oynat")
        btn_play.clicked.connect(self.player.play)

        btn_pause = QPushButton("Duraklat")
        btn_pause.clicked.connect(self.player.pause)

        btn_stop = QPushButton("Durdur")
        btn_stop.clicked.connect(self.player.stop)

        # Ses seviyesi slider
        self.volume_slider = QSlider(Qt.Orientation.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.audio_output.setVolume)

        # Layout düzeni
        controls = QHBoxLayout()
        controls.addWidget(btn_open)
        controls.addWidget(btn_play)
        controls.addWidget(btn_pause)
        controls.addWidget(btn_stop)

        layout.addLayout(controls)
        layout.addWidget(QLabel("Ses Seviyesi"))
        layout.addWidget(self.volume_slider)

        self.setLayout(layout)

    def open_file(self):
        fname, _ = QFileDialog.getOpenFileName(
            self, "Parça Aç", "", "Audio Files (*.mp3 *.wav *.ogg)"
        )
        if fname:
            url = QUrl.fromLocalFile(fname)
            self.player.setSource(url)


class PhotoViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PhotoViewer - Flourescent OS")
        layout = QVBoxLayout()

        # Görüntü alanı
        self.label = QLabel("Resim açılmadı")
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        # Kontroller
        btn_open = QPushButton("Resim Aç")
        btn_open.clicked.connect(self.open_file)
        btn_next = QPushButton("Sonraki")
        btn_next.clicked.connect(self.next_image)
        btn_prev = QPushButton("Önceki")
        btn_prev.clicked.connect(self.prev_image)

        controls = QHBoxLayout()
        controls.addWidget(btn_open)
        controls.addWidget(btn_prev)
        controls.addWidget(btn_next)

        layout.addLayout(controls)
        self.setLayout(layout)

        # Resim listesi
        self.images = []
        self.current_index = -1

    def open_file(self):
        fnames, _ = QFileDialog.getOpenFileNames(
            self, "Resim Aç", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        if fnames:
            self.images = fnames
            self.current_index = 0
            self.show_image()

    def show_image(self):
        if 0 <= self.current_index < len(self.images):
            pixmap = QPixmap(self.images[self.current_index])
            self.label.setPixmap(
                pixmap.scaled(
                    self.label.size(),
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                )
            )

    def next_image(self):
        if self.images and self.current_index < len(self.images) - 1:
            self.current_index += 1
            self.show_image()

    def prev_image(self):
        if self.images and self.current_index > 0:
            self.current_index -= 1
            self.show_image()

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QFileDialog, QMessageBox
)
import ffmpeg

class VideoEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VideoEditor - Flourescent OS")
        layout = QVBoxLayout()

        # Dosya açma butonu
        btn_open = QPushButton("Video Aç")
        btn_open.clicked.connect(self.open_file)

        # Kesme aralığı girişleri
        self.start_input = QLineEdit()
        self.start_input.setPlaceholderText("Başlangıç (saniye)")
        self.end_input = QLineEdit()
        self.end_input.setPlaceholderText("Bitiş (saniye)")

        # Kesme butonu
        btn_cut = QPushButton("Kes ve Kaydet")
        btn_cut.clicked.connect(self.cut_video)

        layout.addWidget(btn_open)
        layout.addWidget(QLabel("Kesme Aralığı"))
        layout.addWidget(self.start_input)
        layout.addWidget(self.end_input)
        layout.addWidget(btn_cut)

        self.setLayout(layout)
        self.current_file = None

    def open_file(self):
        fname, _ = QFileDialog.getOpenFileName(
            self, "Video Aç", "", "Video Files (*.mp4 *.avi *.mov)"
        )
        if fname:
            self.current_file = fname

    def cut_video(self):
        if not self.current_file:
            return
        try:
            start = int(self.start_input.text())
            end = int(self.end_input.text())
            save_name, _ = QFileDialog.getSaveFileName(
                self, "Kaydet", "", "Video Files (*.mp4)"
            )
            if save_name:
                (
                    ffmpeg
                    .input(self.current_file, ss=start, to=end)
                    .output(save_name)
                    .run()
                )
                QMessageBox.information(self, "Başarılı", "Video kesildi ve kaydedildi!")
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Kesme hatası: {e}")

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QPushButton, QMessageBox, QFileDialog
)

import sounddevice as sd
import wave
import numpy as np
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLineEdit,
    QFileDialog, QMessageBox, QProgressBar
)
from PyQt6.QtCore import QTimer

class Recorder(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Recorder - Flourescent OS")
        self.resize(400, 200)

        layout = QVBoxLayout()

        # Süre girişi
        self.duration_input = QLineEdit()
        self.duration_input.setPlaceholderText("Süre (saniye)")
        layout.addWidget(self.duration_input)

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setValue(0)
        layout.addWidget(self.progress)

        # Butonlar
        btn_record = QPushButton("Kaydı Başlat")
        btn_record.clicked.connect(self.start_recording)
        layout.addWidget(btn_record)

        btn_stop = QPushButton("Kaydı Durdur")
        btn_stop.clicked.connect(self.stop_recording)
        layout.addWidget(btn_stop)

        self.setLayout(layout)

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)

        # State
        self.fs = 48000
        self.channels = 1
        self.recording = None
        self.duration = 0
        self.elapsed = 0

    def start_recording(self):
        try:
            self.duration = int(self.duration_input.text())
            self.elapsed = 0
            self.progress.setValue(0)

            # NumPy array döner
            self.recording = sd.rec(
                int(self.duration * self.fs),
                samplerate=self.fs,
                channels=self.channels,
                dtype='int16'
            )
            self.timer.start(1000)  # her saniye güncelle
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Kayıt başlatılamadı: {e}")

    def stop_recording(self):
        try:
            sd.stop()
            self.timer.stop()

            fname, _ = QFileDialog.getSaveFileName(
                self, "Kaydet", "", "WAV Files (*.wav)"
            )
            if fname and self.recording is not None:
                with wave.open(fname, "wb") as wf:
                    wf.setnchannels(self.channels)
                    wf.setsampwidth(2)  # 16-bit PCM
                    wf.setframerate(self.fs)
                    wf.writeframes(self.recording.tobytes())

                QMessageBox.information(self, "Başarılı", f"Kayıt tamamlandı: {fname}")
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Kayıt durdurulamadı: {e}")

    def update_progress(self):
        self.elapsed += 1
        if self.duration > 0:
            percent = int((self.elapsed / self.duration) * 100)
            self.progress.setValue(min(percent, 100))
        if self.elapsed >= self.duration:
            self.stop_recording()


import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QMessageBox
)
from PyQt6.QtMultimedia import QCamera, QImageCapture, QMediaCaptureSession
from PyQt6.QtMultimediaWidgets import QVideoWidget
from PyQt6.QtCore import QDir

class Camera(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camera - Flourescent OS")
        self.resize(800, 600)

        layout = QVBoxLayout()

        # Görüntü alanı
        self.viewfinder = QVideoWidget()
        layout.addWidget(self.viewfinder)

        # Kamera ve capture session
        self.camera = QCamera()
        self.capture = QImageCapture(self.camera)
        self.session = QMediaCaptureSession()
        self.session.setCamera(self.camera)
        self.session.setVideoOutput(self.viewfinder)
        self.session.setImageCapture(self.capture)

        # Kontroller
        btn_start = QPushButton("Kamerayı Aç")
        btn_start.clicked.connect(self.start_camera)

        btn_capture = QPushButton("Fotoğraf Çek")
        btn_capture.clicked.connect(self.capture_photo)

        btn_stop = QPushButton("Kapat")
        btn_stop.clicked.connect(self.stop_camera)

        layout.addWidget(btn_start)
        layout.addWidget(btn_capture)
        layout.addWidget(btn_stop)

        self.setLayout(layout)

    def start_camera(self):
        try:
            self.camera.start()
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Kamera açılamadı: {e}")

    def capture_photo(self):
        try:
            save_path = os.path.join(QDir.homePath(), "camera_capture.jpg")
            self.capture.captureToFile(save_path)
            QMessageBox.information(self, "Bilgi", f"Fotoğraf kaydedildi: {save_path}")
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Fotoğraf çekilemedi: {e}")

    def stop_camera(self):
        self.camera.stop()


class Gallery(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gallery - Flourescent OS")
        layout = QVBoxLayout()

        # Resim listesi
        self.list = QListWidget()
        layout.addWidget(self.list)

        # Resim ekleme butonu
        btn_open = QPushButton("Resim Ekle")
        btn_open.clicked.connect(self.add_image)
        layout.addWidget(btn_open)

        self.setLayout(layout)

    def add_image(self):
        fnames, _ = QFileDialog.getOpenFileNames(
            self, "Resim Aç", "", "Image Files (*.png *.jpg *.jpeg *.bmp)"
        )
        for f in fnames:
            self.list.addItem(f)

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel
)
from PyQt6.QtGui import QPixmap, QColor, QPainter, QPen
from PyQt6.QtCore import Qt, QPoint

class Paint(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Paint - Flourescent OS")
        layout = QVBoxLayout()

        # Tuval
        self.canvas = QLabel()
        self.canvas.setFixedSize(600, 400)
        self.canvas.setStyleSheet("background-color: white; border: 1px solid black;")
        layout.addWidget(self.canvas)

        self.setLayout(layout)

        # Çizim için QPixmap
        self.image = QPixmap(self.canvas.size())
        self.image.fill(Qt.GlobalColor.white)
        self.canvas.setPixmap(self.image)

        # Fırça ayarları
        self.brush_color = QColor(Qt.GlobalColor.black)
        self.brush_size = 3
        self.last_point = None

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_point = event.position().toPoint()

    def mouseMoveEvent(self, event):
        if (event.buttons() & Qt.MouseButton.LeftButton) and self.last_point is not None:
            painter = QPainter(self.canvas.pixmap())
            pen = QPen(self.brush_color, self.brush_size, Qt.PenStyle.SolidLine)
            painter.setPen(pen)
            painter.drawLine(self.last_point, event.position().toPoint())
            painter.end()
            self.canvas.update()
            self.last_point = event.position().toPoint()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.last_point = None

import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLineEdit, QTextEdit, QFileDialog, QMessageBox
)

class Messenger(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Messenger - Flourescent OS")
        layout = QVBoxLayout()

        # Sohbet ekranı
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        # Mesaj giriş alanı
        self.message_input = QLineEdit()
        self.message_input.setPlaceholderText("Mesaj yaz...")
        layout.addWidget(self.message_input)

        # Butonlar
        btn_send = QPushButton("Gönder")
        btn_send.clicked.connect(self.send_message)
        layout.addWidget(btn_send)

        btn_save = QPushButton("Sohbeti Kaydet")
        btn_save.clicked.connect(self.save_chat)
        layout.addWidget(btn_save)

        btn_load = QPushButton("Sohbeti Aç")
        btn_load.clicked.connect(self.load_chat)
        layout.addWidget(btn_load)

        self.setLayout(layout)
        self.chat_history = []

    def send_message(self):
        text = self.message_input.text()
        if text:
            self.chat_display.append(f"Sen: {text}")
            self.chat_history.append(f"Sen: {text}")
            self.message_input.clear()

    def save_chat(self):
        fname, _ = QFileDialog.getSaveFileName(
            self, "Sohbeti Kaydet", "", "JSON Files (*.json)"
        )
        if fname:
            try:
                with open(fname, "w", encoding="utf-8") as f:
                    json.dump(self.chat_history, f, indent=2)
                QMessageBox.information(self, "Başarılı", "Sohbet kaydedildi!")
            except Exception as e:
                QMessageBox.warning(self, "Hata", f"Kaydetme hatası: {e}")

    def load_chat(self):
        fname, _ = QFileDialog.getOpenFileName(
            self, "Sohbeti Aç", "", "JSON Files (*.json)"
        )
        if fname:
            try:
                with open(fname, "r", encoding="utf-8") as f:
                    self.chat_history = json.load(f)
                self.chat_display.clear()
                for line in self.chat_history:
                    self.chat_display.append(line)
                QMessageBox.information(self, "Başarılı", "Sohbet yüklendi!")
            except Exception as e:
                QMessageBox.warning(self, "Hata", f"Açma hatası: {e}")

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton
)
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtCore import QUrl

class Browser(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Flourescent Owl Browser")
        self.resize(1200, 800)

        # Ana layout
        layout = QVBoxLayout()

        # URL bar + butonlar için üst bar
        top_bar = QHBoxLayout()

        # Geri butonu
        btn_back = QPushButton("←")
        btn_back.clicked.connect(self.go_back)
        top_bar.addWidget(btn_back)

        # İleri butonu
        btn_forward = QPushButton("→")
        btn_forward.clicked.connect(self.go_forward)
        top_bar.addWidget(btn_forward)

        # Yenile butonu
        btn_reload = QPushButton("⟳")
        btn_reload.clicked.connect(self.reload_page)
        top_bar.addWidget(btn_reload)

        # Ana sayfa butonu
        btn_home = QPushButton("🏠")
        btn_home.clicked.connect(self.go_home)
        top_bar.addWidget(btn_home)

        # URL giriş alanı
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("URL gir...")
        top_bar.addWidget(self.url_input)

        # Git butonu
        btn_go = QPushButton("Git")
        btn_go.clicked.connect(self.load_url)
        top_bar.addWidget(btn_go)

        layout.addLayout(top_bar)

        # Web görüntüleyici
        self.webview = QWebEngineView()
        layout.addWidget(self.webview)

        self.setLayout(layout)

        # Varsayılan ana sayfa
        self.home_url = "http://www.google.com"
        self.webview.setUrl(QUrl(self.home_url))

    def load_url(self):
        url = self.url_input.text().strip()
        if not url.startswith("http"):
            url = "http://" + url
        self.webview.setUrl(QUrl(url))

    def go_back(self):
        self.webview.back()

    def go_forward(self):
        self.webview.forward()

    def reload_page(self):
        self.webview.reload()

    def go_home(self):
        self.webview.setUrl(QUrl(self.home_url))

import sys, os, json, datetime, psutil
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QLabel, QStackedWidget, QMessageBox, QInputDialog, QTextEdit
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPixmap

# 🔑 Multitasking katmanı
class AppManager:
    def __init__(self):
        self.opened_apps = {}

    def open_app(self, name, widget_class, workspace):
        if name in self.opened_apps:
            workspace.setCurrentWidget(self.opened_apps[name])
        else:
            app_instance = widget_class()
            workspace.addWidget(app_instance)
            self.opened_apps[name] = app_instance
            workspace.setCurrentWidget(app_instance)

    def close_app(self, name, workspace):
        if name in self.opened_apps:
            widget = self.opened_apps.pop(name)
            workspace.removeWidget(widget)
            widget.deleteLater()

    def switch_app(self, name, workspace):
        if name in self.opened_apps:
            workspace.setCurrentWidget(self.opened_apps[name])

    def list_apps(self):
        return list(self.opened_apps.keys())


# 🔑 Örnek uygulama: Texter
class Texter(QWidget):
    def __init__(self):
        super().__init__()
        self.editor = QTextEdit()
        layout = QVBoxLayout()
        layout.addWidget(self.editor)
        self.setLayout(layout)

    def save_state(self):
        return {"text": self.editor.toPlainText()}

    def load_state(self, data):
        self.editor.setText(data.get("text", ""))


# 🔑 DesktopUI entegrasyonu
class DesktopUI(QWidget):
    def __init__(self, apps_dict):
        super().__init__()
        self.setWindowTitle("Flourescent OS Virtual Machine Desktop")
        self.resize(900, 600)

        # 🔥 Arka plan resmi
        self.bg_label = QLabel(self)
        self.bg_label.setGeometry(240, 16, self.width(), self.height())
        self.bg_label.lower()

        self.state_file = "savestate.json"
        self.app_manager = AppManager()

        main_layout = QVBoxLayout()
        self.setLayout(main_layout)

        # Status bar
        self.status_bar = QHBoxLayout()
        self.clock_label = QLabel()
        self.date_label = QLabel()
        self.battery_label = QLabel()
        self.status_bar.addWidget(self.clock_label)
        self.status_bar.addStretch()
        self.status_bar.addWidget(self.date_label)
        self.status_bar.addWidget(self.battery_label)
        main_layout.addLayout(self.status_bar)

        # Workspace
        self.workspace = QStackedWidget()
        main_layout.addWidget(self.workspace)

        # Dock
        dock_layout = QHBoxLayout()
        dock_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        main_layout.addLayout(dock_layout)

        self.apps_dict = apps_dict
        for name, widget_class in apps_dict.items():
            btn = QPushButton(name)
            btn.setFixedSize(50, 50)
            btn.clicked.connect(lambda checked, w=widget_class, n=name:
                self.app_manager.open_app(n, w, self.workspace))
            dock_layout.addWidget(btn)

        # Task Manager butonu
        task_btn = QPushButton("Görev Yöneticisi")
        task_btn.clicked.connect(self.show_task_manager)
        dock_layout.addWidget(task_btn)

        # Timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_status)
        self.timer.start(1000)
        self.update_status()

        # Savestate yükle
        self.load_state()

        # İlk wallpaper ayarı
        self.set_wallpaper("mountain_wallpaper.jpeg")

    def set_wallpaper(self, path):
        # 2560x720 çözünürlükteki resmi pencereyi tam kaplayacak şekilde ayarla
        self.bg_label.setPixmap(
            QPixmap(path).scaled(
                self.size(),
                Qt.AspectRatioMode.IgnoreAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
        )

    def resizeEvent(self, event):
        # Pencere boyutu değişince wallpaper yeniden ayarlanır
        self.set_wallpaper("mountain_wallpaper.jpeg")
        super().resizeEvent(event)

    def show_task_manager(self):
        tasks = self.app_manager.list_apps()
        if not tasks:
            QMessageBox.information(self, "Görev Yöneticisi", "Hiç uygulama açık değil")
            return
        app_name, ok = QInputDialog.getItem(self, "Görev Yöneticisi",
                                            "Uygulama seç:", tasks, 0, False)
        if ok and app_name:
            action, ok2 = QInputDialog.getItem(self, "İşlem Seç",
                                               "Ne yapmak istiyorsun?",
                                               ["Geçiş Yap", "Kapat"], 0, False)
            if ok2:
                if action == "Geçiş Yap":
                    self.app_manager.switch_app(app_name, self.workspace)
                elif action == "Kapat":
                    self.app_manager.close_app(app_name, self.workspace)

    def update_status(self):
        now = datetime.datetime.now()
        self.clock_label.setText(f"🕒 {now.strftime('%H:%M:%S')}")
        self.date_label.setText(f"📅 {now.strftime('%d/%m/%Y')}")
        try:
            battery = psutil.sensors_battery()
            if battery:
                percent = battery.percent
                plugged = battery.power_plugged
                self.battery_label.setText(f"{'🔌' if plugged else '🔋'} {percent}%")
            else:
                self.battery_label.setText("🔌 Fiş")
        except Exception:
            self.battery_label.setText("❓ Batarya Yok")

    def save_state(self, app_name=None):
        state = {
            "geometry": [self.x(), self.y(), self.width(), self.height()],
            "current_app_name": app_name,
            "apps": {}
        }
        for n,w in self.app_manager.opened_apps.items():
            if hasattr(w, "save_state"):
                state["apps"][n] = w.save_state()
        with open(self.state_file, "w") as f:
            json.dump(state, f)

    def load_state(self):
        if os.path.exists(self.state_file):
            with open(self.state_file, "r") as f:
                state = json.load(f)
            if "geometry" in state:
                x,y,w,h = state["geometry"]
                self.setGeometry(x,y,w,h)
            for app_name, app_data in state.get("apps", {}).items():
                if app_name in self.apps_dict:
                    self.app_manager.open_app(app_name, self.apps_dict[app_name], self.workspace)
                    widget = self.app_manager.opened_apps[app_name]
                    if hasattr(widget, "load_state"):
                        widget.load_state(app_data)

    def closeEvent(self, event):
        current_widget = self.workspace.currentWidget()
        if current_widget:
            for n,w in self.app_manager.opened_apps.items():
                if w == current_widget:
                    self.save_state(n)
                    break
        event.accept()

# 🔑 MAIN
if __name__ == "__main__":
    app = QApplication(sys.argv)

    apps_dict = {
        "📝": Texter,
        "💳": Biller,
        "📒": Notes,
        "📆": Calendar,
        "📧": EmailClient,
        "📽": Presentator,
        "🎬": MediaPlayer,
        "🎹": MusicStudio,
        "🖼": PhotoViewer,
        "🎞": VideoEditor,
        "🎙": Recorder,
        "📷": Camera,
        "🖼️": Gallery,
        "🎨": Paint,
        "🌐": Browser,
        "🧮": Calculator,     # yeni
        "📖": Dictionary,     # yeni
        "🌍": Translator,     # yeni
        "☁️": Weather,        # yeni
        "📰": NewsReader,     # yeni
        "🗺": Maps,           # yeni
        "🎮": Games,          # yeni
        "⚙️": Settings,       # yeni
        "📑": PDFViewer,      # yeni
        "🎵": Music,          # yeni
        "🖥": AppRunner,
        "🛒": StoreApp,
        
    }

    desktop = DesktopUI(apps_dict)
    desktop.show()
    sys.exit(app.exec())
