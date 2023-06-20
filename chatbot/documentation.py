
from utils import PRODUCT_DOCUMENTATION_SYSTEM_MESSAGE
from chatbot.chatgpt import ChatGPT

class ProductDocumentation:
    def __init__(self):
        self.ChatModel = ChatGPT()
    
    def product_documentation(self, user_message, assistant_message):
        system_message = PRODUCT_DOCUMENTATION_SYSTEM_MESSAGE

        messages = [
            {'role': 'system', 'content': system_message},
            {'role': 'user', 'content': user_message},
            {'role': 'assistant',
                'content': f"""Relevant document information \
        {assistant_message}""",
            },
        ]
        return self.ChatModel.get_completion_from_messages(messages)
