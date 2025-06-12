import os
import json
import requests
import logging
from typing import Dict, Any
from .base_ai_manager import BaseAIManager, AIResponse

logger = logging.getLogger(__name__)

class GemmaManager(BaseAIManager):
    """Manages interactions with Gemma models via Ollama."""
    
    def __init__(self, config: Dict[str, Any], reminder_callback):
        """
        Initialize Gemma Manager with configuration.
        
        Args:
            config: Dictionary containing Gemma configuration
            reminder_callback: Callback function for reminders
        """
        # Resolve model name discrepancies
        config['model'] = self._resolve_model_name(
            config.get('model', config.get('model_name', 'gemma3:1b'))
        )
        
        super().__init__(config, reminder_callback)
        
        # Check if Ollama is running and if the Gemma model is available
        self._check_service_status()

    def _resolve_model_name(self, config_model_name: str) -> str:
        """Resolve model name discrepancies between config and Ollama"""
        model_mapping = {
            'gemma:1b': 'gemma3:1b' 
        }
        resolved_name = model_mapping.get(config_model_name, config_model_name)
        
        if resolved_name != config_model_name:
            logger.info(f"Resolved model name: {config_model_name} -> {resolved_name}")
        
        return resolved_name

    def _get_ai_response(self, user_input: str) -> AIResponse:
        """Generate a response from the Gemma model with optimized performance."""
        try:
            # Add user input to conversation history
            self.conversation_history.append({"role": "user", "content": user_input})
            
            # Keep conversation history manageable before making the request
            if hasattr(self, 'conversation_history_limit'):
                if len(self.conversation_history) > self.conversation_history_limit:
                    self.conversation_history = self.conversation_history[-self.conversation_history_limit:]
            
            # Apply memory optimization if enabled
            context_window = self.conversation_history
            if hasattr(self, 'memory_optimization') and self.memory_optimization:
                # Use only the most recent conversations to reduce memory usage
                context_window = self.conversation_history[-min(5, len(self.conversation_history)):]
            
            # Prepare the prompt - optimize for token efficiency
            full_prompt = f"{self.system_prompt}\n\n"
            
            # Only include relevant context
            for msg in context_window:
                if isinstance(msg, dict):
                    role = msg.get('role', 'user')
                    content = msg.get('content', '')
                    full_prompt += f"{role.capitalize()}: {content}\n"
            
            full_prompt += f"Assistant: "
            
            # Optimize request parameters
            data = {
                "prompt": full_prompt,
                "model": self._resolve_model_name(self.model_name),
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "num_predict": self.max_tokens,
                    "num_ctx": self.context_length
                }
            }
            
            # Implement retry logic
            retry_attempts = getattr(self, 'retry_attempts', 2)
            for attempt in range(retry_attempts):
                try:
                    # Adjust parameters for retry
                    if attempt > 0:
                        logger.warning(f"Retry attempt {attempt} with reduced parameters")
                        data["options"]["num_predict"] = min(data["options"]["num_predict"], 256)
                        data["options"]["temperature"] = max(0.1, self.temperature - 0.2)
                    
                    # Set timeout based on attempt
                    timeout = getattr(self, 'request_timeout', 30) * (1 + attempt * 0.5)
                    
                    response = requests.post(
                        f"{self.base_url}/api/generate", 
                        json=data, 
                        stream=False,
                        timeout=timeout
                    )
                    response.raise_for_status()
                    
                    # If successful, break out of retry loop
                    break
                        
                except (requests.exceptions.Timeout, requests.exceptions.HTTPError):
                    if attempt == retry_attempts - 1:  # Last attempt
                        raise
                    logger.warning("Request failed, will retry with reduced parameters")
                    continue
            
            response_data = response.json()
            model_response = response_data.get('response', '').strip()
            
            if model_response:
                # Update conversation history efficiently
                self.conversation_history.append({"role": "assistant", "content": model_response})
                
                return AIResponse(success=True, content=model_response)
            else:
                logger.warning("Empty response from Gemma model")
                return AIResponse(
                    success=False, 
                    content="", 
                    error="Empty response from model"
                )
    
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error: {e}")
            return AIResponse(
                success=False, 
                content="I encountered an error connecting to the AI service. Please check if Ollama is running correctly.",
                error=f"HTTP error: {e.response.status_code if hasattr(e, 'response') else 'unknown'}"
            )
        except requests.exceptions.Timeout:
            logger.error("Request to Gemma model timed out")
            return AIResponse(
                success=False, 
                content="The AI model is taking too long to respond. It might be overloaded or still loading. Please try again in a moment.",
                error="Request timed out"
            )
        except requests.exceptions.ConnectionError:
            logger.error("Failed to connect to Ollama for Gemma")
            return AIResponse(
                success=False, 
                content="I can't connect to the AI service. Please make sure Ollama is running.",
                error="Connection failed"
            )
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON response: {e}")
            return AIResponse(
                success=False, 
                content="I received an invalid response from the AI service. This might be a temporary issue.",
                error="Invalid response format"
            )
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return AIResponse(
                success=False, 
                content="Sorry, I encountered an unexpected error. Please try again.",
                error=f"Unexpected error: {str(e)}"
            )

    def generate_response(self, user_input: str) -> str:
        """
        Generate a response using Gemma with fallback error handling.
        
        Args:
            user_input: The user's message
            
        Returns:
            str: The AI response or error message
        """
        ai_response = super().generate_response(user_input)
        
        if ai_response.success:
            return ai_response.content
        else:
            error_msg = ai_response.error or "Unknown error occurred"
            return f"Sorry, I encountered an error: {error_msg}"