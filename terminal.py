import logging, json
from controller import Controller
from argparse import ArgumentParser
import sys
from datetime import datetime
from accuracy_metrics import rouge_metric, sbert_metric
# Configure the logging settings
logging.basicConfig(filename='debug.log', filemode='a', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def run():
    controller = Controller()
    print("Ask any question about the data. Enter 'q' to quit. Enter 'r' to reset ChatGPT.")
    while True:
        dialogue = dict()
        user_input = input("Question: ")
        # user_input = "how many people visited Denny's last week?"
        if user_input.lower() == 'q':
            break
        if user_input == "r":
            controller.chatModel.reset()
            continue
        try:
            result = controller.run(dialogue, message=user_input, sender="USER")
            print(f"ChatGPT: {result}")
        except ValueError:
            print("Invalid input. Please enter a number or 'q' to quit.")

def test(file_path):
    with open(f"{file_path}.json", 'r') as f:
        test_questions = json.load(f)

    controller = Controller()
    for idx, dialogue in enumerate(test_questions):
        if dialogue["turn_id"] == 0 and idx != 0:
            # Start new conversation
            controller.reset()
        
        user_input = dialogue['prompt']
        print(f"Q: {user_input}")
        try:
            result = controller.run(dialogue, message=user_input, sender="USER")
            dialogue['chatgpt_completion'] = result
            print(f"ChatGPT: {result}")
        except ValueError:
            print("Invalid input. Please enter a number or 'q' to quit.")
        
        # Accuracy metrics
        dialogue["rouge"] = rouge_metric(dialogue)
        dialogue["sbert"] = sbert_metric(dialogue["completion"], dialogue["chatgpt_completion"])
        
    
    with open(f"{file_path}_output_{datetime.now()}.json", 'w') as f:
        json.dump(test_questions, f)

if __name__ == "__main__":
    print(sys.version)
    parser = ArgumentParser()
    subparser = parser.add_subparsers()
    for mode in ['run']:
        mode_parser = subparser.add_parser(mode, help=mode)
        mode_parser.set_defaults(mode=mode)

    testing_parser = subparser.add_parser('test', help='run the model on testing conversations')
    testing_parser.add_argument('--file_path', help="path name for file for testing. In the form 'output_file' without the '.json'")
    testing_parser.set_defaults(mode='test')

    args = parser.parse_args()

    if args.mode == 'run':
        run()
    elif args.mode == 'test':
        test(args.file_path)
    
