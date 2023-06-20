import openai, os
import configparser
import time
config = configparser.ConfigParser()
config.read("config.ini.default")

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv()) # read local .env file

openai.api_key = os.getenv("OPENAI_API_KEY")

class ChatGPT:
    def __init__(self):
       pass
    
    def get_completion_from_messages(self, messages, 
                                    model="gpt-3.5-turbo", 
                                    temperature=0, 
                                    max_tokens=500,
                                    counter=0):
        
        if counter > 3:
            return "openai error: too many requests"
        try:
            response = openai.ChatCompletion.create(
                model=model,
                messages=messages,
                temperature=temperature, 
                max_tokens=max_tokens,
            )
            return response.choices[0].message["content"]
    
        except Exception as e:
            # RateLimitError ChatGPT only allows certain calls per minutes. If it fails then apply a 30 second waiting and try again
            print(f"Wait 30 seconds to run again to solve: {e}")
            time.sleep(30)
            return self.get_completion_from_messages(messages, counter=counter+1)
            
        
