from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QLineEdit, QPushButton, QFrame, QScrollArea, QLabel)
from PyQt5.QtCore import QThread, pyqtSignal, QObject, Qt, QDateTime
from PyQt5.QtGui import QIcon, QFont, QTextCharFormat, QTextCursor
from core.utils.helpers import truncate_string
from ui.windows.voice_panel import VoicePanel
import re
import logging

logger = logging.getLogger(__name__)

class ResponseWorker(QObject):
    finished = pyqtSignal(str)

    def __init__(self, ollama_manager, user_input):
        super().__init__()
        self.ollama_manager = ollama_manager
        self.user_input = user_input

    def run(self):
        response = self.ollama_manager.generate_response(self.user_input)
        self.finished.emit(response)

class ChatPanel(QWidget):
    def __init__(self, ollama_manager, voice_components=None, parent=None):
        super().__init__(parent)
        self.ollama_manager = ollama_manager
        self.voice_components = voice_components
        self.parent_window = parent
        self.message_count = 0
        
        # Connect to theme changes if parent supports it
        if hasattr(parent, 'theme_changed'):
            parent.theme_changed.connect(self.on_theme_changed)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup the user interface"""
        layout = QVBoxLayout()
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Chat display area with custom styling
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setObjectName("chatDisplay")
        
        # Set font for better readability
        font = QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(11)
        self.chat_display.setFont(font)
        
        # Custom scrollbar styling will be handled by the main theme
        layout.addWidget(self.chat_display)
        
        # Input area with enhanced styling
        input_container = QFrame()
        input_container.setObjectName("inputContainer")
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(10, 10, 10, 10)
        input_layout.setSpacing(10)
        
        # Text input field
        self.input_field = QLineEdit()
        self.input_field.setObjectName("messageInput")
        self.input_field.setPlaceholderText("Ask Aurix anything...")
        self.input_field.returnPressed.connect(self.send_message)
        self.input_field.setMinimumHeight(45)
        input_layout.addWidget(self.input_field)
        
        # Voice button (if voice components are available)
        if self.voice_components and 'stt' in self.voice_components:
            self.voice_panel = VoicePanel(self.voice_components)
            self.voice_panel.voice_input.connect(self.handle_voice_input)
            input_layout.addWidget(self.voice_panel)
        
        # Send button with enhanced styling
        self.send_button = QPushButton("Send")
        self.send_button.setObjectName("sendButton")
        self.send_button.clicked.connect(self.send_message)
        self.send_button.setMinimumSize(80, 45)
        input_layout.addWidget(self.send_button)
        
        # Clear button
        self.clear_button = QPushButton("Clear")
        self.clear_button.setObjectName("clearButton")
        self.clear_button.clicked.connect(self.clear_chat)
        self.clear_button.setMinimumSize(80, 45)
        input_layout.addWidget(self.clear_button)
        
        layout.addWidget(input_container)
        self.setLayout(layout)
        
        # Add welcome message
        self.add_welcome_message()
    
    def add_welcome_message(self):
        """Add a welcome message when the chat starts"""
        welcome_html = self.create_message_html(
            "Hello! I'm Aurix, your AI desktop assistant. How can I help you today?",
            "Aurix",
            is_user=False,
            is_welcome=True
        )
        self.chat_display.insertHtml(welcome_html)
        self.scroll_to_bottom()
    
    def create_message_html(self, message, sender, is_user=True, is_welcome=False):
        """Create formatted HTML for a message"""
        self.message_count += 1
        timestamp = QDateTime.currentDateTime().toString("hh:mm")
        
        # Color scheme (will be overridden by theme)
        if is_user:
            bubble_class = "user-message"
            alignment = "right"
            sender_color = "#0066cc"
        else:
            bubble_class = "assistant-message"
            alignment = "left" 
            sender_color = "#00d4ff" if not is_welcome else "#ff6b6b"
        
        # Format message content (preserve line breaks)
        formatted_message = message.replace('\n', '<br>')
        
        html = f"""
        <div style="margin: 10px 0; padding: 8px; text-align: {alignment};">
            <div style="display: inline-block; max-width: 70%; text-align: left;">
                <div style="
                    background: {'#f0f8ff' if is_user else ('#fff5f5' if is_welcome else '#f8f9fa')};
                    border: 1px solid {'#0066cc' if is_user else ('#ff6b6b' if is_welcome else '#00d4ff')};
                    border-radius: 18px;
                    padding: 12px 16px;
                    margin: 5px 0;
                    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
                ">
                    <div style="
                        font-weight: bold; 
                        color: {sender_color}; 
                        font-size: 12px; 
                        margin-bottom: 5px;
                    ">
                        {sender}
                    </div>
                    <div style="color: #333; line-height: 1.4; word-wrap: break-word;">
                        {formatted_message}
                    </div>
                    <div style="
                        font-size: 10px; 
                        color: #888; 
                        text-align: right; 
                        margin-top: 5px;
                    ">
                        {timestamp}
                    </div>
                </div>
            </div>
        </div>
        """
        
        return html
    
    def handle_voice_input(self, text):
        """Handle voice input from the integrated voice panel"""
        if text:
            logger.info(f"Voice input received: {text}")
            # Clean the voice input
            cleaned_text = text.replace("<think>", "").replace("</think>", "").strip()
            
            # Set the text in the input field
            self.input_field.setText(cleaned_text)
            
            # Optionally auto-send the voice input
            # Uncomment the next line if you want voice input to be sent automatically
            # self.send_message()
    
    def process_ai_response(self, response):
        """Process AI response to remove <think> tags"""
        response = re.sub(r"<think>.*?</think>", "", response, flags=re.DOTALL)
        return response.strip()
    
    def send_message(self):
        """Send a message and get AI response"""
        user_input = self.input_field.text().strip()
        if not user_input:
            return
    
        # Display user message
        user_html = self.create_message_html(user_input, "You", is_user=True)
        self.chat_display.insertHtml(user_html)
        self.scroll_to_bottom()
        
        # Clear input field
        self.input_field.clear()
        
        # Check for close application commands
        if hasattr(self.parent_window, 'app_launcher'):
            close_patterns = ["close ", "terminate ", "exit ", "quit "]
            input_lower = user_input.lower()
            
            for pattern in close_patterns:
                if input_lower.startswith(pattern):
                    app_name = input_lower[len(pattern):].strip()
                    if app_name:
                        # Process the close command directly
                        response = self.parent_window.app_launcher.close_app(app_name)
                        self.display_ai_response(response)
                        return
        
        # Disable input while processing
        self.set_input_enabled(False)
    
        # Show loading indicator
        if hasattr(self.parent_window, 'show_loading'):
            self.parent_window.show_loading()
    
        # Create worker thread
        self.thread = QThread()
        self.worker = ResponseWorker(self.ollama_manager, user_input)
        self.worker.moveToThread(self.thread)
    
        # Connect signals
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self.display_ai_response)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
    
        # Start thread
        self.thread.start()

    def display_ai_response(self, response):
        """Display AI response in the chat"""
        # Process the response
        cleaned_response = self.process_ai_response(response)
        
        # Create and display message
        assistant_html = self.create_message_html(cleaned_response, "Aurix", is_user=False)
        self.chat_display.insertHtml(assistant_html)
        self.scroll_to_bottom()
        
        # Re-enable input
        self.set_input_enabled(True)
        
        # Focus back to input field
        self.input_field.setFocus()

        # Hide loading indicator
        if hasattr(self.parent_window, 'hide_loading'):
            self.parent_window.hide_loading()
    
    def set_input_enabled(self, enabled):
        """Enable or disable input controls"""
        self.input_field.setEnabled(enabled)
        self.send_button.setEnabled(enabled)
        if hasattr(self, 'voice_panel'):
            self.voice_panel.setEnabled(enabled)
    
    def scroll_to_bottom(self):
        """Scroll chat display to bottom"""
        scrollbar = self.chat_display.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def on_theme_changed(self, is_dark_mode):
        """Handle theme changes"""
        # if is_dark_mode:
        #     self.apply_dark_chat_theme()
        # else:
        self.apply_light_chat_theme()
    
    # def apply_dark_chat_theme(self):
    #     """Apply dark theme to chat elements"""
    #     dark_chat_style = """
    #         #chatDisplay {
    #             background-color: #2d2d2d;
    #             color: #ffffff;  /* Ensure text color is white */
    #             border: 1px solid #555555;
    #             border-radius: 10px;
    #             padding: 10px;
    #             selection-background-color: #00d4ff;
    #         }
            
    #         #inputContainer {
    #             background-color: #363636;
    #             border: 1px solid #555555;
    #             border-radius: 25px;
    #             padding: 5px;
    #         }
            
    #         #messageInput {
    #             background-color: #404040;
    #             color: #ffffff;  /* Ensure text color is white */
    #             border: 2px solid #606060;
    #             border-radius: 20px;
    #             padding: 10px 15px;
    #             font-size: 14px;
    #         }
            
    #         #messageInput:focus {
    #             border-color: #00d4ff;
    #             background-color: #4a4a4a;
    #         }
            
    #         #sendButton {
    #             background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
    #                 stop:0 #00d4ff, stop:1 #0099cc);
    #             color: #ffffff;  /* Ensure button text color is white */
    #             border: none;
    #             border-radius: 20px;
    #             font-weight: bold;
    #             font-size: 14px;
    #         }
            
    #         #sendButton:hover {
    #             background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
    #                 stop:0 #00b8e6, stop:1 #0088bb);
    #         }
            
    #         #sendButton:pressed {
    #             background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
    #                 stop:0 #0099cc, stop:1 #0077aa);
    #         }
            
    #         #sendButton:disabled {
    #             background-color: #666666;
    #             color: #999999;
    #         }
    #     """
        
    #     self.setStyleSheet(dark_chat_style)
    #     self.update_message_bubbles_theme(True)
    
    def apply_light_chat_theme(self):
        """Apply light theme to chat elements"""
        light_chat_style = """
            #chatDisplay {
                background-color: #ffffff;
                color: #333333;  /* Ensure text color is dark */
                border: 1px solid #e0e0e0;
                border-radius: 10px;
                padding: 10px;
                selection-background-color: #0066cc;
            }
            
            #inputContainer {
                background-color: #fafafa;
                border: 1px solid #e0e0e0;
                border-radius: 25px;
                padding: 5px;
            }
            
            #messageInput {
                background-color: #ffffff;
                color: #333333;  /* Ensure text color is dark */
                border: 2px solid #e0e0e0;
                border-radius: 20px;
                padding: 10px 15px;
                font-size: 14px;
            }
            
            #messageInput:focus {
                border-color: #0066cc;
                background-color: #f8f9fa;
            }
            
            #sendButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0066cc, stop:1 #004499);
                color: #ffffff;
                border: none;
                border-radius: 20px;
                font-weight: bold;
                font-size: 14px;
            }
            
            #sendButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #0052a3, stop:1 #003366);
            }
            
            #sendButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #004499, stop:1 #002255);
            }
            
            #sendButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """
        
        self.setStyleSheet(light_chat_style)
        self.update_message_bubbles_theme(False)
    
    def update_message_bubbles_theme(self, is_dark):
        """Update existing message bubbles to match current theme"""
        # This would require re-rendering all messages with new colors
        # For now, new messages will use the current theme
        # A full implementation would store messages and re-render them
        pass
    
    def clear_chat(self):
        """Clear all messages from chat"""
        self.chat_display.clear()
        self.message_count = 0
        self.add_welcome_message()
    
    def export_chat(self):
        """Export chat history to text file"""
        try:
            chat_content = self.chat_display.toPlainText()
            timestamp = QDateTime.currentDateTime().toString("yyyy-MM-dd_hh-mm-ss")
            filename = f"aurix_chat_{timestamp}.txt"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"Aurix Chat Export - {QDateTime.currentDateTime().toString()}\n")
                f.write("=" * 50 + "\n\n")
                f.write(chat_content)
            
            logger.info(f"Chat exported to {filename}")
            return filename
        except Exception as e:
            logger.error(f"Failed to export chat: {e}")
            return None