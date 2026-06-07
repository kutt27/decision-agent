from std.python import Python
from dotenv import dotenv_values, load_dotenv
from std.os import getenv

def test():
    var api_key: String = dotenv_values(".env")
    var key = api_key["OPENROUTER_KEY"]
    print(key)

def handleCall() raises:
    # 1. Import the Python requests library inside Mojo
    var requests = Python.import_module("requests")
    var json = Python.import_module("json")

    # 2. Define your API configuration
    # Note: Replace this with your actual API key or use an environment variable
    var api_key: String = "your_openrouter_api_key_here"
    var url: String = "https://openrouter.ai/api/v1/chat/completions"

    # 3. Set up headers (OpenRouter requires these)
    var headers = Python.dict()
    headers["Authorization"] = "Bearer " + api_key
    headers["Content-Type"] = "application/json"
    # OpenRouter rankings require these two optional headers to identify your app
    headers["HTTP-Referer"] = "https://localhost:3000" 
    headers["X-Title"] = "Mojo OpenRouter Client"

    # 4. Define the payload
    # We will use a popular free model tier like Google's Gemma 2 9b or Llama 3
    var payload = Python.dict()
    payload["model"] = "google/gemma-2-9b-it:free"
    
    # Create the messages list
    var messages = Python.list()
    var user_message = Python.dict()
    user_message["role"] = "user"
    user_message["content"] = "Explain quantum computing in one short sentence."
    messages.append(user_message)
    
    payload["messages"] = messages

    print("Sending request to OpenRouter...")

    # 5. Make the POST request
    var response = requests.post(
        url, 
        headers=headers, 
        data=json.dumps(payload)
    )

    # 6. Parse and handle the response
    if response.status_code == 200:
        var response_json = response.json()
        # Navigate the JSON structure to get the text response
        var choices = response_json["choices"]
        var first_choice = choices[0]
        var message = first_choice["message"]
        var content = message["content"]
        
        print("\n--- Response ---")
        print(content)
        print("----------------")
    else:
        print("Error:", response.status_code)
        print(response.text)
