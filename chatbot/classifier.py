from utils import EXPLODE_DAILY_VISITS, SQL_SYSTEM_MESSAGE, WHERE_CONDITIONS_SYSTEM_MESSAGES
from google.cloud import bigquery
client = bigquery.Client()
from chatbot.chatgpt import ChatGPT
import json, re

def is_valid_dictionary(variable):
    return (
        isinstance(variable, dict)
        and len(variable) == 2
        and 'primary' in variable
        and 'secondary' in variable
    )

class Classifier:
    def __init__(self, system_message):
        self.ChatModel = ChatGPT()
        self.delimiter = "####"
        self.system_message = system_message
        self.startMessageStack =  [  {'role':'system', 
                                     'content':self.system_message}]
    
    def hardcode_incorrect_response(self, hc_response=None):
        if hc_response is None:
            hc_response = {"primary": "Fallback response", "secondary": "miscellaneous"}
        return hc_response, f"'{hc_response}'"
 
    def classify_user_message(self, messageStack, message):
        messageStack.append({'role':'user','content': f"{self.delimiter}{message}{self.delimiter}"})
        responseString =  self.ChatModel.get_completion_from_messages(messageStack)
        response, responseString = self.check_chat_output(responseString)
        messageStack.append({'role':'assistant','content': f"{response}"})
        return response, messageStack
    
    def check_chat_output(self, responseString):
        try: 
            response = json.loads(responseString[:-1] if responseString.endswith('.') else responseString)
        except ValueError as e:
            try:
                response = json.loads(responseString[:-1].replace("'", "\"") if responseString.endswith('.') else responseString.replace("'", "\""))
            except ValueError as e:
                # hardcode when gpt doesn't give correctly formatted response
                response, responseString = self.hardcode_incorrect_response()
        
        # check the response is a valid dict, if not run again
        if not is_valid_dictionary(response):
            # hardcode when gpt doesn't give correctly formatted response
            response, responseString = self.hardcode_incorrect_response()
        return response, responseString
 

if __name__ == "__main__":
    classifier = Classifier()
    classifier.classify_user_message("hello")