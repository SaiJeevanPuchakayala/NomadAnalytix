import pandas as pd
from classes import get_primer, format_question, run_request, create_desc_primer
import warnings
from dotenv import load_dotenv
import os
import streamlit as st

warnings.filterwarnings("ignore")
load_dotenv()
st.set_option('deprecation.showPyplotGlobalUse', False)

available_models = {"Gemini-Flash": "gemini-1.5-flash", "Gemini-Pro": "gemini-1.5-pro-latest", "ChatGPT-4o": "gpt-4o", "ChatGPT-3.5": "gpt-3.5-turbo-16k"}
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
	issues = {}
	for i, chosen_dataset in enumerate(datasets):
		primer0 += f'\nDataset {i + 1} is {chosen_dataset}.\n'
		primer, issue = create_desc_primer(datasets[chosen_dataset])
		primer0 += primer + '\n'
		issues[chosen_dataset] = issue

	for key, value in issues.items():
		if value:
			messages.warning(f"Dataset {key} has issues in the following columns: {value}\nThis may cause problems in the output please clean data.")

	primer1, primer2 = get_primer(datasets)
	primer1 = primer0 + primer1
	# Create model, run the request and print the results
	# Format the question
	question_to_ask = format_question(primer1, primer2, question, selected_model)

	# Run the question
	answer = run_request(question_to_ask, available_models[selected_model])

	# if "gpt" in available_models[selected_model]:
	answer = primer2 + answer
	# the answer is the completed Python script so add to the beginning of the script to it.

	# print(question_to_ask)
	return answer


if __name__ == "__main__":
	datasets = create_filename_dict("files")
	with st.sidebar:
		st.title("Selected Datasets")
		for i in range(len(datasets)):
			st.write(list(datasets.keys())[i])

	selected_model = st.radio(r"$\textsf{Select Model}$", list(available_models.keys()))

	# Text area for query
	messages = st.container()
	if prompt := messages.chat_input("Ask something"):
		messages.chat_message("user").write(prompt)
		with messages.chat_message("assistant").status("Running...") as status:
			answer = main(datasets, selected_model, prompt)
			print(answer)
			st.code(answer)
			fig = exec(answer)
			status.update(label="Done", state="complete")
			messages.pyplot(fig)

