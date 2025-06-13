from PyQt5.QtWidgets import QPushButton, QSizePolicy, QToolTip
from PyQt5.QtCore import QThread, pyqtSignal, pyqtSlot, QSize, QTimer
from PyQt5.QtGui import QIcon, QFont
import logging
import time

logger = logging.getLogger(__name__)

class VoiceWorker(QThread):
    """Worker thread for voice recognition"""
    result_ready = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, stt_engine=None):
        super().__init__()
        self.stt_engine = stt_engine
        self.running = False
    
    def run(self):
        """Run voice recognition in a separate thread"""
        self.running = True
        try:
            if self.stt_engine:
                while self.running:
                    text = self.stt_engine.listen()
                    if text and self.running:
                        self.result_ready.emit(text)
                        break  # Stop after getting one result for inline use
            else:
                logger.error("STT engine not initialized")
                self.error_occurred.emit("STT engine not initialized")
        except Exception as e:
            logger.error(f"Error in voice recognition: {e}")
            self.error_occurred.emit(f"Error: {str(e)}")
        finally:
            self.running = False
    
    def stop(self):
        """Stop the voice recognition thread"""
        self.running = False
        self.wait(1000)  # Wait up to 1 second for thread to finish


class VoicePanel(QPushButton):
    """Enhanced voice input button with theme support"""
    
    voice_input = pyqtSignal(str)
    
    def __init__(self, voice_components=None):
        super().__init__()
        self.stt_engine = voice_components.get('stt') if voice_components else None
        self.listening = False
        self.thread = None
        self.worker = None
        self.is_dark_mode = False
        
        # Animation timer for breathing effect
        self.animation_timer = QTimer()
        self.animation_timer.timeout.connect(self.animate_button)
        self.animation_frame = 0
        
        # Configure button appearance
        self.setup_button_style()
        
        # Connect signals
        self.clicked.connect(self.toggle_listening)
    
    def setup_button_style(self):
        """Setup the button style for inline integration"""
        # Try to load icons, fall back to text if not available
        try:
            self.mic_off_icon = QIcon("ui/assets/mic_off.png")
            self.mic_on_icon = QIcon("ui/assets/mic_recording.png")
            self.has_icons = True
        except:
            # Fall back to emoji-based button if icons are not available
            self.mic_off_icon = None
            self.mic_on_icon = None
            self.has_icons = False
        
        # Button properties
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setMinimumSize(45, 45)
        self.setMaximumSize(45, 45)
        
        # Set initial state
        self.update_button_appearance()
        
        # Apply theme-aware styling
        self.apply_theme_styling()
    
    def apply_theme_styling(self, is_dark_mode=False):
        """Apply theme-specific styling"""
        self.is_dark_mode = is_dark_mode
        
        if is_dark_mode:
            # Dark theme styling
            base_style = """
                QPushButton {
                    border: 2px solid #606060;
                    border-radius: 22px;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #505050, stop:1 #404040);
                    color: #ffffff;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #606060, stop:1 #505050);
                    border-color: #00d4ff;
                    box-shadow: 0 0 10px rgba(0, 212, 255, 0.3);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #404040, stop:1 #303030);
                }
            """
            
            listening_style = """
                QPushButton[listening="true"] {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ff6b6b, stop:1 #ff5252);
                    border-color: #ff4444;
                    color: #ffffff;
                }
                QPushButton[listening="true"]:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ff8080, stop:1 #ff6b6b);
                }
            """
        else:
            # Light theme styling
            base_style = """
                QPushButton {
                    border: 2px solid #d0d0d0;
                    border-radius: 22px;
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ffffff, stop:1 #f0f0f0);
                    color: #333333;
                    font-size: 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #f8f9fa, stop:1 #e9ecef);
                    border-color: #0066cc;
                    box-shadow: 0 0 10px rgba(0, 102, 204, 0.2);
                }
                QPushButton:pressed {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #e9ecef, stop:1 #dee2e6);
                }
            """
            
            listening_style = """
                QPushButton[listening="true"] {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ff6b6b, stop:1 #ff5252);
                    border-color: #ff4444;
                    color: #ffffff;
                }
                QPushButton[listening="true"]:hover {
                    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                        stop:0 #ff8080, stop:1 #ff6b6b);
                }
            """
        
        # Disabled state
        disabled_style = """
            QPushButton:disabled {
                background-color: #cccccc;
                border-color: #aaaaaa;
                color: #666666;
            }
        """
        
        full_style = base_style + listening_style + disabled_style
        self.setStyleSheet(full_style)
    
    def update_button_appearance(self):
        """Update button appearance based on current state"""
        if self.listening:
            if self.has_icons and self.mic_on_icon:
                self.setIcon(self.mic_on_icon)
                self.setIconSize(QSize(24, 24))
                self.setText("")
            else:
                self.setText("⏹️")
            self.setToolTip("Click to stop voice input\n(Currently listening...)")
            self.setProperty("listening", "true")
        else:
            if self.has_icons and self.mic_off_icon:
                self.setIcon(self.mic_off_icon)
                self.setIconSize(QSize(24, 24))
                self.setText("")
            else:
                self.setText("🎤")
            self.setToolTip("Click to start voice input\nSpeak clearly into your microphone")
            self.setProperty("listening", "false")
        
        # Refresh styling
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()
    
    def toggle_listening(self):
        """Toggle between listening and not listening states"""
        if not self.stt_engine:
            self.show_error_tooltip("Voice recognition not available")
            return
            
        if self.listening:
            self.stop_listening()
        else:
            self.start_listening()
    
    def start_listening(self):
        """Start listening for voice input"""
        if self.stt_engine is None:
            logger.warning("No STT engine available")
            self.show_error_tooltip("Speech-to-text engine not initialized")
            return
            
        # Create and start worker thread if not already running
        if not self.thread or not self.thread.isRunning():
            self.thread = QThread()
            self.worker = VoiceWorker(self.stt_engine)
            
            # Move worker to thread
            self.worker.moveToThread(self.thread)
            
            # Connect signals
            self.thread.started.connect(self.worker.run)
            self.worker.result_ready.connect(self.handle_voice_input)
            self.worker.error_occurred.connect(self.handle_error)
            self.worker.finished.connect(self.on_listening_finished)
            
            # Start thread
            self.thread.start()
            
            # Update UI and start animation
            self.listening = True
            self.update_button_appearance()
            self.start_animation()
            
            logger.debug("Started listening for voice input")
    
    def stop_listening(self):
        """Stop listening for voice input"""
        if self.thread and self.thread.isRunning() and self.worker:
            # Stop the worker
            self.worker.stop()
            
            # Wait for thread to finish
            self.thread.quit()
            self.thread.wait(1000)  # Wait up to 1 second
            
            # Update UI and stop animation
            self.listening = False
            self.update_button_appearance()
            self.stop_animation()
            
            logger.debug("Stopped listening for voice input")
    
    def start_animation(self):
        """Start breathing animation while listening"""
        self.animation_timer.start(100)  # Update every 100ms
    
    def stop_animation(self):
        """Stop breathing animation"""
        self.animation_timer.stop()
        self.animation_frame = 0
    
    def animate_button(self):
        """Create breathing effect animation"""
        if self.listening:
            # Create a pulsing effect by varying opacity
            self.animation_frame += 1
            pulse = abs((self.animation_frame % 20) - 10) / 10.0  # 0 to 1 to 0
            opacity = 0.7 + (pulse * 0.3)  # Vary between 0.7 and 1.0
            self.setWindowOpacity(opacity)
    
    def show_error_tooltip(self, message):
        """Show error message as tooltip"""
        QToolTip.showText(self.mapToGlobal(self.rect().center()), message)
    
    @pyqtSlot(str)
    def handle_voice_input(self, text):
        """Handle recognized voice input"""
        if text:
            logger.info(f"Voice input recognized: {text}")
            self.voice_input.emit(text)
            # Auto-stop listening after getting input
            self.stop_listening()
    
    @pyqtSlot()
    def on_listening_finished(self):
        """Handle when listening is finished"""
        self.listening = False
        self.update_button_appearance()
        self.stop_animation()
    
    @pyqtSlot(str)
    def handle_error(self, error_message):
        """Handle errors from voice recognition"""
        logger.error(f"Voice recognition error: {error_message}")
        self.listening = False
        self.update_button_appearance()
        self.stop_animation()
        self.show_error_tooltip(f"Voice Error: {error_message}")

