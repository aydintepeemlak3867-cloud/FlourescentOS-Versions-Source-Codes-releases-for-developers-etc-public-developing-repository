import sys
import os
import urllib.parse
import asyncio
import httpx
import requests
import vlc

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, 
    QHBoxLayout, QPushButton, QLabel, QTabWidget, 
    QMessageBox, QProgressBar, QSlider, QListWidget, 
    QSplitter, QComboBox
)
from PyQt6.QtCore import QThread, pyqtSignal, Qt, QTimer
from PyQt6.QtGui import QKeyEvent, QFont

# --- GİT / REPO AYARLARI ---
GITHUB_USER = "aydintepeemlak3867-cloud"
REPO_NAME = "Ro-StreamHub.Net"
BRANCH = "main"

# --- FARKLI UYDU VE BÖLGE M3U HAVUZLARI ---
SATELLITE_SOURCES = {
    "4444 Özel Kanal Havuzu": [
        "https://raw.githubusercontent.com/IPTV-Org/iptv/master/index.m3u"
    ],
    "Türksat (Türkiye - Yerel & Ulusal)": [
        "https://raw.githubusercontent.com/IPTV-Org/iptv/master/streams/tr.m3u"
    ],
    "Hotbird / Avrupa Uydu Paketi": [
        "https://raw.githubusercontent.com/IPTV-Org/iptv/master/streams/it.m3u",
        "https://raw.githubusercontent.com/IPTV-Org/iptv/master/streams/de.m3u"
    ],
    "Astra / Global & Uluslararası": [
        "https://raw.githubusercontent.com/IPTV-Org/iptv/master/streams/gb.m3u",
        "https://raw.githubusercontent.com/IPTV-Org/iptv/master/streams/fr.m3u"
    ],
    "Dünya Belgesel Kanalları Havuzu": [
        "https://raw.githubusercontent.com/IPTV-Org/iptv/master/categories/documentary.m3u"
    ],
    "Dünya Spor Kanalları Havuzu": [
        "https://raw.githubusercontent.com/IPTV-Org/iptv/master/categories/sports.m3u"
    ]
}

# --- BAŞLANGIÇ KANAL LİSTESİ ---
GLOBAL_IPTV_CHANNELS = {
    "TRT1": {
        "name": "TRT 1 HD",
        "frequency": "11794 V / 30000",
        "band": "Türksat 4A",
        "quality": "HD (1080p)",
        "stream_url": "https://tv-trt1.medya.trt.com.tr/master_720.m3u8",
        "category": "Ulusal Kanallar",
        "country": "Türkiye"
    },
    "ATV": {
        "name": "ATV HD",
        "frequency": "12053 H / 27500",
        "band": "Türksat 4A",
        "quality": "HD (1080p)",
        "stream_url": "https://trkvz-live.daioncdn.net/atv/atv.m3u8",
        "category": "Ulusal Kanallar",
        "country": "Türkiye"
    }
}


# --- ARKA PLAN OTOMATİK LİNK DOĞRULAMA VE M3U PARSER ---
class AutoM3UFetcher(QThread):
    channels_fetched = pyqtSignal(dict)

    def __init__(self, selected_urls):
        super().__init__()
        self.selected_urls = selected_urls

    def run(self):
        combined_channels = {}
        for source_url in self.selected_urls:
            try:
                res = requests.get(source_url, timeout=10)
                if res.status_code == 200:
                    lines = res.text.splitlines()
                    current_name = "Oto Kanal"
                    current_group = "Yerel ve Diğer"
                    parsed_items = []
                    
                    for line in lines:
                        line = line.strip()
                        if line.startswith("#EXTINF:"):
                            if "group-title=\"" in line:
                                try:
                                    start = line.index("group-title=\"") + 13
                                    end = line.index("\"", start)
                                    current_group = line[start:end]
                                except:
                                    pass
                            if "," in line:
                                current_name = line.split(",")[-1].strip()
                        elif line and not line.startswith("#"):
                            low_name = current_name.lower()
                            if any(x in low_name for x in ["adult", "xxx"]):
                                continue
                            
                            cat = "Uydu Yayınları"
                            low_grp = current_group.lower()
                            if "news" in low_grp or "haber" in low_grp:
                                cat = "Haber"
                            elif "documentary" in low_grp or "belgesel" in low_grp:
                                cat = "Belgesel"
                            elif "sports" in low_grp or "spor" in low_grp:
                                cat = "Spor"

                            parsed_items.append((current_name, line, cat))

                    for idx, (name, url, cat) in enumerate(parsed_items[:500]):
                        key = f"SAT_{idx}_{name[:4].upper()}"
                        combined_channels[key] = {
                            "name": name,
                            "frequency": "Özel Havuz Tarandı",
                            "band": "IPTV Cloud",
                            "quality": "HD/SD",
                            "stream_url": url,
                            "category": cat,
                            "country": "Özel Liste"
                        }
            except Exception:
                pass
        
        if combined_channels:
            self.channels_fetched.emit(combined_channels)


