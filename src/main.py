import sys
from PySide6.QtWidgets import QApplication, QDialog, QListWidget, QVBoxLayout, QLineEdit
from PySide6.QtCore import QTimer, Qt, Signal
from PySide6.QtGui import QKeyEvent
import pyperclip
from pynput import keyboard

class ClipboardManager:
    def __init__(self):
        self.history = []
        self.last_clip = ""
        self.timer = QTimer()
        self.timer.timeout.connect(self.check_clipboard)
        self.timer.start(500)  

    def check_clipboard(self):
        try:
            current = pyperclip.paste()
            if current != self.last_clip and current.strip():
                self.history.insert(0, current)
                self.last_clip = current
                if len(self.history) > 50:  
                    self.history.pop()
        except Exception as e:
            print(f"Error checking clipboard: {e}")

class ClipDialog(QDialog):
    def __init__(self, history):
        super().__init__()
        self.history = history
        self.filtered = history[:]
        self.setWindowTitle("ClipJet")
        self.setModal(True)
        self.resize(600, 400)

        layout = QVBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search clipboard history...")
        self.search.textChanged.connect(self.filter_items)

        self.list_widget = QListWidget()
        self.list_widget.addItems(self.filtered)
        if self.filtered:
            self.list_widget.setCurrentRow(0)

        layout.addWidget(self.search)
        layout.addWidget(self.list_widget)
        self.setLayout(layout)

    def filter_items(self):
        query = self.search.text().lower()
        self.filtered = [item for item in self.history if query in item.lower()]
        self.list_widget.clear()
        self.list_widget.addItems(self.filtered)
        if self.filtered:
            self.list_widget.setCurrentRow(0)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_J:
            current = self.list_widget.currentRow()
            if current < self.list_widget.count() - 1:
                self.list_widget.setCurrentRow(current + 1)
        elif event.key() == Qt.Key.Key_K:
            current = self.list_widget.currentRow()
            if current > 0:
                self.list_widget.setCurrentRow(current - 1)
        elif event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            selected = self.list_widget.currentItem()
            if selected:
                pyperclip.copy(selected.text())
                self.accept()
        elif event.key() == Qt.Key.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)

class ClipJetApp(QApplication):
    show_popup_signal = Signal()

    def __init__(self, *args):
        super().__init__(*args)
        self.show_popup_signal.connect(self.show_popup)
        self.manager = ClipboardManager()
        self.hotkey = keyboard.GlobalHotKeys({'<ctrl>+<shift>+v': self.trigger_popup})
        self.hotkey.start()

    def trigger_popup(self):
        self.show_popup_signal.emit()

    def show_popup(self):
        dialog = ClipDialog(self.manager.history)
        dialog.exec()

if __name__ == "__main__":
    app = ClipJetApp(sys.argv)
    sys.exit(app.exec())