import sys
import json
import re
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, pyqtSlot

class SiriInterface(QWidget):
    # This is the "secure pipe" to send data to the UI thread
    update_signal = pyqtSignal(str, str, bool)

    def __init__(self):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.ww, self.wh = 600, 160
        self.setFixedSize(self.ww, self.wh)
        
        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width() - self.ww) // 2, screen.height() - 250)

        # Container with Glassmorphism
        self.container = QWidget(self)
        self.container.setFixedSize(self.ww, self.wh)
        self.container.setStyleSheet("""
            QWidget {
                background-color: rgba(25, 25, 25, 230);
                border-radius: 30px;
                border: 1px solid rgba(255, 255, 255, 40);
            }
        """)

        self.label = QLabel("Waiting...", self.container)
        self.label.setGeometry(20, 20, 560, 100)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setStyleSheet("color: white; font-size: 18px; font-weight: bold; background: transparent;")
        
        self.glow_bar = QWidget(self.container)
        self.glow_bar.setGeometry((self.ww - 250) // 2, self.wh - 12, 250, 4)
        
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(250)
        
        # Connect the signal to the safe update function
        self.update_signal.connect(self._safe_update)
        
        self.setWindowOpacity(0.0)
        self.hide()

    @pyqtSlot(str, str, bool)
    def _safe_update(self, message, state, visible):
        """This function runs ONLY on the Main Thread."""
        if visible:
            clean_text = self._parse_text(message)
            self.label.setText(clean_text)
            
            # Update Glow
            colors = {"listening": "#00f2ff", "thinking": "#bd00ff", "responding": "#ffffff"}
            self.glow_bar.setStyleSheet(f"background-color: {colors.get(state, '#ffffff')}; border-radius: 2px;")
            
            if self.isHidden() or self.windowOpacity() < 0.1:
                self.show()
                self.fade_anim.setStartValue(0.0)
                self.fade_anim.setEndValue(1.0)
                self.fade_anim.start()
            self.raise_()
        else:
            self.fade_anim.setStartValue(self.windowOpacity())
            self.fade_anim.setEndValue(0.0)
            self.fade_anim.finished.connect(self.hide)
            self.fade_anim.start()

    def _parse_text(self, message):
        try:
            data = json.loads(message)
            return data.get('content', message)
        except:
            return re.sub(r'\[.*?\]:?', '', message).strip()

    def update_ui(self, message, state="listening", visible=True):
        """Called from the background thread safely."""
        self.update_signal.emit(message, state, visible)