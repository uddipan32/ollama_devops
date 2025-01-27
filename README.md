# OLLAMA DEVTOOLS

Ollama DevTools is a Python-based DevOps toolkit for automating routine operations and monitoring system health. It features availability checks for websites and APIs, cron job management, an alert system for critical events, and system querying for resource and process information.

This is an AI Agent that uses OLLAMA to interact with the system and the user. It is designed to be used in a Slack channel. It is able to check the status of the endpoints, send messages to the user, and send messages to the Slack channel. Also can provide solutions to the endpoints that are not working.

## Requirements

- ollama
- python
- pip
- pymongo
- python-dotenv
- slack-bolt
- schedule
- APScheduler
- requests

## Installation

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

## ENV Variables

```bash
MONGODB_URI
SLACK_TOKEN
SLACK_CHANNEL_ID
2FACTOR_API_KEY
OLLAMA_MODEL
```
