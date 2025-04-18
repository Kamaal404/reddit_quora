"""
Engagement Tracker for social media platforms.

This module tracks engagement metrics and history for the bot across different platforms.
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

class EngagementTracker:
    """
    Tracks engagement metrics and history for social media platforms.
    
    This class stores data about previous engagements, including:
    - Comments posted
    - Content engaged with
    - Performance metrics
    """
    
    def __init__(self, data_directory: str):
        """
        Initialize the engagement tracker.
        
        Args:
            data_directory: Directory to store engagement data
        """
        self.data_directory = data_directory
        self.engagement_data_file = os.path.join(data_directory, "engagement_history.json")
        self.engagement_data = self._load_engagement_data()
        
        # Ensure the data directory exists
        os.makedirs(data_directory, exist_ok=True)
    
    def _load_engagement_data(self) -> Dict[str, Any]:
        """
        Load engagement data from disk.
        
        Returns:
            Dictionary containing engagement data
        """
        if not os.path.exists(self.engagement_data_file):
            return {
                "platforms": {},
                "total_engagements": 0,
                "last_updated": datetime.now().isoformat()
            }
            
        try:
            with open(self.engagement_data_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logger.error(f"Error loading engagement data: {e}")
            return {
                "platforms": {},
                "total_engagements": 0,
                "last_updated": datetime.now().isoformat()
            }
    
    def _save_engagement_data(self) -> None:
        """Save engagement data to disk."""
        try:
            with open(self.engagement_data_file, 'w') as f:
                self.engagement_data["last_updated"] = datetime.now().isoformat()
                json.dump(self.engagement_data, f, indent=2)
        except IOError as e:
            logger.error(f"Error saving engagement data: {e}")
    
    def record_engagement(self, platform: str, content_id: str, 
                          content_type: str, engagement_type: str,
                          metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Record a new engagement with content.
        
        Args:
            platform: Platform name (e.g., 'reddit', 'quora')
            content_id: Unique identifier for the content
            content_type: Type of content (e.g., 'post', 'question')
            engagement_type: Type of engagement (e.g., 'comment', 'answer')
            metadata: Additional metadata about the engagement
        """
        if platform not in self.engagement_data["platforms"]:
            self.engagement_data["platforms"][platform] = {
                "engagements": [],
                "engagement_count": 0
            }
        
        # Record the engagement
        engagement = {
            "content_id": content_id,
            "content_type": content_type,
            "engagement_type": engagement_type,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self.engagement_data["platforms"][platform]["engagements"].append(engagement)
        self.engagement_data["platforms"][platform]["engagement_count"] += 1
        self.engagement_data["total_engagements"] += 1
        
        # Save after each engagement
        self._save_engagement_data()
        
        logger.info(f"Recorded {engagement_type} on {platform} for content ID: {content_id}")
    
    def has_engaged_with(self, platform: str, content_id: str) -> bool:
        """
        Check if the bot has already engaged with specific content.
        
        Args:
            platform: Platform name
            content_id: Unique identifier for the content
            
        Returns:
            True if already engaged, False otherwise
        """
        if platform not in self.engagement_data["platforms"]:
            return False
            
        for engagement in self.engagement_data["platforms"][platform]["engagements"]:
            if engagement["content_id"] == content_id:
                return True
                
        return False
    
    def get_platform_stats(self, platform: str) -> Dict[str, Any]:
        """
        Get engagement statistics for a specific platform.
        
        Args:
            platform: Platform name
            
        Returns:
            Dictionary with platform statistics
        """
        if platform not in self.engagement_data["platforms"]:
            return {
                "engagement_count": 0,
                "last_engagement": None
            }
            
        platform_data = self.engagement_data["platforms"][platform]
        engagements = platform_data["engagements"]
        
        stats = {
            "engagement_count": platform_data["engagement_count"],
            "last_engagement": engagements[-1]["timestamp"] if engagements else None
        }
        
        return stats
    
    def get_recent_engagements(self, platform: Optional[str] = None, 
                               limit: int = 10) -> List[Dict[str, Any]]:
        """
        Get most recent engagements.
        
        Args:
            platform: Optional platform to filter by
            limit: Maximum number of engagements to return
            
        Returns:
            List of recent engagements
        """
        recent = []
        
        if platform:
            if platform in self.engagement_data["platforms"]:
                engagements = self.engagement_data["platforms"][platform]["engagements"]
                recent = sorted(engagements, key=lambda e: e["timestamp"], reverse=True)[:limit]
        else:
            # Gather engagements from all platforms
            all_engagements = []
            for platform_data in self.engagement_data["platforms"].values():
                all_engagements.extend(platform_data["engagements"])
                
            recent = sorted(all_engagements, key=lambda e: e["timestamp"], reverse=True)[:limit]
            
        return recent
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Get a summary of all engagement data.
        
        Returns:
            Dictionary with engagement summary
        """
        platforms = {}
        for platform, data in self.engagement_data["platforms"].items():
            platforms[platform] = {
                "engagement_count": data["engagement_count"]
            }
            
        return {
            "total_engagements": self.engagement_data["total_engagements"],
            "platforms": platforms,
            "last_updated": self.engagement_data["last_updated"]
        }