"""
Configuration loader for Pokemon Red with .env support
"""
import os
from typing import Optional, Dict, Any

class ConfigLoader:
    """Load configuration from .env file and environment variables"""

    def __init__(self, env_file: str = ".env"):
        self.env_file = env_file
        self.config = {}
        self._load_env_file()

    def _load_env_file(self):
        """Load .env file if it exists"""
        if os.path.exists(self.env_file):
            with open(self.env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if line.startswith('#') or not line:
                        continue
                    # Parse key=value pairs
                    if '=' in line:
                        key, value = line.split('=', 1)
                        self.config[key.strip()] = value.strip()

    def get(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get configuration value with priority: env var > .env file > default"""
        # Priority 1: Environment variable
        env_value = os.environ.get(key)
        if env_value is not None:
            return env_value

        # Priority 2: .env file
        if key in self.config:
            return self.config[key]

        # Priority 3: Default value
        return default

    def get_rom_language(self) -> str:
        """Get ROM language setting (JP/EN -> japanese/english)"""
        lang_code = self.get('ROM_LANGUAGE', 'EN').upper()
        if lang_code == 'JP':
            return 'japanese'
        elif lang_code == 'EN':
            return 'english'
        else:
            print(f"[ConfigLoader] Unknown ROM_LANGUAGE: {lang_code}, defaulting to english")
            return 'english'

    def get_model_output_language(self) -> str:
        """Get model output language setting"""
        lang_code = self.get('MODEL_OUTPUT_LANGUAGE', 'EN').upper()
        return lang_code

    def is_debug_enabled(self) -> bool:
        """Check if debug mode is enabled"""
        debug = self.get('DEBUG_LANGUAGE_DETECTION', 'false').lower()
        return debug in ['true', '1', 'yes', 'on']

# Global config instance
config = ConfigLoader()