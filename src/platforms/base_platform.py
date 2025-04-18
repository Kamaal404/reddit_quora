"""
Base platform class for all social media platforms.
"""

import logging
import os
import random
import time
from abc import ABC, abstractmethod
from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Optional, Tuple, Union

from src.core.content_analyzer import ContentAnalyzer
from src.core.comment_generator import CommentGenerator
from src.core.engagement_tracker import EngagementTracker
from src.config.niches import NICHES

logger = logging.getLogger(__name__)


class BasePlatform(ABC):
    """
    Abstract base class for all social media platform implementations.
    
    This class defines the common interface that all platform-specific
    implementations must adhere to.
    """

    def __init__(self, config: Dict[str, Any], platform_name: str, dry_run: bool = False):
        """
        Initialize the platform with configuration and credentials.
        
        Args:
            config: Dictionary containing platform configuration
            platform_name: Name of the platform (e.g., 'reddit', 'quora')
            dry_run: If True, simulate actions instead of performing them
        """
        self.config = config
        self.platform_name = platform_name
        self.dry_run = dry_run
        
        # Extract platform-specific config
        platforms_config = config.get('platforms', {})
        platform_config = platforms_config.get(platform_name, {}) if isinstance(platforms_config, dict) else {}
        
        # Initialize comment counter
        self.comments_today = 0
        self.max_daily_comments = platform_config.get('max_daily_comments', 10)
        self.last_comment_time = None
        
        # Comment delay in seconds (min, max)
        self.comment_delay_range = platform_config.get('comment_delay_range', [60, 180])
        
        # Set up engagement tracker
        data_directory = os.path.join(config.get('data_directory', 'data'), platform_name)
        self.engagement_tracker = EngagementTracker(data_directory)
        
        # Initialize content analyzer and comment generator
        self.content_analyzer = ContentAnalyzer(config)
        self.comment_generator = CommentGenerator(config)
        
        # Keywords and niches
        self.keywords = platform_config.get('keywords', [])
        
        # Initialize niches support from dedicated module
        self.niches_enabled = config.get("general", {}).get("niches_enabled", False)
        self.enabled_niches = list(NICHES.keys()) if self.niches_enabled else []
        self.current_niche = None
        
        # Initialize content counters
        self.today_comment_count = 0
        self.last_date = date.today()
        
        # Track IDs of content we've already engaged with to avoid duplicates
        self.engaged_content_ids = set()
        
        logger.info(f"Initialized {platform_name} platform")
        
    def _reset_daily_counters_if_needed(self) -> None:
        """Reset daily counters if it's a new day."""
        today = date.today()
        if today != self.last_date:
            logger.info(
                f"New day detected. Resetting daily counters for {self.platform_name}."
            )
            self.today_comment_count = 0
            self.last_date = today
            
    def has_reached_daily_limit(self) -> bool:
        """
        Check if the platform has reached its daily comment limit.
        
        Returns:
            bool: True if daily limit reached, False otherwise
        """
        self._reset_daily_counters_if_needed()
        
        return self.today_comment_count >= self.max_daily_comments
        
    def increment_comment_count(self) -> None:
        """Increment the daily comment counter."""
        self.today_comment_count += 1
        logger.info(
            f"{self.platform_name} daily comment count: "
            f"{self.today_comment_count}/{self.max_daily_comments}"
        )
        
    def has_engaged_with(self, content_id: str) -> bool:
        """
        Check if we've already engaged with this content.
        
        Args:
            content_id: Unique identifier for the content
            
        Returns:
            bool: True if already engaged, False otherwise
        """
        return content_id in self.engaged_content_ids
        
    def mark_as_engaged(self, content_id: str) -> None:
        """
        Mark content as already engaged with.
        
        Args:
            content_id: Unique identifier for the content
        """
        self.engaged_content_ids.add(content_id)
        
    def set_current_niche(self, niche: str) -> None:
        """
        Set the current niche for this engagement session.
        
        Args:
            niche: The niche identifier
        """
        if niche in self.enabled_niches:
            self.current_niche = niche
            logger.info(f"Set current niche to: {niche}")
        else:
            logger.warning(f"Attempted to set invalid niche: {niche}. Using default behavior.")
            self.current_niche = None

    def get_niche_for_community(self, community_name: str) -> Optional[str]:
        """
        Get the niche associated with a community or topic.
        
        Args:
            community_name: The name of the community/subreddit/topic
            
        Returns:
            The niche identifier or None if not found
        """
        # Implementation will depend on the platform type (reddit or quora)
        # Override in subclasses
        return None

    def get_niche_keywords(self, niche: Optional[str] = None) -> List[str]:
        """
        Get keywords associated with a specific niche.
        
        Args:
            niche: The niche to get keywords for, or None to use current niche
            
        Returns:
            List of keywords for the niche
        """
        target_niche = niche or self.current_niche
        if not target_niche:
            return []
            
        if target_niche in NICHES:
            return NICHES[target_niche].get("keywords", [])
        return []
        
    @abstractmethod
    def authenticate(self) -> bool:
        """
        Authenticate with the platform API.
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        pass
        
    @abstractmethod
    def monitor_and_engage(self) -> List[Dict[str, Any]]:
        """
        Monitor the platform for engagement opportunities and post comments.
        
        Returns:
            List of dictionaries containing details about the engagements made
        """
        pass
        
    @abstractmethod
    def cleanup(self) -> None:
        """Clean up resources when shutting down."""
        pass

    def _check_daily_limit(self) -> bool:
        """
        Check if the daily comment limit has been reached.
        
        Returns:
            True if the limit has not been reached, False otherwise
        """
        if self.comments_today >= self.max_daily_comments:
            logger.warning(f"Daily comment limit reached ({self.max_daily_comments})")
            return False
        return True
        
    def _should_engage_with_content(self, content_id: str, content_type: str, 
                                    content_info: Dict[str, Any]) -> bool:
        """
        Determine whether to engage with specific content.
        
        Args:
            content_id: Unique identifier for the content
            content_type: Type of content (e.g., 'post', 'question')
            content_info: Dictionary containing content details
            
        Returns:
            True if should engage, False otherwise
        """
        # Check if already engaged with this content
        if self.engagement_tracker.has_engaged_with(self.platform_name, content_id):
            logger.info(f"Already engaged with content ID: {content_id}")
            return False
            
        # Extract text from content
        title = content_info.get('title', '')
        body = content_info.get('text', '')
        content_text = f"{title} {body}"
        
        # Get niche-specific keywords if applicable
        niche = content_info.get('niche')
        extra_keywords = self.get_niche_keywords(niche) if self.niches_enabled and niche else []
        
        # Check if content matches our criteria using the content analyzer
        product_matches, relevance_score = self.content_analyzer.analyze_content(
            content_text,
            extra_keywords=extra_keywords
        )
        
        # Define the minimum threshold for engagement
        platform_config = self.config.get('platforms', {}).get(self.platform_name, {})
        min_relevance = platform_config.get('relevance_threshold', 0.6)
        
        if relevance_score < min_relevance:
            logger.info(f"Content relevance too low: {relevance_score:.2f} < {min_relevance}")
            return False
            
        if not product_matches:
            logger.info("No product matches found for this content")
            return False
            
        # Store the analysis results in the content_info for later use
        content_info['relevance_score'] = relevance_score
        content_info['product_matches'] = product_matches
            
        return True
    
    def _record_engagement(self, content_id: str, content_type: str, 
                          engagement_type: str, metadata: Dict[str, Any]) -> None:
        """
        Record a new engagement with content.
        
        Args:
            content_id: Unique identifier for the content
            content_type: Type of content (e.g., 'post', 'question')
            engagement_type: Type of engagement (e.g., 'comment', 'answer')
            metadata: Additional metadata about the engagement
        """
        self.comments_today += 1
        self.last_comment_time = datetime.now()
        
        # Record in engagement tracker
        self.engagement_tracker.record_engagement(
            self.platform_name,
            content_id,
            content_type,
            engagement_type,
            metadata
        ) 