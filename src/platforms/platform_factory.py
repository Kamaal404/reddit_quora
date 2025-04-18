"""
Factory for creating platform-specific instances.
"""

import logging
from typing import Dict, List, Any, Optional

# Import platform specific classes
from src.platforms.base_platform import BasePlatform
from src.platforms.reddit_platform import RedditPlatform
from src.platforms.quora_platform import QuoraPlatform

# Import configuration modules
from src.config.products import PRODUCTS
from src.config.niches import NICHES
from src.config.persona import PERSONA

logger = logging.getLogger(__name__)


class PlatformFactory:
    """
    Factory class for creating platform-specific instances.
    
    This class centralizes the creation of different platform instances,
    making it easier to add new platforms in the future.
    """
    
    def create_platform(
        self,
        platform_name: str,
        config: Dict[str, Any],
        credentials: Optional[Dict[str, Any]] = None,
        dry_run: bool = False
    ) -> BasePlatform:
        """
        Create a platform instance based on the platform name.
        
        Args:
            platform_name: Name of the platform (e.g., 'reddit', 'quora')
            config: Configuration dictionary
            credentials: Platform-specific credentials (optional in dry run mode)
            dry_run: If True, simulate actions instead of performing them
        
        Returns:
            BasePlatform: An instance of the appropriate platform class
            
        Raises:
            ValueError: If the platform name is not supported
        """
        # Verify required configuration modules are available
        if not PRODUCTS:
            logger.warning("Products configuration module is empty")
            
        if not NICHES:
            logger.warning("Niches configuration module is empty")
            
        if not PERSONA:
            logger.warning("Persona configuration module is empty")
        
        # Create platform instance based on platform name
        platform_name = platform_name.lower()
        
        if platform_name == "reddit":
            if not credentials and not dry_run:
                raise ValueError("Reddit credentials are required when not in dry run mode")
            return RedditPlatform(config, credentials or {}, dry_run)
            
        elif platform_name == "quora":
            if not credentials and not dry_run:
                raise ValueError("Quora credentials are required when not in dry run mode")
            return QuoraPlatform(config, credentials or {}, dry_run)
            
        else:
            raise ValueError(f"Unsupported platform: {platform_name}") 