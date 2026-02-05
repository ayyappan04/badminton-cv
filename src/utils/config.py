import yaml
import os
from typing import Dict, Any, Optional

class ConfigLoader:
    def __init__(self, config_path: str = "config/default.yaml"):
        self.config_path = config_path
        self.config = self.load_config(config_path)

    def load_config(self, path: str) -> Dict[str, Any]:
        """Load configuration from a YAML file."""
        if not os.path.exists(path):
            raise FileNotFoundError(f"Configuration file not found at {path}")
        
        with open(path, 'r') as f:
            try:
                config = yaml.safe_load(f)
                return config or {}
            except yaml.YAMLError as e:
                print(f"Error parsing YAML file: {e}")
                return {}

    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value using dot notation (e.g., 'video.resolution')."""
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value

    def merge_with(self, other_config: Dict[str, Any]):
        """Merge another configuration dictionary into the current one."""
        self._deep_merge(self.config, other_config)

    def _deep_merge(self, source: Dict[str, Any], destination: Dict[str, Any]):
        """Recursively merge two dictionaries."""
        for key, value in destination.items():
            if isinstance(value, dict) and key in source and isinstance(source[key], dict):
                self._deep_merge(source[key], value)
            else:
                source[key] = value

# Singleton instance for easy access
_config_instance = None

def get_config(config_path: Optional[str] = None) -> ConfigLoader:
    global _config_instance
    if _config_instance is None:
        if config_path is None:
             # Default to config/default.yaml relative to project root
             # Assuming script run from project root or src/
             base_path = os.getcwd()
             default_path = os.path.join(base_path, "config", "default.yaml")
             config_path = default_path
        
        _config_instance = ConfigLoader(config_path)
    
    return _config_instance
