import schedule
import time
from dotenv import load_dotenv
from src.slack_helper import SlackBot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

class Scheduler:
    def __init__(self, mongodb, ollama):
        load_dotenv()
        self.scheduler = AsyncIOScheduler()
        self.mongodb = mongodb
        self.ollama = ollama
        self.schedule_job(self.sendGoodMorningMessage, trigger='interval', minutes=1)
        asyncio.get_event_loop().run_until_complete(self.start_scheduler())
    
    # send a unique good morning message to the channel so that the user knows that the bot is running
    async def sendGoodMorningMessage(self):
        print("Sending good morning message")

        response = await self.ollama.chat(message={
            "role": "user",
            "content": "Say good morning!"
        }, ignore_history=True)
        response = response["message"]["content"]
        print(response)
        slack_helper = SlackBot(self.mongodb, self.ollama)
        slack_helper.send_message(response)

    async def _run_job(self, job):
        # Properly await the coroutine
        await job()
        
    def schedule_job(self, job, trigger='cron', **trigger_args):
        # Wrap the job in an async function that can be called by the scheduler
        async def wrapper():
            await self._run_job(job)
            
        self.scheduler.add_job(wrapper, trigger, **trigger_args)
    
    async def start_scheduler(self):
        if not self.scheduler.running:
            self.scheduler.start()
            # Keep the scheduler running
            while True:
                await asyncio.sleep(1)

       


