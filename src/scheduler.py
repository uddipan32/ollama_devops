import schedule
import time
from dotenv import load_dotenv
from src.slack_helper import SlackBot
from src.http_checkup import HttpCheckup
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
from datetime import datetime

class Scheduler:
    def __init__(self, mongodb, ollama):
        load_dotenv()
        self.scheduler = AsyncIOScheduler()
        self.mongodb = mongodb
        self.ollama = ollama
        # schedule the job to run at 10:00 AM IST
        self.schedule_job(self.sendGoodMorningMessage, trigger='cron', hour=10, minute=0, timezone='Asia/Kolkata')
        self.schedule_job(self.check_endpoint_status, trigger='interval', minutes=5)
        asyncio.get_event_loop().run_until_complete(self.start_scheduler())
    
    # send a unique good morning message to the channel so that the user knows that the bot is running
    async def sendGoodMorningMessage(self):
        print("Sending good morning message")
        # get otp balance
        http_checkup = HttpCheckup()
        otp_balance = http_checkup.check_otp_balance()
        if otp_balance.status_code == 200:
            otp_balance = otp_balance.json()["Details"]
            print(otp_balance)
        else:
            otp_balance = "Error fetching OTP balance"
            return

        time_of_day = datetime.now().strftime("%H:%M")

        response = await self.ollama.chat(message={
            "role": "user",
            "content": "You are a helpful information bot. You greet the user in unique ways based on the time of day and also provide a summary of the OTP balance: " + str(otp_balance) + " The time of day is: " + time_of_day + "Do not ask for any information from the user. Just greet the user and provide the summary and the greeting."
        }, ignore_history=True)
        response = response["message"]["content"]
        slack_helper = SlackBot(self.mongodb, self.ollama)
        slack_helper.send_message(response)

    async def check_endpoint_status(self):
        http_checkup = HttpCheckup()
        endpoints = self.mongodb.get_endpoints()
        for endpoint in endpoints:
            response = http_checkup.check_http(endpoint)
            print(response)
            if isinstance(response, Exception):
                response = await self.ollama.chat(message={
                    "role": "user",
                    "content": "You are a helpful information bot. You are given a list of information and you need to provide a summary of the information. The information is as follows: " + str(response)
                }, ignore_history=True)
                response = response["message"]["content"]
                slack_helper = SlackBot(self.mongodb, self.ollama)
                slack_helper.send_message(response)
            else:
                print(f"Endpoint {endpoint['name']} is working fine")
       

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

       


