# ChatGPT Customer Assistant

This repository contains a ChatGPT Minimum Viable Product (MVP) implementation that demonstrates a chatbot using OpenAI's GPT-3.5 model.

## File Structure
- `run_chatbot.py`: The main script to run the chatbot and interact with users.
- `chatbot/`
  - `chatgpt.py`: Module responsible for generating responses using the GPT-3.5 model.
  - `classifier.py`: Module for classifying user input or messages.
  - `controller.py`: Module that controls the flow of conversation and handles user interactions.
  - `database.py`: Module for interacting with the database or data storage.
  - `documentation.py`: Module for interacting with product documentation for the user.
  - `enquiries.py`: Module for handling specific inquiries or queries from users.
- `utils.py`: All the hardcoded system messages needed for the different ChatGPT instances.

## Prerequisites

- Python 3.7 or higher
- OpenAI API credentials (API key)

## Installation
1. Clone this repository:

   ```bash
   git clone https://github.com/ella-olvin/chatgpt_mvp.git
   
2. Install the required Python dependencies. This creates a conda env called `chatgpt_sql` :
    ```bash
    conda env create -f environment_chatgpt_sql.yml
   
3. Create a `.env` file locally to save your OpenAI API credentials like this `OPENAI_API_KEY = {API_KEY}`

Note:  `.env` is currently included in `.gitignore` because if you push it to git the API key will be deactivated for security reasons. 

## Methodology

The aim of this script is to understand the customer question and answer it accurately. 

For the MVP there are three different categories of question that can be answered: 
- **General Inquiry** - If the customer enquires about pricing or general sales/business questions. 
- **Data Generation and Characteristics** - Any questions about how the data is generated, how accurate it is, the product methodology etc. 
- **Data Queries and Insights** - Any specific data sample questions that require querying the database. 

The script first classifies the user input into one of these three categories. Dependent on the output it is then directed to the correct class to be answered. Each class has it's own instance of ChatGPT created specifically for answering that type of question.

### General Inquiry
If the user question is classified as a general inquiry then it is sent to the `enquiries.py` where an instance of chatGPT with GENERAL_ENQUIRY_SYSTEM_MESSAGE is created and an answer returned. 

### Data Generation and Characteristics
If the user question is classified as data generation and characteristics then it is sent to the `documentation.py`
where an instance of ChatGPT with PRODUCT_DOCUMENTATION_SYSTEM_MESSAGE is created and an answer returned. 

### Data Queries and Insights
If the user question is classified as data queries and insights then it is sent to `database.py`. Here an new instance of ChatGPT is created that turns the user input into a SQL query. This query is then sent to BigQuery and an answer returned. Another instance of chatGPT is then created to return the response in natural language. 


## Usage
1. Run the chatbot in interactive mode:
    ```bash
    python run_chatbot.py run --debug

This command will start the chatbot in the interactive mode with debug mode enabled. You can provide input or messages, and the chatbot will generate responses based on the GPT-3.5 model. Debug mode will display additional debug information or logs for troubleshooting. 

2. Run the chatbot in test mode:
   ```bash
    python run_chatbot.py test --debug

This command will execute the chatbot in test mode, running predefined test cases or scenarios. Currently these Debug mode will provide additional debug information during the test execution.

Note: The --debug flag is optional. If not specified, the script will run without debug mode enabled.

## Configuration
- Modify the settings in controller.py and chatgpt.py to customize the behavior of the chatbot.
- Adjust the database connection settings in database.py if required. Currently this accesses BigQuery. 

## Examples
Here are some examples to get you started:

Example 1: Interacting with the chatbot

```bash
    # Example code snippet 
```

## Troubleshooting
If the chatbot is not generating expected responses, make sure you have valid API credentials and a stable internet connection. 
Sometime calling ChatGPT may fail for internal reasons. This will be printed if it happens and the current fix is to wait 30 seconds and then try running again. 
