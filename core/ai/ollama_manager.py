import os
import json
import requests
import logging
from typing import Dict, Any
from .base_ai_manager import BaseAIManager, AIResponse

logger = logging.getLogger(__name__)

class OllamaManager(BaseAIManager):
    """Manages interactions with local Ollama models."""
    
    def __init__(self, config: Dict[str, Any], reminder_callback):
        """
        Initialize Ollama Manager with configuration.
        
        Args:
            config: Dictionary containing Ollama configuration
            reminder_callback: Callback function for reminders
        """
        # Set default model if not specified
        if 'model' not in config:
            config['model'] = os.getenv('OLLAMA_MODEL', 'deepseek-r1:1.5b')
        
        super().__init__(config, reminder_callback)
        
        # Check if Ollama is running
        self._check_service_status()

    def _get_ai_response(self, user_input: str) -> AIResponse:
        """Get AI response from Ollama with optimized performance"""
        try:
            # Add user input to conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            
            # Keep conversation history manageable before making the request
            if len(self.conversation_history) > self.conversation_history_limit:
                self.conversation_history = self.conversation_history[-self.conversation_history_limit:]
            
            # Apply memory optimization if enabled
            context_window = self.conversation_history
            if self.memory_optimization:
                # Use only the most recent conversations to reduce memory usage
                context_window = self.conversation_history[-min(5, len(self.conversation_history)):]
            
            # Prepare the API request with optimized parameters
            payload = {
                "model": self.model_name,
                "messages": [{"role": "system", "content": self.system_prompt}] + context_window,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens,
                    "num_ctx": self.context_length
                }
            }
            
            logger.info(f"Sending request to Ollama with model: {self.model_name}")
            
            # Make the API call with retry logic
            for attempt in range(self.retry_attempts):
                try:
                    # Adjust parameters for retry
                    if attempt > 0:
                        logger.warning(f"Retry attempt {attempt} with reduced parameters")
                        payload["options"]["num_predict"] = min(payload["options"]["num_predict"], 256)
                        payload["options"]["temperature"] = max(0.1, self.temperature - 0.2)
                        logger.info(f"Retrying with reduced parameters: num_predict={payload['options']['num_predict']}, temperature={payload['options']['temperature']}")
                    
                    # Set timeout based on attempt
                    timeout = self.request_timeout * (1 + attempt * 0.5)  # Increase timeout with each retry
                    
                    response = requests.post(
                        f"{self.base_url}/api/chat",
                        json=payload,
                        timeout=timeout
                    )
                    
                    # If successful, break out of retry loop
                    if response.status_code == 200:
                        break
                        
                except requests.exceptions.Timeout:
                    if attempt == self.retry_attempts - 1:  # Last attempt
                        raise
                    logger.warning("Request timed out, will retry with reduced parameters")
                    continue
            
            if response.status_code == 200:
                result = response.json()
                ai_message = result.get('message', {}).get('content', '')
                
                # Add AI response to conversation history
                self.conversation_history.append({"role": "assistant", "content": ai_message})
                
                return AIResponse(success=True, content=ai_message)
            else:
                error_msg = f"API Error: {response.status_code} - {response.text}"
                logger.error(error_msg)
                return AIResponse(
                    success=False, 
                    content="", 
                    error=f"API Error: {response.status_code}"
                )
            
        except requests.exceptions.Timeout:
            logger.error("Ollama timeout - consider model size reduction")
            return AIResponse(
                success=False,
                content="Response timeout. Please try a simpler query or smaller model.",
                error="Service timeout"
            )
        except requests.exceptions.ConnectionError:
            logger.error("Failed to connect to Ollama")
            return AIResponse(
                success=False, 
                content="I can't connect to the AI service. Please make sure Ollama is running.",
                error="Connection failed"
            )
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return AIResponse(
                success=False, 
                content="Sorry, I encountered an unexpected error. Please try again.",
                error=f"Unexpected error: {str(e)}"
            )

    def generate_response(self, user_input: str) -> str:
        """Generate a response to user input with exit handling"""
        # Check for exit commands first
        if user_input.lower().strip() in ["exit", "quit", "bye", "goodbye", "close"]:
            return self.exit_application()
        
        # Check for close application commands
        close_patterns = ["close ", "terminate ", "exit ", "quit "]
        input_lower = user_input.lower()
        for pattern in close_patterns:
            if input_lower.startswith(pattern):
                app_name = input_lower[len(pattern):].strip()
                if app_name:
                    try:
                        from core.automation.app_launcher import AppLauncher
                        app_launcher = AppLauncher()
                        return app_launcher.close_app(app_name)
                    except Exception as e:
                        logger.error(f"Error closing application {app_name}: {e}")
                        return f"Sorry, I couldn't close {app_name}. Error: {str(e)}"
            
        try:
            # Process automation commands first
            automation_response = self._process_automation_commands(user_input)
            if automation_response:
                return automation_response
                
            # Get AI response
            response = self._get_ai_response(user_input)
            
            if response.success:
                return response.content
            else:
                error_msg = response.error or "Unknown error"
                logger.error(f"Failed to generate response: {error_msg}")
                return f"Sorry, I encountered an error while processing your request."
                
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error in generate_response: {error_msg}")
            return f"Sorry, I encountered an error: {error_msg}"