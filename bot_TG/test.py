import os
import json
import openai
from dotenv import load_dotenv
openai.organization = "org-jQiQUXq2cDw7pTdCAXjdczQt"
openai.api_key = os.getenv("CHAT_GPT3_API_KEY")
openai.Model.list()