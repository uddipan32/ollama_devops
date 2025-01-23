from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
from dotenv import load_dotenv
import time
import asyncio

class SlackBot:
    def __init__(self, mongodb, ollama):
        load_dotenv()
        
        # Initialize the Slack client
        self.client = WebClient(token=os.environ["SLACK_TOKEN"])
        self.channel_id = os.environ["SLACK_CHANNEL_ID"]
        self.mongodb = mongodb
        self.ollama = ollama
        
        # Keep track of the last processed message timestamp
        self.last_ts = None

    async def process_message(self, message):
        try:
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "get_endpoints",
                        "description": "Get all API endpoints from the database. This is the only available function to retrieve endpoint information.",
                        "parameters": {},
                        "required": [],
                        "examples": [
                            "get all endpoints",
                            "show me the endpoints",
                            "list endpoints"
                        ]
                    }
                }
            ]

            # Process message with Ollama
            response = await self.ollama.chat(
                {'role': 'user', 'content': message}, 
                tools
            )

            # Handle function calls or regular responses
            if response["message"].get("tool_calls"):
                for tool in response["message"]["tool_calls"]:
                    if tool["function"]["name"] == "get_endpoints":
                        endpoints = self.mongodb.get_endpoints()
                        print(f"endpoints: {endpoints}")
                        system_prompt = {
                            "role": "system",
                            "content": """You are a helpful assistant that manages API endpoints. 
                            When showing endpoints, please format them clearly and highlight important details like:
                            - Endpoint name
                            - URL
                            - HTTP method
                            - Any authentication requirements
                        
                            Present the information in a structured and easy-to-read format."""
                        }
                        formatted_response = await self.ollama.chat(
                            {'role': 'user', 'content': f"The endpoints are: {endpoints}"},
                            [],
                            system_prompt
                        )
                        return formatted_response["message"]["content"]
            else:
                return response["message"]["content"]

        except Exception as e:
            return f"Sorry, an error occurred: {str(e)}"

    def send_message(self, text):
        try:
            response = self.client.chat_postMessage(
                channel=self.channel_id,
                text=text
            )
            return response
        except SlackApiError as e:
            print(f"Error sending message: {e.response['error']}")

    async def listen(self):
        print(f"Listening for messages in channel {self.channel_id}...")
        
        while True:
            try:
                # Get channel history
                result = self.client.conversations_history(
                    channel=self.channel_id,
                    limit=1  # Only get the latest message
                )
                
                if result["messages"]:
                    latest_message = result["messages"][0]
                    
                    # Only process new messages
                    if self.last_ts != latest_message["ts"]:
                        self.last_ts = latest_message["ts"]
                        
                        # Don't process bot messages
                        if "bot_id" not in latest_message:
                            print(f"Received message: {latest_message['text']}")
                            response = await self.process_message(latest_message["text"])
                            self.send_message(response)
                
                # Sleep to avoid hitting rate limits
                await asyncio.sleep(1)

            except Exception as e:
                print(f"Error: {str(e)}")
                await asyncio.sleep(5)  # Wait longer if there's an error 