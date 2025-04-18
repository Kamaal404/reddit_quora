#!/usr/bin/env python
"""
Setup script for the QiLifeStore Social Media Engagement Bot.
This script creates the necessary directories and initial files.
"""

import os
import sys
import shutil
from pathlib import Path


def create_directory(path):
    """Create a directory if it doesn't exist."""
    if not os.path.exists(path):
        os.makedirs(path)
        print(f"Created directory: {path}")


def create_file(path, content=""):
    """Create a file with optional content if it doesn't exist."""
    if not os.path.exists(path):
        with open(path, "w") as f:
            f.write(content)
        print(f"Created file: {path}")


def setup_environment():
    """Set up the project environment."""
    # Get project root directory
    root_dir = Path(__file__).parent.parent
    
    # Create required directories
    directories = [
        os.path.join(root_dir, "logs"),
        os.path.join(root_dir, "logs", "activity"),
        os.path.join(root_dir, "data"),
        os.path.join(root_dir, "data", "cache"),
        os.path.join(root_dir, "config"),
        os.path.join(root_dir, "src", "templates", "reddit"),
        os.path.join(root_dir, "src", "templates", "quora"),
    ]
    
    for directory in directories:
        create_directory(directory)
    
    # Create credentials file from example if it doesn't exist
    credentials_example = os.path.join(root_dir, "config", "credentials.example.yml")
    credentials_file = os.path.join(root_dir, "config", "credentials.yml")
    
    if os.path.exists(credentials_example) and not os.path.exists(credentials_file):
        shutil.copy(credentials_example, credentials_file)
        print(f"Created credentials file from example: {credentials_file}")
        print("IMPORTANT: Edit this file with your actual API credentials.")
    
    print("\nSetup complete. Your environment is ready.")
    print("To run the bot, use one of the following commands:")
    print("  - On Linux/Mac: scripts/run_bot.sh")
    print("  - On Windows: scripts\\run_bot.bat")


if __name__ == "__main__":
    setup_environment() 