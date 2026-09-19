import sys, datetime, psutil, os, feedparser
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QMessageBox, QProgressBar, QStackedWidget, QTextEdit,
    QTableWidget, QTableWidgetItem, QFileDialog, QInputDialog
)

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPainter, QPen, QPixmap
from PyQt5.QtMultimedia import QMediaPlayer, QMediaContent
from PyQt5.QtMultimediaWidgets import QVideoWidget
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

# --- Pack 1: Texter, Biller, Presentator, EmailClient ---
class Texter(QWidget):
    def __init__(self):
        super().__init__()
        l=QVBoxLayout(); self.text_area=QTextEdit(); l.addWidget(self.text_area)
        r=QHBoxLayout()
        for name,func in [("Yeni",lambda: self.text_area.clear()),
                          ("Aç",self.open_file),("Kaydet",self.save_file)]:
            b=QPushButton(name); b.clicked.connect(func); r.addWidget(b)
        l.addLayout(r); self.setLayout(l)
    def open_file(self):
        f,_=QFileDialog.getOpenFileName(self,"Dosya Aç","","*.txt")
        if f: self.text_area.setText(open(f,"r",encoding="utf-8").read())
    def save_file(self):
        f,_=QFileDialog.getSaveFileName(self,"Kaydet","","*.txt")
        if f: open(f,"w",encoding="utf-8").write(self.text_area.toPlainText())

class Biller(QWidget):
    def __init__(self):
        super().__init__()
        l=QVBoxLayout(); self.table=QTableWidget(0,2)
        self.table.setHorizontalHeaderLabels(["Müşteri","Tutar"]); l.addWidget(self.table)
        b1=QPushButton("Fatura Ekle"); b1.clicked.connect(self.add_invoice)
        b2=QPushButton("Toplam Hesapla"); b2.clicked.connect(self.calculate_total)
        l.addWidget(b1); l.addWidget(b2); self.setLayout(l)
    def add_invoice(self):
        n,ok1=QInputDialog.getText(self,"Müşteri","Ad:")
        if not ok1: return
        a,ok2=QInputDialog.getDouble(self,"Tutar","Fatura:",0,0,1e6,2)
        if not ok2: return
        r=self.table.rowCount(); self.table.insertRow(r)
        self.table.setItem(r,0,QTableWidgetItem(n))
        self.table.setItem(r,1,QTableWidgetItem(str(a)))
    def calculate_total(self):
        t=0
        for r in range(self.table.rowCount()):
            try: t+=float(self.table.item(r,1).text())
            except: pass
        QMessageBox.information(self,"Toplam",f"Toplam: {t}")

class Presentator(QWidget):
    def __init__(self):
        super().__init__()
        l=QVBoxLayout(); self.slides=QListWidget(); l.addWidget(self.slides)
        b1=QPushButton("Slayt Ekle"); b1.clicked.connect(self.add_slide)
        b2=QPushButton("Slayt Sil"); b2.clicked.connect(self.delete_slide)
        l.addWidget(b1); l.addWidget(b2); self.setLayout(l)
    def add_slide(self):
        t,ok=QInputDialog.getText(self,"Slayt","Başlık:")
        if ok and t.strip(): self.slides.addItem(t)
    def delete_slide(self):
        r=self.slides.currentRow()
        if r>=0: self.slides.takeItem(r)

class EmailClient(QWidget):
    def __init__(self):
        super().__init__()
        l=QVBoxLayout(); self.inbox=QTableWidget(0,2)
        self.inbox.setHorizontalHeaderLabels(["Kime","Konu"]); l.addWidget(self.inbox)
        b=QPushButton("Yeni Mail"); b.clicked.connect(self.compose_mail); l.addWidget(b)
        self.setLayout(l)
    def compose_mail(self):
        to,ok1=QInputDialog.getText(self,"Mail","Kime:")
        if not ok1: return
        s,ok2=QInputDialog.getText(self,"Mail","Konu:")
        if not ok2: return
        r=self.inbox.rowCount(); self.inbox.insertRow(r)
        self.inbox.setItem(r,0,QTableWidgetItem(to))
        self.inbox.setItem(r,1,QTableWidgetItem(s))

