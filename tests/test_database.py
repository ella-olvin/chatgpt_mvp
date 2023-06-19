import sys
sys.path.append("/Users/ella/GIT_REPOS/chatgpt_mvp_v1")
from chatbot.database import AccessDatabase
from chatbot.chatgpt import ChatGPT
from utils import *
import re 

if __name__ == "__main__":
    database = AccessDatabase()
    ChatModel = ChatGPT()

    previous_messages = [
{'role': 'user', 'content': '####How do you generate your foot traffic data?####'},
{'role': 'assistant', 'content': '{"primary":"Data Generation and Characteristics", "secondary":"Data accuracy"}'},
{'role': 'assistant', 'content': 'Thank you for your question! Our foot traffic data is generated using location data and machine learning methodologies. For more information on data accuracy, please visit www.olvindataaccuracy.com.'},
{'role': 'user', 'content': '####How many retails stores do you have data for and how many devices do you analyze?####'},
{'role': 'assistant', 'content': '{"primary":"Data Generation and Characteristics", "secondary":"Data volumes"}'},
{'role': 'assistant', 'content': 'For information on data volumes, please visit www.olvindatavolumes.com. This document provides details on the number of retail stores we have data for and the number of devices we analyze.'},
{'role': 'user', 'content': '####How accurate is the data?####'},
{'role': 'assistant', 'content': '{"primary":"Data Generation and Characteristics", "secondary":"Data accuracy"}'},
{'role': 'assistant', 'content': 'For information on data accuracy, please visit www.olvindataaccuracy.com.'}
]
    user_messages = [
        "Interesting. Can you tell me what the busiest grocery store in soho is?",
        "OK, how did Uniqlo do last quarter compared to the same quarter last year?",
        # "yes",
        "How many visits were that to Walmart last year?",
        "what was the best restaurant to visit in LA in 2021?"]
    
    for message in user_messages:
        
        print(message)
        # messages = [ {'role': 'system', 'content': SQL_SYSTEM_MESSAGE.strip()} ] + previous_messages + [{'role': 'user', 'content': message}]
        evaluation_response, final_output = database.query_db(message, previous_messages)
        print(evaluation_response, final_output)
      