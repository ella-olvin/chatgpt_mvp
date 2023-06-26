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
{'role': 'assistant', 'content': 'Thank you for your question! Our foot traffic data is generated using location data and machine learning methodologies. For more information on data accuracy, please visit www.olvindataaccuracy.com.'},
{'role': 'user', 'content': '####How many retails stores do you have data for and how many devices do you analyze?####'},
{'role': 'assistant', 'content': 'For information on data volumes, please visit www.olvindatavolumes.com. This document provides details on the number of retail stores we have data for and the number of devices we analyze.'},
{'role': 'user', 'content': '####How accurate is the data?####'},
{'role': 'assistant', 'content': 'For information on data accuracy, please visit www.olvindataaccuracy.com.'}
]
    user_messages = [
        "Interesting. Can you tell me what the busiest grocery store in manhattan is?",
        # "OK, how did Uniqlo do last quarter compared to the same quarter last year?",
        # # "yes",
        # "How many visits were that to Walmart last year?",
        # "what was the best restaurant to visit in LA in 2021?"
        ]
    
    for message in user_messages:
        
        print(message)
        messages = [ {'role': 'system', 'content': SQL_SYSTEM_MESSAGE.strip()} ] + previous_messages + [{'role': 'user', 'content': message}]
        sql_query, messages = database.get_query(messages,r"####(.*?)####")
        full_query = database.append_cte_to_dynamic_query(sql_query)
        final_output = database.call_bigquery(full_query)

        if not final_output:
            messages_2 = [messages[0]] + [{'role': 'user', 'content': message}]+ [ {'role': 'assistant', 'content': sql_query} ] + \
                [ {'role': 'user', 'content': \
                   'The previous query returned null. \
                    Explain in natural language what has been queried and ask the user to rephrase their query if this is not correct.'} ]
            sql_query = database.ChatModel.get_completion_from_messages(messages_2)
          
            print(sql_query)
            messages_3 = messages_2 + [ {'role': 'assistant', 'content': sql_query}] + \
            [ {'role': 'user', 'content': 'Please can you only filter by manhattan not ny'}] 
            
            # full_query = database.append_cte_to_dynamic_query(sql_query)
            final_output = database.call_bigquery(sql_query)
            sql_query = database.ChatModel.get_completion_from_messages(messages_2)
            queries = [x for x in sql_query.split("````") if x.startswith("SELECT")]
            for query in queries: 
                full_query = database.append_cte_to_dynamic_query(sql_query)
                final_output = database.call_bigquery(full_query)
                messages_3 = messages_3 + [{'role': 'user', 'content': final_output}]

        # evaluation_response, sql_query, sql_output = database.run_database(message, previous_messages)
        # print(evaluation_response, sql_output)
      