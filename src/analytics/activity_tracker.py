"""
Activity Tracker for monitoring and recording bot engagement activities.
"""

import json
import logging
import os
from datetime import datetime, date
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class ActivityTracker:
    """
    Tracks and records all bot engagement activities.
    
    This class is responsible for keeping track of all comments posted,
    their performance, and generating reports on bot activity.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the ActivityTracker.
        
        Args:
            config: Application configuration dictionary
        """
        self.config = config
        self.analytics_config = config.get("analytics", {})
        self.enabled = self.analytics_config.get("enabled", True)
        
        # Data storage
        self.engagements = []
        self.daily_stats = {}
        self.product_stats = {}
        
        # File paths
        self.data_dir = config.get("general", {}).get("data_directory", "data")
        self.engagements_file = os.path.join(self.data_dir, "engagements.json")
        self.stats_file = os.path.join(self.data_dir, "activity_stats.json")
        
        # Load saved data if exists
        self._load_data()

    def _load_data(self) -> None:
        """Load previously saved engagement and statistics data."""
        if not self.enabled:
            return
            
        try:
            # Create data directory if it doesn't exist
            if not os.path.exists(self.data_dir):
                os.makedirs(self.data_dir)
                
            # Load engagements
            if os.path.exists(self.engagements_file):
                with open(self.engagements_file, "r") as f:
                    self.engagements = json.load(f)
                logger.info(f"Loaded {len(self.engagements)} previous engagements")
                
            # Load statistics
            if os.path.exists(self.stats_file):
                with open(self.stats_file, "r") as f:
                    stats_data = json.load(f)
                    self.daily_stats = stats_data.get("daily_stats", {})
                    self.product_stats = stats_data.get("product_stats", {})
                logger.info("Loaded previous statistics data")
                
        except Exception as e:
            logger.error(f"Error loading activity data: {e}")
            # Initialize empty if loading fails
            self.engagements = []
            self.daily_stats = {}
            self.product_stats = {}

    def save_data(self) -> None:
        """Save engagement and statistics data to disk."""
        if not self.enabled:
            return
            
        try:
            # Create data directory if it doesn't exist
            if not os.path.exists(self.data_dir):
                os.makedirs(self.data_dir)
                
            # Save engagements
            with open(self.engagements_file, "w") as f:
                json.dump(self.engagements, f, indent=2)
                
            # Save statistics
            stats_data = {
                "daily_stats": self.daily_stats,
                "product_stats": self.product_stats
            }
            with open(self.stats_file, "w") as f:
                json.dump(stats_data, f, indent=2)
                
            logger.info("Saved activity data")
            
        except Exception as e:
            logger.error(f"Error saving activity data: {e}")

    def track_engagement(self, platform: str, engagement_data: Dict[str, Any]) -> None:
        """
        Track a new engagement (posted comment/answer).
        
        Args:
            platform: Platform name (reddit, quora)
            engagement_data: Dictionary containing engagement details
        """
        if not self.enabled:
            return
            
        try:
            # Add timestamp and platform if not present
            if "timestamp" not in engagement_data:
                engagement_data["timestamp"] = datetime.now().timestamp()
                
            if "platform" not in engagement_data:
                engagement_data["platform"] = platform
                
            # Add to engagements list
            self.engagements.append(engagement_data)
            
            # Update statistics
            self._update_statistics(platform, engagement_data)
            
            # Save data periodically (e.g., after every 5 engagements)
            if len(self.engagements) % 5 == 0:
                self.save_data()
                
            logger.info(f"Tracked engagement on {platform}")
            
        except Exception as e:
            logger.error(f"Error tracking engagement: {e}")

    def _update_statistics(self, platform: str, engagement_data: Dict[str, Any]) -> None:
        """
        Update statistical counters for reporting.
        
        Args:
            platform: Platform name (reddit, quora)
            engagement_data: Dictionary containing engagement details
        """
        # Get date string for daily stats
        timestamp = engagement_data.get("timestamp", datetime.now().timestamp())
        date_str = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d")
        
        # Update daily stats
        if date_str not in self.daily_stats:
            self.daily_stats[date_str] = {
                "reddit": {"count": 0, "relevance_sum": 0},
                "quora": {"count": 0, "relevance_sum": 0},
                "total": 0,
                "products": {}
            }
            
        # Increment counters
        self.daily_stats[date_str][platform]["count"] += 1
        self.daily_stats[date_str]["total"] += 1
        
        # Add relevance score if available
        relevance_score = engagement_data.get("relevance_score", 0)
        self.daily_stats[date_str][platform]["relevance_sum"] += relevance_score
        
        # Track products mentioned
        product_matches = engagement_data.get("product_matches", [])
        for product in product_matches:
            # Update daily product stats
            if product not in self.daily_stats[date_str]["products"]:
                self.daily_stats[date_str]["products"][product] = 0
            self.daily_stats[date_str]["products"][product] += 1
            
            # Update overall product stats
            if product not in self.product_stats:
                self.product_stats[product] = {
                    "total_mentions": 0,
                    "reddit_mentions": 0,
                    "quora_mentions": 0
                }
            self.product_stats[product]["total_mentions"] += 1
            self.product_stats[product][f"{platform}_mentions"] += 1

    def get_daily_report(self, date_str: Optional[str] = None) -> Dict[str, Any]:
        """
        Get a report of activity for a specific day.
        
        Args:
            date_str: Date string in format "YYYY-MM-DD" (default: today)
            
        Returns:
            Dictionary containing daily activity statistics
        """
        if not self.enabled:
            return {}
            
        if date_str is None:
            date_str = datetime.now().strftime("%Y-%m-%d")
            
        # Get stats for the specified day
        daily_data = self.daily_stats.get(date_str, {
            "reddit": {"count": 0, "relevance_sum": 0},
            "quora": {"count": 0, "relevance_sum": 0},
            "total": 0,
            "products": {}
        })
        
        # Calculate average relevance scores
        reddit_avg_relevance = 0
        quora_avg_relevance = 0
        
        if daily_data["reddit"]["count"] > 0:
            reddit_avg_relevance = (
                daily_data["reddit"]["relevance_sum"] / daily_data["reddit"]["count"]
            )
            
        if daily_data["quora"]["count"] > 0:
            quora_avg_relevance = (
                daily_data["quora"]["relevance_sum"] / daily_data["quora"]["count"]
            )
            
        # Create report
        report = {
            "date": date_str,
            "total_engagements": daily_data["total"],
            "platforms": {
                "reddit": {
                    "count": daily_data["reddit"]["count"],
                    "avg_relevance": round(reddit_avg_relevance, 2)
                },
                "quora": {
                    "count": daily_data["quora"]["count"],
                    "avg_relevance": round(quora_avg_relevance, 2)
                }
            },
            "products": daily_data.get("products", {})
        }
        
        return report

    def get_product_report(self) -> Dict[str, Any]:
        """
        Get a report of product mentions across all engagements.
        
        Returns:
            Dictionary containing product mention statistics
        """
        if not self.enabled:
            return {}
            
        # Get overall product stats
        product_report = {
            "total_products": len(self.product_stats),
            "products": self.product_stats
        }
        
        # Calculate most mentioned products
        sorted_products = sorted(
            self.product_stats.items(),
            key=lambda x: x[1]["total_mentions"],
            reverse=True
        )
        
        product_report["most_mentioned"] = [
            {"id": product_id, "mentions": data["total_mentions"]}
            for product_id, data in sorted_products[:3]
        ]
        
        return product_report

    def get_engagement_summary(self, days: int = 7) -> Dict[str, Any]:
        """
        Get a summary of recent engagement activities.
        
        Args:
            days: Number of days to include in summary (default: 7)
            
        Returns:
            Dictionary containing engagement summary
        """
        if not self.enabled:
            return {}
            
        # Calculate date cutoff
        today = datetime.now().date()
        date_cutoff = today.toordinal() - days
        
        # Filter recent engagements
        recent_engagements = []
        for engagement in self.engagements:
            timestamp = engagement.get("timestamp", 0)
            engagement_date = datetime.fromtimestamp(timestamp).date()
            
            if engagement_date.toordinal() >= date_cutoff:
                recent_engagements.append(engagement)
                
        # Count platform engagements
        platform_counts = {"reddit": 0, "quora": 0}
        for engagement in recent_engagements:
            platform = engagement.get("platform", "unknown")
            if platform in platform_counts:
                platform_counts[platform] += 1
                
        # Create summary
        summary = {
            "period": f"Last {days} days",
            "total_engagements": len(recent_engagements),
            "platform_breakdown": platform_counts,
            "daily_average": round(len(recent_engagements) / days, 1)
        }
        
        return summary 