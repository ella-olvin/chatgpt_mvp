import sys
sys.path.append("/Users/ella/GIT_REPOS/chatgpt_mvp_v1")
from chatbot.enquiries import GeneralEnquiry
from chatbot.controller import Controller
from chatbot.chatgpt import ChatGPT
from utils import *
import re 

if __name__ == "__main__":
    ChatModel = ChatGPT()
    enquiries = GeneralEnquiry()
    user_messages = [
        "How do you generate your foot traffic data?",
        "How many retails stores do you have data for and how many devices do you analyze?",
        "How accurate is the data?",
        "Interesting. Can you tell me what the busiest grocery store in Manhattan is?",
        "OK, how did Uniqlo do last quarter compared to the same quarter last year?",
        "yes",
        "how old am I?",
        "How many visits were that to Walmart last year"]
    
    for message in user_messages:
        result = enquiries.general_enquiry(message)
        print(f"\n\n{message}, \n {result}")

        