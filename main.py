import os
import dotenv
import asyncio

from src.mongodb_helper import ConnectMongoDB
from src.connect_ollama import ConnectOllama
from src.slack_helper import SlackBot

def main():
    dotenv.load_dotenv()

   

    # tools = [
    #         {
    #             "type": "function",
    #             "function": {
    #                 "name": "get_endpoints",
    #                 "description": "Get all API endpoints from the database.",
    #                 "parameters": {},
    #                 "required": [],
    #                 "examples": [
    #                     "get all endpoints",
    #                     "show me the endpoints",
    #                     "list endpoints"
    #                 ]
    #             }
    #         },
    #         {
    #             "type": "function",
    #             "function": {
    #                 "name": "get_endpoint_by_name",
    #                 "description": "Get an endpoint by its name.",
    #                 "parameters": {"name": "str"},
    #                 "required": ["name"],
    #                 "examples": [
    #                     "get endpoint by name test",
    #                     "show me the endpoint test",
    #                     "list endpoint test",
    #                     "details of endpoint test"
    #                 ]
    #             }
    #         }
    #     ]
     
    dotenv.load_dotenv()
    # connect mongodb 
    mongodb = ConnectMongoDB(os.getenv("MONGODB_URI"))

   
    tools = [
        mongodb.get_endpoints,
        mongodb.get_endpoint_by_name
    ]

    # add endpoint
    # mongodb.add_endpoint({
    #     "name": "test",
    #     "url": "https://api.example.com/test",
    #     "method": "GET",
    #     "headers": {"Authorization": "Bearer 1234567890"},
    #     "body": "{}"
    # })
    # get endpoints
    # endpoints = mongodb.get_endpoints()
    # print(list(endpoints))
    # ollama
    ollama = ConnectOllama()
    # message = {'role': 'user', 'content': "Get all endpoints"}

    # connect slack
    slack = SlackBot(mongodb, ollama)
    asyncio.run(slack.listen())
    return 

    while True:
        # get command line input
        command = input("Enter message: ")
        message = {'role': 'user', 'content': command}


        response = asyncio.run(ollama.chat(message, tools))
        # print(response)

            # Check if the model decided to use the provided function
        if not response["message"].get("tool_calls"):
            print("\nThe model didn't use the function. Its response was:")
            print(response["message"]["content"])
            return
        
        if response["message"].get("tool_calls"):
            # print(f"\nThe model used some tools")
            available_functions = {
                "get_endpoints": mongodb.get_endpoints,
                "get_endpoint_by_name": mongodb.get_endpoint_by_name,
            }
            for tool in response["message"]["tool_calls"]:
                function_to_call = available_functions[tool["function"]["name"]]
                print(f"function to call: {function_to_call}")

                if function_to_call == mongodb.get_endpoints:
                    function_response = function_to_call()
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
                    # First message with system prompt
                    message = {
                        'role': 'user', 
                        'content': f"The endpoints are: {function_response}. Please format them clearly."
                    }

                    print(f"message: {message}")

        
                    response1 = asyncio.run(ollama.chat(message, [], system_prompt))
                    print(f"function response: {response1['message']['content']}")
                # if function_to_call == mongodb.get_endpoint_by_name:
                #     function_response = function_to_call(tool["function"]["arguments"])
                #     system_prompt = {
                #         "role": "system",
                #         "content": system_prompt
                #     }
                #     # First message with system prompt
                #     message = {
                #         'role': 'user', 
                #         'content': function_response["function_content"]
                #     }
                #     print(f"message: {message}")
                #     response1 = asyncio.run(ollama.chat(message, [], system_prompt))
                #     print(f"function response: {response1['message']['content']}")

if __name__ == "__main__":
    main()