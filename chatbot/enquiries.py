from utils import GENERAL_ENQUIRY_SYSTEM_MESSAGE
from chatbot.chatgpt import ChatGPT

class GeneralEnquiry:
    def __init__(self):
        self.ChatModel = ChatGPT()

    def general_enquiry(self, user_message, assistant_message):
    
        messages =  [  
        {'role':'system',
        'content': GENERAL_ENQUIRY_SYSTEM_MESSAGE},   
        {'role':'user',
        'content': user_message},  
        {'role':'assistant',
        'content': f"""Relevant previous information \
        {assistant_message}"""},   
        ]
        return self.ChatModel.get_completion_from_messages(messages)
