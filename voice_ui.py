import sys
import json
import re
from PyQt6.QtWidgets import QWidget, QLabel, QApplication
from PyQt6.QtCore import Qt, QPropertyAnimation, QEasingCurve, pyqtSignal, pyqtSlot

class SiriInterface(QWidget):
    # Signal to safely communicate between background thread and UI thread
    update_signal = pyqtSignal(str, str, bool)

    def __init__(self):
        super().__init__()
        # Frameless, Always on Top, and Hidden from Dock
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | 
                            Qt.WindowType.WindowStaysOnTopHint | 
                            Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # UI Dimensions
        self.ww, self.wh = 600, 160
        self.setFixedSize(self.ww, self.wh)
        
        # Position: Center Bottom
        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width() - self.ww) // 2, screen.height() - 220)

        # Main Styled Container
        self.container = QWidget(self)
        self.container.setFixedSize(self.ww, self.wh)
        self.container.setStyleSheet("""
            QWidget {
                background-color: rgba(25, 25, 25, 235);
                border-radius: 30px;
                border: 1px solid rgba(255, 255, 255, 45);
            }
        """)

        # Response/Status Label
        self.label = QLabel("Waiting...", self.container)
        self.label.setGeometry(30, 20, 540, 100)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setStyleSheet("""
            color: white; 
            font-family: 'SF Pro Display', 'Helvetica Neue';
            font-size: 19px; 
            font-weight: bold; 
            background: transparent;
        """)
        
        # Bottom Glow Bar
        self.glow_bar = QWidget(self.container)
        self.glow_bar.setGeometry((self.ww - 260) // 2, self.wh - 12, 260, 4)
        
        # Animation for Smooth Transitions
        self.fade_anim = QPropertyAnimation(self, b"windowOpacity")
        self.fade_anim.setDuration(250)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.OutQuad)
        
        # Connect Signal
        self.update_signal.connect(self._safe_update)
        
        # Set initial state (Hidden but active)
        self.setWindowOpacity(0.0)
        self.show()

    @pyqtSlot(str, str, bool)
    def _safe_update(self, message, state, visible):
        """Processes UI changes on the Main Thread."""
        if visible:
            # Parse text if it's JSON from the agent
            try:
                data = json.loads(message)
                clean_text = data.get('content', message)
            except:
                clean_text = re.sub(r'\[.*?\]:?', '', message).strip()
            
            self.label.setText(clean_text)
            
            # Update Glow Colors
            colors = {"listening": "#00f2ff", "thinking": "#bd00ff", "responding": "#ffffff"}
            self.glow_bar.setStyleSheet(f"background-color: {colors.get(state, '#ffffff')}; border-radius: 2px;")
            
            # Trigger Fade In
            self.fade_anim.stop()
            self.fade_anim.setStartValue(self.windowOpacity())
            self.fade_anim.setEndValue(1.0)
            self.fade_anim.start()
            self.raise_()
        else:
            # Trigger Fade Out
            self.fade_anim.stop()
            self.fade_anim.setStartValue(self.windowOpacity())
            self.fade_anim.setEndValue(0.0)
            self.fade_anim.start()

    def update_ui(self, message, state="listening", visible=True):
        """Public method to call from voice thread."""
        self.update_signal.emit(message, state, visible)