from std.python import Python

def handleCall() raises:
    var requests = Python.import_module("requests")
    var json = Python.import_module("json")
    var dotenv = Python.import_module("dotenv")
    var config = dotenv.get_config()
    var api_key = String(config["OPENROUTER_KEY"])
    var endpoint = String(config["ENDPOINT"])

    var headers = Python.dict()
    headers["Authorization"] = "Bearer " + api_key
    headers["Content-Type"] = "application/json"
    headers["HTTP-Referer"] = "https://localhost:3000" 
    headers["X-Title"] = "Mojo OpenRouter Client"

    var payload = Python.dict()
    payload["model"] = "google/gemma-2-9b-it:free"
    
    var messages = Python.list()
    var user_message = Python.dict()
    user_message["role"] = "user"
    user_message["content"] = "Explain quantum computing in one short sentence."
    messages.append(user_message)
    
    payload["messages"] = messages

    print("Sending request to OpenRouter...")

    var response = requests.post(
        endpoint, 
        headers=headers, 
        data=json.dumps(payload)
    )

    if response.status_code == 200:
        var response_json = response.json()
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
