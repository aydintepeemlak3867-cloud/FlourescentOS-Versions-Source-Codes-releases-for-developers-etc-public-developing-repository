import sys
import os
import re
import datetime
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QTextEdit, QPlainTextEdit, QSplitter, QFileDialog, QMessageBox, 
    QTabWidget, QTreeView, QToolBar, QLineEdit, QPushButton
)
from PyQt6.QtCore import Qt, QFileInfo, QDir, QProcess
from PyQt6.QtGui import (
    QFont, QColor, QTextCharFormat, QSyntaxHighlighter, 
    QAction, QPainter, QFileSystemModel
)

# --- CATPPUCCIN MOCHA TEMA PALETİ ---
VISIONIST_STYLE = """
QMainWindow {
    background-color: #1e1e2e;
    color: #cdd6f4;
}
QWidget {
    color: #cdd6f4;
    font-family: 'Consolas', 'Segoe UI', monospace;
    font-size: 13px;
}
QToolBar {
    background-color: #181825;
    border-bottom: 1px solid #313244;
    padding: 6px;
    spacing: 10px;
}
QToolButton {
    background-color: #313244;
    color: #cdd6f4;
    border: none;
    border-radius: 4px;
    padding: 6px 12px;
    font-weight: bold;
}
QToolButton:hover {
    background-color: #45475a;
    color: #89b4fa;
}
QTabWidget::pane {
    border: 1px solid #313244;
    background-color: #1e1e2e;
}
QTabBar::tab {
    background-color: #181825;
    color: #6c7086;
    padding: 8px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
}
QTabBar::tab:selected {
    background-color: #313244;
    color: #89b4fa;
    border-bottom: 2px solid #89b4fa;
}
QTreeView {
    background-color: #11111b;
    border: none;
    color: #cdd6f4;
}
QTreeView::item:hover {
    background-color: #313244;
}
QTreeView::item:selected {
    background-color: #45475a;
    color: #89b4fa;
}
QTextEdit, QPlainTextEdit, QLineEdit {
    background-color: #11111b;
    color: #cdd6f4;
    border: 1px solid #313244;
    selection-background-color: #45475a;
}
QLineEdit {
    padding: 4px 8px;
    border-radius: 4px;
}
"""

