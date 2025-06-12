import os
import sys
import logging
import argparse
from pathlib import Path
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from core.ai.model_selector import ModelSelector
from core.ai.ollama_manager import OllamaManager
from ui.windows.main_window import MainWindow
from core.utils.config_loader import ConfigLoader
from core.voice.stt_engine import STTEngine
from core.utils.logger import setup_logger
from core.voice.tts_engine import TTSEngine
from core.voice.wake_word import WakeWordDetector

# Add project root to path to allow imports
project_root = Path(__file__).parent.absolute()
sys.path.append(str(project_root))

# Initialize logger
logger = logging.getLogger(__name__)

# Global variables
tts_engine = None
main_window = None

def reminder_callback(message):
    logger.info(f"Reminder triggered: {message}")
    global tts_engine, main_window
    if tts_engine:
        tts_engine.speak(f"Reminder: {message}")
    if main_window:
        main_window.show_notification("Aurix Reminder", message)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Aurix - AI Desktop Assistant')
    parser.add_argument('--config', type=str, default='config.yaml',
                        help='Path to configuration file')
    parser.add_argument('--no-voice', action='store_true',
                        help='Disable voice interaction')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug logging')
    parser.add_argument('--headless', action='store_true',
                        help='Run without GUI (command-line only)')
    parser.add_argument('--dark-mode', action='store_true',
                        help='Start in dark mode')
    return parser.parse_args()

def validate_input(user_input):
    """Validate and sanitize user input"""
    # Remove any potential command injection characters
    sanitized_input = ''.join(char for char in user_input if char.isalnum() or char.isspace() or char in '.,!?-')
    # Limit input length
    return sanitized_input[:1000]  # Adjust the length limit as needed

def setup_application():
    """Setup the QApplication with proper attributes"""
    # Enable high DPI support
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Aurix")
    app.setApplicationDisplayName("Aurix - AI Desktop Assistant")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Aurix AI")
    
    # Set application icon
    try:
        app.setWindowIcon(QIcon("ui/assets/app_icon.ico"))
    except:
        logger.warning("Application icon not found")
    
    return app
def process_close_command(user_input, app_launcher):
    """Process application close commands"""
    # Check for close/terminate/exit/quit app commands
    input_lower = user_input.lower()
    
    # Match patterns like "close word", "terminate excel", "exit chrome", "quit notepad"
    close_patterns = ["close ", "terminate ", "exit ", "quit "]
    
    for pattern in close_patterns:
        if input_lower.startswith(pattern):
            app_name = input_lower[len(pattern):].strip()
            if app_name:
                logger.info(f"Attempting to close application: {app_name}")
                try:
                    return app_launcher.close_app(app_name)
                except Exception as e:
                    logger.error(f"Error closing application {app_name}: {e}")
                    return f"Sorry, I couldn't close {app_name}. Error: {str(e)}"
    
    return None

