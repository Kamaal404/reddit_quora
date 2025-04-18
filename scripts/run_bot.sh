#!/bin/bash
# Script to run the QiLifeStore Social Media Engagement Bot

# Change to the project root directory
cd "$(dirname "$0")/.."

# Check for Python virtual environment
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate || source venv/Scripts/activate
fi

# Run the bot with provided arguments
python run.py "$@"

# Check the exit code
if [ $? -eq 0 ]; then
    echo "Bot execution completed successfully."
else
    echo "Bot execution failed. Check logs for details."
fi 