# --- Pack 2: Mario, Tetris, Riddles, FileExplorer, Store ---
class Mario(QWidget):
    def __init__(self):
        super().__init__()
        l=QVBoxLayout(); self.label=QLabel("🙂 Mario burada! ← → ile hareket et")
        self.label.setAlignment(Qt.AlignCenter); l.addWidget(self.label)
        self.setLayout(l); self.pos=0
    def keyPressEvent(self,e):
        if e.key()==Qt.Key_Left: self.pos-=1
        elif e.key()==Qt.Key_Right: self.pos+=1
        self.label.setText("🙂 "+" "*self.pos+"Mario")

class Tetris(QWidget):
    def __init__(self):
        super().__init__()
        l=QVBoxLayout(); l.addWidget(QLabel("🧩 Tetris Oyunu (placeholder)"))
        self.setLayout(l)

class Riddles(QWidget):
    def __init__(self):
        super().__init__()
        l=QVBoxLayout(); self.list=QListWidget()
        self.riddles={"Uçar kanadı yok...":"Bulut","Ne kadar alırsan...":"Çukur","Hep ileri gider...":"Zaman"}
        for q in self.riddles: self.list.addItem(q)
        l.addWidget(self.list)
        b=QPushButton("Cevabı Göster"); b.clicked.connect(self.show_answer)
        l.addWidget(b); self.setLayout(l)
    def show_answer(self):
        r=self.list.currentRow()
        if r>=0: q=self.list.item(r).text()
        QMessageBox.information(self,"Cevap",self.riddles[q])

class FileExplorer(QWidget):
    def __init__(self):
        super().__init__()
        l=QVBoxLayout(); self.list=QListWidget(); self.refresh_files(); l.addWidget(self.list)
        b1=QPushButton("Dosya Aç"); b1.clicked.connect(self.open_file)
        b2=QPushButton("Dosya Sil"); b2.clicked.connect(self.delete_file)
        l.addWidget(b1); l.addWidget(b2); self.setLayout(l)
    def refresh_files(self):
        self.list.clear(); [self.list.addItem(f) for f in os.listdir(".")]
    def open_file(self):
        r=self.list.currentRow()
        if r>=0: QMessageBox.information(self,"Dosya Aç",self.list.item(r).text())
    def delete_file(self):
        r=self.list.currentRow()
        if r>=0:
            f=self.list.item(r).text()
            try: os.remove(f); QMessageBox.information(self,"Sil",f+" silindi"); self.refresh_files()
            except: QMessageBox.warning(self,"Hata",f+" silinemedi")

class Store(QWidget):
    def __init__(self):
        super().__init__()
        l=QVBoxLayout(); self.list=QListWidget()
        self.list.addItems(["Texter","Biller","Presentator","EmailClient","Mario","Tetris","Riddles"])
        l.addWidget(self.list)
        b=QPushButton("Yükle"); b.clicked.connect(self.install_app); l.addWidget(b)
        self.setLayout(l)
    def install_app(self):
        r=self.list.currentRow()
        if r>=0: QMessageBox.information(self,"Yükleme",self.list.item(r).text()+" yüklendi!")

class MediaPlayer(QWidget):
    def __init__(self):
        super().__init__()
        l=QVBoxLayout()
        self.player=QMediaPlayer()
        self.video=QVideoWidget()
        self.player.setVideoOutput(self.video)
        l.addWidget(self.video)
        for name,func in [("Dosya Aç",self.open_file),
                          ("Oynat",self.player.play),
                          ("Duraklat",self.player.pause),
                          ("Durdur",self.player.stop)]:
            b=QPushButton(name); b.clicked.connect(func); l.addWidget(b)
        self.setLayout(l)

    def open_file(self):
        f,_=QFileDialog.getOpenFileName(self,"Medya Aç",
                                        "","*.mp4 *.avi *.mkv *.mp3 *.wav")
        if f:
            self.player.setMedia(QMediaContent(QUrl.fromLocalFile(f)))

