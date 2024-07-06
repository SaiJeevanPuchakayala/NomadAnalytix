import matplotlib.pyplot as plt
import warnings
from dotenv import load_dotenv
import streamlit as st
from control import *

warnings.filterwarnings("ignore")
load_dotenv()
st.set_option('deprecation.showPyplotGlobalUse', False)


def get_system_prompt(datasets):
	sysp = f'There are {len(datasets)} datasets available.'
	issues = {}
	for i, chosen_dataset in enumerate(datasets):
		sysp += f'\nDataset {i + 1} is {chosen_dataset}.\n'
		data_desc, issue = create_data_desc(datasets[chosen_dataset])
		sysp += data_desc + '\n'
		issues[chosen_dataset] = issue

	for key, value in issues.items():
		if value:
			st.warning(f"Dataset {key} has issues in the following columns: {value}\nThis may cause problems in the output, please clean data.")

	return sysp

def get_graph(datasets, selected_model, question):
	# Execute chatbot query

	instructions = '''
Label the x and y axes appropriately.
Add a title. Set the fig suptitle as empty.
"datasets" is a dictionary containing the dataframes. 
IMPORTANT: Do not assume and use any columns that have not been provided in the system prompt. Use only the columns specific to that dataset.
Do not include the lines of code that have already been provided in the prompt.
Using Python version 3.9.12, create a script using the dataframe df to generate a graph using which a human can infer the following:'''

	code_begin = '''
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
fig,ax = plt.subplots(1,1)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
'''

	for df_name in datasets:
		code_begin = code_begin + f"{df_name} = datasets['{df_name}'].copy()\n"

	# Create model, run the request and print the results
	# Format the question
	question_to_ask = f"{instructions} {question} \n{code_begin}"
	st.session_state.messages.append({"role": "user", "content": question_to_ask})

	# Run the question
	answer = run_request(selected_model, st.session_state.messages)
	answer = code_begin + answer
	st.session_state.messages[-1]["content"] = question
	# the answer is the completed Python script so add to the beginning of the script to it.

	return answer


if __name__ == "__main__":
	st.title("Data Science Assistant")

	datasets = {}
	with st.sidebar:
		st.title("Selected Datasets")

		uploaded_files = st.file_uploader("Choose a CSV file", accept_multiple_files=True)
		for uploaded_file in uploaded_files:
			datasets[uploaded_file.name.split('.')[0]] = pd.read_csv(uploaded_file)
		if st.button("Reset", type="primary"):
			del st.session_state["messages"]
		if len(st.session_state.messages) > 1:
			if st.button("Rerun"):
				del st.session_state["messages"][-3:]

	if "openai_model" not in st.session_state:
		st.session_state["text_model"] = "gpt-4o"
		st.session_state["vision_model"] = "gpt-4-turbo-2024-04-09"

	if "messages" not in st.session_state:
		st.session_state.messages = []
		st.session_state.messages.append({"role": "system", "content": get_system_prompt(datasets)})

	for message in st.session_state.messages:
		if message["role"] == "system":
			continue
		if isinstance(message["content"], list):
			with st.chat_message("assistant"):
				st.image(decode_image(message["content"][1]["image_url"]["url"].split(',')[-1]))
			continue
		if message["role"] == "assistant":
			with st.chat_message("inference", avatar="✨"):
				st.markdown(message["content"])
		else:
			with st.chat_message(message["role"]):
				st.markdown(message["content"])

	if datasets:
		if prompt := st.chat_input("Ask something "):
			with st.chat_message("user"):
				st.markdown(prompt)

			with st.chat_message("assistant").status("Running...") as status:
				for _ in range(3):
					try:
						graph = get_graph(datasets, st.session_state["text_model"], prompt)
						st.code(graph)
						print(graph)
						exec(graph, globals(), locals())
						error_flag = False
						status.update(label="Done", state="complete")
						break
					except Exception as e:
						st.write(f"Error: {e}")
						st.session_state.messages.pop()
						continue
				else:
					status.update(label="Error", state="error")
					error_flag = True

			if error_flag:
				st.write('There was an error, ask the question again to retry or try changing the question')

			elif not error_flag:
				st.pyplot(fig)
				plt.savefig("output.png")

				with st.chat_message("inference", avatar="✨").status("Running...") as status:
					out = run_image_request(prompt, st.session_state["vision_model"], "output.png",
					                        st.session_state.messages)
					status.update(label="Done", state="complete")

				st.write(out)
				st.session_state.messages.append({"role": "assistant", "content": out})
			print(st.session_state.messages[0])


