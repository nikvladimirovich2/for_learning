import os
import dotenv 

dotenv.load_dotenv('.env')

api_key = os.environ['api_key']
print(api_key)
# print(os.getenv("api_key"))

# def my_key(api_key):
#     load_dotenv()
#     print(api_key)
