import os
from dotenv import load_dotenv, find_dotenv
                     
def load_env():
    _ = load_dotenv(find_dotenv(), override=True)

def get_openai_api_key():
    #load_env()
    #openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_api_key = "your_key_here"
    return openai_api_key

def get_phoenix_endpoint():
    phoenix_endpoint = "http://localhost:6006/v1/traces"
    return phoenix_endpoint

