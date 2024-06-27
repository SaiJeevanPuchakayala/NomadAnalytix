import openai
import google.generativeai as genai
import os
import re
import base64


def run_request(question_to_ask, model_type):
    if "gpt" in model_type :
        key = os.environ['OPENAI_API_KEY']
        # Run OpenAI ChatCompletion API
        task = "Generate Python Code Script that provides a graph for the asked question."
        if model_type == "gpt-4o":
            # Ensure GPT-4 does not include additional comments
            task = task + " The script should only include code, no comments."
        openai.api_key = key
        response = openai.ChatCompletion.create(model=model_type,
            messages=[{"role": "system", "content": task},{"role": "user", "content": question_to_ask}])

        llm_response = response["choices"][0]["message"]["content"]
        llm_response = format_response(llm_response)

    elif "gemini" in model_type:
        # Gemini model
        genai.configure(api_key=os.environ['GEMINI_API_KEY'])
        # Choose a model that's appropriate for your use case.
        model = genai.GenerativeModel(model_type)

        prompt = question_to_ask

        llm_response = model.generate_content(prompt).text
        llm_response = find_code_blocks(format_response(llm_response))[0]

    return llm_response


def format_response(res):
    # Remove the load_csv from the answer if it exists
    csv_line = res.find("read_csv")
    if csv_line > 0:
        return_before_csv_line = res[0:csv_line].rfind("\n")
        if return_before_csv_line == -1:
            # The read_csv line is the first line so there is nothing to need before it
            res_before = ""
        else:
            res_before = res[0:return_before_csv_line]
        res_after = res[csv_line:]
        return_after_csv_line = res_after.find("\n")
        if return_after_csv_line == -1:
            # The read_csv is the last line
            res_after = ""
        else:
            res_after = res_after[return_after_csv_line:]
        res = res_before + res_after
    return res


def format_question(primer_desc, primer_code, question, model_type):
    # Fill in the model_specific_instructions variable
    instructions = "'datasets' is a dictionary containing the dataframes. Do not include the lines of code that have already been provided in the prompt."
    instructions += "\nDo not assume any columns that have not been provided in the prompt."

    if model_type == "Code Llama":
        # Code llama tends to misuse the "c" argument when creating scatter plots
        instructions += "\nDo not use the 'c' argument in the plot function, use 'color' instead and only pass color names like 'green', 'red', 'blue'."

    instructions += "\nOutput only the code, no explanations or comments."

    primer_desc = primer_desc.format(instructions)
    # Put the question at the end of the description primer within quotes, then add on the code primer.
    return '"""\n' + primer_desc + question + '\n"""\n' + primer_code


def get_primer(datasets):
    primer_desc = "Label the x and y axes appropriately."
    primer_desc = primer_desc + "\nAdd a title. Set the fig suptitle as empty."
    primer_desc = primer_desc + "{}" # Space for additional instructions if needed
    primer_desc = primer_desc + "\nUsing Python version 3.9.12, create a script using the dataframe df to generate a graph looking at which a human can infer the following: "
    pimer_code = "import pandas as pd\nimport matplotlib.pyplot as plt\nimport seaborn as sns\nimport numpy as np\n"
    pimer_code = pimer_code + "fig,ax = plt.subplots(1,1)\n"
    pimer_code = pimer_code + "ax.spines['top'].set_visible(False)\nax.spines['right'].set_visible(False) \n"
    for df_name in datasets:
        pimer_code = pimer_code + f"{df_name} = datasets['{df_name}'].copy()\n"
    return primer_desc, pimer_code


def create_desc_primer(df_dataset):
    # Primer function to take a dataframe and its name
    # and the name of the columns
    # and any columns with less than 20 unique values it adds the values to the primer
    # and horizontal grid lines and labeling
    primer_desc = f"This dataset has columns '" \
        + "','".join(str(x) for x in df_dataset.columns) + "'. "
    issues = []
    for i in df_dataset.columns:
        if len(df_dataset[i].drop_duplicates()) < 20 and df_dataset.dtypes[i]=="O":
            primer_desc = primer_desc + "\nThe column '" + i + "' has categorical values '" + \
                "','".join(str(x) for x in df_dataset[i].drop_duplicates()) + "'. "
        elif df_dataset.dtypes[i]=="int64" or df_dataset.dtypes[i]=="float64":
            primer_desc = primer_desc + "\nThe column '" + i + "' is type " + str(df_dataset.dtypes[i]) + " and contains numeric values. "
        else:
            if df_dataset[i].map(lambda x: x.replace('.','',1).isdigit()).sum() > 20:
                primer_desc = primer_desc + "\nThe column '" + i + "' is probably integer type but contains categorical values. This column has to be cleaned. "
                issues.append(i)
            else:
                primer_desc = primer_desc + "\nThe column '" + i + "' has categorical values."
    return primer_desc, issues


def find_code_blocks(text):
    # Define a regular expression pattern to match ``` followed by anything
    # (non-greedy matching with .*?) and then again ```
    pattern = r"```python(.*?)```"

    # Use re.findall to find all occurrences of the pattern
    code_blocks = re.findall(pattern, text, re.DOTALL)  # re.DOTALL allows matching across lines
    return code_blocks


def run_image_request(question_to_ask, model_type, image_path):
    if "gpt" in model_type:
        key = os.environ['OPENAI_API_KEY']
        # Run OpenAI ChatCompletion API
        task = "Generate Python Code Script."
        openai.api_key = key
        response = openai.ChatCompletion.create(model='gpt-4o',
                                                messages=[
                                                    {
                                                        "role": "system",
                                                        "content": "For the question asked, generate and inference from the graph provided",
                                                    },
                                                    {
                                                        "role": "user",
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
                                                    }
                                                ],
                                                max_tokens=300,
                                                )
        llm_response = response["choices"][0]["message"]["content"]
        return llm_response

    elif "gemini" in model_type:
        # Gemini model
        genai.configure(api_key=os.environ['GEMINI_API_KEY'])
        # Choose a model that's appropriate for your use case.
        model = genai.GenerativeModel(model_type)

        image = genai.upload_file(path=image_path, display_name="Graph Image")

        prompt = "Looking at the graph given make an inference and answer the following: "
        prompt += question_to_ask

        model = genai.GenerativeModel(model_name=model_type)
        llm_response = model.generate_content([image, question_to_ask]).text

        return llm_response


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')