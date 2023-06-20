from utils import EXPLODE_DAILY_VISITS, SQL_SYSTEM_MESSAGE, WHERE_CONDITIONS_SYSTEM_MESSAGES
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
    
    def analyse_query_filters(self, response_str, pattern):
        # check where conditions
        messages = [ {'role': 'system', 'content': WHERE_CONDITIONS_SYSTEM_MESSAGES.strip()} ] + [{'role': 'user', 'content': response_str}]
        responseString = self.ChatModel.get_completion_from_messages(messages)
        response_str = re.findall(pattern, responseString, re.DOTALL)
        
        # query the db
        db_output = []
        for where_condition_query in response_str:
            appended_where_condition =self.append_cte_to_dynamic_query(where_condition_query)
            try:
                output = self.call_bigquery(appended_where_condition)
            except Exception as e: 
                output = []
            if not len(output):
                db_output.append(f"{where_condition_query} returns null")
  
        return db_output, response_str

    def analyse_query_filters(self, response_str, pattern):
        # check where conditions
        messages = [ {'role': 'system', 'content': WHERE_CONDITIONS_SYSTEM_MESSAGES.strip()} ] + [{'role': 'user', 'content': response_str}]
        responseString = self.ChatModel.get_completion_from_messages(messages)
        response_str = re.findall(pattern, responseString, re.DOTALL)
        
        # query the db
        db_output = []
        for where_condition_query in response_str:
            appended_where_condition =self.append_cte_to_dynamic_query(where_condition_query)
            try:
                output = self.call_bigquery(appended_where_condition)
            except Exception as e: 
                output = []
            if not len(output):
                db_output.append(f"{where_condition_query} returns null")
  
        return db_output, response_str

    def get_query(self, messages, pattern, counter=0):
        
        if counter > 2:
            return (None, None)
        responseString = self.ChatModel.get_completion_from_messages(messages)

        # extract query from between delimiters #### 
        try:
            response_str = re.findall(pattern, responseString, re.DOTALL)[0]
        except Exception as e:
                # pass the response and loop to get user to change their question
            # e.g of when i put fake place in the response is good so they could try again
             return self.get_query(messages + [{'role': 'user', 'content': "Create the query again in SQL syntax surrounded by #### delimiters"}], pattern, counter=counter+1)

        if not response_str:
            return (None, None)
        
        return response_str, messages

    def get_bigquery_output(self, messages, response, counter, pattern):
        if counter > 2:
            return (None, None)
        try:
            return ' '.join([str(element)for element in (self.call_bigquery(response["message_append_cte"]))])[:400]
        except Exception as e:
            if messages:
                response, messages = self.get_query(messages + [{'role': 'user', 'content': f"Create the query again in SQL syntax changing it to fix this error: {str(e)}"}], pattern, counter=counter+1)
            else:
                return self.get_bigquery_output(messages, response, counter+1)
        
    def query_database(self,  messages, counter, pattern=r"####(.*?)####", ):  
        # try SQL query
        if counter > 2:
            return [], [], messages
        
        sql_query, messages = self.get_query(messages, pattern, counter)
        if sql_query:
            full_query = self.append_cte_to_dynamic_query(sql_query)
        else:
            return [], [], messages 

        try:
            final_output = self.call_bigquery(full_query)
            return final_output, sql_query, messages
        except Exception as e:
            messages = messages + [{"role": "assistant", "content": sql_query}] +[{"role": "user", "content": f"That query failed with this error please try again:{str(e)}"}]
            return self.query_database(messages, counter=counter+1)

    
    def run_database(self, message, previous_messages, debug, counter=0, delimiter="####", pattern=r"####(.*?)####"):
        # Add new message
        if counter == 0:
            # on first instance use all messages to system message
            messages = [ {'role': 'system', 'content': SQL_SYSTEM_MESSAGE.strip()} ] + previous_messages + [{'role': 'user', 'content': message}]
        elif counter <=5:
            # on all other instances only add newest message so chatgpt knows what to correct
            messages = previous_messages + [{'role': 'user', 'content': message}]
        else: 
            return "Failed to create valid SQL query", ""

        # try SQL query
        sql_output, sql_query, messages = self.query_database(messages, counter=0)
        
        if not sql_query:
            # can't create a query - need a fallback
            return [],[],[]
        elif not sql_output:
            # the sql_output returns null so check the filter from the query
            db_output, response_str = self.analyse_query_filters(sql_query, pattern)
        else:
            db_output = []

        system_message =  f"""You are a customer service assistant informing a customer of the result in response to their query. 
        If the result is null then direct the user to a sales representative. Do not say that there is no data available for their request. 
        If a result has been found use as much information from the query sent to the database when describing the answer, for example specify the location, date and category queried.
        """ 
        messages = [
            {'role': 'system', 'content': system_message},
            {'role': 'user', 'content':  f"""Customer initial message: {delimiter}{message}{delimiter}"""},
            {'role': 'assistant', 'content': f"""Query sent to database: {delimiter}{sql_query}{delimiter}"""}]
        
        if db_output:
            # where conditions aren't satisfied
            messages = messages + [   
            {'role': 'assistant', 'content': f"""No response was found because these conditions returned null: {delimiter}{db_output}{delimiter}"""},
            ]
        
        elif not sql_output:
             #combinations of conditions doesn't have any result
            messages =  messages + [
            {'role': 'assistant', 'content': f"""No response was found because although the individual conditions were satisfied a combination of the conditions {delimiter}{' '.join(response_str)}{delimiter} doesn't give any results"""},
            ]
        else:
            # result returned
            messages =  messages + [
            {'role': 'assistant', 'content': f"""Result from query: {delimiter}{sql_output}{delimiter}"""},
            ]

        if debug:
            print("SQL query:", sql_query)
        evaluation_response = self.ChatModel.get_completion_from_messages(messages)
        # print("Response:", evaluation_response)
        return evaluation_response, sql_query, sql_output
    
