import pandas as pd
from classes import get_primer, format_question, run_request, create_desc_primer
import warnings
from dotenv import load_dotenv
import os

warnings.filterwarnings("ignore")
load_dotenv()

available_models = {"Gemini":"gemini-1.5-flash", "ChatGPT-4o": "gpt-4o", "ChatGPT-3.5": "gpt-3.5-turbo-16k"}
# gpt-3.5-turbo-16k, gpt-4o-2024-05-13, gpt-4o


def create_filename_dict(folder_path):
	# Create an empty dictionary to store the filenames
	filename_dict = {}

	# Iterate over all files in the specified folder
	for filename in os.listdir(folder_path):
		# Check if the current item is a file (and not a directory)
		if os.path.isfile(os.path.join(folder_path, filename)):
			# Split the filename into name and extension
			name, extension = os.path.splitext(filename)
			# Add the name and full filename to the dictionary
			filename_dict[name] = pd.read_csv(os.path.join(folder_path, filename))

	return filename_dict


def main(datasets, selected_model, question):
	# Execute chatbot query
	primer0 = f'There are {len(datasets)} datasets available.'
	for i, chosen_dataset in enumerate(datasets):
		primer0 += f'\nDataset {i + 1} is {chosen_dataset}.\n'
		primer0 += create_desc_primer(datasets[chosen_dataset]) + '\n'

	primer1, primer2 = get_primer(datasets)
	primer1 = primer0 + primer1
	# Create model, run the request and print the results
	# Format the question
	question_to_ask = format_question(primer1, primer2, question, selected_model)

	# Run the question
	answer = run_request(question_to_ask, available_models[selected_model])
	# the answer is the completed Python script so add to the beginning of the script to it.

	# print(question_to_ask)
	print(answer)
	exec(answer)


if __name__ == "__main__":
	datasets = create_filename_dict("files")

	# selected_model = "Gemini"
	selected_model = "ChatGPT-3.5"

	# Text area for query
	question = "Which are the Top 2 teams with the most wins achieved by chasing targets over the past 3 years?"

	main(datasets, selected_model, question)
