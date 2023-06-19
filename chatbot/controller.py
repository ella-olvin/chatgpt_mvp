from chatbot.chatgpt import ChatGPT
from chatbot.documentation import ProductDocumentation
from chatbot.database import AccessDatabase
from chatbot.enquiries import GeneralEnquiry
import json, openai
from utils import *

def is_valid_dictionary(variable):
    return (
        isinstance(variable, dict)
        and len(variable) == 2
        and 'primary' in variable
        and 'secondary' in variable
    )

class Controller:
    def __init__(self, system_message):
        self.system_message = system_message
        self.startMessageStack =  [  {'role':'system', 
                                     'content':self.system_message}]
        self.ChatModel = ChatGPT()
        self.ProductDoc = ProductDocumentation()
        self.AccessDB = AccessDatabase()
        self.GeneralEnquiry = GeneralEnquiry()

    def classify_user_message(self, message):
        self.startMessageStack.append({'role':'user','content': f"{delimiter}{message}{delimiter}"})
        responseString =  self.ChatModel.get_completion_from_messages(self.startMessageStack)
        return self.check_chat_output(responseString)

    def hardcode_incorrect_response(self, hc_response=None):
        if hc_response is None:
            hc_response = {"primary": "Fallback response", "secondary": "miscellaneous"}
        return hc_response, f"'{hc_response}'"

    def check_chat_output(self, responseString):
        try: 
            response = json.loads(responseString[:-1] if responseString.endswith('.') else responseString)
        except ValueError as e:
            try:
                response = json.loads(responseString.replace("'", "\"")[:-1] if responseString.replace("'", "\"").endswith('.') else responseString)
            except ValueError as e:
                # hardcode when gpt doesn't give correctly formatted response
                response, responseString = self.hardcode_incorrect_response()

        # check the response is a valid dict, if not run again
        if not is_valid_dictionary(response):
            # hardcode when gpt doesn't give correctly formatted response
            response, responseString = self.hardcode_incorrect_response()

        return response, responseString
    
    def add_to_message_stack(self, message, sender):
        if sender=='assistant':
            self.startMessageStack.append({'role':'assistant','content': f"{message}"})
        elif sender=='user':
            self.startMessageStack.append({'role':'user','content': f"{message}"})    

    def direct_user_message(self, user_input, response):
            # Step 3: If message classified then answer the question
        match response["primary"]:
            case "Data Queries and Insights":
                # BigQuery
                final_response, sql_query, sql_output = self.AccessDB.query_db(user_input, [d for d in self.startMessageStack[:-2] if d['role'] != 'system'])
                if not sql_output:
                    # Direct to documentation if no output from SQL
                    response["primary"] = "Data Generation and Characteristics"
                    return self.direct_user_message(user_input, response)
                else:
                    system_message = SQL_MESSAGES[0]['content']
                    self.add_to_message_stack(sql_query, "user")
            case "Data Generation and Characteristics":
                # Send link to documentation
                final_response = self.ProductDoc.product_documentation(user_input, response)
                system_message = PRODUCT_DOCUMENTATION_SYSTEM_MESSAGE.strip()
            case "General Inquiry" | "Fallback response":
                final_response = self.GeneralEnquiry.general_enquiry(user_input, response)
                system_message = GENERAL_ENQUIRY_SYSTEM_MESSAGE.strip()
            case _:
                final_response ="I'm unable to provide the information you're looking for. I'll connect you with a human representative for further assistance"
                system_message = ""

        return final_response, system_message

    def process_user_message(self, user_input, debug=True):
        # Step 1: Check input to see if it flags the Moderation API or is a prompt injection

        response = openai.Moderation.create(input=user_input)
        moderation_output = response["results"][0]
        if moderation_output["flagged"]:
                print("Step 1: Input flagged by Moderation API.")
                return "Sorry, we cannot process this request. Let me direct you to Dylan our sales representative"

        if debug: print("Step 1: Input passed moderation check.")
        
        # Step 2: Classify user message 
        response, responseString = self.classify_user_message(user_input) # should we use last few messages? 
        response, responseString = self.check_chat_output(responseString)
        self.add_to_message_stack(responseString, "assistant")

        if debug: print(f"Step 2: User message classified. \n Classification: {response}")
        
        # Step 3: If message classified then answer the question

        final_response, system_message = self.direct_user_message(user_input, response)

        self.add_to_message_stack(final_response, "assistant")
        if debug: print("Step 3: Got response to question.")

        # Step 4: Put the answer through the Moderation API
        response = openai.Moderation.create(input=final_response)
        moderation_output = response["results"][0]
        if moderation_output["flagged"]:
            if debug: print(f"Step 5: Response flagged by Moderation API. {moderation_output}")
            return "Sorry, we cannot provide this information."

        if debug: print(f"Step 4: Response passed moderation check.")

        return final_response, self.startMessageStack
