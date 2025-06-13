import os
import yaml
import logging
from pathlib import Path
from dotenv import load_dotenv
from typing import Dict, Any
from .config_validator import ConfigValidator

logger = logging.getLogger(__name__)

class ConfigLoader:
    """Loads and manages configuration from YAML files with environment variable support."""
    
    def __init__(self, config_path):
        """
        Initialize the config loader.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config_path = Path(config_path)
        
        # Load environment variables from .env file
        env_path = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))) / '.env'
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
            logger.info(f"Loaded environment variables from {env_path}")
        else:
            logger.warning(f"Environment file not found: {env_path}")
        
    def load(self) -> Dict[str, Any]:
        """
        Load configuration from file with environment variable substitution and validation.
        
        Returns:
            dict: Configuration dictionary
        """
        if not self.config_path.exists():
            logger.error(f"Configuration file not found: {self.config_path}")
            return self._get_default_config()
            
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_str = f.read()
                
            # Replace environment variables in the config string
            config_str = self._substitute_environment_variables(config_str)
            
            # Parse YAML after environment variable substitution
            config = yaml.safe_load(config_str)
            
            # Additional processing for boolean values from environment variables
            self._process_boolean_values(config)
            
            # Validate configuration
            is_valid, errors = ConfigValidator.validate_config(config)
            if not is_valid:
                logger.error("Configuration validation failed:")
                for error in errors:
                    logger.error(f"  - {error}")
                logger.warning("Using default configuration for invalid sections")
                config = self._merge_with_defaults(config)
            
            logger.info(f"Configuration loaded from {self.config_path}")
            return config
            
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML configuration: {e}")
            return self._get_default_config()
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return self._get_default_config()
    
    def _substitute_environment_variables(self, config_str: str) -> str:
        """
        Substitute environment variables in configuration string.
        Supports both ${VAR} and ${VAR:-default} syntax.
        """
        import re
        
        def replace_env_var(match):
            var_expr = match.group(1)
            
            # Check if default value is specified
            if ':-' in var_expr:
                var_name, default_value = var_expr.split(':-', 1)
                return os.getenv(var_name.strip(), default_value.strip())
            else:
                return os.getenv(var_expr.strip(), '')
        
        # Replace ${VAR} and ${VAR:-default} patterns
        pattern = r'\$\{([^}]+)\}'
        return re.sub(pattern, replace_env_var, config_str)
    
    def _process_boolean_values(self, config, path=None):
        """
        Process string boolean values from environment variables to actual booleans.
        
        Args:
            config: Configuration dictionary or value
            path: Current path in the configuration (for nested values)
        """
        if path is None:
            path = []
            
        if isinstance(config, dict):
            for key, value in config.items():
                new_path = path + [key]
                if isinstance(value, (dict, list)):
                    self._process_boolean_values(value, new_path)
                elif isinstance(value, str):
                    # Convert string boolean values
                    if value.lower() in ('true', 'yes', '1', 'on'):
                        config[key] = True
                    elif value.lower() in ('false', 'no', '0', 'off'):
                        config[key] = False
                    elif value.replace('.', '', 1).isdigit():
                        # Convert numeric strings
                        try:
                            if '.' in value:
                                config[key] = float(value)
                            else:
                                config[key] = int(value)
                        except ValueError:
                            pass
        elif isinstance(config, list):
            for i, item in enumerate(config):
                new_path = path + [i]
                if isinstance(item, (dict, list)):
                    self._process_boolean_values(item, new_path)
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Return a default configuration when loading fails."""
        return {
            'system': {
                'name': 'AI Desktop Assistant',
                'version': '0.1.0',
                'log_level': 'INFO',
                'log_dir': 'data/logs',
                'cache_dir': 'data/cache'
            },
            'ai': {
                'primary': {
                    'provider': 'ollama',
                    'base_url': 'http://localhost:11434',
                    'model': 'deepseek-r1:1.5b',
                    'context_length': 4096,
                    'max_tokens': 1024,
                    'temperature': 0.7,
                    'system_prompt_template': 'default.txt'
                }
            },
            'voice': {
                'enabled': False
            },
            'ui': {
                'theme': 'light',
                'font_size': 12,
                'opacity': 0.95,
                'always_on_top': False,
                'start_minimized': False
            },
            'automation': {
                'system_commands': {
                    'allowed': True,
                    'blacklist': ['shutdown', 'format', 'del']
                }
            }
        }
    
    def _merge_with_defaults(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Merge configuration with defaults for any missing sections."""
        default_config = self._get_default_config()
        
        def deep_merge(base: dict, override: dict) -> dict:
            """Deep merge two dictionaries."""
            result = base.copy()
            for key, value in override.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result
        
        return deep_merge(default_config, config)
    
    def save_config(self, config: Dict[str, Any], backup: bool = True) -> bool:
        """
        Save configuration to file with optional backup.
        
        Args:
            config: Configuration dictionary to save
            backup: Whether to create a backup of existing config
            
        Returns:
            bool: True if successful
        """
        try:
            # Create backup if requested
            if backup and self.config_path.exists():
                backup_path = self.config_path.with_suffix('.bak')
                self.config_path.replace(backup_path)
                logger.info(f"Created backup: {backup_path}")
            
            # Ensure directory exists
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save configuration
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)
            
            logger.info(f"Configuration saved to {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving configuration: {e}")
            return False
    
    def validate_config_file(self) -> bool:
        """
        Validate the configuration file without loading it.
        
        Returns:
            bool: True if configuration is valid
        """
        try:
            config = self.load()
            is_valid, errors = ConfigValidator.validate_config(config)
            
            if not is_valid:
                logger.error("Configuration validation failed:")
                for error in errors:
                    logger.error(f"  - {error}")
            
            return is_valid
            
        except Exception as e:
            logger.error(f"Error validating configuration: {e}")
            return False