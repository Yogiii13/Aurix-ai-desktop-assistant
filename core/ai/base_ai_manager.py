import os
import json
import requests
import logging
import subprocess
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from core.automation.app_launcher import AppLauncher
from core.automation.reminder import Reminder
from core.automation.system_ctrl import SystemController
from core.automation.web_actions import WebActions

logger = logging.getLogger(__name__)

@dataclass
class AIResponse:
    success: bool
    content: str
    error: Optional[str] = None

class BaseAIManager:
    """Base class for AI model managers to reduce code duplication."""
    
    def __init__(self, config: Dict[str, Any], reminder_callback):
        """
        Initialize Base AI Manager with configuration.
        
        Args:
            config: Dictionary containing AI configuration
            reminder_callback: Callback function for reminders
        """
        self.base_url = config.get('base_url', 'http://localhost:11434')
        self.model_name = config.get('model', 'default-model')
        self.context_length = config.get('context_length', 4096)
        self.max_tokens = config.get('max_tokens', 512)
        self.temperature = config.get('temperature', 0.7)
        
        # Initialize model management settings
        self._initialize_model_management(config)
        
        # Load system prompt
        self.system_prompt = self._load_system_prompt(config)
        
        # Conversation history
        self.conversation_history = []
        
        # Initialize automation components
        self._initialize_automation_components(reminder_callback)

    def _initialize_model_management(self, config: Dict[str, Any]):
        """Initialize model management settings from config"""
        model_mgmt = config.get('model_management', {})
        
        # Extract model management settings with more conservative defaults
        self.auto_start_ollama = model_mgmt.get('auto_start_ollama', False)
        self.preload_models = model_mgmt.get('preload_models', False)
        self.retry_attempts = model_mgmt.get('retry_attempts', 3)  # Increased from 2
        self.memory_optimization = model_mgmt.get('memory_optimization', True)  # Default to True
        self.conversation_history_limit = model_mgmt.get('conversation_history_limit', 10)  # Reduced from 20
        
        # Extract timeout from config with a more conservative default
        self.request_timeout = config.get('timeout', 45)  # Increased from 30
        
        # Set default model parameters if not already set
        if not hasattr(self, 'max_tokens'):
            self.max_tokens = model_mgmt.get('max_tokens', 512)  # Conservative default
        if not hasattr(self, 'context_length'):
            self.context_length = model_mgmt.get('context_length', 2048)  # Conservative default
        
        logger.info(f"Model management initialized: retry_attempts={self.retry_attempts}, "
                    f"history_limit={self.conversation_history_limit}, timeout={self.request_timeout}")
    

    def _load_system_prompt(self, config: Dict[str, Any]) -> str:
        """Load system prompt from template file."""
        prompt_template_path = os.path.join(
            os.path.dirname(__file__), 
            'prompt_templates', 
            config.get('system_prompt_template', 'default.txt')
        )
        try:
            with open(prompt_template_path, 'r', encoding='utf-8') as f:
                system_prompt = f.read()
            logger.debug(f"Loaded system prompt from {prompt_template_path}")
            return system_prompt
        except Exception as e:
            logger.error(f"Failed to load system prompt: {e}")
            return "You are a helpful AI desktop assistant."

    def _initialize_automation_components(self, reminder_callback):
        """Initialize automation components with proper error handling"""
        # App Launcher
        try:
            self.app_launcher = AppLauncher()
            logger.info("App launcher initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize app launcher: {e}")
            self.app_launcher = None
        
        # Reminder System
        try:
            self.reminder = Reminder(reminder_callback)
            logger.info("Reminder system initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize reminder system: {e}")
            self.reminder = None
        
        # System Controller
        try:
            self.system_ctrl = SystemController()
            logger.info("System controller initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize system controller: {e}")
            self.system_ctrl = None
        
        # Web Actions
        try:
            self.web_actions = WebActions()
            logger.info("Web actions initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize web actions: {e}")
            self.web_actions = None

    def _check_service_status(self) -> bool:
        """Enhanced service check with auto-start capability"""
        try:
            response = requests.get(f"{self.base_url}/", timeout=5)
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Service unreachable: {e}")
            # Auto-start is now handled in __init__
            return False
            
    def _start_ollama_service(self) -> bool:
        """Attempt to start the Ollama service if not running"""
        logger.info("Attempting to start Ollama service...")
        try:
            # Different start commands based on OS
            if os.name == 'nt':  # Windows
                # Start Ollama in background
                subprocess.Popen(
                    ['start', '/B', 'ollama', 'serve'],
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
            else:  # Unix-like
                subprocess.Popen(
                    ['ollama', 'serve', '&'],
                    shell=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL
                )
                
            # Give it a moment to start
            import time
            time.sleep(5)
            
            logger.info("Ollama service start initiated")
            return True
        except FileNotFoundError:
            logger.error("Ollama command not found. Please ensure Ollama is installed correctly.")
            return False
        except Exception as e:
            logger.error(f"Failed to start Ollama service: {e}")
            return False

    def _pull_model(self) -> bool:
        """Pull the specified model from repository with robust error handling."""
        logger.info(f"Pulling model {self.model_name}...")
        try:
            process = subprocess.Popen(
                ['ollama', 'pull', self.model_name],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                encoding='utf-8',
                errors='replace'  # Handle encoding issues gracefully
            )
            
            stdout, stderr = process.communicate(timeout=300)  # 5 min timeout
            
            if process.returncode == 0:
                logger.info(f"Successfully pulled model: {self.model_name}")
                return True
            else:
                logger.error(f"Failed to pull model: {stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            process.kill()
            logger.error("Model pull timed out")
            return False
        except FileNotFoundError:
            logger.error("Ollama command not found. Ensure Ollama is installed and in PATH.")
            return False
        except Exception as e:
            logger.error(f"Error pulling model: {e}")
            return False

    def validate_user_input(self, user_input: str) -> bool:
        """Validate user input for security and sanity."""
        if not user_input or not user_input.strip():
            return False
        if len(user_input) > 10000:  # Reasonable limit
            logger.warning(f"User input too long: {len(user_input)} characters")
            return False
        return True

    def generate_response(self, user_input: str) -> AIResponse:
        """
        Generate a response using the AI model with proper error handling.
        
        Args:
            user_input: The user's message
            
        Returns:
            AIResponse: Response object with success status and content
        """
        if not self.validate_user_input(user_input):
            return AIResponse(
                success=False, 
                content="", 
                error="Invalid input provided"
            )
        
        # Process automation commands first
        automation_response = self._process_automation_commands(user_input)
        if automation_response:
            return AIResponse(success=True, content=automation_response)
        
        # If not an automation command, proceed with AI response
        return self._get_ai_response(user_input)

    def _process_automation_commands(self, user_input: str) -> Optional[str]:
        """Process automation commands and return response if handled"""
        user_input_lower = user_input.lower().strip()
        
        # Exit commands
        if user_input_lower in ["exit", "quit", "bye", "goodbye", "close"]:
            return self.exit_application()
        
        # App launching commands
        if user_input_lower.startswith(("launch ", "open ")):
            return self._handle_app_launch(user_input)
        
        # App closing commands
        if user_input_lower.startswith(("close ", "exit ")):
            app_name = user_input_lower.split(" ", 1)[1]
            if app_name not in ["app", "application", "program"]:  # Avoid generic terms
                return self._handle_app_close(app_name)
        
        # Reminder commands
        if user_input_lower.startswith(("remind me to ", "set reminder ")):
            return self._handle_reminder_command(user_input)
        
        if user_input_lower in ["show reminders", "list reminders"]:
            return self._handle_show_reminders()
        
        if user_input_lower in ["clear reminders", "delete reminders"]:
            return self._handle_clear_reminders()
        
        # System control commands
        if user_input_lower.startswith("set volume "):
            return self._handle_volume_control(user_input, "set")
        
        if user_input_lower in ["get volume", "current volume", "volume level"]:
            return self._handle_volume_control(user_input, "get")
        
        if user_input_lower.startswith("set brightness "):
            return self._handle_brightness_control(user_input, "set")
        
        if user_input_lower in ["get brightness", "current brightness", "brightness level"]:
            return self._handle_brightness_control(user_input, "get")
        
        if user_input_lower in ["mute", "mute volume"]:
            return self._handle_volume_control(user_input, "mute")
        
        if user_input_lower in ["unmute", "unmute volume"]:
            return self._handle_volume_control(user_input, "unmute")
        
        # New system control commands
        if user_input_lower.startswith(("shutdown", "turn off computer", "power off")):
            return self._handle_system_control(user_input, "shutdown")
        
        if user_input_lower.startswith(("restart", "reboot")):
            return self._handle_system_control(user_input, "restart")
        
        if user_input_lower in ["cancel shutdown", "abort shutdown", "cancel restart"]:
            return self._handle_system_control(user_input, "cancel_shutdown")
        
        if user_input_lower in ["sleep", "sleep mode", "put system to sleep"]:
            return self._handle_system_control(user_input, "sleep")
        
        if user_input_lower in ["lock", "lock screen", "lock computer"]:
            return self._handle_system_control(user_input, "lock")
        
        if user_input_lower in ["system info", "computer info", "system information"]:
            return self._handle_system_control(user_input, "info")
        
        # Web action commands
        if user_input_lower.startswith("search "):
            return self._handle_web_search(user_input)
        
        if user_input_lower.startswith("scrape "):
            return self._handle_web_scrape(user_input)
        
        if user_input_lower.startswith("quick answer "):
            return self._handle_quick_answer(user_input)
        
        return None  # Not an automation command
    
    def _handle_system_control(self, user_input: str, action: str) -> str:
        """Handle system control commands like shutdown, restart, sleep, etc."""
        if not self.system_ctrl:
            return "System control is not available. Please check dependencies."
        
        try:
            if action == "shutdown":
                # Extract delay if specified
                delay = 30  # Default delay
                parts = user_input.split()
                for i, part in enumerate(parts):
                    if part.isdigit() and i > 0 and parts[i-1].lower() in ["in", "after", "wait"]:
                        delay = int(part)
                        break
                
                return self.system_ctrl.shutdown_system(delay)
                
            elif action == "restart":
                # Extract delay if specified
                delay = 30  # Default delay
                parts = user_input.split()
                for i, part in enumerate(parts):
                    if part.isdigit() and i > 0 and parts[i-1].lower() in ["in", "after", "wait"]:
                        delay = int(part)
                        break
                        
                return self.system_ctrl.restart_system(delay)
                
            elif action == "cancel_shutdown":
                return self.system_ctrl.cancel_shutdown()
                
            elif action == "sleep":
                return self.system_ctrl.sleep_system()
                
            elif action == "lock":
                return self.system_ctrl.lock_screen()
                
            elif action == "info":
                return self.system_ctrl.get_system_info()
                
        except Exception as e:
            logger.error(f"Error with system control: {e}")
            return f"System control failed: {str(e)}"
    
    def _handle_app_launch(self, user_input: str) -> str:
        """Handle app launch commands"""
        if not self.app_launcher:
            return "App launcher is not available. Please check dependencies."
        
        try:
            # Extract app name from command
            command_parts = user_input.lower().split(" ", 1)
            if len(command_parts) < 2:
                return "Please specify an application to launch."
            
            app_name = command_parts[1].strip()
            
            # Handle special cases
            if app_name in ["file explorer", "explorer", "my computer"]:
                app_name = "explorer"
            elif app_name in ["browser", "web browser", "internet"]:
                app_name = "chrome"  # Default to Chrome, can be customized
            
            return self.app_launcher.launch_app(app_name)
        except Exception as e:
            logger.error(f"Error launching app: {e}")
            return f"Failed to launch application: {str(e)}"
    
    def _handle_app_close(self, app_name: str) -> str:
        """Handle app close commands"""
        if not self.app_launcher:
            return "App launcher is not available. Please check dependencies."
        
        try:
            return self.app_launcher.close_app(app_name)
        except Exception as e:
            logger.error(f"Error closing app: {e}")
            return f"Failed to close application: {str(e)}"
        
    def _handle_reminder_command(self, user_input: str) -> str:
        """Handle reminder setting commands"""
        if not self.reminder:
            return "Reminder system is not available."
        
        try:
            # Parse reminder command
            if user_input.lower().startswith("remind me to "):
                content = user_input[13:]  # Remove "remind me to "
            elif user_input.lower().startswith("set reminder "):
                content = user_input[13:]  # Remove "set reminder "
            else:
                return "Invalid reminder command format."
            
            # Look for time specification
            if " in " in content:
                parts = content.split(" in ")
                if len(parts) == 2:
                    message, time_str = parts
                    return self._parse_and_set_reminder(message.strip(), time_str.strip())
            
            return "Please specify the reminder in format: 'Remind me to [task] in [number] [minutes/hours]'"
        
        except Exception as e:
            logger.error(f"Error setting reminder: {e}")
            return f"Failed to set reminder: {str(e)}"

    def _parse_and_set_reminder(self, message: str, time_str: str) -> str:
        """Parse time string and set reminder"""
        try:
            parts = time_str.split()
            if len(parts) < 2:
                return "Invalid time format. Use: [number] [minutes/hours]"
            
            time_value = int(parts[0])
            time_unit = parts[1].lower()
            
            if time_unit in ["minute", "minutes", "min", "mins"]:
                when = datetime.now() + timedelta(minutes=time_value)
            elif time_unit in ["hour", "hours", "hr", "hrs"]:
                when = datetime.now() + timedelta(hours=time_value)
            else:
                return "Sorry, I can only set reminders for minutes or hours from now."
            
            return self.reminder.add_reminder(message, when)
        
        except ValueError:
            return "Invalid time value. Please use a number."
        except Exception as e:
            return f"Error parsing reminder time: {str(e)}"

    def _handle_show_reminders(self) -> str:
        """Handle showing reminders"""
        if not self.reminder:
            return "Reminder system is not available."
        
        try:
            reminders = self.reminder.get_reminders()
            if reminders:
                return "Here are your current reminders:\n" + "\n".join(reminders)
            else:
                return "You don't have any active reminders."
        except Exception as e:
            logger.error(f"Error getting reminders: {e}")
            return f"Failed to get reminders: {str(e)}"

    def _handle_clear_reminders(self) -> str:
        """Handle clearing reminders"""
        if not self.reminder:
            return "Reminder system is not available."
        
        try:
            return self.reminder.clear_reminders()
        except Exception as e:
            logger.error(f"Error clearing reminders: {e}")
            return f"Failed to clear reminders: {str(e)}"

    def _handle_volume_control(self, user_input: str, action: str) -> str:
        """Handle volume control commands"""
        if not self.system_ctrl:
            return "System control is not available. Please check dependencies (pycaw)."
        
        try:
            if action == "set":
                # Extract number from end of string
                parts = user_input.split()
                if parts and parts[-1].isdigit():
                    level = int(parts[-1])
                    return self.system_ctrl.set_volume(level)
                else:
                    return "Please specify a volume level (0-100)."
            elif action == "get":
                return self.system_ctrl.get_volume()
            elif action == "mute":
                return self.system_ctrl.mute_volume()
            elif action == "unmute":
                return self.system_ctrl.unmute_volume()
        except ValueError:
            return "Invalid volume level. Please provide a number between 0 and 100."
        except Exception as e:
            logger.error(f"Error with volume control: {e}")
            return f"Volume control failed: {str(e)}"

    def _handle_brightness_control(self, user_input: str, action: str) -> str:
        """Handle brightness control commands"""
        if not self.system_ctrl:
            return "System control is not available. Please check dependencies."
        
        try:
            if action == "set":
                # Extract number from end of string
                parts = user_input.split()
                if parts and parts[-1].isdigit():
                    level = int(parts[-1])
                    return self.system_ctrl.set_brightness(level)
                else:
                    return "Please specify a brightness level (0-100)."
            elif action == "get":
                return self.system_ctrl.get_brightness()
        except ValueError:
            return "Invalid brightness level. Please provide a number between 0 and 100."
        except Exception as e:
            logger.error(f"Error with brightness control: {e}")
            return f"Brightness control failed: {str(e)}"

    def _handle_web_search(self, user_input: str) -> str:
        """Handle web search commands"""
        if not self.web_actions:
            return "Web actions are not available. Please check internet connection."
        
        try:
            query = user_input[7:].strip()  # Remove "search "
            if not query:
                return "Please specify a search query."
                
            results = self.web_actions.search(query)
            if results:
                response = "Here are the top search results:\n\n"
                for i, result in enumerate(results, 1):
                    response += f"{i}. {result['title']}\n   {result['link']}\n   {result['snippet']}\n\n"
                return response
            else:
                return "Sorry, I couldn't find any results for that search."
        except Exception as e:
            logger.error(f"Error with web search: {e}")
            return f"Web search failed: {str(e)}"

    def _handle_web_scrape(self, user_input: str) -> str:
        """Handle web scraping commands"""
        if not self.web_actions:
            return "Web actions are not available."
        
        try:
            url = user_input[7:].strip()  # Remove "scrape "
            if not url:
                return "Please specify a URL to scrape."
                
            content = self.web_actions.scrape_webpage(url)
            return f"Here's a summary of the webpage content:\n\n{content}"
        except Exception as e:
            logger.error(f"Error with web scraping: {e}")
            return f"Web scraping failed: {str(e)}"

    def _handle_quick_answer(self, user_input: str) -> str:
        """Handle quick answer commands"""
        if not self.web_actions:
            return "Web actions are not available."
        
        try:
            query = user_input[13:].strip()  # Remove "quick answer "
            if not query:
                return "Please specify a query for quick answer."
                
            answer = self.web_actions.quick_answer(query)
            if answer:
                return f"Quick answer: {answer}"
            else:
                return "Sorry, I couldn't find a quick answer for that query."
        except Exception as e:
            logger.error(f"Error with quick answer: {e}")
            return f"Quick answer failed: {str(e)}"

    def _get_ai_response(self, user_input: str) -> AIResponse:
        """Get AI response - to be implemented by subclasses"""
        raise NotImplementedError("Subclasses must implement _get_ai_response")

    def clear_conversation(self) -> None:
        """Clear the conversation history."""
        self.conversation_history = []
        logger.debug("Cleared conversation history")

    def get_installed_apps(self) -> List[str]:
        """Return a list of installed applications."""
        if self.app_launcher:
            return self.app_launcher.get_installed_apps()
        return []

    def get_automation_status(self) -> Dict[str, bool]:
        """Get status of all automation components"""
        return {
            "app_launcher": self.app_launcher is not None,
            "reminder": self.reminder is not None,
            "system_ctrl": self.system_ctrl is not None,
            "web_actions": self.web_actions is not None
        }
            
    def exit_application(self) -> str:
            """Safely exit the application with cleanup"""
            try:
                # Clean up any resources
                if self.reminder:
                    # Save any pending reminders
                    self.reminder.save_reminders()
                    
                # Log the exit
                logger.info("Application exit requested by user")
                
                # Return success message
                return "Exiting application. Goodbye!"
            except Exception as e:
                logger.error(f"Error during application exit: {e}")
                return f"Error during exit: {str(e)}"
        