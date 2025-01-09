from ollama import chat
from ollama import ChatResponse
from ollama import AsyncClient

class ConnectOllama:
    def __init__(self, model: str = "llama3.2:latest"):
        self.model = model

    async def chat(self, prompt: str) -> str:
        message = {'role': 'user', 'content': prompt}
        response = await AsyncClient().chat(
            model=self.model,
            messages=[message],
        )

        return response.message.content
