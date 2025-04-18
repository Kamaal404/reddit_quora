# QiLifeStore Social Media Engagement Bot

An automated solution for engaging with relevant discussions on Reddit and Quora to promote QiLifeStore.com products through a personalized approach.

## Overview

This bot monitors Reddit and Quora for discussions related to biohacking, PEMF therapy, spirituality, frequency healing, and health tech. It uses a fictional persona named "David Wong" to post contextually relevant comments that subtly promote QiLifeStore products.

## Features

- **Multi-platform Integration**: Engages with both Reddit and Quora
- **Intelligent Comment Generation**: Creates contextually appropriate, personalized responses
- **Scheduling System**: Configurable monitoring intervals with activity limitations
- **Safety and Rate Limiting**: Complies with platform policies to avoid detection
- **Performance Analytics**: Tracks engagement and effectiveness

## Products Promoted

The bot promotes six main products from QiLifeStore.com:
- Qi Coil
- Qi Coil Aura
- Quantum Frequencies
- Qi Resonance Sound Bed
- Qi Red Light Therapy
- Qi Wand

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/qilifestore-social-bot.git
cd qilifestore-social-bot

# Set up a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure credentials
cp config/credentials.example.yml config/credentials.yml
# Edit config/credentials.yml with your API keys and login information
```

## Usage

```bash
# Start the bot with default settings
python run.py

# Start with custom configuration
python run.py --config custom_config.yml
```

## Configuration

See `config/default.yml` for all available configuration options.

## Legal Notice

This bot is designed to comply with the terms of service of all platforms it interacts with. Users are responsible for ensuring their use of this tool complies with relevant platform policies and regulations.

## License

[MIT License](LICENSE) 