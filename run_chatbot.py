from utils import CLASSIFIER_SYSTEM_MESSAGE
from chatbot.controller import Controller
from argparse import ArgumentParser
import sys

def run_stored_messages(debug):
    user_messages = [
        "How do you generate your foot traffic data?",
        "How many retails stores do you have data for and how many devices do you analyze?",
        "How accurate is the data?",
        "Interesting. Can you tell me what the busiest grocery store in Manhattan is?",
        "OK, how did Uniqlo do last quarter compared to the same quarter last year?",
        "yes",
        "how old am I?",
        "How many visits were that to Walmart last year"]

    controller = Controller()

    for user_message in user_messages:
        print("\n Question: ", user_message)
        response, _ = controller.process_user_message(user_message, debug)
        print(f" ChatGPT: {response}")

def run_interactive(debug):      
    controller = Controller()
    print("Ask any question about the data. Enter 'q' to quit. Enter 'r' to reset ChatGPT.")
    while True:
        user_input = input(" Question: ")
        if user_input.lower() == 'q':
            break
        if user_input == "r":
            controller.chatModel.reset()
            continue
        try:
            response, _ = controller.process_user_message(user_input, debug)
            print(f" ChatGPT: {response}")

        except ValueError:
            print("Invalid input. Please enter a number or 'q' to quit.")


if __name__ == "__main__":
    print(sys.version)
    parser = ArgumentParser()
    subparser = parser.add_subparsers()

    running_parser = subparser.add_parser('run', help='run the model in interactive mode')
    running_parser.add_argument('--debug', action="store_true", help="Whether to print steps of output")
    running_parser.set_defaults(mode='run')

    testing_parser = subparser.add_parser('test', help='run the model on testing conversations')
    testing_parser.add_argument('--debug', action="store_true", help="Whether to print steps of output")
    testing_parser.set_defaults(mode='test')

    args = parser.parse_args()

    if args.mode == 'run':
        run_interactive(args.debug)
    elif args.mode == 'test':
        run_stored_messages(args.debug)