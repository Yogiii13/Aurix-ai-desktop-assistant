from typing import Dict, Any
from .ollama_manager import OllamaManager
from .gemma_manager import GemmaManager
import logging

logger = logging.getLogger(__name__)

class ModelSelector:
    """
    Manages model selection and fallback mechanisms for AI responses.
    """
    def __init__(self, config: Dict[str, Any], reminder_callback):
        """
        Initializes the ModelSelector with the given configuration.
        
        Args:
            config (Dict[str, Any]): A dictionary containing the configuration
                settings for the AI models.
            reminder_callback: Callback function for reminders
        """
        self.config = config
        self.primary_model = None
        self.fallback_model = None
        self._initialize_models(reminder_callback)
    
    def _initialize_models(self, reminder_callback) -> None:
        """Initialize primary and fallback AI models."""
        try:
            # Initialize primary model
            primary_config = self.config.get('primary', {})
            provider = primary_config.get('provider', 'gemma')
            
            if provider == 'gemma':
                self.primary_model = GemmaManager(primary_config, reminder_callback=reminder_callback)
                logger.info(f"Initialized primary model: {self.primary_model.model_name}")
            elif provider == 'ollama':
                self.primary_model = OllamaManager(primary_config, reminder_callback=reminder_callback)
                logger.info(f"Initialized primary model: {self.primary_model.model_name}")
            else:
                logger.error(f"Unsupported provider for primary model: {provider}")
                
            # Initialize fallback model if configured
            if 'fallback' in self.config:
                fallback_config = self.config.get('fallback', {})
                fallback_provider = fallback_config.get('provider', 'ollama')
                
                if fallback_provider == 'ollama':
                    self.fallback_model = OllamaManager(fallback_config, reminder_callback=reminder_callback)
                    logger.info(f"Initialized fallback model: {self.fallback_model.model_name}")
                elif fallback_provider == 'gemma':
                    self.fallback_model = GemmaManager(fallback_config, reminder_callback=reminder_callback)
                    logger.info(f"Initialized fallback model: {self.fallback_model.model_name}")
                else:
                    logger.error(f"Unsupported provider for fallback model: {fallback_provider}")
                    
        except Exception as e:
            logger.error(f"Error initializing models: {e}")
    
    def get_primary_model(self):
        """Returns the primary AI model."""
        return self.primary_model
    
    def get_fallback_model(self):
        """
        Get the fallback AI model.
        
        Returns:
            The fallback AI model instance or None
        """
        return self.fallback_model
    
    def generate_response(self, user_input: str) -> str:
        """
        Generate a response using the appropriate model with fallback logic.
        
        Args:
            user_input: The user's message
            
        Returns:
            str: The AI response
        """
        if not user_input:
            return "I didn't receive any input."
        
        # Try primary model first
        if self.primary_model:
            try:
                logger.debug(f"Generating response with primary model: {self.primary_model.model_name}")
                response = self.primary_model.generate_response(user_input)
                
                # If response is valid, return it
                if response and not response.startswith("Sorry, I encountered an error"):
                    return response
                
                logger.warning("Primary model failed to generate response, trying fallback")
            except Exception as e:
                logger.error(f"Error with primary model: {e}")
        
        # Try fallback model if available
        if self.fallback_model:
            try:
                logger.debug(f"Generating response with fallback model: {self.fallback_model.model_name}")
                response = self.fallback_model.generate_response(user_input)
                return response
            except Exception as e:
                logger.error(f"Error with fallback model: {e}")
        
        # If all models fail
        return "Sorry, I'm unable to generate a response at the moment."