import os
import requests

class HttpCheckup:
    def check_http(self, endpoint: dict):
        try:
            url = endpoint["url"]
            method = endpoint["method"]
            headers = endpoint["headers"] if "headers" in endpoint else None
            body = endpoint["body"] if "body" in endpoint else None

            if method == "GET":
                print(f"GET request to {url} with headers {headers}")
                # if headers is not empty, add them to the request
                if headers is not None:
                    response = requests.get(url, headers=headers)
                else:
                    response = requests.get(url)

            elif method == "POST":
                print(f"POST request to {url} with headers {headers} and body {body}")
                # if headers is not empty, add them to the request
                if headers is not None:
                    response = requests.post(url, headers=headers, json=body)
                else:
                    response = requests.post(url, json=body)
            else:
                return f"Unsupported method: {method}"

            return response
        except Exception as e:
            return f"Error: {str(e)}"

    def check_otp_balance(self):
        print("Checking OTP balance")
        x = requests.get(f"https://2factor.in/API/V1/{os.getenv('2FACTOR_API_KEY')}/BAL/SMS")
        return x