def print_banner():
    """Print application banner"""
    banner = """
    ╔═══════════════════════════════════════════════════════════════════════════════╗
    ║                                                                               ║
    ║      █████╗ ██╗   ██╗██████╗ ██╗██╗  ██╗    ██╗  ██╗████████╗                 ║
    ║     ██╔══██╗██║   ██║██╔══██╗██║██║  ██║    ██║  ██║╚══██╔══╝                 ║
    ║     ███████║██║   ██║██████╔╝██║███╗██╔╝    ███████║   ██║                    ║
    ║     ██╔══██║██║   ██║██╔══██╗██║██╔╝██║     ██╔══██║   ██║                    ║
    ║     ██║  ██║╚██████╔╝██║  ██║██║██║  ██║    ██║  ██║   ██║                    ║
    ║     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═╝╚═╝╚═╝  ╚═╝    ╚═╝  ╚═╝   ╚═╝                    ║
    ║                                                                               ║
    ║                     🤖 AI Desktop Assistant 🤖                                ║
    ║                                                                               ║
    ║                    Your Intelligent Digital Companion                         ║
    ║                                                                               ║
    ╚═══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)

def main():
    """Main application entry point."""
    global tts_engine, main_window
    
    # Print banner
    print_banner()
    
    args = parse_arguments()
    
    # Setup logging
    log_level = logging.DEBUG if args.debug else logging.INFO
    setup_logger(log_level)
    logger.info("🚀 Starting Aurix AI Desktop Assistant...")
    
    # Load configuration
    config_path = Path(args.config)
    config = ConfigLoader(config_path).load()
    logger.debug(f"✅ Loaded configuration from {config_path}")
    
    # Apply dark mode from command line argument
    if args.dark_mode:
        config.setdefault('ui', {})['theme'] = 'dark'
    
    # Initialize AI models
    ai_model = None
    try:
        model_selector = ModelSelector(config['ai'], reminder_callback)
        primary_model = model_selector.get_primary_model()
        fallback_model = model_selector.get_fallback_model()
        
        if primary_model:
            logger.info(f"🧠 Using primary AI model: {primary_model.model_name}")
            ai_model = primary_model
        elif fallback_model:
            logger.info(f"🔄 Using fallback AI model: {fallback_model.model_name}")
            ai_model = fallback_model
        else:
            logger.error("❌ No AI models available")
    except Exception as e:
        logger.error(f"❌ Failed to initialize AI models: {e}")

    # Initialize Ollama Manager with reminder callback
    ollama_manager = None
    try:
        ollama_manager = OllamaManager(config['ai'], reminder_callback)
        logger.info("✅ Ollama manager initialized successfully")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Ollama manager: {e}")
    
    # Initialize voice components if enabled
    voice_components = None
    if not args.no_voice:
        try:
            logger.info("🎤 Initializing voice components...")
            stt = STTEngine(config['voice']['stt'])
            tts_engine = TTSEngine(config['voice']['tts'])
            wake_word = WakeWordDetector(config['voice']['wake_word'])
            voice_components = {
                'stt': stt,
                'tts': tts_engine,
                'wake_word': wake_word
            }
            logger.info("🎵 Voice components initialized successfully")
        except ImportError as ie:
            logger.error(f"❌ Failed to import voice component: {ie}")
            logger.warning("⚠️  Make sure all required packages are installed")
        except Exception as e:
            logger.error(f"❌ Failed to initialize voice components: {e}")
        
        if not voice_components:
            logger.warning("⚠️  Continuing without voice interaction")

    # Start UI or run in headless mode
    if not args.headless:
        logger.info("🖥️  Starting GUI mode...")
        
        # Setup application
        app = setup_application()
        
        # Create main window
        main_window = MainWindow(ollama_manager or ai_model, voice_components, config)
        
        # Show window
        main_window.show()
        
        # Show startup notification
        main_window.show_notification(
            "Aurix Started", 
            "Your AI assistant is ready to help!"
        )
        
        logger.info("✅ Aurix GUI started successfully")
        
        # Run application
        sys.exit(app.exec_())
    else:
        # Headless mode - command line interaction
        logger.info("💻 Running in headless mode")
        print("\n🤖 Aurix AI Assistant (Console Mode)")
        print("Type 'exit' or 'quit' to terminate")
        print("Type 'help' for available commands")
        print("-" * 50)
        
        # Initialize app launcher for close commands
        try:
            from core.automation.app_launcher import AppLauncher
            app_launcher = AppLauncher()
        except Exception as e:
            logger.error(f"Failed to initialize AppLauncher: {e}")
            app_launcher = None
        
        while True:
            try:
                user_input = input("\n👤 You: ").strip()
                
                if not user_input:
                    continue
                    
                # Handle special commands
                if user_input.lower() in ('exit', 'quit', 'bye'):
                    print("\n👋 Goodbye! Thanks for using Aurix!")
                    break
                elif user_input.lower() == 'help':
                    print("\n📋 Available commands:")
                    print("  • exit/quit/bye - Terminate Aurix")
                    print("  • help - Show this help message")
                    print("  • clear - Clear conversation history")
                    print("  • close/terminate/exit/quit [app] - Close an application")
                    print("  • Just type your question to chat with Aurix!")
                    continue
                elif user_input.lower() == 'clear':
                    print("\n🧹 Conversation cleared!")
                    continue
                
                # Check for close application commands
                if app_launcher:
                    close_result = process_close_command(user_input, app_launcher)
                    if close_result:
                        print(f"\n🤖 Aurix: {close_result}")
                        continue
                
                # Validate and process input
                validated_input = validate_input(user_input)
                if not validated_input:
                    print("⚠️  Invalid input. Please try again.")
                    continue
                
                # Generate response
                print("🤔 Aurix is thinking...")
                
                if ollama_manager:
                    response = ollama_manager.generate_response(validated_input)
                elif ai_model:
                    response = ai_model.generate_response(validated_input)
                else:
                    raise ValueError("No AI model available")
                
                print(f"\n🤖 Aurix: {response}")
                
                # Use TTS to speak the response
                if tts_engine:
                    tts_engine.speak(response)
                    
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye! Thanks for using Aurix!")
                logger.info("User interrupted the program")
                break
            except ValueError as ve:
                logger.error(f"Value Error: {ve}")
                print(f"❌ Sorry, {ve}")
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                print("❌ Sorry, I encountered an unexpected error. Please try again.")
    
    logger.info("🛑 Shutting down Aurix AI Desktop Assistant")

if __name__ == "__main__":
    main()