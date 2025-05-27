import json

import requests
api_key="sk-wMRk3xvAGOkLhZ7WQhezrv9JYyukspkMjRLFWpLzDwxfiAhF"
model="gemini-2.5-flash-preview-05-20"
def create_chat_response(formatted_prompt):
    payload = json.dumps({
    "messages": [
        {
            "role": "user",
            "content": formatted_prompt
        }
    ],
    "model": model,
    "temperature": 0.1,
    "top_p": 1.0,
    "stream": False
    })

    headers = {
        'Accept': 'application/json',
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    url = "https://yunwu.ai/v1/chat/completions"
    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)


create_chat_response("hello")