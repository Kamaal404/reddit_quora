"""
Configuration loader for the QiLifeStore Social Media Engagement Bot.
"""

import logging
import os
from pathlib import Path
from typing import Dict, Any

import yaml

logger = logging.getLogger(__name__)


class ConfigLoader:
    """Load and validate configuration files."""

    def __init__(self, config_path: str):
        """
        Initialize the ConfigLoader.
        
        Args:
            config_path: Path to the main configuration file
        """
        self.config_path = config_path
        self.base_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent.parent

    def load(self) -> Dict[str, Any]:
        """
        Load the configuration from YAML files.
        
        Returns:
            Dict containing the merged configuration
        """
        logger.info(f"Loading configuration from {self.config_path}")
        
        # Load main configuration
        config = self._load_yaml(self.config_path)
        if not config:
            raise ValueError(f"Failed to load configuration from {self.config_path}")
        
        # Load credentials if available
        credentials_path = os.path.join(self.base_dir, "config", "credentials.yml")
        credentials = self._load_yaml(credentials_path)
        
        if not credentials:
            logger.warning(
                f"Credentials file not found at {credentials_path}. "
                "Using example credentials for reference only."
            )
            # Try to load example credentials for structure
            example_path = os.path.join(self.base_dir, "config", "credentials.example.yml")
            credentials = self._load_yaml(example_path)
            if credentials:
                # Mark as using example credentials
                credentials["_using_example"] = True
        
        # Merge configurations
        if credentials:
            config["credentials"] = credentials
        
        # Validate the configuration
        self._validate_config(config)
        
        return config

    def _load_yaml(self, file_path: str) -> Dict[str, Any]:
        """
        Load a YAML configuration file.
        
        Args:
            file_path: Path to the YAML file
            
        Returns:
            Dict containing the configuration or None if file not found
        """
        try:
            with open(file_path, "r") as file:
                return yaml.safe_load(file)
        except FileNotFoundError:
            logger.warning(f"Configuration file not found: {file_path}")
            return None
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML configuration: {e}")
            return None

    def _validate_config(self, config: Dict[str, Any]) -> None:
        """
        Validate the configuration.
        
        Args:
            config: Configuration dictionary to validate
        """
        # Check if using example credentials
        if config.get("credentials", {}).get("_using_example", False):
            logger.warning(
                "Using example credentials. The bot will not be able to post comments. "
                "Please create a credentials.yml file with your actual credentials."
            )
        
        # Check required sections
        required_sections = ["general", "platforms"]
        for section in required_sections:
            if section not in config:
                logger.warning(f"Missing required configuration section: {section}")
        
        # Check for products section - but note that we may be using the new products module instead
        if "products" not in config:
            try:
                from src.config.products import PRODUCTS
                logger.info(f"Products configuration not found in config file, but found {len(PRODUCTS)} products in products module.")
            except ImportError:
                logger.warning("Missing required configuration section: products, and no products module found.")
        
        # Check platform configurations
        if "platforms" in config:
            platforms = config["platforms"]
            
            # Validate Reddit configuration
            if "reddit" in platforms and platforms["reddit"].get("enabled", False):
                if not config.get("credentials", {}).get("reddit"):
                    logger.warning("Reddit is enabled but credentials are missing")
            
            # Validate Quora configuration
            if "quora" in platforms and platforms["quora"].get("enabled", False):
                if not config.get("credentials", {}).get("quora"):
                    logger.warning("Quora is enabled but credentials are missing") 