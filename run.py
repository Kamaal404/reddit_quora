#!/usr/bin/env python
"""
QiLifeStore Social Media Engagement Bot
Main entry point for the application.
"""

import argparse
import logging
import os
import sys
from pathlib import Path

# Add the src directory to the Python path
sys.path.append(str(Path(__file__).parent))

from src.core.bot_manager import BotManager
from src.utils.config_loader import ConfigLoader
from src.utils.logger import setup_logger


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="QiLifeStore Social Media Engagement Bot"
    )
    parser.add_argument(
        "--config",
        default="config/default.yml",
        help="Path to configuration file (default: config/default.yml)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        help="Set the logging level (default: INFO)",
    )
    parser.add_argument(
        "--platforms",
        nargs="+",
        choices=["reddit", "quora", "all"],
        default=["all"],
        help="Platforms to engage with (default: all)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without posting comments (for testing)",
    )
    return parser.parse_args()


def main():
    """Main function to run the social media bot."""
    args = parse_arguments()
    
    # Setup logging
    log_file = os.path.join("logs", "bot.log")
    setup_logger(log_file, args.log_level)
    logger = logging.getLogger(__name__)
    
    logger.info("Starting QiLifeStore Social Media Engagement Bot")
    
    try:
        # Load configuration
        config_loader = ConfigLoader(args.config)
        config = config_loader.load()
        
        # Update config with command line arguments
        if args.dry_run:
            config["dry_run"] = True
        
        # Determine which platforms to use
        platforms = args.platforms
        if "all" in platforms:
            platforms = ["reddit", "quora"]
        
        # Initialize and run the bot manager
        bot_manager = BotManager(config, platforms)
        bot_manager.start()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.exception(f"An error occurred: {e}")
        return 1
    
    logger.info("Bot execution completed")
    return 0


if __name__ == "__main__":
    sys.exit(main()) 