from ollama import chat
from ollama import ChatResponse
from ollama import AsyncClient

class ConnectOllama:
    def __init__(self, model: str = "llama3.2:latest"):
        self.model = model
        self.message_history = []
        self.memory_size = 100
       

    async def chat(self, message: dict, tools: list = [], system_prompt: str = "") -> str:
        # self.message_history.append(message)
 # Initialize or update message history with system prompt
        if system_prompt and not self.message_history:
            self.message_history = [system_prompt]
        
        if message:
            self.message_history.append(message)
        response = await AsyncClient().chat(
            model=self.model,
            messages=self.message_history,
            tools=tools,
        )

        # self.message_history.append({'role': 'assistant', 'content': response.message.content})
        self.clear_memory()
        return response

    def clear_memory(self):
        print(self.message_history)
        if len(self.message_history) > self.memory_size:
            self.message_history = self.message_history[-self.memory_size:]
