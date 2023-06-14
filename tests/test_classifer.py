import sys
sys.path.append("/Users/ella/GIT_REPOS/chatgpt")
from chatbot.controller import Controller
from utils import *

if __name__ == "__main__":
    controller = Controller(system_message=CLASSIFIER_SYSTEM_MESSAGE)
    user_messages = [
        ("How do you generate your foot traffic data?", {'primary': 'Data Generation and Characteristics', 'secondary': 'Data accuracy'}),
        ("How many retails stores do you have data for and how many devices do you analyze?", {'primary': 'Data Generation and Characteristics', 'secondary': 'Data volumes'}),
        ("How accurate is the data?", {'primary': 'Data Generation and Characteristics', 'secondary': 'Data accuracy'}),
        ("Interesting. Can you tell me what the busiest grocery store in Manhattan is?", {'primary': 'Data Queries and Insights', 'secondary': 'Query database'}),
        ("OK, how did Uniqlo do last quarter compared to the same quarter last year?",  {'primary': 'Data Queries and Insights', 'secondary': 'Query database'}),
        ("yes",  {'primary': 'Data Queries and Insights', 'secondary': 'Query database'}),
        ("how old am I?",  {'primary': 'General Inquiry', 'secondary': 'Speak to a human'}),
        ("How many visits were that to Walmart last year?", {'primary': 'Data Queries and Insights', 'secondary': 'Query database'})]
    count = 0
    correct = 0
    for message, answer in user_messages:
        result = controller.classify_user_message(message)[0]
        print(f"\n\n{message}, \n {result}")
        if answer == result:
            correct += 1
        count += 1
        
    print(f"Accuracy: {correct/count * 100} % ")
        # print(f"\n\n{message}, \n {controller.classify_user_message(message)[0]}")
