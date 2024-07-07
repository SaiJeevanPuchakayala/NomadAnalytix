import matplotlib.pyplot as plt
import warnings
import streamlit as st
from control import *
from dotenv import load_dotenv
import sqlite3

import openai

warnings.filterwarnings("ignore")

# Retrieve OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]
load_dotenv()
st.set_option('deprecation.showPyplotGlobalUse', False)

# Set up page configuration
st.set_page_config(
    page_title="Nomad Analytix",
    page_icon="📊",
)

def get_system_prompt(datasets, dataset_names):
    # Role
    role = "You are a highly advanced data analysis assistant."

    # Goal
    goal = "Your goal is to assist users by providing accurate and insightful information and visualizations based solely on the provided datasets."

    # Context
    context = f"There are {len(datasets)} datasets available 📊. You should only answer questions or queries about these datasets and not provide any information or answer any questions unrelated to them."

    # Dataset details
    dataset_details = ""
    issues = {}
    for i, (df_name, name) in enumerate(zip(datasets.values(), dataset_names.values())):
        dataset_details += f'\nDataset {i + 1}: {name} 📁\n'
        data_desc, issue = create_data_desc(df_name)
        dataset_details += data_desc + '\n'
        issues[name] = issue

    for key, value in issues.items():
        if value:
            st.warning(f"⚠️ Dataset {key} has issues in the following columns: {value}\nThis may cause problems in the output, please clean the data.")

    # Combining role, goal, context, and dataset details into the system prompt
    sysp = f"{role}\n{goal}\n{context}\n{dataset_details}"

    return sysp

def perform_eda(df):
    eda_report = f"Dataset: {df.name}\n\n"
    eda_report += "### Basic Information\n"
    eda_report += f"Shape: {df.shape}\n"
    eda_report += f"Columns: {df.columns.tolist()}\n"
    eda_report += f"Data Types:\n{df.dtypes}\n"
    eda_report += f"Missing Values:\n{df.isnull().sum()}\n\n"
    eda_report += "### Descriptive Statistics\n"
    eda_report += f"{df.describe()}\n\n"
    eda_report += "### Unique Values per Column\n"
    for col in df.columns:
        eda_report += f"{col}: {df[col].nunique()} unique values\n"
    return eda_report

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
6. Validate the column data types and handle any errors gracefully with clear messages.
7. Avoid duplicating lines of code already provided in the prompt.
8. Utilize EDA results to inform the visualization.
'''

    eda_reports = {}
    for df_name in datasets:
        datasets[df_name].name = df_name  # Adding name attribute to the dataframe
        eda_reports[df_name] = perform_eda(datasets[df_name])

    eda_context = "\n".join(eda_reports.values())
    instructions = f"{role}\n{goal}\n{context}\n{eda_context}"

    code_begin = '''
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

fig, ax = plt.subplots(1, 1)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)

def validate_columns(df, required_columns):
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing columns: {', '.join(missing_columns)}")

def validate_column_types(df, column_types):
    type_errors = []
    for col, col_type in column_types.items():
        if col in df.columns and not pd.api.types.is_dtype_equal(df[col].dtype, col_type):
            type_errors.append(f"Column '{col}' should be of type {col_type}, but got {df[col].dtype}")
    if type_errors:
        raise TypeError(", ".join(type_errors))

