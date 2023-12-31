from chatbot.chatgpt import ChatGPT
from chatbot.documentation import ProductDocumentation
from chatbot.database import AccessDatabase
from chatbot.enquiries import GeneralEnquiry
from chatbot.classifier import Classifier
import json, openai
from utils import *


class Controller:
    def __init__(self):
        self.startMessageStack =  [  {'role':'system', 
                                     'content':GENERAL_ENQUIRY_SYSTEM_MESSAGE}]
        self.ChatModel = ChatGPT()
        self.ProductDoc = ProductDocumentation()
        self.AccessDB = AccessDatabase()
        self.GeneralEnquiry = GeneralEnquiry()
        self.Classifier = Classifier(CLASSIFIER_SYSTEM_MESSAGE)
        self.ClassifierMessageStack = [  {'role':'system', 
                                     'content':self.Classifier.system_message}]

            
    def reset(self):
        self.startMessageStack = [ {'role':'system', 
                                     'content':GENERAL_ENQUIRY_SYSTEM_MESSAGE}]
        print('model was reset to initial state')
 
    def add_to_message_stack(self, message, sender):
        if sender=='assistant':
            self.startMessageStack.append({'role':'assistant','content': f"{message}"})
        elif sender=='user':
            self.startMessageStack.append({'role':'user','content': f"{message}"})    

    def direct_user_message(self, user_input, response, debug):
        # Step 3: If message classified then answer the question
        match response["primary"]:
            case "Data Queries and Insights":
                # BigQuery
                final_response, sql_query, sql_output = self.AccessDB.run_database(user_input, [d for d in self.startMessageStack[:-1] if d['role'] != 'system'], debug)
                if not sql_query:
                    # Direct to documentation if no output from SQL
                    response["primary"] = "Data Generation and Characteristics"
                    return self.direct_user_message(user_input, response, debug)
                else:
                    self.add_to_message_stack(sql_query, "user")
            case "Data Generation and Characteristics":
                # Send link to documentation
                final_response = self.ProductDoc.product_documentation(user_input, response)
            case "General Inquiry" | "Fallback response":
                final_response = self.GeneralEnquiry.general_enquiry(user_input, self.startMessageStack)
            case _:
                final_response ="I'm unable to provide the information you're looking for. Please contact Dylan at dylan@olvin.com."
          

        return final_response

    def process_user_message(self, user_input, debug=True):
        
        # Step 1: Check input to see if it flags the Moderation API or is a prompt injection
        response = openai.Moderation.create(input=user_input)
        moderation_output = response["results"][0]
        if moderation_output["flagged"]:
                print("Step 1: Input flagged by Moderation API.")
                return "Sorry, we cannot process this request. Let me direct you to Dylan our sales representative"

        if debug: print("Step 1: Input passed moderation check.")
        
        # One passed the moderation check add the user message to the stack
        self.add_to_message_stack(user_input, 'user')
        # Step 2: Classify user message 
        response, self.ClassifierMessageStack = self.Classifier.classify_user_message(self.ClassifierMessageStack, user_input) # should we use last few messages? 

        if debug: print(f"Step 2: User message classified. \n Classification: {response}")
        
        # Step 3: If message classified then answer the question
        final_response = self.direct_user_message(user_input, response, debug)

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