class RepoScannerWorker(QThread):
    finished = pyqtSignal(list)
    error_occurred = pyqtSignal(str)

    def run(self):
        try:
            api_url = f"https://api.github.com/repos/{GITHUB_USER}/{REPO_NAME}/contents"
            headers = {"Accept": "application/vnd.github.v3+json"}
            response = requests.get(api_url, headers=headers, timeout=10)
            
            playlist = []
            if response.status_code == 200:
                files = response.json()
                for file in files:
                    if file.get('type') == 'file' and file.get('name', '').lower().endswith(('.mp4', '.mkv', '.avi', '.mov', '.webm', '.flv')):
                        filename = file['name']
                        encoded_name = urllib.parse.quote(filename)
                        raw_link = f"https://raw.githubusercontent.com/{GITHUB_USER}/{REPO_NAME}/{BRANCH}/{encoded_name}"
                        playlist.append((filename, raw_link))
                self.finished.emit(playlist)
            else:
                self.error_occurred.emit(f"GitHub API Hatası: Kod {response.status_code}")
        except Exception as e:
            self.error_occurred.emit(f"Bağlantı hatası: {str(e)}")


# --- ANA WIDGET YAPISI (QMainWindow YERİNE QWidget) ---
class SatelliteReceiverWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet(self.get_stylesheet())

        self.playlist = []
        self.current_channel_key = "TRT1" 

        vlc_args = [
            '--no-xlib', 
            '--quiet', 
            '--live-caching=3000',
            '--network-caching=3000',
            '--http-reconnect',
            '--rtsp-tcp',
            '--avcodec-skiploopfilter=4',
            '--http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        ]
        self.vlc_instance = vlc.Instance(vlc_args)
        self.media_player = self.vlc_instance.media_player_new()
        self.media_player.audio_set_volume(80)

        self.status_timer = QTimer(self)
        self.status_timer.setInterval(1000)
        self.status_timer.timeout.connect(self.update_stream_status)
        self.status_timer.start()

        self.init_ui()
        self.start_repo_scan()
        self.load_selected_satellite("4444 Özel Kanal Havuzu")

    def get_stylesheet(self):
        return """
            QWidget { background-color: #0b0e14; color: #ffffff; }
            QTabWidget::pane { border: 1px solid #1f293d; background: #111827; border-radius: 6px; }
            QTabBar::tab { background: #1f293d; color: #9ca3af; padding: 10px 20px; margin-right: 4px; border-top-left-radius: 4px; border-top-right-radius: 4px; font-weight: bold; }
            QTabBar::tab:selected { background: #e50914; color: #ffffff; }
            QPushButton { background-color: #1f293d; color: white; border: none; padding: 8px 14px; border-radius: 4px; font-weight: bold; }
            QPushButton:hover { background-color: #374151; }
            QPushButton#PlayButton { background-color: #e50914; }
            QPushButton#PlayButton:hover { background-color: #f40612; }
            QLabel { color: #e5e7eb; font-family: 'Segoe UI', Arial; }
            QListWidget { background-color: #0f172a; border: 1px solid #1f293d; color: #f3f4f6; border-radius: 6px; padding: 5px; }
            QListWidget::item { padding: 8px; border-bottom: 1px solid #1e293b; border-radius: 4px; }
            QListWidget::item:selected { background-color: #e50914; color: white; }
            QComboBox { background-color: #1f293d; color: white; border: 1px solid #374151; padding: 6px; border-radius: 4px; font-weight: bold; }
            QComboBox::drop-down { border: 0px; }
            QProgressBar { background: #1f293d; border: none; border-radius: 4px; text-align: center; color: white; }
            QProgressBar::chunk { background-color: #e50914; border-radius: 3px; }
            QSlider::groove:horizontal { height: 6px; background: #1f293d; border-radius: 3px; }
            QSlider::sub-page:horizontal { background: #e50914; border-radius: 3px; }
            QSlider::handle:horizontal { background: #fff; width: 14px; margin: -4px 0; border-radius: 7px; }
        """

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)

        self.tabs = QTabWidget()
        self.tab_tv = QWidget()
        self.tab_repo = QWidget()

        self.tabs.addTab(self.tab_tv, "🛰️ Çoklu Uydu ve Kanal Seçici")
        self.tabs.addTab(self.tab_repo, "📂 Ham Bulut Deposu")

        main_layout.addWidget(self.tabs)
        self.setup_satellite_tab(self.tab_tv)
        self.setup_repo_tab(self.tab_repo)

    def setup_satellite_tab(self, tab):
        layout = QHBoxLayout(tab)

        left_panel = QVBoxLayout()
        
        left_panel.addWidget(QLabel("<b>📡 Aktif Uydu / Kaynak Paketi:</b>"))
        self.sat_combo = QComboBox()
        self.sat_combo.addItems(list(SATELLITE_SOURCES.keys()))
        self.sat_combo.setCurrentText("4444 Özel Kanal Havuzu")
        self.sat_combo.currentTextChanged.connect(self.load_selected_satellite)
        left_panel.addWidget(self.sat_combo)

        self.lbl_osd_banner = QLabel("<b>OSD: SİSTEM HAZIR</b>")
        self.lbl_osd_banner.setStyleSheet("color: #46d369; font-size: 11px;")
        left_panel.addWidget(self.lbl_osd_banner)

        self.list_channels = QListWidget()
        self.list_channels.currentRowChanged.connect(self.on_channel_row_changed)
        left_panel.addWidget(self.list_channels)

        left_panel.addWidget(QLabel("<b>Kanal Detayları</b>"))
        self.list_themes = QListWidget()
        left_panel.addWidget(self.list_themes)

        container_left = QWidget()
        container_left.setLayout(left_panel)
        container_left.setMaximumWidth(380)

        right_panel = QVBoxLayout()
        self.lbl_status = QLabel("● YAYINA HAZIR | Ses: %80")
        self.lbl_status.setStyleSheet("font-size: 13px; font-weight: bold; color: #46d369; background: #1f293d; padding: 8px; border-radius: 4px;")
        right_panel.addWidget(self.lbl_status)

        self.video_container = QWidget()
        self.video_container.setStyleSheet("background-color: black; border-radius: 8px; border: 2px solid #1f293d;")
        self.video_container.setMinimumHeight(440)
        
        video_layout = QVBoxLayout(self.video_container)
        video_layout.setContentsMargins(0, 0, 0, 0)
        
        self.video_frame = QWidget()
        self.video_frame.setStyleSheet("background-color: black;")
        video_layout.addWidget(self.video_frame)

        self.lbl_no_signal = QLabel("⚠️ SİNYAL BULUNAMADI", self.video_container)
        self.lbl_no_signal.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_no_signal.setStyleSheet("""
            color: #f87171;
            background-color: rgba(15, 23, 42, 220);
            border: 2px dashed #ef4444;
            border-radius: 8px;
            font-size: 18px;
            font-weight: bold;
            padding: 10px 20px;
        """)
        self.lbl_no_signal.adjustSize()

        self.lbl_watermark = QLabel("AutoStream\nLive HD", self.video_container)
        self.lbl_watermark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_watermark.setStyleSheet("""
            color: rgba(255, 140, 0, 230);
            background-color: rgba(15, 23, 42, 180);
            border: 1px solid rgba(229, 9, 20, 180);
            border-radius: 6px;
            font-size: 11px;
            font-weight: bold;
            padding: 4px 8px;
        """)
        self.lbl_watermark.adjustSize()

        right_panel.addWidget(self.video_container)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(5)
        self.progress_bar.setTextVisible(False)
        right_panel.addWidget(self.progress_bar)

        self.time_slider = QSlider(Qt.Orientation.Horizontal)
        self.time_slider.setRange(0, 1000)
        right_panel.addWidget(self.time_slider)

        btn_layout = QHBoxLayout()
        self.play_btn = QPushButton("▶ Canlı Yayını Başlat")
        self.play_btn.setObjectName("PlayButton")
        self.play_btn.clicked.connect(self.play_live_stream)
        btn_layout.addWidget(self.play_btn)

        self.stop_btn = QPushButton("⏹ Yayını Durdur")
        self.stop_btn.clicked.connect(self.stop_video)
        btn_layout.addWidget(self.stop_btn)

        btn_layout.addStretch()
        self.lbl_time = QLabel("ÇOKLU UYDU AKTİF")
        btn_layout.addWidget(self.lbl_time)
        right_panel.addLayout(btn_layout)

        container_right = QWidget()
        container_right.setLayout(right_panel)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(container_left)
        splitter.addWidget(container_right)
        splitter.setSizes([360, 740])
        
        layout.addWidget(splitter)

    def load_selected_satellite(self, sat_name):
        urls = SATELLITE_SOURCES.get(sat_name, [])
        self.lbl_osd_banner.setText(f"<b>⏳ {sat_name} taranıyor...</b>")
        
        global GLOBAL_IPTV_CHANNELS
        GLOBAL_IPTV_CHANNELS = {
            "TRT1": {
                "name": "TRT 1 HD",
                "frequency": "11794 V / 30000",
                "band": "Türksat 4A",
                "quality": "HD (1080p)",
                "stream_url": "https://tv-trt1.medya.trt.com.tr/master_720.m3u8",
                "category": "Ulusal Kanallar",
                "country": "Türkiye"
            },
            "ATV": {
                "name": "ATV HD",
                "frequency": "12053 H / 27500",
                "band": "Türksat 4A",
                "quality": "HD (1080p)",
                "stream_url": "https://trkvz-live.daioncdn.net/atv/atv.m3u8",
                "category": "Ulusal Kanallar",
                "country": "Türkiye"
            }
        }

        self.auto_fetcher = AutoM3UFetcher(urls)
        self.auto_fetcher.channels_fetched.connect(self.on_sat_channels_loaded)
        self.auto_fetcher.start()

    def on_sat_channels_loaded(self, new_channels):
        GLOBAL_IPTV_CHANNELS.update(new_channels)
        self.list_channels.clear()
        for ch_key, data in GLOBAL_IPTV_CHANNELS.items():
            self.list_channels.addItem(f"[{data['category']}] {data['name']}")
        if GLOBAL_IPTV_CHANNELS:
            self.list_channels.setCurrentRow(0)
        self.lbl_osd_banner.setText(f"<b>OSD: Toplam {len(GLOBAL_IPTV_CHANNELS)} kanal yüklendi.</b>")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'video_container'):
            if hasattr(self, 'lbl_watermark'):
                margin_right = 15
                margin_bottom = 15
                x = self.video_container.width() - self.lbl_watermark.width() - margin_right
                y = self.video_container.height() - self.lbl_watermark.height() - margin_bottom
                self.lbl_watermark.move(x, y)
            
            if hasattr(self, 'lbl_no_signal'):
                x_sig = (self.video_container.width() - self.lbl_no_signal.width()) // 2
                y_sig = (self.video_container.height() - self.lbl_no_signal.height()) // 2
                self.lbl_no_signal.move(x_sig, y_sig)

    def setup_repo_tab(self, tab):
        layout = QVBoxLayout(tab)
        lbl = QLabel("GitHub Sunucusundaki Ham Medya Dosyaları Havuzu")
        lbl.setStyleSheet("color: #9ca3af; font-size: 13px; font-weight: bold;")
        layout.addWidget(lbl)
        self.list_repo_files = QListWidget()
        layout.addWidget(self.list_repo_files)

        btn_refresh = QPushButton("🔄 Depoyu Yenile")
        btn_refresh.clicked.connect(self.start_repo_scan)
        layout.addWidget(btn_refresh)

    def start_repo_scan(self):
        self.scanner = RepoScannerWorker()
        self.scanner.finished.connect(self.on_repo_scanned)
        self.scanner.error_occurred.connect(lambda msg: self.lbl_status.setText(f"Hata: {msg}"))
        self.scanner.start()

    def on_repo_scanned(self, playlist):
        self.playlist = playlist
        self.list_repo_files.clear()
        for filename, url in playlist:
            self.list_repo_files.addItem(filename)

    def on_channel_row_changed(self, row):
        keys = list(GLOBAL_IPTV_CHANNELS.keys())
        if 0 <= row < len(keys):
            ch_key = keys[row]
            self.current_channel_key = ch_key
            ch_data = GLOBAL_IPTV_CHANNELS[ch_key]
            self.list_themes.clear()
            self.list_themes.addItems([
                f"Kanal: {ch_data['name']}",
                f"Kategori: {ch_data['category']}",
                f"Frekans: {ch_data['frequency']}",
                f"Uydu/Paket: {ch_data['band']}",
                f"Kalite: {ch_data['quality']}"
            ])
            vol = self.media_player.audio_get_volume()
            self.lbl_status.setText(f"● SEÇİLDİ: {ch_data['name']} | Ses: %{vol}")

    def update_stream_status(self):
        if not hasattr(self, 'media_player'):
            return
        state = self.media_player.get_state()
        vol = self.media_player.audio_get_volume()
        ch_data = GLOBAL_IPTV_CHANNELS.get(self.current_channel_key, {})
        ch_name = ch_data.get('name', 'Bilinmiyor')

        if state == vlc.State.Playing:
            self.lbl_status.setText(f"● OYNATILIYOR: {ch_name} | Ses: %{vol}")
            self.lbl_status.setStyleSheet("font-size: 13px; font-weight: bold; color: #46d369; background: #1f293d; padding: 8px; border-radius: 4px;")
            if self.lbl_no_signal.isVisible():
                self.lbl_no_signal.hide()
        elif state == vlc.State.Buffering:
            self.lbl_status.setText(f"⏳ ARABELLEĞE ALINIYOR: {ch_name}...")
            self.lbl_status.setStyleSheet("font-size: 13px; font-weight: bold; color: #f59e0b; background: #1f293d; padding: 8px; border-radius: 4px;")
        elif state in (vlc.State.Ended, vlc.State.Error, vlc.State.Stopped):
            if not self.lbl_no_signal.isVisible():
                self.lbl_no_signal.show()

    def keyPressEvent(self, event: QKeyEvent):
        key = event.key()
        current_row = self.list_channels.currentRow()
        max_row = self.list_channels.count() - 1
        current_vol = self.media_player.audio_get_volume()

        if key == Qt.Key.Key_Up:
            if current_row > 0:
                self.list_channels.setCurrentRow(current_row - 1)
            event.accept()
        elif key == Qt.Key.Key_Down:
            if current_row < max_row:
                self.list_channels.setCurrentRow(current_row + 1)
            event.accept()
        elif key == Qt.Key.Key_Right:
            new_vol = min(100, current_vol + 5)
            self.media_player.audio_set_volume(new_vol)
            event.accept()
        elif key == Qt.Key.Key_Left:
            new_vol = max(0, current_vol - 5)
            self.media_player.audio_set_volume(new_vol)
            event.accept()
        else:
            super().keyPressEvent(event)

    def play_live_stream(self):
        ch_data = GLOBAL_IPTV_CHANNELS.get(self.current_channel_key, {})
        stream_url = ch_data.get("stream_url")

        if not stream_url:
            QMessageBox.warning(self, "Hata", "Bu kanal için akış adresi bulunamadı!")
            return

        self.lbl_status.setText(f"● BAĞLANTI KURULUYOR: {ch_data.get('name')}...")
        
        media = self.vlc_instance.media_new(stream_url)
        media.add_option(":http-user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        media.add_option(":network-caching=3000")

        self.media_player.set_media(media)

        hwnd = int(self.video_frame.winId())
        if sys.platform.startswith('win'):
            self.media_player.set_hwnd(hwnd)
        elif sys.platform.startswith('darwin'):
            self.media_player.set_nsobject(hwnd)
        else:
            self.media_player.set_xwindow(hwnd)

        self.media_player.play()
        self.lbl_no_signal.hide()
        self.lbl_status.setText(f"● OYNATILIYOR: {ch_data.get('name')}")

    def stop_video(self):
        if hasattr(self, 'media_player'):
            self.media_player.stop()
        self.lbl_no_signal.show()
        self.lbl_status.setText("● YAYIN DURDURULDU")
        self.lbl_status.setStyleSheet("font-size: 13px; font-weight: bold; color: #9ca3af; background: #1f293d; padding: 8px; border-radius: 4px;")

    def closeEvent(self, event):
        if hasattr(self, 'status_timer'):
            self.status_timer.stop()
        if hasattr(self, 'media_player') and self.media_player:
            self.media_player.stop()
            self.media_player.release()
        if hasattr(self, 'vlc_instance') and self.vlc_instance:
            self.vlc_instance.release()
        event.accept()


# Test amaçlı bağımsız çalıştırma bloğu
if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = SatelliteReceiverWidget()
    widget.resize(1250, 850)
    widget.show()
    sys.exit(app.exec())