class WebBrowser(QWidget):
    def __init__(self):
        super().__init__()
        l=QVBoxLayout()
        self.browser=QWebEngineView()
        self.browser.setUrl(QUrl("https://www.google.com"))
        l.addWidget(self.browser)
        for name,url in [("Google","https://www.google.com"),
                         ("YouTube","https://www.youtube.com"),
                         ("Wikipedia","https://www.wikipedia.org")]:
            b=QPushButton(name)
            b.clicked.connect(lambda _,u=url: self.browser.setUrl(QUrl(u)))
            l.addWidget(b)
        self.setLayout(l)

class News(QWidget):
    def __init__(self):
        super().__init__()
        l=QVBoxLayout()
        self.label=QLabel("📰 Haberler")
        l.addWidget(self.label)
        b=QPushButton("Haberleri Getir")
        b.clicked.connect(self.fetch_news)
        l.addWidget(b)
        self.setLayout(l)

    def fetch_news(self):
        feed=feedparser.parse("https://rss.cnn.com/rss/edition.rss")
        if feed.entries:
            headlines="\n".join([entry.title for entry in feed.entries[:5]])
            QMessageBox.information(self,"Son Haberler",headlines)
        else:
            QMessageBox.warning(self,"Hata","Haberler alınamadı.")

# --- Pack 4: Calculator, Notepad, MiniPaint ---
class Calculator(QWidget):
    def __init__(self):
        super().__init__()
        l=QVBoxLayout()
        self.display=QTextEdit(); self.display.setFixedHeight(40)
        l.addWidget(self.display)
        g=QHBoxLayout()
        for b in ["7","8","9","+","4","5","6","-","1","2","3","*","0",".","=","/"]:
            btn=QPushButton(b); btn.clicked.connect(lambda _,x=b: self.on_click(x)); g.addWidget(btn)
        l.addLayout(g); self.setLayout(l)
    def on_click(self,char):
        if char=="=":
            try: self.display.setText(str(eval(self.display.toPlainText())))
            except: self.display.setText("Hata")
        else: self.display.insertPlainText(char)

class Notepad(QWidget):
    def __init__(self):
        super().__init__()
        l=QVBoxLayout(); self.text_area=QTextEdit(); l.addWidget(self.text_area)
        b1=QPushButton("Aç"); b1.clicked.connect(self.open_file)
        b2=QPushButton("Kaydet"); b2.clicked.connect(self.save_file)
        l.addWidget(b1); l.addWidget(b2); self.setLayout(l)
    def open_file(self):
        f,_=QFileDialog.getOpenFileName(self,"Dosya Aç","","*.txt")
        if f: self.text_area.setText(open(f,"r",encoding="utf-8").read())
    def save_file(self):
        f,_=QFileDialog.getSaveFileName(self,"Kaydet","","*.txt")
        if f: open(f,"w",encoding="utf-8").write(self.text_area.toPlainText())

class MiniPaint(QWidget):
    def __init__(self):
        super().__init__()
        l=QVBoxLayout()
        self.canvas=QLabel(); self.canvas.setFixedSize(400,300)
        self.canvas.setStyleSheet("background:white; border:1px solid black;")
        self.canvas.setPixmap(QPixmap(400,300))   # ✅ crash yok
        l.addWidget(self.canvas); self.setLayout(l)
        self.last_x,self.last_y=None,None
    def mousePressEvent(self,e): self.last_x,self.last_y=e.x(),e.y()
    def mouseMoveEvent(self,e):
        if self.last_x is None: return
        pixmap=self.canvas.pixmap(); painter=QPainter(pixmap); pen=QPen(Qt.black,3); painter.setPen(pen)
        painter.drawLine(self.last_x,self.last_y,e.x(),e.y()); painter.end()
        self.canvas.setPixmap(pixmap); self.last_x,self.last_y=e.x(),e.y()
    def mouseReleaseEvent(self,e): self.last_x,self.last_y=None,None

