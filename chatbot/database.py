from utils import EXPLODE_DAILY_VISITS, SQL_SYSTEM_MESSAGE, SQL_MESSAGES
from google.cloud import bigquery
client = bigquery.Client()
from chatbot.chatgpt import ChatGPT
import json, re


class AccessDatabase:
    def __init__(self):
        self.ChatModel = ChatGPT()
        
    
    def append_cte_to_dynamic_query(self, message):
        # need to make this dynamic 
        return (EXPLODE_DAILY_VISITS + ( message
                            .replace("llm_mvp.SGPlaceDailyVisitsRaw","daily_visits")
                            .replace("SGPlaceDailyVisitsRaw", "daily_visits")
                            .replace("llm_mvp.SGPlaceRaw.fk_sgplaces", "SGPlaceRaw.fk_sgplaces")
                            .replace("llm_mvp.SGPlaceRaw.name", "SGPlaceRaw.name")
                        ))  

    def call_bigquery(self, message):
        try:
            return (list(client.query(message).to_dataframe().values.flatten()))
        except Exception as e:
            
            return (list(client.query(message).to_dataframe().values.flatten()))

    def check_output(self, messages, responseString, counter):
        if counter > 3:
            return {"role":"assistant", "content":{"recipient":"user", "content":"Too many invalid responses"}}
        try:
            return json.loads(responseString[:-1] if responseString.endswith('.') else responseString)
        except ValueError:
            try: 
                start_index = responseString.find('####')
                end_index = responseString.rfind('####') + 1
                json_string = responseString[start_index:end_index]
                return json.loads(json_string[:-1] if json_string.endswith('.') else json_string)
            except ValueError:
                messages = messages+ [{"role": "assistant", "content": responseString}] + [{"role": "user", 
                    "content": "Please repeat that answer but use valid JSON only"} ] 
                responseString = self.ChatModel.get_completion_from_messages(messages)
                return self.check_output(messages, responseString, counter=counter+1)
    
    def get_query(self, messages, counter=0):
        
        if counter > 2:
            return (None, None)

        responseString = self.ChatModel.get_completion_from_messages(messages)

        # extract query from between delimiters #### 
        pattern = r"####(.*?)####"
        try:
            response_str = re.findall(pattern, responseString, re.DOTALL)[0]
            if not response_str:
                return (None, None)
            response = {"message": response_str}
            messages = messages +  [{"role": "user", "content": f"{response_str}" } ]
            response["message_append_cte"] = self.append_cte_to_dynamic_query(response_str)
            return response, messages
        
        except Exception as e:
             return self.get_query(messages + [{'role': 'user', 'content': "Create the query again in SQL syntax surrounded by #### delimiters"}], counter=counter+1)

    
        # response = {"message": response_str}
        # messages = messages +  [{"role": "user", "content": f"{response_str}" } ]
        # response["message_append_cte"] = self.append_cte_to_dynamic_query(response_str)
        # return response, messages
    
    def get_bigquery_output(self, messages, response, counter):
        if counter > 2:
            return (None, None)

        try:
            return ' '.join([str(element)for element in (self.call_bigquery(response["message_append_cte"]))])[:400]
        except Exception as e:
            if messages:
                response, messages = self.get_query(messages + [{'role': 'user', 'content': f"Create the query again in SQL syntax changing it to fix this error: {str(e)}"}], counter=counter+1)
            else:
                return self.get_bigquery_output(messages, response, counter+1)
        
    def query_db(self,  message, previous_messages, counter=0):
        if counter == 0:
            # on first instance use all messages to system message
            messages = [ {'role': 'system', 'content': SQL_SYSTEM_MESSAGE.strip()} ] + previous_messages + [{'role': 'user', 'content': message}]
            # messages = SQL_MESSAGES + previous_messages + [{'role': 'user', 'content': message}]
        elif counter <=5:
            # on all other instances only add newest message so chatgpt knows what to correct
            messages = previous_messages + [{'role': 'user', 'content': message}]
        else: 
            return "Failed to create valid SQL query", ""

        sql_query, messages = self.get_query(messages, counter=0)
        sql_output = self.get_bigquery_output(messages, sql_query, counter=0)

        print("SQL_OUTPUT:", sql_output)
        if not sql_output:
            return (None, None)
        
        # create a response 
        messages = [ {'role': 'system', 'content':  "Give the user a natural language response to the SQL output that answers the question"} ] + \
        [d for d in messages if d['role'] != 'system'] + \
         [{'role': 'user', 'content': sql_output}]
        
        evaluation_response = self.ChatModel.get_completion_from_messages(messages)
        return evaluation_response, sql_query["message"]
    