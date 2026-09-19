import sys, json, smtplib, imaplib, email, wave, ffmpeg, sounddevice as sd
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QStackedWidget,
    QListWidget, QMenuBar, QAction, QTextEdit, QTableWidget, QTableWidgetItem,
    QInputDialog, QLineEdit, QSlider, QMessageBox, QFileDialog, QColorDialog
)
from PyQt5.QtCore import Qt, QTimer, QDateTime, QUrl
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget


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
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QMenuBar, QAction, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QFileDialog, QInputDialog
)

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

        # Dosya yolu
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
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QMenuBar, QAction, QListWidget,
    QPushButton, QFileDialog, QInputDialog
)

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

        # Dosya yolu
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

class Calendar(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calendar - Flourescent OS")
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

        self.list = QListWidget()
        layout.addWidget(self.list)

        btn_add = QPushButton("Etkinlik Ekle")
        btn_add.clicked.connect(self.add_event)
        btn_delete = QPushButton("Seçili Etkinliği Sil")
        btn_delete.clicked.connect(self.delete_event)

        layout.addWidget(btn_add)
        layout.addWidget(btn_delete)

        self.setLayout(layout)
        self.current_file = None

    def add_event(self):
        title, ok1 = QInputDialog.getText(self, "Yeni Etkinlik", "Etkinlik adı:")
        if not ok1 or not title: return
        date, ok2 = QInputDialog.getText(self, "Yeni Etkinlik", "Tarih (GG/AA/YYYY):")
        if not ok2 or not date: return
        self.list.addItem(f"{date} - {title}")

    def delete_event(self):
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
            for ev in data.get("events", []):
                self.list.addItem(ev)
            self.current_file = fname

    def save_file(self):
        events = [self.list.item(i).text() for i in range(self.list.count())]
        data = {"events": events}

        if self.current_file:
            fname = self.current_file
        else:
            fname, _ = QFileDialog.getSaveFileName(self, "Dosya Kaydet", "", "JSON Files (*.json)")
            if not fname: return
            self.current_file = fname

        with open(fname, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

class EmailClient(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EmailClient - Flourescent OS")
        layout = QVBoxLayout()

        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("E-posta adresi")
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Şifre / Uygulama Şifresi")
        self.pass_input.setEchoMode(QLineEdit.Password)
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

        self.inbox = QListWidget()
        layout.addWidget(self.inbox)

        btn_fetch = QPushButton("Postaları Getir")
        btn_fetch.clicked.connect(self.fetch_mails)
        layout.addWidget(btn_fetch)

        btn_compose = QPushButton("Yeni Mail")
        btn_compose.clicked.connect(self.compose_mail)
        layout.addWidget(btn_compose)

        self.setLayout(layout)

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
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QMenuBar, QAction, QListWidget,
    QPushButton, QFileDialog, QInputDialog
)

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
        if not ok1 or not title: return
        content, ok2 = QInputDialog.getText(self, "Yeni Slayt", "İçerik:")
        if not ok2: return
        self.list.addItem(f"{title} | {content}")

    def edit_slide(self):
        row = self.list.currentRow()
        if row < 0: return
        current = self.list.item(row).text().split(" | ")
        title, ok1 = QInputDialog.getText(self, "Slaytı Düzenle", "Başlık:", text=current[0])
        if not ok1: return
        content, ok2 = QInputDialog.getText(self, "Slaytı Düzenle", "İçerik:", text=current[1])
        if not ok2: return
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
            if not fname: return
            self.current_file = fname

        with open(fname, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtCore import QUrl

class MediaPlayer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MediaPlayer - Flourescent OS")
        layout = QVBoxLayout()

        self.video = QVideoWidget()
        layout.addWidget(self.video)

        self.player = QMediaPlayer()
        self.player.setVideoOutput(self.video)

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
        fname, _ = QFileDialog.getOpenFileName(self, "Dosya Aç", "", "Media Files (*.mp3 *.mp4 *.wav *.avi)")
        if fname:
            url = QUrl.fromLocalFile(fname)
            self.player.setMedia(QMediaContent(url))

class MusicStudio(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("MusicStudio - Flourescent OS")
        layout = QVBoxLayout()

        self.player = QMediaPlayer()

        btn_open = QPushButton("Parça Aç")
        btn_open.clicked.connect(self.open_file)
        btn_play = QPushButton("Oynat")
        btn_play.clicked.connect(self.player.play)
        btn_pause = QPushButton("Duraklat")
        btn_pause.clicked.connect(self.player.pause)
        btn_stop = QPushButton("Durdur")
        btn_stop.clicked.connect(self.player.stop)

        self.volume_slider = QSlider(Qt.Horizontal)
        self.volume_slider.setRange(0, 100)
        self.volume_slider.setValue(50)
        self.volume_slider.valueChanged.connect(self.player.setVolume)

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
        fname, _ = QFileDialog.getOpenFileName(self, "Parça Aç", "", "Audio Files (*.mp3 *.wav *.ogg)")
        if fname:
            url = QUrl.fromLocalFile(fname)
            self.player.setMedia(QMediaContent(url))


class PhotoViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PhotoViewer - Flourescent OS")
        layout = QVBoxLayout()

        self.label = QLabel("Resim açılmadı")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)

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

        self.images = []
        self.current_index = -1

    def open_file(self):
        fnames, _ = QFileDialog.getOpenFileNames(self, "Resim Aç", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if fnames:
            self.images = fnames
            self.current_index = 0
            self.show_image()

    def show_image(self):
        if 0 <= self.current_index < len(self.images):
            pixmap = QPixmap(self.images[self.current_index])
            self.label.setPixmap(pixmap.scaled(self.label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def next_image(self):
        if self.images and self.current_index < len(self.images) - 1:
            self.current_index += 1
            self.show_image()

    def prev_image(self):
        if self.images and self.current_index > 0:
            self.current_index -= 1
            self.show_image()

import ffmpeg
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLineEdit, QLabel, QFileDialog, QMessageBox

class VideoEditor(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("VideoEditor - Flourescent OS")
        layout = QVBoxLayout()

        btn_open = QPushButton("Video Aç")
        btn_open.clicked.connect(self.open_file)

        self.start_input = QLineEdit()
        self.start_input.setPlaceholderText("Başlangıç (saniye)")
        self.end_input = QLineEdit()
        self.end_input.setPlaceholderText("Bitiş (saniye)")

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
        fname, _ = QFileDialog.getOpenFileName(self, "Video Aç", "", "Video Files (*.mp4 *.avi *.mov)")
        if fname:
            self.current_file = fname

    def cut_video(self):
        if not self.current_file: return
        try:
            start = int(self.start_input.text())
            end = int(self.end_input.text())
            save_name, _ = QFileDialog.getSaveFileName(self, "Kaydet", "", "Video Files (*.mp4)")
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

import sounddevice as sd, wave

class Recorder(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Recorder - Flourescent OS")
        layout = QVBoxLayout()

        self.duration_input = QLineEdit()
        self.duration_input.setPlaceholderText("Süre (saniye)")
        btn_record = QPushButton("Kaydı Başlat")
        btn_record.clicked.connect(self.record_audio)

        layout.addWidget(self.duration_input)
        layout.addWidget(btn_record)
        self.setLayout(layout)

    def record_audio(self):
        try:
            duration = int(self.duration_input.text())
            fs = 44100
            recording = sd.rec(int(duration * fs), samplerate=fs, channels=2)
            sd.wait()
            fname, _ = QFileDialog.getSaveFileName(self, "Kaydet", "", "WAV Files (*.wav)")
            if fname:
                wf = wave.open(fname, "wb")
                wf.setnchannels(2)
                wf.setsampwidth(2)
                wf.setframerate(fs)
                wf.writeframes(recording.tobytes())
                wf.close()
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Kayıt hatası: {e}")

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QMessageBox
from PyQt5.QtMultimedia import QCamera, QCameraImageCapture
from PyQt5.QtMultimediaWidgets import QCameraViewfinder
from PyQt5.QtCore import QDir
import os

class Camera(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Camera - Flourescent OS")
        layout = QVBoxLayout()

        # Görüntü alanı
        self.viewfinder = QCameraViewfinder()
        layout.addWidget(self.viewfinder)

        # Kamera
        self.camera = QCamera()
        self.camera.setViewfinder(self.viewfinder)

        # Fotoğraf yakalama
        self.capture = QCameraImageCapture(self.camera)

        # Butonlar
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
            self.capture.capture(save_path)
            QMessageBox.information(self, "Bilgi", f"Fotoğraf kaydedildi: {save_path}")
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Fotoğraf çekilemedi: {e}")

    def stop_camera(self):
        self.camera.stop()

class Paint(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Paint - Flourescent OS")
        layout = QVBoxLayout()

        self.canvas = QLabel()
        self.canvas.setFixedSize(600, 400)
        self.canvas.setStyleSheet("background-color: white; border: 1px solid black;")
        layout.addWidget(self.canvas)

        self.setLayout(layout)
        self.image = QPixmap(self.canvas.size())
        self.image.fill(Qt.white)
        self.canvas.setPixmap(self.image)

        self.brush_color = QColor(Qt.black)
        self.brush_size = 3
        self.last_point = None

class Gallery(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gallery - Flourescent OS")
        layout = QVBoxLayout()

        self.list = QListWidget()
        layout.addWidget(self.list)

        btn_open = QPushButton("Resim Ekle")
        btn_open.clicked.connect(self.add_image)
        layout.addWidget(btn_open)

        self.setLayout(layout)

    def add_image(self):
        fnames, _ = QFileDialog.getOpenFileNames(self, "Resim Aç", "", "Image Files (*.png *.jpg *.jpeg *.bmp)")
        for f in fnames:
            self.list.addItem(f)

from PyQt5.QtWebEngineWidgets import QWebEngineView

class Browser(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Browser - Flourescent OS")
        layout = QVBoxLayout()

        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("URL giriniz...")
        btn_go = QPushButton("Git")
        btn_go.clicked.connect(self.load_url)

        controls = QHBoxLayout()
        controls.addWidget(self.url_input)
        controls.addWidget(btn_go)

        self.webview = QWebEngineView()
        layout.addLayout(controls)
        layout.addWidget(self.webview)

        self.setLayout(layout)

    def load_url(self):
        url = self.url_input.text()
        if not url.startswith("http"):
            url = "http://" + url
        self.webview.setUrl(QUrl(url))

import requests

class News(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("News - Flourescent OS")
        layout = QVBoxLayout()

        self.list = QListWidget()
        layout.addWidget(self.list)

        btn_fetch = QPushButton("Haberleri Getir")
        btn_fetch.clicked.connect(self.fetch_news)
        layout.addWidget(btn_fetch)

        self.setLayout(layout)

    def fetch_news(self):
        try:
            resp = requests.get("https://newsapi.org/v2/top-headlines?country=tr&apiKey=YOUR_API_KEY")
            data = resp.json()
            self.list.clear()
            for article in data.get("articles", []):
                self.list.addItem(article["title"])
        except Exception as e:
            self.list.addItem(f"Hata: {e}")

class Weather(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Weather - Flourescent OS")
        layout = QVBoxLayout()

        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("Şehir adı giriniz")
        btn_fetch = QPushButton("Hava Durumu Getir")
        btn_fetch.clicked.connect(self.fetch_weather)

        self.result = QLabel("Sonuç yok")

        layout.addWidget(self.city_input)
        layout.addWidget(btn_fetch)
        layout.addWidget(self.result)
        self.setLayout(layout)

    def fetch_weather(self):
        try:
            city = self.city_input.text()
            resp = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid=YOUR_API_KEY&units=metric&lang=tr")
            data = resp.json()
            temp = data["main"]["temp"]
            desc = data["weather"][0]["description"]
            self.result.setText(f"{city}: {temp}°C, {desc}")
        except Exception as e:
            self.result.setText(f"Hata: {e}")


class Maps(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Maps - Flourescent OS")
        layout = QVBoxLayout()

        self.webview = QWebEngineView()
        self.webview.setUrl(QUrl("https://www.google.com/maps"))
        layout.addWidget(self.webview)

        self.setLayout(layout)


class Dictionary(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dictionary - Flourescent OS")
        layout = QVBoxLayout()

        self.word_input = QLineEdit()
        self.word_input.setPlaceholderText("Kelime giriniz")
        btn_search = QPushButton("Ara")
        btn_search.clicked.connect(self.search_word)

        self.result = QLabel("Sonuç yok")

        layout.addWidget(self.word_input)
        layout.addWidget(btn_search)
        layout.addWidget(self.result)
        self.setLayout(layout)

    def search_word(self):
        word = self.word_input.text()
        try:
            resp = requests.get(f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}")
            data = resp.json()
            meaning = data[0]["meanings"][0]["definitions"][0]["definition"]
            self.result.setText(f"{word}: {meaning}")
        except Exception as e:
            self.result.setText(f"Hata: {e}")


class Translator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Translator - Flourescent OS")
        layout = QVBoxLayout()

        self.text_input = QLineEdit()
        self.text_input.setPlaceholderText("Çevrilecek metin")
        btn_translate = QPushButton("Türkçe → İngilizce")
        btn_translate.clicked.connect(self.translate_text)

        self.result = QLabel("Sonuç yok")

        layout.addWidget(self.text_input)
        layout.addWidget(btn_translate)
        layout.addWidget(self.result)
        self.setLayout(layout)

    def translate_text(self):
        try:
            text = self.text_input.text()
            resp = requests.get(f"https://api.mymemory.translated.net/get?q={text}&langpair=tr|en")
            data = resp.json()
            translated = data["responseData"]["translatedText"]
            self.result.setText(translated)
        except Exception as e:
            self.result.setText(f"Hata: {e}")

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton, QFileDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

class PDFViewer(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDFViewer - Flourescent OS")
        layout = QVBoxLayout()

        # WebEngine tabanlı PDF görüntüleyici
        self.viewer = QWebEngineView()
        layout.addWidget(self.viewer)

        btn_open = QPushButton("PDF Aç")
        btn_open.clicked.connect(self.open_pdf)
        layout.addWidget(btn_open)

        self.setLayout(layout)

    def open_pdf(self):
        fname, _ = QFileDialog.getOpenFileName(self, "PDF Aç", "", "PDF Files (*.pdf)")
        if fname:
            self.viewer.setUrl(QUrl.fromLocalFile(fname))


class Music(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Music - Flourescent OS")
        layout = QVBoxLayout()

        self.player = QMediaPlayer()

        btn_open = QPushButton("Parça Aç")
        btn_open.clicked.connect(self.open_file)
        btn_play = QPushButton("Oynat")
        btn_play.clicked.connect(self.player.play)
        btn_pause = QPushButton("Duraklat")
        btn_pause.clicked.connect(self.player.pause)

        layout.addWidget(btn_open)
        layout.addWidget(btn_play)
        layout.addWidget(btn_pause)
        self.setLayout(layout)

    def open_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Parça Aç", "", "Audio Files (*.mp3 *.wav)")
        if fname:
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(fname)))


class Settings(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings - Flourescent OS")
        layout = QVBoxLayout()

        self.theme_input = QLineEdit()
        self.theme_input.setPlaceholderText("Tema (light/dark)")
        btn_apply = QPushButton("Uygula")
        btn_apply.clicked.connect(self.apply_settings)

        layout.addWidget(self.theme_input)
        layout.addWidget(btn_apply)
        self.setLayout(layout)

    def apply_settings(self):
        theme = self.theme_input.text()
        QMessageBox.information(self, "Ayarlar", f"Tema {theme} olarak ayarlandı!")

class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculator - Flourescent OS")
        layout = QVBoxLayout()

        self.expr_input = QLineEdit()
        self.expr_input.setPlaceholderText("İfade giriniz (örn: 2+2)")
        btn_calc = QPushButton("Hesapla")
        btn_calc.clicked.connect(self.calculate)

        self.result = QLabel("Sonuç: -")

        layout.addWidget(self.expr_input)
        layout.addWidget(btn_calc)
        layout.addWidget(self.result)
        self.setLayout(layout)

    def calculate(self):
        try:
            expr = self.expr_input.text()
            res = eval(expr)
            self.result.setText(f"Sonuç: {res}")
        except Exception as e:
            self.result.setText(f"Hata: {e}")


import random
from PyQt5.QtWidgets import QWidget, QGridLayout, QPushButton, QMessageBox

class Minesweeper(QWidget):
    def __init__(self, rows=8, cols=8, mines=10):
        super().__init__()
        self.setWindowTitle("Minesweeper - Flourescent OS")
        self.rows, self.cols, self.mines = rows, cols, mines
        self.grid = QGridLayout()
        self.setLayout(self.grid)
        self.buttons = {}
        self.mine_positions = set(random.sample(range(rows*cols), mines))
        self.revealed = set()

        for r in range(rows):
            for c in range(cols):
                btn = QPushButton("")
                btn.setFixedSize(40,40)
                btn.clicked.connect(lambda _, x=r, y=c: self.reveal(x,y))
                self.grid.addWidget(btn, r, c)
                self.buttons[(r,c)] = btn

    def reveal(self, r, c):
        if (r*self.cols+c) in self.mine_positions:
            for (x,y), b in self.buttons.items():
                if (x*self.cols+y) in self.mine_positions:
                    b.setText("💣")
            QMessageBox.information(self, "Oyun Bitti", "Mayına bastın!")
            for b in self.buttons.values():
                b.setEnabled(False)
            return

        count = self.count_adjacent(r,c)
        self.buttons[(r,c)].setText(str(count) if count>0 else "")
        self.buttons[(r,c)].setEnabled(False)
        self.revealed.add((r,c))

        if count == 0:
            for nx,ny in self.neighbors(r,c):
                if (nx,ny) not in self.revealed:
                    self.reveal(nx,ny)

        if len(self.revealed) == self.rows*self.cols - self.mines:
            QMessageBox.information(self, "Kazandın", "Tüm mayınlardan kaçtın!")

    def count_adjacent(self, r,c):
        return sum((nx*self.cols+ny) in self.mine_positions for nx,ny in self.neighbors(r,c))

    def neighbors(self, r,c):
        for dx in [-1,0,1]:
            for dy in [-1,0,1]:
                if dx==0 and dy==0: continue
                nx, ny = r+dx, c+dy
                if 0<=nx<self.rows and 0<=ny<self.cols:
                    yield nx, ny


import random
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QPainter

class Tetris(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TETPNC - Flourescent OS")
        self.setFixedSize(300,600)
        self.rows, self.cols = 20, 10
        self.board = [[0]*self.cols for _ in range(self.rows)]
        self.shapes = [
            [[1,1,1,1]],                # I
            [[1,1],[1,1]],              # O
            [[0,1,0],[1,1,1]],          # T
            [[1,0,0],[1,1,1]],          # J
            [[0,0,1],[1,1,1]],          # L
            [[1,1,0],[0,1,1]],          # S
            [[0,1,1],[1,1,0]]           # Z
        ]
        self.current = self.new_piece()
        self.cx, self.cy = 3, 0
        self.timer = QTimer()
        self.timer.timeout.connect(self.drop)
        self.timer.start(500)

    def new_piece(self):
        return random.choice(self.shapes)

    def paintEvent(self,event):
        painter = QPainter(self)
        for y in range(self.rows):
            for x in range(self.cols):
                if self.board[y][x]:
                    painter.fillRect(x*30,y*30,30,30,Qt.blue)
        for y,row in enumerate(self.current):
            for x,val in enumerate(row):
                if val:
                    painter.fillRect((self.cx+x)*30,(self.cy+y)*30,30,30,Qt.red)

    def keyPressEvent(self,event):
        if event.key()==Qt.Key_Left: self.cx -= 1
        elif event.key()==Qt.Key_Right: self.cx += 1
        elif event.key()==Qt.Key_Down: self.drop()
        elif event.key()==Qt.Key_Up: self.current = list(zip(*self.current[::-1]))
        self.update()

    def drop(self):
        self.cy += 1
        if self.collision():
            self.cy -= 1
            self.lock_piece()
            self.clear_lines()
            self.current = self.new_piece()
            self.cx, self.cy = 3,0
        self.update()

    def collision(self):
        for y,row in enumerate(self.current):
            for x,val in enumerate(row):
                if val:
                    nx, ny = self.cx+x, self.cy+y
                    if nx<0 or nx>=self.cols or ny>=self.rows or self.board[ny][nx]:
                        return True
        return False

    def lock_piece(self):
        for y,row in enumerate(self.current):
            for x,val in enumerate(row):
                if val:
                    self.board[self.cy+y][self.cx+x]=1

    def clear_lines(self):
        self.board = [row for row in self.board if any(v==0 for v in row)]
        while len(self.board)<self.rows:
            self.board.insert(0,[0]*self.cols)

import sys, os, json, datetime, psutil
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QStackedWidget, QMessageBox, QInputDialog, QTextEdit
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QPixmap   # 🔥 eklendi

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


# 🔑 Örnek uygulama: Texter (state destekli)
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
        self.setWindowTitle("Flourescent OS Desktop")
        self.resize(480, 600)

        # 🔥 Arka plan resmi (dağ manzarası)
        self.bg_label = QLabel(self)
        self.bg_label.setPixmap(QPixmap("mountain_wallpaper.jpeg").scaled(self.size(), Qt.KeepAspectRatioByExpanding))
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
        dock_layout.setAlignment(Qt.AlignCenter)
        main_layout.addLayout(dock_layout)

        self.apps_dict = apps_dict
        for name, widget_class in apps_dict.items():
            btn = QPushButton(name)
            btn.setFixedSize(40, 40)
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

    # 🔥 Resize event → arka plan resmi pencere boyutuna uyar
    def resizeEvent(self, event):
        self.bg_label.setPixmap(QPixmap("mountain_wallpaper.jpeg").scaled(self.size(), Qt.KeepAspectRatioByExpanding))
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
        "🎨": Paint,
        "🖼️": Gallery,
        "🌐": Browser,
        "📰": News,
        "☁️": Weather,
        "🗺": Maps,
        "📖": Dictionary,
        "🌍": Translator,
        "📑": PDFViewer,
        "🎵": Music,
        "⚙️": Settings,
        "🎮": Tetris,
        "💣": Minesweeper,
        "🧮": Calculator,
        "📝": Texter, # Start düğmesi sadece ikon
    }

    desktop = DesktopUI(apps_dict)
    desktop.show()
    sys.exit(app.exec_())

