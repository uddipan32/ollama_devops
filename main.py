
from src.connect_ollama import ConnectOllama
import asyncio

def main():
    ollama = ConnectOllama()
    response = asyncio.run(ollama.chat("What is the capital of France?"))
    print(response)

if __name__ == "__main__":
    main()
