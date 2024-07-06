import matplotlib.pyplot as plt
import warnings
from dotenv import load_dotenv
import streamlit as st
from control import *

warnings.filterwarnings("ignore")

# Retrieve OpenAI API key from Streamlit secrets
# openai.api_key = st.secrets["OPENAI_API_KEY"]
load_dotenv()
st.set_option('deprecation.showPyplotGlobalUse', False)

def get_system_prompt(datasets):
    sysp = f'There are {len(datasets)} datasets available 📊.'
    issues = {}
    for i, chosen_dataset in enumerate(datasets):
        sysp += f'\nDataset {i + 1} is {chosen_dataset} 📁.\n'
        data_desc, issue = create_data_desc(datasets[chosen_dataset])
        sysp += data_desc + '\n'
        issues[chosen_dataset] = issue

    for key, value in issues.items():
        if value:
            st.warning(f"⚠️ Dataset {key} has issues in the following columns: {value}\nThis may cause problems in the output, please clean data.")

    return sysp

def get_graph(datasets, selected_model, question):
    # Role, Goal, Context Prompting Framework
    role = "You are a highly advanced data analysis assistant."
    goal = "Your goal is to generate accurate and insightful visualizations from the provided datasets, based on user queries."
    context = '''
The datasets are provided as a dictionary where the keys are dataset names and values are dataframes. Your task is to:
1. Label the x and y axes appropriately.
2. Add a title to the graph.
3. Set the figure's suptitle as empty.
4. Ensure the code is suitable for Python version 3.9.12.
5. Use only the columns specified in the prompt.
6. Avoid duplicating lines of code already provided in the prompt.
'''

    instructions = f"{role}\n{goal}\n{context}"

    code_begin = '''
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
fig, ax = plt.subplots(1, 1)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
'''

    for df_name in datasets:
        code_begin += f"{df_name} = datasets['{df_name}'].copy()\n"

    question_to_ask = f"{instructions}\nUsing the dataframe, create a graph to help a human infer the following: {question}\n{code_begin}"
    st.session_state.messages.append({"role": "user", "content": question_to_ask})

    answer = run_request(selected_model, st.session_state.messages)
    answer = code_begin + answer
    st.session_state.messages[-1]["content"] = question

    return answer

if __name__ == "__main__":
    st.title("Nomad Analytix 🤖📊")

    datasets = {}
    with st.sidebar:
        st.title("📂 Selected Datasets")

        uploaded_files = st.file_uploader("📑 Choose a CSV file", accept_multiple_files=True)
        for uploaded_file in uploaded_files:
            datasets[uploaded_file.name.split('.')[0]] = pd.read_csv(uploaded_file)
        if st.button("🔄 Reset", type="primary"):
            del st.session_state["messages"]
        if "openai_model" not in st.session_state:
            st.session_state["text_model"] = "gpt-4o"
            st.session_state["vision_model"] = "gpt-4-turbo-2024-04-09"

        if "messages" not in st.session_state:
            st.session_state.messages = []
            # st.session_state.messages.append({"role": "system", "content": get_system_prompt(datasets)})
        if len(st.session_state.messages) > 1:
            if st.button("Rerun"):
                del st.session_state["messages"][-3:]

        st.header("About Nomad Analytix 🌟")
        st.markdown("""
        **Nomad Analytix** is a revolutionary platform designed to automate and enhance data analysis tasks, making sophisticated data insights accessible to non-technical teams. Here are some of its key features:
        - 📊 **Automated Data Analysis:** Simplifies complex data analysis tasks.
        - 🗣️ **Natural Language Interface:** Interact with data using intuitive natural language prompts.
        - 📈 **Advanced Visualizations:** Generate insightful visualizations effortlessly.
        - 🎯 **Actionable Recommendations:** Receive recommendations based on comprehensive data analysis.
        - 🚀 **Prototype on Streamlit:** Demonstrates capabilities on the Streamlit platform.
        - 🔍 **Future Integration with VLMs:** Plans to integrate Vision Language Models for enhanced functionality.
        """)


    if not datasets:
        st.markdown("""
        ## Welcome to Nomad Analytix!
        
        Nomad Analytix is an innovative data analysis assistant designed to help you extract valuable insights from your data with ease. 
        Using advanced AI and vision models, our platform automates complex data analysis tasks and makes sophisticated insights accessible to everyone, regardless of technical expertise.
        
        ### Features:
        - **Automated Data Analysis**: Let our AI handle the heavy lifting of data analysis.
        - **Natural Language Interface**: Ask questions about your data in plain English.
        - **Insightful Visualizations**: Generate clear and actionable visualizations.
        - **Actionable Recommendations**: Get data-driven recommendations for your business.
        
        ### Get Started:
        1. **Upload Your Data**: Use the sidebar to upload your CSV files.
        2. **Ask Questions**: Enter your questions about the data in the input box.
        3. **View Results**: See visualizations and insights generated from your data.
        
        Let's unlock the full potential of your data together! 🚀
        """)

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
        if not st.session_state['messages']:
            st.session_state.messages.append({"role": "system", "content": get_system_prompt(datasets)})

        if prompt := st.chat_input("Ask something "):
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant").status("Running... 🏃‍") as status:
                for _ in range(3):
                    try:
                        graph = get_graph(datasets, st.session_state["text_model"], prompt)
                        st.code(graph)
                        print(graph)
                        exec(graph, globals(), locals())
                        error_flag = False
                        status.update(label="Done ✔️", state="complete")
                        break
                    except Exception as e:
                        st.write(f"Error: {e}")
                        st.session_state.messages.pop()
                        continue
                else:
                    status.update(label="Error ⚠️", state="error")
                    error_flag = True

            if error_flag:
                st.write('There was an error, ask the question again to retry or try changing the question')

            elif not error_flag:
                st.pyplot(fig)
                plt.savefig("output.png")

                with st.chat_message("inference", avatar="✨").status("Running...") as status:
                    out = run_image_request(prompt, st.session_state["vision_model"], "output.png",
                                            st.session_state.messages)
                    status.update(label="Done ✔️", state="complete")

                st.write(out)
                st.session_state.messages.append({"role": "assistant", "content": out})
            print(st.session_state.messages[0])