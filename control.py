import openai
import os
import base64
import pandas as pd
import re


def run_request(model_type, messages):
	key = os.environ['OPENAI_API_KEY']
	openai.api_key = key
	response = openai.ChatCompletion.create(model=model_type, messages=messages)

	llm_response = response["choices"][0]["message"]["content"]
	return find_code_blocks(llm_response)[0]


def run_image_request(question_to_ask, model_type, image_path, messages):
	key = os.environ['OPENAI_API_KEY']
	openai.api_key = key
	messages.append({   "role": "user",
						"content": [
							{
								"type": "text",
								"text": question_to_ask,
							},
							{
								"type": "image_url",
								"image_url": {
									"url": f"data:image/jpeg;base64,{encode_image(image_path)}",
								},
							},
						],
					})
	response = openai.ChatCompletion.create(model=model_type, messages=messages, max_tokens=300,)
	llm_response = response["choices"][0]["message"]["content"]
	return llm_response


def encode_image(image_path):
	with open(image_path, "rb") as image_file:
		return base64.b64encode(image_file.read()).decode('utf-8')


def decode_image(image_string):
	return base64.b64decode(image_string)


def create_data_desc(df_dataset):
	# Primer function to take a dataframe and its name
	# and the name of the columns
	# and any columns with less than 20 unique values it adds the values to the primer
	# and horizontal grid lines and labeling
	data_desc = f'''This dataset has columns '{"','".join(str(x) for x in df_dataset.columns)}'. '''
	issues = []
	for col in df_dataset.columns:
		if len(df_dataset[col].drop_duplicates()) < 20 and df_dataset.dtypes[col] == "O":
			data_desc = data_desc + f'''\nThe column '{col}' has categorical values '{"','".join(str(x) for x in df_dataset[col].drop_duplicates())}'. '''
		elif df_dataset.dtypes[col] == "int64" or df_dataset.dtypes[col] == "float64":
			data_desc = data_desc + f"\nThe column '{col}' is type {str(df_dataset.dtypes[col])} and contains numeric values. "
		else:
			if df_dataset[col].map(lambda x: x.replace('.', '', 1).isdigit()).sum() > 20:
				data_desc = data_desc + (f"\nThe column '{col}' is probably integer type but contains categorical "
										f"values. This column has to be cleaned.")
				issues.append(col)
			else:
				data_desc = data_desc + f"\nThe column '{col}' has categorical values."
	return data_desc, issues


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


def find_code_blocks(text):
	# Define a regular expression pattern to match ``` followed by anything
	# (non-greedy matching with .*?) and then again ```
	pattern = r"```python(.*?)```"

	# Use re.findall to find all occurrences of the pattern
	code_blocks = re.findall(pattern, text, re.DOTALL)  # re.DOTALL allows matching across lines
	return code_blocks
