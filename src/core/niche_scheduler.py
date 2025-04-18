"""
Niche Scheduler for optimized niche rotation across platforms.

This module manages the scheduling and rotation of niches for social media platforms,
ensuring balanced coverage and optimal engagement across all niches.
"""

import logging
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple

from src.config.niches import NICHES

logger = logging.getLogger(__name__)

class NicheScheduler:
    """
    Manages niche rotation and scheduling for social media platforms.
    
    This class ensures optimal coverage across niches and prevents repetition,
    while also prioritizing niches based on configured weights and performance.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the niche scheduler.
        
        Args:
            config: Application configuration dictionary
        """
        self.config = config
        self.niches_enabled = config.get("general", {}).get("niches_enabled", False)
        
        # Initialize niches from module
        self.niches = list(NICHES.keys())
        
        # Initialize niche history for each platform
        self.niche_history: Dict[str, List[Dict[str, Any]]] = {
            "reddit": [],
            "quora": []
        }
        
        # Custom weights for niches (higher means more priority)
        self.niche_weights = {
            "pemf": 5,               # Primary focus
            "frequency_healing": 4,  # Secondary focus
            "biohacking": 3,
            "spirituality": 3,
            "health_tech": 2
        }
        
        # Last used niche per platform
        self.last_used: Dict[str, Optional[str]] = {
            "reddit": None,
            "quora": None
        }
        
        # Performance tracking for adaptive scheduling
        self.niche_performance: Dict[str, Dict[str, float]] = {}
        for niche in self.niches:
            self.niche_performance[niche] = {
                "engagement_rate": 1.0,  # Base engagement rate
                "success_rate": 1.0,     # Success rate for comments
                "priority_boost": 0.0    # Dynamic boost based on performance
            }
            
        logger.info(f"Initialized NicheScheduler with {len(self.niches)} niches")
        
    def record_niche_use(self, platform: str, niche: str, 
                         timestamp: Optional[datetime] = None) -> None:
        """
        Record the use of a niche on a specific platform.
        
        Args:
            platform: Platform name (e.g., 'reddit', 'quora')
            niche: Niche that was used
            timestamp: When the niche was used (defaults to now)
        """
        if timestamp is None:
            timestamp = datetime.now()
            
        # Record the use
        self.niche_history[platform].append({
            "niche": niche,
            "timestamp": timestamp
        })
        
        # Limit history size
        if len(self.niche_history[platform]) > 50:
            self.niche_history[platform] = self.niche_history[platform][-50:]
            
        # Update last used
        self.last_used[platform] = niche
    
    def record_niche_performance(self, niche: str, 
                                engagement_rate: Optional[float] = None,
                                success_rate: Optional[float] = None) -> None:
        """
        Update performance metrics for a niche to influence future scheduling.
        
        Args:
            niche: Niche to update
            engagement_rate: Rate of engagement (0-1)
            success_rate: Rate of successful comments (0-1)
        """
        if niche not in self.niche_performance:
            self.niche_performance[niche] = {
                "engagement_rate": 1.0,
                "success_rate": 1.0,
                "priority_boost": 0.0
            }
            
        # Update metrics if provided
        if engagement_rate is not None:
            # Use exponential moving average to update
            current = self.niche_performance[niche]["engagement_rate"]
            self.niche_performance[niche]["engagement_rate"] = (0.7 * current) + (0.3 * engagement_rate)
            
        if success_rate is not None:
            current = self.niche_performance[niche]["success_rate"]
            self.niche_performance[niche]["success_rate"] = (0.7 * current) + (0.3 * success_rate)
            
        # Calculate priority boost based on performance
        engagement = self.niche_performance[niche]["engagement_rate"]
        success = self.niche_performance[niche]["success_rate"]
        self.niche_performance[niche]["priority_boost"] = (engagement * success) - 1.0
        
    def get_niche_usage_count(self, platform: str, niche: str, 
                             hours_back: int = 24) -> int:
        """
        Get the number of times a niche was used on a platform in a time period.
        
        Args:
            platform: Platform name
            niche: Niche to check
            hours_back: How many hours to look back
            
        Returns:
            Number of times the niche was used
        """
        cutoff_time = datetime.now() - timedelta(hours=hours_back)
        
        count = 0
        for entry in self.niche_history[platform]:
            if entry["niche"] == niche and entry["timestamp"] >= cutoff_time:
                count += 1
                
        return count
    
    def get_next_niche(self, platform: str) -> str:
        """
        Get the next niche to use for a specific platform based on optimal rotation.
        
        Args:
            platform: Platform name
            
        Returns:
            Niche name to use next
        """
        if not self.niches_enabled or not self.niches:
            # Default to first niche if available, otherwise None
            return self.niches[0] if self.niches else "pemf"
            
        # Get usage counts for the last 24 hours
        usage_counts = {}
        for niche in self.niches:
            usage_counts[niche] = self.get_niche_usage_count(platform, niche)
            
        # Get least used niches
        min_usage = min(usage_counts.values())
        least_used = [n for n, count in usage_counts.items() if count == min_usage]
        
        # If we have multiple least used niches, use weights to decide
        if len(least_used) > 1:
            weights = []
            niches = []
            
            for niche in least_used:
                base_weight = self.niche_weights.get(niche, 1)
                performance_boost = self.niche_performance.get(niche, {}).get("priority_boost", 0)
                
                # Avoid the immediately previous niche if possible
                recency_penalty = 0.5 if niche == self.last_used[platform] else 1.0
                
                effective_weight = (base_weight + performance_boost) * recency_penalty
                weights.append(max(0.1, effective_weight))  # Ensure weight is positive
                niches.append(niche)
                
            # Select weighted random niche from least used
            selected_niche = random.choices(niches, weights=weights, k=1)[0]
        else:
            # Only one least used niche
            selected_niche = least_used[0]
            
        # Record that we're using this niche
        self.record_niche_use(platform, selected_niche)
        
        logger.info(f"Selected niche for {platform}: {selected_niche} (Usage in last 24h: {usage_counts[selected_niche]})")
        return selected_niche
    
    def get_niche_rotation_plan(self, platform: str, hours: int = 24) -> List[str]:
        """
        Create an optimized niche rotation plan for a given time period.
        
        Args:
            platform: Platform name
            hours: Number of hours to plan for
            
        Returns:
            List of niches in optimal rotation order
        """
        # For full rotation, first sort niches by priority
        sorted_niches = sorted(
            self.niches, 
            key=lambda n: self.niche_weights.get(n, 1) + self.niche_performance.get(n, {}).get("priority_boost", 0),
            reverse=True
        )
        
        # Create a balanced plan with higher priority niches appearing more often
        plan = []
        total_slots = hours
        
        # Allocate slots based on relative priority
        total_weight = sum(self.niche_weights.get(n, 1) for n in self.niches)
        
        for niche in sorted_niches:
            weight = self.niche_weights.get(niche, 1)
            slots = max(1, int((weight / total_weight) * total_slots))
            
            for _ in range(slots):
                plan.append(niche)
                
        # Randomize the order but ensure variety (no consecutive repeats if possible)
        random.shuffle(plan)
        
        # If plan is shorter than requested hours, extend it
        while len(plan) < hours:
            plan.extend(random.sample(sorted_niches, min(hours - len(plan), len(sorted_niches))))
            
        # Trim to requested hours
        plan = plan[:hours]
        
        return plan 