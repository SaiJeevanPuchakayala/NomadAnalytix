from control import *
import streamlit as st


def get_system_prompt(datasets):
    # Role, Goal, Context Prompting Framework
    role = "You are a highly advanced data analysis assistant."
    goal = "Your goal is to assist users by providing accurate and insightful information and visualizations based solely on the provided datasets."
    context = f"There are {len(datasets)} datasets available 📊. You should only answer questions or queries about these datasets and not provide any information or answer any questions unrelated to them."

    # Dataset details
    dataset_details = ""
    issues = {}

    for i, chosen_dataset in enumerate(datasets):
        dataset_details += f'\nDataset {i + 1}: {chosen_dataset} 📁\n'
        data_desc, issue = create_data_desc(datasets[chosen_dataset])
        dataset_details += data_desc + '\n'
        issues[chosen_dataset] = issue

    for key, value in issues.items():
        if value:
            st.warning(f"⚠️ Dataset {key} has issues in the following columns: {value}\nThis may cause problems in the output, please clean the data.")

    sysp = f"{role}\n{goal}\n{context}\n{dataset_details}"

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
6. Validate the column data types and handle any errors gracefully with clear messages.
7. Do not output the lines of code already provided in the prompt and do not load the dataset again.
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
    answer = find_code_blocks(answer)[0]
    answer = code_begin + answer
    st.session_state.messages[-1]["content"] = question

    return answer


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


def handle_descriptive_query(question):
    # Role, Goal, Context Prompting Framework
    role = "You are an inference bot that provides insights and recommendations based on visualizations."
    goal = "Given the chat history, use the images and the data to provide a detailed answer for the question: "
    context = f'''
    The visualization presented is based on the following user query: {question}.
    Your task is to:
    1. Analyze the graph/image provided.
    2. Infer key insights from the visualization.
    3. Provide actionable recommendations based on the insights.
    4. Ensure the analysis is in simple, understandable language.
    '''
    instructions = f"{role}\n{goal}\n{context}"
    question_to_ask = f"{instructions}\nGot through he chat history and answer the required questions."

    st.session_state.messages.append({"role": "user", "content": question_to_ask})
    response = run_request(st.session_state["text_model"], st.session_state.messages)
    st.session_state.messages[-1]["content"] = question

    return response


def check_descriptive(question):
    catch_words = ["describe", "summary", "details"]
    for word in catch_words:
        if word in question.lower():
            return True
    return False