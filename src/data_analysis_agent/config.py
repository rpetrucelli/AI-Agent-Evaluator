from helper import get_openai_api_key
from openai import OpenAI

openai_api_key = get_openai_api_key()
client = OpenAI(api_key=openai_api_key)
MODEL = "gpt-4o-mini"
