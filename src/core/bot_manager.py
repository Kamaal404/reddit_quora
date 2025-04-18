"""
Bot Manager for coordinating different social media platforms.
"""

import logging
import time
from datetime import datetime, time as dt_time
from typing import Dict, List, Any, Optional
import random

import schedule

from src.platforms.platform_factory import PlatformFactory
from src.platforms.base_platform import BasePlatform
from src.analytics.activity_tracker import ActivityTracker
from src.utils.logger import get_activity_logger
from src.config.niches import NICHES
from src.core.niche_scheduler import NicheScheduler

logger = logging.getLogger(__name__)


class BotManager:
    """
    Manages the social media bot operations across platforms.
    
    This class coordinates the different platform-specific bots,
    handles scheduling, and ensures rate limits are respected.
    """

    def __init__(self, config: Dict[str, Any], platforms: List[str]):
        """
        Initialize the BotManager.
        
        Args:
            config: Application configuration dictionary
            platforms: List of platforms to use (e.g., ["reddit", "quora"])
        """
        self.config = config
        self.platform_names = platforms
        self.platform_instances: Dict[str, BasePlatform] = {}
        self.dry_run = config.get("general", {}).get("dry_run", False)
        self.activity_tracker = ActivityTracker(config)
        
        # Initialize the niche scheduler for optimized niche rotation
        self.niche_scheduler = NicheScheduler(config)
        
        # Niche configuration from dedicated module
        self.niches_enabled = config.get("general", {}).get("niches_enabled", False)
        self.enabled_niches = list(NICHES.keys()) if self.niches_enabled else []
        
        # Initialize platforms
        self._initialize_platforms()
        
        # Set up scheduling
        self._setup_scheduling()
        
        if self.dry_run:
            logger.warning("Running in DRY RUN mode. No comments will be posted.")
            
        if self.niches_enabled:
            logger.info(f"Niches enabled with {len(self.enabled_niches)} niches: {', '.join(self.enabled_niches)}")
            
            # Create and log the niche rotation plan for the next 24 hours
            for platform_name in self.platform_names:
                if platform_name in self.platform_instances:
                    rotation_plan = self.niche_scheduler.get_niche_rotation_plan(platform_name)
                    logger.info(f"Niche rotation plan for {platform_name} (next 24h): {rotation_plan}")

    def _initialize_platforms(self) -> None:
        """Initialize the platform-specific bot instances."""
        platform_factory = PlatformFactory()
        
        for platform_name in self.platform_names:
            platform_config = self.config.get("platforms", {}).get(platform_name)
            
            if not platform_config:
                logger.warning(f"No configuration found for platform: {platform_name}")
                continue
                
            if not platform_config.get("enabled", False):
                logger.info(f"Platform {platform_name} is disabled in configuration")
                continue
                
            # Get credentials for this platform
            credentials = self.config.get("credentials", {}).get(platform_name)
            if not credentials and not self.dry_run:
                logger.warning(
                    f"No credentials found for {platform_name}. "
                    "This platform will be skipped."
                )
                continue
                
            # Create platform instance
            try:
                platform_instance = platform_factory.create_platform(
                    platform_name,
                    self.config,
                    credentials,
                    self.dry_run
                )
                self.platform_instances[platform_name] = platform_instance
                logger.info(f"Initialized {platform_name} platform")
            except Exception as e:
                logger.exception(f"Failed to initialize {platform_name} platform: {e}")

    def _setup_scheduling(self) -> None:
        """Set up the scheduling for platform monitoring."""
        for platform_name, platform in self.platform_instances.items():
            platform_config = self.config.get("platforms", {}).get(platform_name, {})
            interval_minutes = platform_config.get("monitoring_interval", 60)
            
            # Schedule the monitoring task
            schedule.every(interval_minutes).minutes.do(
                self._run_platform_monitoring, platform_name=platform_name
            )
            
            logger.info(
                f"Scheduled {platform_name} monitoring every {interval_minutes} minutes"
            )

    def _is_within_active_hours(self) -> bool:
        """
        Check if the current time is within the configured active hours.
        
        Returns:
            bool: True if within active hours, False otherwise
        """
        active_hours = self.config.get("general", {}).get("active_hours", {})
        start_str = active_hours.get("start", "08:00")
        end_str = active_hours.get("end", "22:00")
        
        # Parse time strings
        start_time = dt_time.fromisoformat(start_str)
        end_time = dt_time.fromisoformat(end_str)
        
        # Get current time
        now = datetime.now().time()
        
        # Check if current time is within active hours
        if start_time <= end_time:
            return start_time <= now <= end_time
        else:  # Handle case where active hours cross midnight
            return now >= start_time or now <= end_time

    def _is_active_day(self) -> bool:
        """
        Check if today is an active day according to configuration.
        
        Returns:
            bool: True if today is an active day, False otherwise
        """
        active_days = self.config.get("general", {}).get("active_days", [])
        
        # If no active days specified, assume all days are active
        if not active_days:
            return True
            
        # Get current day of week
        current_day = datetime.now().strftime("%A").lower()
        
        return current_day in [day.lower() for day in active_days]

    def _select_niche_for_cycle(self) -> Optional[str]:
        """
        Select a niche for the current monitoring cycle using the niche scheduler.
        
        Returns:
            str: Selected niche name or None if niches not enabled
        """
        if not self.niches_enabled or not self.enabled_niches:
            return None
            
        # Let the niche scheduler decide the next optimal niche
        # We use the first platform in our list as the decision maker
        # This ensures coordinated niche selection across potentially multiple BotManager instances
        decision_platform = self.platform_names[0] if self.platform_names else "reddit"
            
        return self.niche_scheduler.get_next_niche(decision_platform)

    def _run_platform_monitoring(self, platform_name: str) -> None:
        """
        Run the monitoring and engagement process for a specific platform.
        
        Args:
            platform_name: The name of the platform to monitor
        """
        # Check if we should be active now
        if not self._is_within_active_hours():
            logger.info(f"Outside active hours, skipping {platform_name} monitoring")
            return
            
        if not self._is_active_day():
            logger.info(f"Not an active day, skipping {platform_name} monitoring")
            return
        
        platform = self.platform_instances.get(platform_name)
        if not platform:
            logger.error(f"Platform {platform_name} not initialized")
            return
            
        try:
            activity_logger = get_activity_logger(platform_name)
            activity_logger.info(f"Starting monitoring cycle for {platform_name}")
            
            # Check if we've reached the daily limit
            if platform.has_reached_daily_limit():
                logger.info(
                    f"{platform_name} has reached its daily comment limit. "
                    "Skipping this cycle."
                )
                return
            
            # Select niche for this cycle if enabled
            if self.niches_enabled:
                # Get the optimal niche from the scheduler for this specific platform
                selected_niche = self.niche_scheduler.get_next_niche(platform_name)
                
                if selected_niche:
                    platform.set_current_niche(selected_niche)
                    logger.info(f"Selected niche for {platform_name} monitoring: {selected_niche}")
                
            # Run the monitoring and posting process
            engagement_results = platform.monitor_and_engage()
            
            # Log and track activity
            if engagement_results:
                activity_logger.info(
                    f"Engagement results: {len(engagement_results)} comments posted"
                )
                
                # Update niche performance in the scheduler based on results
                for result in engagement_results:
                    niche = result.get('niche')
                    relevance_score = result.get('relevance_score', 0)
                    
                    if niche and self.niches_enabled:
                        # Use relevance score as a proxy for engagement quality
                        self.niche_scheduler.record_niche_performance(
                            niche, 
                            engagement_rate=min(1.0, relevance_score + 0.3),
                            success_rate=1.0  # Assume success if we got a result
                        )
                        
                    niche_info = f" (niche: {niche})" if niche else ""
                    activity_logger.info(
                        f"Posted comment on {result.get('url', 'unknown')} "
                        f"with relevance score {relevance_score}{niche_info}"
                    )
                    self.activity_tracker.track_engagement(
                        platform_name, result
                    )
            else:
                activity_logger.info("No engagement opportunities found")
                
                # If we're using niches, record a slightly lower success rate
                # for the current niche when we don't find opportunities
                current_niche = platform.current_niche
                if current_niche and self.niches_enabled:
                    self.niche_scheduler.record_niche_performance(
                        current_niche,
                        success_rate=0.8  # Slight penalty for not finding content
                    )
                
        except Exception as e:
            logger.exception(f"Error during {platform_name} monitoring cycle: {e}")
            
            # If there was an error with a specific niche, record poor performance
            current_niche = getattr(platform, 'current_niche', None)
            if current_niche and self.niches_enabled:
                self.niche_scheduler.record_niche_performance(
                    current_niche,
                    success_rate=0.5  # More significant penalty for errors
                )

    def start(self) -> None:
        """Start the bot manager and run the scheduling loop."""
        if not self.platform_instances:
            logger.error("No platforms were successfully initialized. Exiting.")
            return
            
        logger.info(
            f"Starting QiLifeStore Social Bot with platforms: "
            f"{', '.join(self.platform_instances.keys())}"
        )
        
        # Run an initial cycle for each platform
        for platform_name in self.platform_instances:
            logger.info(f"Running initial monitoring cycle for {platform_name}")
            self._run_platform_monitoring(platform_name)
        
        # Keep running until interrupted
        try:
            while True:
                schedule.run_pending()
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Bot manager stopped by user")
        except Exception as e:
            logger.exception(f"Unexpected error in bot manager: {e}")
        finally:
            # Clean up
            for platform_name, platform in self.platform_instances.items():
                try:
                    platform.cleanup()
                except Exception as e:
                    logger.error(f"Error cleaning up {platform_name} platform: {e}")
                    
            # Save analytics data
            try:
                self.activity_tracker.save_data()
            except Exception as e:
                logger.error(f"Error saving analytics data: {e}")
                
            logger.info("Bot manager shutdown complete") 