from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import os
from dotenv import load_dotenv
import time
import asyncio
import ssl

class SlackBot:
    def __init__(self, mongodb, ollama):
        load_dotenv()
        
        # Create a custom SSL context that ignores certificate verification
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE
        
        # Initialize the Slack client with the custom SSL context
        self.client = WebClient(
            token=os.environ["SLACK_TOKEN"],
            ssl=ssl_context
        )
        self.channel_id = os.environ["SLACK_CHANNEL_ID"]
        self.mongodb = mongodb
        self.ollama = ollama
        
        # Keep track of the last processed message timestamp
        self.last_ts = None

    def send_message(self, text):
        try:
            response = self.client.chat_postMessage(
                channel=self.channel_id,
                text=text
            )
            return response
        except SlackApiError as e:
            print(f"Error sending message: {e.response['error']}")

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
                    function_to_call = tool["function"]["name"]
                    print(f"function_to_call: {function_to_call}")
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
                    limit=5  # Increased limit to get more messages
                )
                
                if result["messages"]:
                    tasks = []
                    for message in result["messages"]:
                        # Only process messages we haven't seen before
                        if (not hasattr(self, 'processed_messages')):
                            self.processed_messages = set()
                            
                        if message["ts"] not in self.processed_messages and "bot_id" not in message:
                            self.processed_messages.add(message["ts"])
                            # Create task for each message
                            task = asyncio.create_task(self._handle_message(message))
                            tasks.append(task)
                    
                    # Wait for all message processing to complete
                    if tasks:
                        await asyncio.gather(*tasks)
                
                # Clean up old processed messages (optional)
                if hasattr(self, 'processed_messages') and len(self.processed_messages) > 1000:
                    self.processed_messages = set(list(self.processed_messages)[-1000:])
                
                # Sleep to avoid hitting rate limits
                await asyncio.sleep(1)

            except Exception as e:
                print(f"Error: {str(e)}")
                await asyncio.sleep(5)  # Wait longer if there's an error

    async def _handle_message(self, message):
        """Helper method to process a single message"""
        try:
            print(f"Processing message: {message['text']}")
            response = await self.process_message(message["text"])
            self.send_message(response)
        except Exception as e:
            print(f"Error processing message: {str(e)}") 