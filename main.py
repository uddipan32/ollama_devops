import os
import dotenv
import asyncio

from src.mongodb_helper import ConnectMongoDB
from src.connect_ollama import ConnectOllama
from src.slack_helper import SlackBot
from src.scheduler import Scheduler

def main():
    dotenv.load_dotenv()
    # connect mongodb 
    mongodb = ConnectMongoDB(os.getenv("MONGODB_URI"))
    # ollama
    ollama = ConnectOllama()
    # connect slack
    slack = SlackBot(mongodb, ollama)
    # asyncio.run(slack.listen())
    # scheduler
    scheduler = Scheduler(mongodb, ollama)
    asyncio.run(scheduler.start_scheduler())

    return 

if __name__ == "__main__":
    main()