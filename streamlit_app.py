import matplotlib.pyplot as plt
import warnings
import streamlit as st
import sqlite3
from control import *
from query_handler import *

import openai

warnings.filterwarnings("ignore")

# Set up page configuration
st.set_page_config(
    page_title="Nomad Analytix",
    page_icon="📊",
)

st.set_option('deprecation.showPyplotGlobalUse', False)

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

        if len(st.session_state.messages) > 1 and st.button("Rerun"):
            while st.session_state["messages"][-1]["role"] != "user":
                st.session_state.messages.pop()
            st.session_state.messages.pop()

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

    if not (datasets and os.path.exists(".streamlit/secrets.toml")):
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
        # Retrieve OpenAI API key from Streamlit secrets
        if not os.path.exists(".streamlit/secrets.toml"):
            key = st.text_input("Enter OpenAI API Key to begin", type="password")
            if not key:
                st.stop()
            with open(".streamlit/secrets.toml", "w") as file:
                file.write(f'OPENAI_API_KEY="{key}"')

        openai.api_key = st.secrets["OPENAI_API_KEY"]


    else:
        # Message history setup
        openai.api_key = st.secrets["OPENAI_API_KEY"]
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

        if not st.session_state['messages']:
            st.session_state.messages.append({"role": "system", "content": get_system_prompt(datasets)})

        # Chatbot interface
        if prompt := st.chat_input("Ask something "):
            with st.chat_message("user"):
                st.markdown(prompt)

            # Check if the user is asking for a descriptive summary
            if check_descriptive(prompt):
                with st.chat_message("inference", avatar="✨").status("Running...") as status:
                    response = handle_descriptive_query(prompt)
                    status.update(label="Done ✔️", state="complete")

                st.markdown(response)
                st.session_state.messages.append({"role": "assistant", "content": response})

            # Handle code generation and visualization
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
