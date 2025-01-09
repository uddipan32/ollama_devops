import os
import dotenv
import asyncio

from src.mongodb_helper import ConnectMongoDB
from src.connect_ollama import ConnectOllama

def main():
    dotenv.load_dotenv()
    # connect mongodb 
    mongodb = ConnectMongoDB(os.getenv("MONGODB_URI"))
    # add endpoint
    mongodb.add_endpoint({
        "name": "test",
        "url": "https://api.example.com/test",
        "method": "GET",
        "headers": {"Authorization": "Bearer 1234567890"},
        "body": "{}"
    })
    # get endpoints
    endpoints = mongodb.get_endpoints()
    print(list(endpoints))
    # ollama
    ollama = ConnectOllama()
    response = asyncio.run(ollama.chat("What is the capital of France?"))
    print(response)

if __name__ == "__main__":
    main()