# --- Chatbot ---
class Chatbot(QWidget):
    def __init__(self):
        super().__init__()
        l=QVBoxLayout()
        self.chat_area=QTextEdit(); self.chat_area.setReadOnly(True)
        self.input_area=QTextEdit(); self.input_area.setFixedHeight(50)
        b=QPushButton("Gönder"); b.clicked.connect(self.send_message)
        l.addWidget(QLabel("🤖 Yapay Zeka Chatbot"))
        l.addWidget(self.chat_area); l.addWidget(self.input_area); l.addWidget(b)
        self.setLayout(l); self.history=[]
    def send_message(self):
        t=self.input_area.toPlainText().strip()
        if t:
            self.chat_area.append(f"👤 {t}"); self.history.append(t.lower())
            self.chat_area.append("🤖 "+self.generate_reply(t)); self.input_area.clear()
    def generate_reply(self,t):
        t=t.lower()
        if "merhaba" in t: return "Merhaba Kuzey! Nasılsın?"
        if "yardım" in t: return "Hangi uygulamayı açmak istiyorsun?"
        if "tarih" in t or "saat" in t: return datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        if "uygulama" in t: return "Son kullanılanlar: "+", ".join(self.history[-3:])
        return "Bunu tam anlamadım, biraz daha açar mısın?"

import sys, datetime, psutil, os, json
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QPushButton, QListWidget, QMessageBox, QProgressBar, QStackedWidget, QTextEdit,
    QTableWidget, QTableWidgetItem, QFileDialog, QInputDialog
)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont

# --- Burada Texter, Biller, Presentator, EmailClient, Mario, Tetris, Riddles,
# FileExplorer, Store, MediaPlayer, WebBrowser, News, Calculator, Notepad,
# MiniPaint, Chatbot sınıfları aynen duruyor (senin dosyanda zaten var) ---