'''

    for df_name in datasets:
        code_begin += f"{df_name} = datasets['{df_name}'].copy()\n"

    question_to_ask = f"{instructions}\nUsing the dataframe, create a graph to help a human infer the following: {question}\n{code_begin}"
    st.session_state.messages.append({"role": "user", "content": question_to_ask})

    answer = run_request(selected_model, st.session_state.messages)
    answer = code_begin + answer
    st.session_state.messages[-1]["content"] = question

    return answer

def handle_descriptive_query(datasets, question):
    response = "Here is the information you requested:\n\n"
    for df_name in datasets:
        response += perform_eda(datasets[df_name])
        response += "\n"
    return response

def see_graph(image, selected_model, question):
    # Role, Goal, Context Prompting Framework
    role = "You are an inference bot that provides insights and recommendations based on visualizations."
    goal = "Your goal is to provide accurate, insightful, and actionable recommendations derived from the visualized data."
    context = f'''
    The visualization presented is based on the following user query: {question}.
    Your task is to:
    1. Analyze the graph/image provided.
    2. Infer key insights from the visualization.
    3. Provide actionable recommendations based on the insights.
    4. Ensure the analysis is in simple, understandable language.
    '''
    instructions = f"{role}\n{goal}\n{context}"

    prompt = f"{instructions}\nAnalyze the following graph and provide insights and recommendations:"
    inference = run_image_request(prompt, selected_model, image, st.session_state.messages)
    return inference

if __name__ == "__main__":
    st.title("Nomad Analytix 🤖📊")

    datasets = {}
    with st.sidebar:
        st.image("./Images/logo.png", width=150)  # Replace with your logo path
        st.title("📂 Upload Your Datasets")

        st.markdown("**Supported file types:** CSV, Excel, JSON, SQLite")

        uploaded_files = st.file_uploader("📑 Choose a file", accept_multiple_files=True)
        for uploaded_file in uploaded_files:
            up_file_split = uploaded_file.name.split('.')
            if up_file_split[1] == 'csv':
                datasets[up_file_split[0]] = pd.read_csv(uploaded_file)
            elif up_file_split[1] == 'xlsx':
                datasets[up_file_split[0]] = pd.read_excel(uploaded_file)
            elif up_file_split[1] == 'json':
                datasets[up_file_split[0]] = pd.read_json(uploaded_file)
            elif up_file_split[1] == 'db':
                with open(os.path.join("runtime_files", uploaded_file.name), "wb") as f:
                    f.write(uploaded_file.getbuffer())
                conn = sqlite3.connect("runtime_files/" + uploaded_file.name)
                table_names = pd.read_sql_query("SELECT name FROM sqlite_master WHERE type='table';", conn)['name'].tolist()
                for table_name in table_names:
                    datasets[table_name] = pd.read_sql_query(f"SELECT * FROM {table_name};", conn)
        if st.button("🔄 Reset", type="primary"):
            del st.session_state["messages"]
        if "openai_model" not in st.session_state:
            st.session_state["text_model"] = "gpt-4o"
            st.session_state["vision_model"] = "gpt-4-turbo-2024-04-09"

        if "messages" not in st.session_state:
            st.session_state.messages = []
            # st.session_state.messages.append({"role": "system", "content": get_system_prompt(datasets)})
        if len(st.session_state.messages) > 1 and st.button("Rerun"):
            del st.session_state["messages"][-3:]

        st.header("About Nomad Analytix 🌟")
        st.markdown("""
        **Nomad Analytix** is a cutting-edge platform designed to automate and elevate data analysis tasks, providing sophisticated data insights to non-technical teams. Here are some of its key features:
        - 📊 **Automated Data Analysis:** Streamlines complex data analysis processes.
        - 🗣️ **Natural Language Interface:** Engage with data using intuitive natural language queries.
        - 📈 **Advanced Visualizations:** Effortlessly create insightful visualizations.
        - 🎯 **Actionable Recommendations:** Receive actionable recommendations based on comprehensive data analysis.
        - 🚀 **Prototype on Streamlit:** Demonstrates capabilities on the Streamlit platform.
        - 🔍 **Integrated with GPT-4 Vision Model:** Leverages advanced Vision Language Models for enhanced functionality, including analyzing and generating insights from visual data.
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
        - **Support for Multiple File Types**: Upload CSV, Excel, JSON, and SQLite database files.
        - **Integrated with GPT-4 Vision Model**: Analyze and derive insights from visual data.
        
        ### Get Started:
        1. **Upload Your Data**: Use the sidebar to upload your files.
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

            if "describe" in prompt.lower() or "summary" in prompt.lower() or "details" in prompt.lower():
                response = handle_descriptive_query(datasets, prompt)
                with st.chat_message("assistant"):
                    st.markdown(response)
            else:
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
                    plt.savefig("runtime_files/output.png")

                    with st.chat_message("inference", avatar="✨").status("Running...") as status:
                        out = see_graph('runtime_files/output.png', st.session_state["vision_model"], prompt)
                        status.update(label="Done ✔️", state="complete")

                    st.write(out)
                    st.session_state.messages.append({"role": "assistant", "content": out})
