#################################################################################
# Chat2VIS
# https://chat2vis.streamlit.app/
# Paula Maddigan
#################################################################################

import pandas as pd
import openai
from classes import get_primer, format_question, run_request
import warnings
from dotenv import load_dotenv

warnings.filterwarnings("ignore")
load_dotenv()

available_models = {"Gemini":"gemini-1.5-flash", "ChatGPT-4": "gpt-4","ChatGPT-3.5": "gpt-3.5-turbo-16k"}
# gpt-3.5-turbo-16k, gpt-4o-2024-05-13, gpt-4o

datasets = {}
datasets["Movies"] = pd.read_csv("movies.csv")

selected_models = ["Gemini", "ChatGPT-3.5"]
model_count = 1

# Text area for query
question = "what is the 10 highest r rated movie?"
chosen_dataset = "Movies"

# Execute chatbot query
if model_count > 0:
	# Get the primer for this dataset
	primer1, primer2 = get_primer(datasets[chosen_dataset], 'datasets["' + chosen_dataset + '"]')
	# Create model, run the request and print the results
	# Format the question
	question_to_ask = format_question(primer1, primer2, question, selected_models[0])
	# Run the question
	answer = ""
	answer = run_request(question_to_ask, available_models[selected_models[1]])
	# the answer is the completed Python script so add to the beginning of the script to it.
	# answer = primer2 + answer
	# print("Model: " + model_type)
	print(answer)

	# print(question_to_ask)