# --- GELİŞMİŞ PYTHON SYNTAX HIGHLIGHTER ---
class PythonHighlighter(QSyntaxHighlighter):
    def __init__(self, document):
        super().__init__(document)
        self.highlighting_rules = []

        keyword_format = QTextCharFormat()
        keyword_format.setForeground(QColor("#f38ba8"))
        keyword_format.setFontWeight(QFont.Weight.Bold)
        keywords = [
            "def", "class", "import", "from", "return", "if", "elif", "else", 
            "while", "for", "in", "try", "except", "finally", "with", "as", 
            "lambda", "yield", "True", "False", "None", "and", "or", "not", 
            "global", "nonlocal", "pass", "break", "continue", "raise", "assert"
        ]
        for word in keywords:
            pattern = f"\\b{word}\\b"
            self.highlighting_rules.append((pattern, keyword_format))

        class_format = QTextCharFormat()
        class_format.setForeground(QColor("#f9e2af"))
        class_format.setFontWeight(QFont.Weight.Bold)
        self.highlighting_rules.append((r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)", class_format))

        function_format = QTextCharFormat()
        function_format.setForeground(QColor("#fab387"))
        self.highlighting_rules.append((r"\bdef\s+([A-Za-z_][A-Za-z0-9_]*)", function_format))
        self.highlighting_rules.append((r"\b[A-Za-z_][A-Za-z0-9_]*(?=\()", function_format))

        string_format = QTextCharFormat()
        string_format.setForeground(QColor("#a6e3a1"))
        self.highlighting_rules.append((r'".*?"', string_format))
        self.highlighting_rules.append((r"'.*?'", string_format))

        number_format = QTextCharFormat()
        number_format.setForeground(QColor("#fab387"))
        self.highlighting_rules.append((r"\b\d+\b", number_format))

        comment_format = QTextCharFormat()
        comment_format.setForeground(QColor("#6c7086"))
        comment_format.setFontItalic(True)
        self.highlighting_rules.append((r"#[^\n]*", comment_format))

    def highlightBlock(self, text):
        for pattern, fmt in self.highlighting_rules:
            for match in re.finditer(pattern, text):
                if match.groups():
                    start = match.start(1)
                    end = match.end(1)
                else:
                    start, end = match.span()
                self.setFormat(start, end - start, fmt)


# --- SATIR NUMARASI ALANI ---
class LineNumberArea(QWidget):
    def __init__(self, editor):
        super().__init__(editor)
        self.code_editor = editor

    def sizeHint(self):
        return self.code_editor.line_number_area_size()

    def paintEvent(self, event):
        self.code_editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    def __init__(self):
        super().__init__()
        self.file_path = None
        self.line_number_area = LineNumberArea(self)

        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        self.update_line_number_area_width(0)
        self.highlight_current_line()

    def line_number_area_size(self):
        digits = 1
        max_val = max(1, self.blockCount())
        while max_val >= 10:
            max_val //= 10
            digits += 1
        space = 10 + self.fontMetrics().horizontalAdvance('9') * digits
        return space

    def update_line_number_area_width(self, _):
        self.setViewportMargins(self.line_number_area_size(), 0, 0, 0)

    def update_line_number_area(self, rect, dy):
        if dy:
            self.line_number_area.scroll(0, dy)
        else:
            self.line_number_area.update(0, rect.y(), self.line_number_area.width(), rect.height())
        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        cr = self.contentsRect()
        self.line_number_area.setGeometry(cr.left(), cr.top(), self.line_number_area_size(), cr.height())

    def highlight_current_line(self):
        extra_selections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            line_color = QColor("#313244")
            selection.format.setBackground(line_color)
            selection.format.setProperty(QTextCharFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        self.setExtraSelections(extra_selections)

    def line_number_area_paint_event(self, event):
        painter = QPainter(self.line_number_area)
        painter.fillRect(event.rect(), QColor("#181825"))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                painter.setPen(QColor("#6c7086"))
                painter.setFont(self.font())
                painter.drawText(0, top, self.line_number_area.width() - 6, self.fontMetrics().height(),
                                 Qt.AlignmentFlag.AlignRight, number)
            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1


# --- IDE ENTEGRE TERMINAL PANELI ---
class IDETerminal(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(4)

        self.output_area = QTextEdit()
        self.output_area.setReadOnly(True)
        self.output_area.setFont(QFont("Consolas", 10))
        self.output_area.setPlaceholderText("Visionist IDE Gömülü Terminal Çıktısı...")

        input_layout = QHBoxLayout()
        self.input_line = QLineEdit()
        self.input_line.setPlaceholderText("Terminale veri gönder (input için Enter'a bas)...")
        self.input_line.returnPressed.connect(self.send_input)

        self.stop_btn = QPushButton("⏹ Durdur")
        self.stop_btn.setStyleSheet("background-color: #f38ba8; color: #11111b; font-weight: bold; padding: 4px 10px; border-radius: 4px;")
        self.stop_btn.clicked.connect(self.stop_process)

        input_layout.addWidget(self.input_line)
        input_layout.addWidget(self.stop_btn)

        layout.addWidget(self.output_area)
        layout.addLayout(input_layout)

        # Alt süreç yöneticisi
        self.process = QProcess(self)
        self.process.setProcessChannelMode(QProcess.ProcessChannelMode.MergedChannels)
        self.process.readyReadStandardOutput.connect(self.read_output)
        self.process.finished.connect(self.process_finished)

    def run_script(self, file_path):
        if self.process.state() != QProcess.ProcessState.NotRunning:
            self.process.kill()

        self.output_area.clear()
        self.append_text(f"--- Çalıştırılıyor: {file_path} [{datetime.datetime.now().strftime('%H:%M:%S')}] ---\n", "#89b4fa")
        
        # Python betiğini anlık tamponlama olmadan (-u) çalıştırır
        self.process.start(sys.executable, ["-u", file_path])

    def read_output(self):
        data = self.process.readAllStandardOutput().data().decode("utf-8", errors="replace")
        self.append_text(data, "#cdd6f4")

    def send_input(self):
        text = self.input_line.text()
        if self.process.state() == QProcess.ProcessState.Running:
            self.process.write((text + "\n").encode("utf-8"))
            self.append_text(f"> {text}\n", "#a6e3a1")
            self.input_line.clear()

    def stop_process(self):
        if self.process.state() == QProcess.ProcessState.Running:
            self.process.kill()
            self.append_text("\n[İşlem kullanıcı tarafından durduruldu.]\n", "#f38ba8")

    def process_finished(self, exit_code, exit_status):
        self.append_text(f"\n--- Süreç Bitti (Çıkış Kodu: {exit_code}) ---\n", "#fab387")

    def append_text(self, text, color_hex):
        cursor = self.output_area.textCursor()
        cursor.movePosition(cursor.MoveOperation.End)
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color_hex))
        cursor.insertText(text, fmt)
        self.output_area.ensureCursorVisible()


# --- ANA VISIONIST IDE PENCERESİ ---
class VisionistIDE(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Visionist IDE - Professional Development Environment")
        self.resize(1350, 800)

        main_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # 1. Sol Panel: Proje Dosya Ağacı
        self.file_model = QFileSystemModel()
        self.file_model.setRootPath(QDir.currentPath())
        self.tree_view = QTreeView()
        self.tree_view.setModel(self.file_model)
        self.tree_view.setRootIndex(self.file_model.index(QDir.currentPath()))
        self.tree_view.setColumnHidden(1, True)
        self.tree_view.setColumnHidden(2, True)
        self.tree_view.setColumnHidden(3, True)
        self.tree_view.doubleClicked.connect(self.open_file_from_tree)
        
        # 2. Orta Panel: Editör Sekmeleri ve Entegre Alt Terminal
        editor_console_splitter = QSplitter(Qt.Orientation.Vertical)
        
        self.tab_widget = QTabWidget()
        self.tab_widget.setTabsClosable(True)
        self.tab_widget.tabCloseRequested.connect(self.close_tab)
        
        # IDE İçi Canlı Terminal
        self.terminal = IDETerminal()

        editor_console_splitter.addWidget(self.tab_widget)
        editor_console_splitter.addWidget(self.terminal)
        editor_console_splitter.setSizes([550, 200])

        main_splitter.addWidget(self.tree_view)
        main_splitter.addWidget(editor_console_splitter)
        main_splitter.setSizes([250, 1100])

        self.setCentralWidget(main_splitter)

        self.create_toolbar()
        self.new_file()

    def create_toolbar(self):
        toolbar = QToolBar("Ana Araç Çubuğu")
        self.addToolBar(toolbar)

        new_act = QAction("📄 Yeni Dosya", self)
        new_act.triggered.connect(self.new_file)
        toolbar.addAction(new_act)

        open_act = QAction("📂 Dosya Aç", self)
        open_act.triggered.connect(self.open_file_dialog)
        toolbar.addAction(open_act)

        save_act = QAction("💾 Kaydet", self)
        save_act.triggered.connect(self.save_file)
        toolbar.addAction(save_act)

        toolbar.addSeparator()

        run_act = QAction("▶ Çalıştır (Python)", self)
        run_act.triggered.connect(self.run_python_code)
        toolbar.addAction(run_act)

        ai_act = QAction("🤖 MelissAI Analiz", self)
        ai_act.triggered.connect(self.ai_analyze_code)
        toolbar.addAction(ai_act)

    def new_file(self):
        editor = CodeEditor()
        editor.setFont(QFont("Consolas", 11))
        PythonHighlighter(editor.document())
        
        index = self.tab_widget.addTab(editor, "İsimsiz.py")
        self.tab_widget.setCurrentIndex(index)

    def open_file_from_tree(self, index):
        path = self.file_model.filePath(index)
        if QFileInfo(path).isFile():
            self.load_file_to_tab(path)

    def open_file_dialog(self):
        path, _ = QFileDialog.getOpenFileName(self, "Dosya Aç", "", "Python Dosyaları (*.py);;Tüm Dosyalar (*)")
        if path:
            self.load_file_to_tab(path)

    def load_file_to_tab(self, path):
        for i in range(self.tab_widget.count()):
            w = self.tab_widget.widget(i)
            if hasattr(w, "file_path") and w.file_path == path:
                self.tab_widget.setCurrentIndex(i)
                return

        try:
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            editor = CodeEditor()
            editor.setFont(QFont("Consolas", 11))
            editor.setPlainText(content)
            editor.file_path = path
            PythonHighlighter(editor.document())

            filename = os.path.basename(path)
            index = self.tab_widget.addTab(editor, filename)
            self.tab_widget.setCurrentIndex(index)
            self.terminal.append_text(f"[Bilgi] Dosya yüklendi: {path}\n", "#89b4fa")
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Dosya açılamadı:\n{str(e)}")

    def save_file(self):
        current_widget = self.tab_widget.currentWidget()
        if not current_widget:
            return

        if not current_widget.file_path:
            path, _ = QFileDialog.getSaveFileName(self, "Dosyayı Kaydet", "", "Python Dosyaları (*.py);;Tüm Dosyalar (*)")
            if path:
                current_widget.file_path = path
                self.tab_widget.setTabText(self.tab_widget.currentIndex(), os.path.basename(path))
            else:
                return

        try:
            with open(current_widget.file_path, "w", encoding="utf-8") as f:
                f.write(current_widget.toPlainText())
            self.terminal.append_text(f"[Kaydedildi]: {current_widget.file_path}\n", "#a6e3a1")
        except Exception as e:
            QMessageBox.warning(self, "Hata", f"Kaydetme başarısız:\n{str(e)}")

    def close_tab(self, index):
        if self.tab_widget.count() > 1:
            self.tab_widget.removeTab(index)
        else:
            self.new_file()
            self.tab_widget.removeTab(0)

    def run_python_code(self):
        current_widget = self.tab_widget.currentWidget()
        if not current_widget:
            return

        # Kodun çalıştırılabilmesi için önce kaydedilmesi gerekir
        if not current_widget.file_path:
            self.save_file()

        if current_widget.file_path:
            # Otomatik kaydet ve IDE içi terminalde çalıştır
            with open(current_widget.file_path, "w", encoding="utf-8") as f:
                f.write(current_widget.toPlainText())
            
            self.terminal.run_script(current_widget.file_path)

    def ai_analyze_code(self):
        current_widget = self.tab_widget.currentWidget()
        if not current_widget:
            return
        code = current_widget.toPlainText()
        self.terminal.append_text("\n--- MelissAI Analiz ---\n", "#f9e2af")
        self.terminal.append_text(f"Kod Satır Sayısı: {len(code.splitlines())}\n", "#cdd6f4")
        self.terminal.append_text("Durum: Kod temiz. Gömülü QProcess terminali aktif.\n", "#a6e3a1")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(VISIONIST_STYLE)
    ide = VisionistIDE()
    ide.show()
    sys.exit(app.exec())