import os
import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)

class ConfigValidator:
    """Validates configuration files and environment variables."""
    
    @staticmethod
    def validate_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate the entire configuration.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Validate AI configuration
        if not ConfigValidator.validate_ai_config(config.get('ai', {})):
            errors.append("Invalid AI configuration")
        
        # Validate voice configuration if enabled
        voice_config = config.get('voice', {})
        if voice_config.get('enabled', False):
            voice_errors = ConfigValidator.validate_voice_config(voice_config)
            errors.extend(voice_errors)
        
        # Validate UI configuration
        ui_errors = ConfigValidator.validate_ui_config(config.get('ui', {}))
        errors.extend(ui_errors)
        
        # Check required environment variables
        env_errors = ConfigValidator.validate_environment_variables(config)
        errors.extend(env_errors)
        
        return len(errors) == 0, errors
    
    @staticmethod
    def validate_ai_config(ai_config: Dict[str, Any]) -> bool:
        """Validate AI configuration section."""
        if not ai_config:
            logger.error("AI configuration is missing")
            return False
        
        # Check primary model configuration
        primary = ai_config.get('primary', {})
        if not primary:
            logger.error("Primary AI model configuration is missing")
            return False
        
        required_fields = ['provider', 'base_url', 'model']
        for field in required_fields:
            if not primary.get(field):
                logger.error(f"Missing required AI config field: {field}")
                return False
        
        # Validate provider
        valid_providers = ['gemma', 'ollama']
        if primary.get('provider') not in valid_providers:
            logger.error(f"Invalid AI provider: {primary.get('provider')}")
            return False
        
        # Validate numeric fields
        numeric_fields = ['context_length', 'max_tokens', 'temperature']
        for field in numeric_fields:
            value = primary.get(field)
            if value is not None:
                try:
                    float(value)  # This works for both int and float
                except (ValueError, TypeError):
                    logger.error(f"Invalid numeric value for {field}: {value}")
                    return False
        
        return True
    
    @staticmethod
    def validate_voice_config(voice_config: Dict[str, Any]) -> List[str]:
        """Validate voice configuration section."""
        errors = []
        
        # Check TTS configuration
        tts_config = voice_config.get('tts', {})
        if tts_config:
            engine = tts_config.get('engine', '')
            
            if engine == 'elevenlabs':
                api_key = tts_config.get('api_key', '')
                if not api_key or api_key.startswith('${'):
                    # Check environment variable
                    env_key = os.getenv('ELEVENLABS_API_KEY')
                    if not env_key:
                        errors.append("ElevenLabs API key not found in environment variables")
                
                voice_id = tts_config.get('voice_id', '')
                if not voice_id or voice_id.startswith('${'):
                    env_voice_id = os.getenv('ELEVENLABS_VOICE_ID')
                    if not env_voice_id:
                        errors.append("ElevenLabs Voice ID not found in environment variables")
        
        # Check STT configuration
        stt_config = voice_config.get('stt', {})
        if stt_config:
            engine = stt_config.get('engine', 'vosk')
            if engine == 'vosk':
                model_path = stt_config.get('model_path', '')
                if model_path and not os.path.exists(model_path):
                    errors.append(f"STT model path does not exist: {model_path}")
        
        # Check wake word configuration
        wake_word_config = voice_config.get('wake_word', {})
        if wake_word_config:
            model_path = wake_word_config.get('model_path', '')
            if model_path and not os.path.exists(model_path):
                errors.append(f"Wake word model path does not exist: {model_path}")
        
        return errors
    
    @staticmethod
    def validate_ui_config(ui_config: Dict[str, Any]) -> List[str]:
        """Validate UI configuration section."""
        errors = []
        
        # Validate theme
        theme = ui_config.get('theme', 'light')
        valid_themes = ['light', 'dark', 'system']
        if theme not in valid_themes:
            errors.append(f"Invalid UI theme: {theme}. Valid options: {valid_themes}")
        
        # Validate opacity
        opacity = ui_config.get('opacity', 0.95)
        try:
            opacity_float = float(opacity)
            if not (0.0 <= opacity_float <= 1.0):
                errors.append(f"UI opacity must be between 0.0 and 1.0, got: {opacity}")
        except (ValueError, TypeError):
            errors.append(f"Invalid opacity value: {opacity}")
        
        # Validate font size
        font_size = ui_config.get('font_size', 12)
        try:
            font_size_int = int(font_size)
            if not (8 <= font_size_int <= 72):
                errors.append(f"Font size should be between 8 and 72, got: {font_size}")
        except (ValueError, TypeError):
            errors.append(f"Invalid font size: {font_size}")
        
        return errors
    
    @staticmethod
    def validate_environment_variables(config: Dict[str, Any]) -> List[str]:
        """Check if all required environment variables are set."""
        errors = []
        required_env_vars = []
        
        # Check voice-related environment variables
        voice_config = config.get('voice', {})
        if voice_config.get('enabled', False):
            tts_config = voice_config.get('tts', {})
            if tts_config.get('engine') == 'elevenlabs':
                required_env_vars.extend(['ELEVENLABS_API_KEY', 'ELEVENLABS_VOICE_ID'])
        
        # Check for missing environment variables
        for var in required_env_vars:
            if not os.getenv(var):
                errors.append(f"Required environment variable not set: {var}")
        
        return errors
    
    @staticmethod
    def validate_file_paths(config: Dict[str, Any]) -> List[str]:
        """Validate that required file paths exist."""
        errors = []
        
        # Check voice model paths
        voice_config = config.get('voice', {})
        if voice_config.get('enabled', False):
            # STT model path
            stt_model_path = voice_config.get('stt', {}).get('model_path', '')
            if stt_model_path and not os.path.exists(stt_model_path):
                errors.append(f"STT model directory not found: {stt_model_path}")
            
            # Wake word model path
            wake_word_model_path = voice_config.get('wake_word', {}).get('model_path', '')
            if wake_word_model_path and not os.path.exists(wake_word_model_path):
                errors.append(f"Wake word model directory not found: {wake_word_model_path}")
        
        # Check automation app paths
        automation_config = config.get('automation', {})
        app_paths = automation_config.get('app_paths', {})
        for app_name, app_path in app_paths.items():
            if app_path and not os.path.exists(app_path):
                errors.append(f"Application path not found for {app_name}: {app_path}")
        
        return errors