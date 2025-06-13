from PyQt5.QtWidgets import (QMainWindow, QVBoxLayout, QWidget, QSystemTrayIcon, 
                             QMenu, QAction, QProgressBar, QLabel, QHBoxLayout, 
                             QPushButton, QFrame)
from PyQt5.QtCore import Qt, QSize, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QMovie, QFont, QPalette, QColor
from ui.windows.chat_panel import ChatPanel
from ui.windows.voice_panel import VoicePanel
import logging

logger = logging.getLogger(__name__)

class MainWindow(QMainWindow):
    """Main application window for Aurix AI Assistant"""
    
    theme_changed = pyqtSignal(bool)  # Signal for theme changes
    
    def __init__(self, ollama_manager, voice_components, config):
        super().__init__()
        self.ollama_manager = ollama_manager
        self.voice_components = voice_components
        self.config = config
        self.dark_mode = False
        
        # Set window properties
        self.setWindowTitle("Aurix - AI Desktop Assistant")
        self.setMinimumSize(900, 700)
        
        # Set window icon if available
        try:
            self.setWindowIcon(QIcon("ui/assets/app_icon.ico"))
        except:
            logger.warning("App icon not found: ui/assets/app_icon.ico")
        
        # Initialize UI
        self.init_ui()
        
        # Create system tray icon
        self.create_tray_icon()
        
        # Apply UI settings from config
        self.apply_ui_settings()
        
        # Apply initial theme
        self.apply_theme()
    
    def init_ui(self):
        """Initialize the user interface"""
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create header
        self.create_header()
        main_layout.addWidget(self.header_frame)
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setObjectName("headerSeparator")
        main_layout.addWidget(separator)
        
        # Add chat panel with integrated voice support
        self.chat_panel = ChatPanel(self.ollama_manager, self.voice_components, self)
        main_layout.addWidget(self.chat_panel)
        
        # Create loading overlay
        self.create_loading_overlay()
    
    def create_header(self):
        """Create the header with branding and controls"""
        self.header_frame = QFrame()
        self.header_frame.setObjectName("headerFrame")
        self.header_frame.setFixedHeight(60)
        
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(15, 10, 15, 10)
        
        # Aurix branding
        brand_layout = QHBoxLayout()
        
        # Logo/Icon (if available)
        try:
            logo_label = QLabel()
            logo_pixmap = QIcon("ui/assets/aurix_logo.png").pixmap(32, 32)
            logo_label.setPixmap(logo_pixmap)
            brand_layout.addWidget(logo_label)
        except:
            pass
        
        # App name and tagline
        title_layout = QVBoxLayout()
        title_layout.setSpacing(0)
        
        app_title = QLabel("Aurix")
        app_title.setObjectName("appTitle")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        app_title.setFont(title_font)
        
        tagline = QLabel("AI Desktop Assistant")
        tagline.setObjectName("tagline")
        tagline_font = QFont()
        tagline_font.setPointSize(10)
        tagline.setFont(tagline_font)
        
        title_layout.addWidget(app_title)
        title_layout.addWidget(tagline)
        
        brand_layout.addLayout(title_layout)
        header_layout.addLayout(brand_layout)
        
        # Spacer
        header_layout.addStretch()
    
    def toggle_theme(self):
        """Toggle between dark and light themes"""
        self.dark_mode = not self.dark_mode
        self.apply_theme()
        self.update_theme_icon()
        self.theme_changed.emit(self.dark_mode)
    
    def update_theme_icon(self):
        """Update the theme toggle button icon"""
        if self.dark_mode:
            self.theme_button.setIcon(QIcon("ui/assets/light_mode.png"))
        else:
            self.theme_button.setIcon(QIcon("ui/assets/dark_mode.png"))
    
    def apply_theme(self):
        # """Apply the current theme"""
        # if self.dark_mode:
        #     self.apply_dark_theme()
        # else:
        self.apply_light_theme()
    
    # def apply_dark_theme(self):
    #     """Apply dark theme styling"""
    #     dark_stylesheet = """
    #         QMainWindow {
    #             background-color: #2b2b2b;
    #             color: #ffffff;  /* Ensure default text color is white */
    #         }
            
    #         #headerFrame {
    #             background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
    #                 stop:0 #3d3d3d, stop:1 #4a4a4a);
    #             border-bottom: 1px solid #555555;
    #         }
            
    #         #appTitle {
    #             color: #00d4ff;
    #             background: transparent;
    #         }
            
    #         #tagline {
    #             color: #cccccc;
    #             background: transparent;
    #         }
            
    #         #themeButton {
    #             background-color: #404040;
    #             border: 1px solid #606060;
    #             border-radius: 15px;
    #             color: #ffffff;
    #             font-size: 14px;
    #         }
            
    #         #themeButton:hover {
    #             background-color: #505050;
    #             border-color: #00d4ff;
    #         }
            
    #         #controlButton {
    #             background-color: #404040;
    #             border: 1px solid #606060;
    #             border-radius: 15px;
    #             color: #ffffff;
    #             font-weight: bold;
    #             font-size: 14px;
    #         }
            
    #         #controlButton:hover {
    #             background-color: #ff6b6b;
    #             border-color: #ff5252;
    #         }
            
    #         #headerSeparator {
    #             color: #555555;
    #         }
            
    #         QTextEdit {
    #             background-color: #363636;
    #             color: #ffffff;  /* Ensure text color is white */
    #             border: 1px solid #555555;
    #             border-radius: 8px;
    #             padding: 10px;
    #             font-size: 14px;
    #             selection-background-color: #00d4ff;
    #         }
            
    #         QLineEdit {
    #             background-color: #404040;
    #             color: #ffffff;  /* Ensure text color is white */
    #             border: 2px solid #606060;
    #             border-radius: 20px;
    #             padding: 8px 15px;
    #             font-size: 14px;
    #         }
            
    #         QLineEdit:focus {
    #             border-color: #00d4ff;
    #         }
            
    #         QPushButton {
    #             background-color: #00d4ff;
    #             color: #000000;
    #             border: none;
    #             border-radius: 20px;
    #             padding: 8px 20px;
    #             font-weight: bold;
    #             font-size: 14px;
    #         }
            
    #         QPushButton:hover {
    #             background-color: #00b8e6;
    #         }
            
    #         QPushButton:pressed {
    #             background-color: #0099cc;
    #         }
            
    #         #loadingOverlay {
    #             background-color: rgba(43, 43, 43, 200);
    #             color: #ffffff;  /* Ensure text color is white */
    #             border-radius: 15px;
    #         }
    #     """
    #     self.setStyleSheet(dark_stylesheet)
    
    def apply_light_theme(self):
        """Apply light theme styling"""
        light_stylesheet = """
            QMainWindow {
                background-color: #ffffff;
                color: #333333;
            }
            
            #headerFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f8f9fa, stop:1 #e9ecef);
                border-bottom: 1px solid #dee2e6;
            }
            
            #appTitle {
                color: #0066cc;
                background: transparent;
            }
            
            #tagline {
                color: #666666;
                background: transparent;
            }
            
            #themeButton {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 15px;
                color: #333333;
                font-size: 14px;
            }
            
            #themeButton:hover {
                background-color: #e9ecef;
                border-color: #0066cc;
            }
            
            #controlButton {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 15px;
                color: #333333;
                font-weight: bold;
                font-size: 14px;
            }
            
            #controlButton:hover {
                background-color: #ff6b6b;
                border-color: #ff5252;
                color: #ffffff;
            }
            
            #headerSeparator {
                color: #dee2e6;
            }
            
            QTextEdit {
                background-color: #ffffff;
                color: #333333;
                border: 1px solid #dee2e6;
                border-radius: 8px;
                padding: 10px;
                font-size: 14px;
                selection-background-color: #0066cc;
            }
            
            QLineEdit {
                background-color: #ffffff;
                color: #333333;
                border: 2px solid #dee2e6;
                border-radius: 20px;
                padding: 8px 15px;
                font-size: 14px;
            }
            
            QLineEdit:focus {
                border-color: #0066cc;
            }
            
            QPushButton {
                background-color: #0066cc;
                color: #ffffff;
                border: none;
                border-radius: 20px;
                padding: 8px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            
            QPushButton:hover {
                background-color: #0052a3;
            }
            
            QPushButton:pressed {
                background-color: #003d7a;
            }
            
            #loadingOverlay {
                background-color: rgba(255, 255, 255, 220);
                color: #333333;
                border-radius: 15px;
            }
        """
        self.setStyleSheet(light_stylesheet)
    

    def create_loading_overlay(self):
        """Create a sophisticated loading overlay"""
        self.loading_overlay = QWidget(self)
        self.loading_overlay.setObjectName("loadingOverlay")
        self.loading_overlay.resize(250, 120)
        self.loading_overlay.hide()
        
        overlay_layout = QVBoxLayout(self.loading_overlay)
        overlay_layout.setSpacing(15)
        overlay_layout.setAlignment(Qt.AlignCenter)
        
        # Loading animation (try to use GIF, fallback to progress bar)
        self.loading_animation = QLabel()
        self.loading_animation.setAlignment(Qt.AlignCenter)
        
        try:
            # Try to load animated GIF
            self.loading_movie = QMovie("ui/assets/loading_spinner.gif")
            if self.loading_movie.isValid():
                self.loading_movie.setScaledSize(QSize(60, 60))
                self.loading_animation.setMovie(self.loading_movie)
            else:
                raise FileNotFoundError
        except:
            # Fallback to progress bar with animation
            self.loading_progress = QProgressBar()
            self.loading_progress.setRange(0, 0)  # Indeterminate progress
            self.loading_progress.setFixedSize(200, 8)
            self.loading_progress.setStyleSheet("""
                QProgressBar {
                    border: none;
                    border-radius: 4px;
                    background-color: rgba(200, 200, 200, 100);
                }
                QProgressBar::chunk {
                    border-radius: 4px;
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #00d4ff, stop:1 #0066cc);
                }
            """)
            overlay_layout.addWidget(self.loading_progress)
        
        if hasattr(self, 'loading_movie'):
            overlay_layout.addWidget(self.loading_animation)
        
        # Loading text with animated dots
        self.loading_text = QLabel("Aurix is thinking")
        self.loading_text.setAlignment(Qt.AlignCenter)
        self.loading_text.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                padding: 10px;
            }
        """)
        overlay_layout.addWidget(self.loading_text)
        
        # Animated dots timer
        self.dots_timer = QTimer()
        self.dots_timer.timeout.connect(self.animate_loading_text)
        self.dots_count = 0
    
    def animate_loading_text(self):
        """Animate the loading text with dots"""
        dots = "." * (self.dots_count % 4)
        self.loading_text.setText(f"Aurix is thinking{dots}")
        self.dots_count += 1
    
    def show_loading(self):
        """Show the loading overlay with animation"""
        if hasattr(self, 'loading_overlay'):
            # Position overlay in center
            self.loading_overlay.move(
                (self.width() - self.loading_overlay.width()) // 2,
                (self.height() - self.loading_overlay.height()) // 2
            )
            
            # Start animations
            if hasattr(self, 'loading_movie'):
                self.loading_movie.start()
            
            self.dots_timer.start(500)  # Update every 500ms
            
            # Show overlay
            self.loading_overlay.show()
            self.loading_overlay.raise_()
    
    def hide_loading(self):
        """Hide the loading overlay"""
        if hasattr(self, 'loading_overlay'):
            # Stop animations
            if hasattr(self, 'loading_movie'):
                self.loading_movie.stop()
            
            self.dots_timer.stop()
            
            # Hide overlay
            self.loading_overlay.hide()
    
    def create_tray_icon(self):
        """Create system tray icon and menu"""
        try:
            self.tray_icon = QSystemTrayIcon(self)
            
            # Set icon
            try:
                self.tray_icon.setIcon(QIcon("ui/assets/app_icon.ico"))
            except:
                logger.warning("Tray icon not found: ui/assets/app_icon.ico")
            
            # Create tray menu
            tray_menu = QMenu()
            
            # Add actions
            show_action = QAction("Show Aurix", self)
            show_action.triggered.connect(self.show)
            tray_menu.addAction(show_action)
            
            hide_action = QAction("Hide", self)
            hide_action.triggered.connect(self.hide)
            tray_menu.addAction(hide_action)
            
            tray_menu.addSeparator()
            
            # Theme toggle in tray
            theme_action = QAction("Toggle Dark Mode", self)
            theme_action.triggered.connect(self.toggle_theme)
            tray_menu.addAction(theme_action)
            
            tray_menu.addSeparator()
            
            exit_action = QAction("Exit", self)
            exit_action.triggered.connect(self.close)
            tray_menu.addAction(exit_action)
            
            # Set context menu
            self.tray_icon.setContextMenu(tray_menu)
            self.tray_icon.setToolTip("Aurix - AI Desktop Assistant")
            
            # Show icon
            self.tray_icon.show()
            
            # Connect signal for tray icon activation
            self.tray_icon.activated.connect(self.tray_icon_activated)
            
            logger.debug("System tray icon created")
        except Exception as e:
            logger.error(f"Failed to create system tray icon: {e}")
    
    def tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.DoubleClick:
            if self.isVisible():
                self.hide()
            else:
                self.show()
                self.activateWindow()
    
    def apply_ui_settings(self):
        """Apply UI settings from config"""
        try:
            ui_config = self.config.get('ui', {})
            
            # Set theme from config
            theme = ui_config.get('theme', 'light')
            if theme == 'dark':
                self.dark_mode = True
            
            # Set opacity
            opacity = ui_config.get('opacity', 0.95)
            self.setWindowOpacity(opacity)
            
            # Set always on top
            always_on_top = ui_config.get('always_on_top', False)
            if always_on_top:
                self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
            
            # Set start minimized
            start_minimized = ui_config.get('start_minimized', False)
            if start_minimized:
                self.showMinimized()
            
            logger.debug("Applied UI settings")
        except Exception as e:
            logger.error(f"Failed to apply UI settings: {e}")
    
    def show_notification(self, title, message):
        """Show system notification"""
        try:
            if hasattr(self, 'tray_icon') and self.tray_icon.isSystemTrayAvailable():
                self.tray_icon.showMessage(title, message, QSystemTrayIcon.Information, 5000)
                logger.debug(f"Showing notification: {title} - {message}")
            else:
                logger.warning("System tray not available for notifications")
        except Exception as e:
            logger.error(f"Failed to show notification: {e}")
    
    def resizeEvent(self, event):
        """Handle window resize event to reposition loading overlay"""
        super().resizeEvent(event)
        if hasattr(self, 'loading_overlay') and self.loading_overlay.isVisible():
            self.loading_overlay.move(
                (self.width() - self.loading_overlay.width()) // 2,
                (self.height() - self.loading_overlay.height()) // 2
            )
    
    def closeEvent(self, event):
        """Handle window close event"""
        event.ignore()
        self.hide()
        self.show_notification("Aurix", "Application minimized to tray")