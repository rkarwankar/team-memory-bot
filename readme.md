markdown# Team Knowledge Memory Bot 🧠💬

A Discord bot that captures, stores, and retrieves team knowledge using Mem0 AI for persistent memory storage.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Setup and Installation](#setup-and-installation)
- [Usage](#usage)
- [Command Examples](#command-examples)
- [Example Results](#example-results)
- [Customization](#customization)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [License](#license)

## 🌟 Overview

Team Knowledge Memory Bot transforms team conversations into a searchable knowledge base. It monitors Discord channels, extracts important information, and makes it easily retrievable using natural language queries. By connecting to Mem0 AI's memory system, it provides persistent storage of team knowledge across time.

## ✨ Features

- 🤖 **Automatic Knowledge Extraction**: Identifies important information from team conversations
- 🧠 **Cloud-Based Memory Storage**: Leverages Mem0 AI for reliable knowledge persistence
- 🔍 **Vector-Based Semantic Search**: Finds information based on meaning, not just keywords
- 📝 **Knowledge Classification**: Organizes information by type (decisions, blockers, etc.)
- 💬 **Natural Language Queries**: Ask questions in plain language to retrieve information
- 📊 **Context Preservation**: Maintains the context in which information was shared
- 🔄 **Manual Saving**: Explicitly save important information with simple commands

## 🏗️ System Architecture

The Team Knowledge Memory Bot features a modular architecture with five key components:

1. **Discord Bot Layer:** Handles all user interactions and command processing through Discord.py, managing message events and command routing.
2. **Knowledge Processing Pipeline:** Extracts and classifies important information from messages, turning unstructured conversations into structured data.
3. **Memory System:** Integrates with Mem0 AI to provide persistent storage of team knowledge with contextual metadata.
4. **Vector Search Engine:** Enables semantic search capabilities through either Pinecone (cloud-based) or an in-memory implementation.
5. **Query Engine:** Processes natural language questions, retrieves relevant information, and generates concise, informative responses.

This design prioritizes modularity and extensibility, allowing components to be developed and tested independently while maintaining clean interfaces between layers.

![System Architecture Diagram](.\Images\sys_arch.JPG)

## 🛠️ Setup and Installation

Prerequisites

Python 3.10 or higher
A Discord bot token (from Discord Developer Portal)
A Mem0 AI API key
[Optional] A Pinecone API key for enhanced vector search

Installation Steps

Clone the repository:
bashgit clone https://github.com/yourusername/team-memory-bot.git
cd team-memory-bot

Create a virtual environment:
bashpython -m venv venv

# On Windows

venv\Scripts\activate

# On macOS/Linux

source venv/bin/activate

Install dependencies:
bashpip install -r requirements.txt

Create a .env file with your configuration:

# Discord Configuration

DISCORD_BOT_TOKEN=your_discord_bot_token_here
DISCORD_GUILD_ID=your_guild_id_here
MONITORED_CHANNELS=123456789012345678,234567890123456789

# Mem0 Configuration

MEM0_API_KEY=your_mem0_api_key_here

# Vector Database (Choose one)

VECTOR_DB=in_memory # or "pinecone"

# If using Pinecone

PINECONE_API_KEY=your_pinecone_api_key_here
PINECONE_ENVIRONMENT=your_pinecone_environment
PINECONE_INDEX_NAME=team-memory

Invite the bot to your server using the OAuth2 URL generator in the Discord Developer Portal (require bot permissions including read/send messages)

## File Structure

team-memory-bot/
├── .env # Environment variables
├── .gitignore # Git ignore file
├── README.md # Project documentation
├── requirements.txt # Python dependencies
├── src/
│ ├── **init**.py
│ ├── main.py # Bot entry point
│ ├── config.py # Configuration module
│ ├── bot/ # Discord bot modules
│ │ ├── **init**.py
│ │ ├── client.py # Bot client implementation
│ │ ├── commands.py # Bot command handlers
│ │ └── listeners.py # Message event listeners
│ ├── preprocessing/ # Text processing modules
│ │ ├── **init**.py
│ │ ├── extractor.py # Knowledge extraction
│ │ └── classifier.py # Message classification
│ ├── memory/ # Memory storage modules
│ │ ├── **init**.py
│ │ ├── mem0.py # Mem0 API integration
│ │ └── vector_store.py # Vector database handling
│ ├── query_engine/ # Query processing modules
│ │ ├── **init**.py
│ │ ├── engine.py # Query orchestration
│ │ └── rag.py # Response generation
│ └── utils/ # Utility functions
│ ├── **init**.py
│ └── helpers.py # Helper utilities
└── tests/ # Test suite
├── **init**.py
└── test_memory.py

## 🚀 Usage

Starting the Bot

Run the bot:
bashpython src/main.py

The bot will connect to Discord and start monitoring the channels specified in your .env file.

Commands

/help_memory - Show help information
/save [type] [content] - Manually save knowledge
/recent [type] [limit] - Show recent memories
/ask [question] - Ask a question about team knowledge

Memory Types

decision - Conclusions or choices made by the team
blocker - Obstacles or impediments to progress
status_update - Information about current progress
milestone - Completion of significant project phases
question - Requests for information or clarification
answer - Information provided in response to questions

## 📝 Command Examples

Saving Knowledge
/save decision We've decided to use React Native for our mobile app to maintain a single codebase for iOS and Android platforms.
/save blocker The integration with the third-party analytics service is blocked because their API is currently experiencing downtime.
/save status_update The notification system refactoring is now 80% complete and scheduled to be finished by the end of the week.
/save milestone We've successfully completed the beta launch with 500 early access users with 87% satisfaction rate.
Retrieving Knowledge
/recent 5
/recent decision 3
/ask What technology are we using for the mobile app?
/ask What's blocking the analytics integration?
/ask What's the status of the notification system?

## 📸 Example Results

1. Help Screen
   ![help_memory](.\Images\ss1.JPG)

2. Saving Knowledge
   ![Saving](.\Images\ss2.JPG)
3. Recent Commands
   ![Recent](.\Images\ss4.JPG)
   ![Recent](.\Images\ss5.JPG)
   ![Recent](.\Images\ss6.JPG)

4. Ask Commands
   ![Recent](.\Images\ss7.JPG)
   ![Recent](.\Images\ss8.JPG)

5. Mem0 Portal
   ![Mem0](.\Images\ss3.JPG)

## ⚙️ Customization

Configuring Monitored Channels
Update the MONITORED_CHANNELS in your .env file with comma-separated Discord channel IDs.
Using Different Vector Storage
The bot supports two vector storage options:

In-Memory Vector Store (default)
VECTOR_DB=in_memory

Pinecone (recommended for production)
VECTOR_DB=pinecone
PINECONE_API_KEY=your_pinecone_api_key
PINECONE_ENVIRONMENT=your_environment
PINECONE_INDEX_NAME=team-memory

Adjusting Response Format
Customize the response format by modifying the generate_rag_response function in src/query_engine/rag.py.

## 🔧 Troubleshooting

Bot Not Responding

Verify that your Discord bot token is correct
Ensure the bot has proper permissions in your Discord server
Check if the monitored channels are correctly set in .env
Look for error messages in the console output

Memory Retrieval Issues

Confirm your Mem0 API key is valid
Verify that memories are being saved properly
Check console logs for API errors
Test with simple queries first to verify functionality

Vector Search Problems

If using Pinecone, verify your API key and environment
Check that vector embeddings are generating correctly
Test with the in-memory vector store to isolate issues

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

Fork the repository
Create your feature branch (git checkout -b feature/amazing-feature)
Commit your changes (git commit -m 'Add some amazing feature')
Push to the branch (git push origin feature/amazing-feature)
Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.
