"""
Reddit platform implementation for the QiLifeStore Social Media Engagement Bot.
"""

import logging
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

import praw
from praw.exceptions import PRAWException, RedditAPIException
from prawcore.exceptions import PrawcoreException
from praw.models import Submission

from src.platforms.base_platform import BasePlatform
from src.core.content_analyzer import ContentAnalyzer

logger = logging.getLogger(__name__)


class RedditPlatform(BasePlatform):
    """
    Reddit platform implementation using the PRAW library.
    """

    def __init__(self, config: Dict[str, Any], credentials: Dict[str, str], dry_run: bool = False):
        """
        Initialize the Reddit platform with configuration and credentials.
        
        Args:
            config: Dictionary containing platform configuration
            credentials: Reddit API credentials
            dry_run: If True, simulate actions instead of performing them
        """
        # Initialize the base platform with the platform name "reddit"
        super().__init__(config, "reddit", dry_run)
        
        # Store credentials separately
        self.credentials = credentials
        
        # Initialize Reddit client to None, will be set in authenticate()
        self.reddit = None
        
        # Extract Reddit-specific config
        reddit_config = config.get('platforms', {}).get('reddit', {})
        
        # Configure subreddit settings
        self.subreddits = reddit_config.get('subreddits', {})
        if not self.subreddits:
            logger.warning("No subreddits configured for Reddit platform")
        
        # Configure post filtering
        self.min_score = reddit_config.get('min_score', 5)
        self.max_posts_per_subreddit = reddit_config.get('max_posts_per_subreddit', 25)
        self.post_time_limit_hours = reddit_config.get('post_time_limit_hours', 24)
        
        # Authenticate with Reddit if not in dry run mode
        if not dry_run:
            self.authenticate()
            
        logger.info("Reddit platform initialized")

    def authenticate(self) -> bool:
        """
        Authenticate with the Reddit API.
        
        Returns:
            bool: True if authentication successful, False otherwise
        """
        try:
            logger.info("Authenticating with Reddit API")
            
            if not self.credentials:
                logger.error("Reddit credentials not provided")
                return False
                
            # Create Reddit client
            self.reddit = praw.Reddit(
                client_id=self.credentials.get("client_id"),
                client_secret=self.credentials.get("client_secret"),
                username=self.credentials.get("username"),
                password=self.credentials.get("password"),
                user_agent=self.credentials.get("user_agent", "QiLifeStore Social Bot v1.0")
            )
            
            # Verify authentication
            username = self.reddit.user.me().name
            logger.info(f"Successfully authenticated as {username}")
            return True
            
        except (PRAWException, PrawcoreException) as e:
            logger.error(f"Failed to authenticate with Reddit: {e}")
            return False
        except Exception as e:
            logger.exception(f"Unexpected error during Reddit authentication: {e}")
            return False

    def _get_weighted_subreddit(self) -> str:
        """
        Select a subreddit based on configured weights, prioritizing the current niche if set.
        
        Returns:
            str: Selected subreddit name
        """
        # If niches are enabled and a current niche is set, prioritize subreddits for that niche
        if self.niches_enabled and self.current_niche:
            # Filter subreddits by the current niche
            niche_subreddits = [sub for sub in self.subreddits if sub.get("niche") == self.current_niche]
            
            # If there are subreddits for this niche, select from them
            if niche_subreddits:
                # Extract subreddit names and weights
                names = [sub.get("name") for sub in niche_subreddits]
                weights = [sub.get("weight", 1) for sub in niche_subreddits]
                
                # Select weighted random subreddit
                logger.info(f"Selecting from {len(niche_subreddits)} subreddits for niche: {self.current_niche}")
                return random.choices(names, weights=weights, k=1)[0]
            else:
                logger.warning(f"No subreddits found for niche: {self.current_niche}, using all subreddits")
        
        # Fall back to selecting from all subreddits
        names = [sub.get("name") for sub in self.subreddits]
        weights = [sub.get("weight", 1) for sub in self.subreddits]
        
        # Select weighted random subreddit
        return random.choices(names, weights=weights, k=1)[0]

    def get_niche_for_community(self, subreddit_name: str) -> Optional[str]:
        """
        Get the niche associated with a subreddit.
        
        Args:
            subreddit_name: The name of the subreddit
            
        Returns:
            The niche identifier or None if not found
        """
        for subreddit in self.subreddits:
            if subreddit.get("name").lower() == subreddit_name.lower():
                return subreddit.get("niche")
        return None

    def _find_relevant_posts(self, subreddit: str, limit: int = 25) -> List[Dict[str, Any]]:
        """
        Find relevant posts in a subreddit.
        
        Args:
            subreddit: Name of the subreddit to search
            limit: Maximum number of posts to analyze
            
        Returns:
            List of dictionaries containing post data and relevance scores
        """
        relevant_posts = []
        
        # Get niche for this subreddit
        subreddit_niche = self.get_niche_for_community(subreddit)
        
        # In dry run mode, return simulated posts
        if self.dry_run or self.reddit is None:
            return self._simulate_posts(subreddit, subreddit_niche)
            
        try:
            # Access the subreddit
            sub = self.reddit.subreddit(subreddit)
            logger.info(f"Searching for posts in r/{subreddit}")
            
            # Get new and hot posts
            posts = list(sub.new(limit=limit//2)) + list(sub.hot(limit=limit//2))
            random.shuffle(posts)  # Randomize posts
            
            # Extract platform config for relevance threshold
            reddit_config = self.config.get('platforms', {}).get('reddit', {})
            relevance_threshold = reddit_config.get('relevance_threshold', 0.7)
            
            for post in posts[:limit]:
                # Skip posts we've already engaged with
                if self.engagement_tracker.has_engaged_with("reddit", post.id):
                    continue
                    
                # Extract post details
                post_data = {
                    "id": post.id,
                    "title": post.title,
                    "text": post.selftext,
                    "url": f"https://www.reddit.com{post.permalink}",
                    "created_utc": post.created_utc,
                    "author": post.author.name if post.author else "[deleted]",
                    "score": post.score,
                    "niche": subreddit_niche
                }
                
                # Skip deleted posts
                if post_data["author"] == "[deleted]" or post_data["text"] == "[deleted]":
                    continue
                    
                # Analyze post content with niche-specific keywords if applicable
                content_text = f"{post_data['title']} {post_data['text']}"
                extra_keywords = self.get_niche_keywords(subreddit_niche) if self.niches_enabled else []
                
                # Use the ContentAnalyzer from the parent class
                product_matches, relevance_score = self.content_analyzer.analyze_content(
                    content_text, 
                    extra_keywords=extra_keywords
                )
                
                # Adjust relevance threshold based on niche
                threshold = relevance_threshold
                if self.niches_enabled and subreddit_niche:
                    # Slightly lower threshold for niche-specific communities
                    threshold = threshold * 0.9
                
                # If post is relevant, add to list
                if relevance_score >= threshold:
                    post_data["relevance_score"] = relevance_score
                    post_data["product_matches"] = product_matches
                    relevant_posts.append(post_data)
                    logger.info(
                        f"Found relevant post: '{post_data['title']}' in r/{subreddit} "
                        f"with score {relevance_score:.2f}"
                    )
                    
            # Sort by relevance score (highest first)
            relevant_posts.sort(key=lambda x: x["relevance_score"], reverse=True)
            
            return relevant_posts
            
        except Exception as e:
            logger.exception(f"Error finding relevant posts: {e}")
            return self._simulate_posts(subreddit, subreddit_niche)
            
    def _simulate_posts(self, subreddit: str, niche: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Simulate Reddit posts for dry run testing.
        
        Args:
            subreddit: Subreddit name for simulation
            niche: Niche category for the subreddit
            
        Returns:
            List of simulated post dictionaries
        """
        fake_posts = []
        timestamp = int(time.time())
        
        # Generate posts based on niche if available
        if niche and niche in ["biohacking", "pemf", "spirituality", "frequency_healing", "health_tech"]:
            # Generate niche-specific content
            if niche == "biohacking":
                fake_posts.extend([
                    {
                        "id": f"sim_biohack_{timestamp}",
                        "title": "Has anyone used frequency devices for cognitive enhancement?",
                        "text": "I'm looking into different biohacking tools for improving focus and memory. Has anyone tried PEMF or other frequency-based devices for cognitive enhancement? What was your experience?",
                        "url": f"https://www.reddit.com/r/{subreddit}/comments/simulated_biohack",
                        "created_utc": timestamp - 3600,
                        "author": "biohacker101",
                        "score": 15,
                        "relevance_score": 0.85,
                        "product_matches": ["qi_coil", "qi_coil_aura", "quantum_frequencies"],
                        "niche": niche
                    }
                ])
            elif niche == "pemf":
                fake_posts.extend([
                    {
                        "id": f"sim_pemf_{timestamp}",
                        "title": "Best affordable PEMF devices for home use?",
                        "text": "I've been researching PEMF therapy for inflammation and sleep issues. What are some good affordable options for home use? Looking for something under $500 if possible.",
                        "url": f"https://www.reddit.com/r/{subreddit}/comments/simulated_pemf_post",
                        "created_utc": timestamp - 7200,
                        "author": "pemf_researcher",
                        "score": 23,
                        "relevance_score": 0.92,
                        "product_matches": ["qi_coil", "qi_coil_aura"],
                        "niche": niche
                    }
                ])
            elif niche == "spirituality":
                fake_posts.extend([
                    {
                        "id": f"sim_spirit_{timestamp}",
                        "title": "Energy healing frequencies - scientific basis?",
                        "text": "I'm interested in the intersection of spirituality and science. Do frequency-based energy healing methods have any scientific backing? Has anyone experienced genuine benefits from these approaches?",
                        "url": f"https://www.reddit.com/r/{subreddit}/comments/simulated_spirit_post",
                        "created_utc": timestamp - 10800,
                        "author": "spirit_seeker",
                        "score": 42,
                        "relevance_score": 0.88,
                        "product_matches": ["quantum_frequencies", "qi_coil"],
                        "niche": niche
                    }
                ])
            elif niche == "frequency_healing":
                fake_posts.extend([
                    {
                        "id": f"sim_freq_{timestamp}",
                        "title": "Specific frequencies for pain relief?",
                        "text": "I've heard that certain specific frequencies can help with different types of pain. Does anyone have experience with this? What frequencies work best for joint pain vs. muscle pain?",
                        "url": f"https://www.reddit.com/r/{subreddit}/comments/simulated_freq_post",
                        "created_utc": timestamp - 14400,
                        "author": "freq_explorer",
                        "score": 18,
                        "relevance_score": 0.9,
                        "product_matches": ["quantum_frequencies", "qi_coil"],
                        "niche": niche
                    }
                ])
            elif niche == "health_tech":
                fake_posts.extend([
                    {
                        "id": f"sim_tech_{timestamp}",
                        "title": "Red light therapy vs PEMF: which technology is more promising?",
                        "text": "I'm interested in both red light therapy and PEMF for wellness. For those who've tried both, which technology do you find more effective and why? Are there devices that combine both?",
                        "url": f"https://www.reddit.com/r/{subreddit}/comments/simulated_tech_post",
                        "created_utc": timestamp - 18000,
                        "author": "tech_health_enthusiast",
                        "score": 31,
                        "relevance_score": 0.87,
                        "product_matches": ["qi_red_light_therapy", "qi_coil", "qi_coil_aura"],
                        "niche": niche
                    }
                ])
        else:
            # Default simulated posts if no niche or unrecognized niche
            fake_posts.extend([
                {
                    "id": f"sim_{timestamp}",
                    "title": f"Question about frequency healing in r/{subreddit}",
                    "text": "Has anyone tried PEMF or frequency healing technology? I'm looking for recommendations.",
                    "url": f"https://www.reddit.com/r/{subreddit}/comments/simulated_post",
                    "created_utc": timestamp - 3600,
                    "author": "curious_user",
                    "score": 12,
                    "relevance_score": 0.82,
                    "product_matches": ["qi_coil", "quantum_frequencies"],
                    "niche": niche
                }
            ])
            
        return fake_posts

    def _post_comment(self, submission: Submission, comment_text: str) -> bool:
        """
        Post a comment on a Reddit submission.
        
        Args:
            submission: PRAW Submission object to comment on
            comment_text: Text content of the comment
            
        Returns:
            True if comment was posted successfully, False otherwise
        """
        if self.dry_run:
            logger.info(f"[DRY RUN] Would post comment on '{submission.title}'")
            logger.info(f"[DRY RUN] Comment text: {comment_text}")
            
            # Record the simulated engagement
            self._record_engagement(
                submission.id,
                "post",
                "comment",
                {
                    "title": submission.title,
                    "subreddit": submission.subreddit.display_name,
                    "comment": comment_text,
                    "simulated": True
                }
            )
            return True
            
        try:
            # Add a delay before commenting to seem more natural
            # Get delay range from config
            reddit_config = self.config.get('platforms', {}).get('reddit', {})
            delay_range = reddit_config.get('comment_delay_range', {})
            min_delay = delay_range.get('min', 60)  # Default 1 minute
            max_delay = delay_range.get('max', 300)  # Default 5 minutes
            
            delay = random.randint(min_delay, max_delay)
            logger.info(f"Adding delay of {delay} seconds before commenting")
            time.sleep(delay)
            
            # Post the comment
            comment = submission.reply(comment_text)
            logger.info(f"Posted comment on '{submission.title}' (ID: {comment.id})")
            
            # Record the engagement
            self._record_engagement(
                submission.id,
                "post",
                "comment",
                {
                    "title": submission.title,
                    "subreddit": submission.subreddit.display_name,
                    "comment": comment_text,
                    "comment_id": comment.id
                }
            )
            return True
            
        except PRAWException as e:
            logger.error(f"Error posting comment: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error posting comment: {str(e)}")
            return False

    def monitor_and_engage(self) -> None:
        """
        Monitor Reddit for relevant posts and engage with them.
        
        This is the main method that should be called regularly to monitor
        and engage with content on the platform.
        """
        if not self.reddit:
            logger.error("Reddit client not authenticated. Call authenticate() first.")
            return
            
        if not self._check_daily_limit():
            return
            
        # Get a weighted subreddit to monitor
        subreddit_name = self._get_weighted_subreddit()
        if not subreddit_name:
            logger.warning("No subreddit selected for monitoring")
            return
            
        logger.info(f"Monitoring subreddit: r/{subreddit_name}")
        
        # Find relevant posts
        posts = self._find_relevant_posts(subreddit_name)
        
        if not posts:
            logger.info(f"No relevant posts found in r/{subreddit_name}")
            return
            
        # Process each post
        for post in posts:
            post_id = post.id
            
            # Skip if already engaged with this post
            if self.engagement_tracker.has_engaged_with("reddit", post_id):
                logger.debug(f"Already engaged with post: {post.title}")
                continue
                
            # Extract post information for content analysis
            post_info = {
                "title": post.title,
                "text": post.selftext,
                "subreddit": post.subreddit.display_name,
                "score": post.score,
                "url": f"https://reddit.com{post.permalink}",
                "niche": self.get_niche_for_community(post.subreddit.display_name)
            }
            
            # Check if we should engage with this post
            if not self._should_engage_with_content(post_id, "post", post_info):
                continue
                
            # Generate a comment for the post
            comment_text = self.comment_generator.generate_comment(
                platform="reddit",
                content_text=f"{post.title} {post.selftext}",
                product_matches=post_info.get("product_matches", []), 
                relevance_score=post_info.get("relevance_score", 0),
                niche=post_info.get("niche")
            )
            
            if not comment_text:
                logger.warning(f"Failed to generate comment for post: {post.title}")
                continue
                
            # Post the comment
            success = self._post_comment(post, comment_text)
            
            if success and not self._check_daily_limit():
                break

    def cleanup(self) -> None:
        """Clean up resources when shutting down."""
        logger.info("Cleaning up Reddit platform resources")
        # Nothing specific to clean up for PRAW
        self.reddit = None 