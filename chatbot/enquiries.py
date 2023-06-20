from utils import GENERAL_ENQUIRY_SYSTEM_MESSAGE
from chatbot.chatgpt import ChatGPT

class GeneralEnquiry:
    def __init__(self):
        self.ChatModel = ChatGPT()

    def general_enquiry(self, user_message, messageStack):
    
        messages =  messageStack + [     
        {'role':'user',
        'content': user_message},   
        ]
        return self.ChatModel.get_completion_from_messages(messages)
