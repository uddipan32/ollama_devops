from ollama import chat
from ollama import ChatResponse
from ollama import AsyncClient

class ConnectOllama:
    def __init__(self, model: str = "llama3.2:latest"):
        self.model = model
        self.message_history = []
        self.memory_size = 100

    async def chat(self, prompt: str) -> str:
        message = {'role': 'user', 'content': prompt}
        self.message_history.append(message)

        response = await AsyncClient().chat(
            model=self.model,
            messages=[message],
        )

        self.message_history.append({'role': 'assistant', 'content': response.message.content})
        self.clear_memory()
        return response.message.content

    def clear_memory(self):
        print(self.message_history)
        if len(self.message_history) > self.memory_size:
            self.message_history = self.message_history[-self.memory_size:]