class Desktop(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DENEYAP_DOS Desktop")
        self.setGeometry(100,100,1200,700)

        # ✅ Koyu mod stylesheet
        self.setStyleSheet("""
            QWidget { background-color: #2b2b2b; color: #f0f0f0; }
            QPushButton { background-color: #444; color: #fff; border: 1px solid #666; padding: 5px; }
            QPushButton:hover { background-color: #666; }
            QTextEdit { background-color: #1e1e1e; color: #f0f0f0; }
            QListWidget { background-color: #1e1e1e; color: #f0f0f0; }
            QTableWidget { background-color: #1e1e1e; color: #f0f0f0; }
        """)

        c=QWidget(); self.setCentralWidget(c); l=QVBoxLayout(); c.setLayout(l)

        # Status bar
        s=QHBoxLayout()
        self.start_btn=QPushButton("🌟 Start"); self.start_btn.clicked.connect(self.show_start_menu)
        self.center=QLabel(); self.center.setAlignment(Qt.AlignCenter)
        self.battery=QLabel("🔋")
        wifi=QPushButton("📶 WiFi"); wifi.clicked.connect(lambda: QMessageBox.information(self,"WiFi","Ağlara bağlanma menüsü"))
        sound=QPushButton("🔊 Ses"); sound.clicked.connect(lambda: QMessageBox.information(self,"Ses","Ses ayarları"))
        notif=QPushButton("🔔 Bildirim"); notif.clicked.connect(lambda: QMessageBox.information(self,"Bildirim","Henüz yok"))
        s.addWidget(self.start_btn); s.addWidget(self.center); s.addWidget(self.battery); s.addWidget(wifi); s.addWidget(sound); s.addWidget(notif)
        sb=QWidget(); sb.setLayout(s); l.addWidget(sb,0)

        # Stack
        self.stack=QStackedWidget(); l.addWidget(self.stack,1)

        # Apps
        self.apps = {
            "Texter": Texter(),"Biller": Biller(),"Presentator": Presentator(),"Email": EmailClient(),
            "Mario": Mario(),"Tetris": Tetris(),"Riddles": Riddles(),"Explorer": FileExplorer(),"Store": Store(),
            "Media": MediaPlayer(),"Web": WebBrowser(),"News": News(),
            "Calculator": Calculator(),"Notepad": Notepad(),"MiniPaint": MiniPaint(),"Chatbot": Chatbot()
        }
        for app in self.apps.values(): self.stack.addWidget(app)

        # Dock
        d=QHBoxLayout(); d.setAlignment(Qt.AlignCenter); self.recent=[]
        for name,app in self.apps.items():
            b=QPushButton(name); b.clicked.connect(lambda _,w=app,n=name:self.open_app(w,n)); d.addWidget(b)
        dock=QWidget(); dock.setLayout(d); l.addWidget(dock,0)

        # Timer
        self.timer=QTimer(); self.timer.timeout.connect(self.update_status); self.timer.start(1000)

        # Açılışta state yükle
        self.load_state()

    def save_state(self):
        state = {
            "recent": self.recent,
            "theme": self.styleSheet(),
            "open_apps": [n for n in self.recent[-5:]]
        }
        with open("deneyap_state.json","w",encoding="utf-8") as f:
            json.dump(state,f,indent=4)

    def load_state(self):
        try:
            with open("deneyap_state.json","r",encoding="utf-8") as f:
                state = json.load(f)
            self.recent = state.get("recent",[])
            self.setStyleSheet(state.get("theme",self.styleSheet()))
            for n in state.get("open_apps",[]):
                if n in self.apps:
                    self.open_app(self.apps[n],n)
        except FileNotFoundError:
            pass

    def closeEvent(self,event):
        self.save_state()
        event.accept()

    def update_status(self):
        now=datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        battery=psutil.sensors_battery()
        self.center.setText(now)
        self.battery.setText(f"🔋 {battery.percent}%" if battery else "🔋 Yok")

    def open_app(self,w,n):
        self.recent.append(n)
        self.stack.setCurrentWidget(w)

    def show_start_menu(self):
        msg="🌟 Start Menu\nSon Kullanılanlar:\n"+"\n".join(self.recent[-5:])+"\nOturumu Kapat / Kapat"
        QMessageBox.information(self,"Start Menu",msg)


class BootScreen(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Booting DENEYAP_DOS...")
        self.setGeometry(100,100,1200,700)

        ascii = (
        
            "▐   DENEYAP_DOS v4.7             ▌\n"
            "▐   copyright(c) SPM 2023-2026   ▌"
        )
        box = QLabel(ascii)
        box.setAlignment(Qt.AlignCenter)
        box.setFont(QFont("Courier",14))

        self.progress = QProgressBar()
        self.progress.setRange(0,100)
        self.progress.setValue(0)

        l = QVBoxLayout()
        l.addWidget(box)
        l.addWidget(self.progress)

        c = QWidget()
        c.setLayout(l)
        self.setCentralWidget(c)

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(50)

    def update_progress(self):
        v = self.progress.value()
        if v < 100:
            self.progress.setValue(v+2)
        else:
            self.timer.stop()
            self.open_login()

    def open_login(self):
        self.close()
        self.login = LoginMenu()
        self.login.show()


class LoginMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login - DENEYAP_DOS")
        self.setGeometry(100,100,600,400)

        layout = QVBoxLayout()
        self.users = QListWidget()
        self.users.addItems(["Kuzey","Guest","Admin"])
        layout.addWidget(QLabel("Kullanıcı Seçiniz:"))
        layout.addWidget(self.users)

        btn_login = QPushButton("Giriş Yap")
        btn_login.clicked.connect(self.open_desktop)
        layout.addWidget(btn_login)

        c = QWidget()
        c.setLayout(layout)
        self.setCentralWidget(c)

    def open_desktop(self):
        self.close()
        self.desktop = Desktop()
        self.desktop.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    boot = BootScreen()
    boot.show()
    sys.exit(app.exec_())





