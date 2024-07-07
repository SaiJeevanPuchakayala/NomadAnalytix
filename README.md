# Nomad Analytix 🤖📊


![Nomad Analytix Logo](./Images/logo.png)


Nomad Analytix is an innovative data analysis assistant designed to help you extract valuable insights from your data with ease. Using advanced AI and vision models, our platform automates complex data analysis tasks and makes sophisticated insights accessible to everyone, regardless of technical expertise.

## Features

- 📊 **Automated Data Analysis:** Streamlines complex data analysis processes.
- 🗣️ **Natural Language Interface:** Engage with data using intuitive natural language queries.
- 📈 **Advanced Visualizations:** Effortlessly create insightful visualizations.
- 🎯 **Actionable Recommendations:** Receive actionable recommendations based on comprehensive data analysis.
- 🚀 **Prototype on Streamlit:** Demonstrates capabilities on the Streamlit platform.
- 🔍 **Integrated with GPT-4 Vision Model:** Leverages advanced Vision Language Models for enhanced functionality, including analyzing and generating insights from visual data.
- 📁 **Support for Multiple File Types:** Upload CSV, Excel, JSON, and SQLite database files.

## Getting Started

### Prerequisites

- Python 3.9.12
- OpenAI API key

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-username/nomad-analytix.git
   cd nomad-analytix
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate   # On Windows, use `venv\Scripts\activate`
   ```

3. **Install the required packages:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables:**
   - Create a `.env` file in the project root and add your OpenAI API key:
     ```plaintext
     OPENAI_API_KEY=your_openai_api_key
     ```

5. **Run the Streamlit app:**
   ```bash
   streamlit run streamlit_app.py
   ```

## File Structure

```plaintext
Nomad Analytix
│   .gitignore
│   LICENSE
│   README.md
│   control.py
│   packages.txt
│   requirements.txt
│   runner.py
│   sqlite_implementation.py
│   streamlit_app.py
│   test.py
├───.streamlit
│       config.toml
├───dataset_files
│       sample_dataset.csv
├───runtime_files
│       example.db
└───Images
        logo.png
```

### Description of Key Files and Directories

- **.streamlit/config.toml:** Configuration file for Streamlit theme and settings.
- **dataset_files/**: Directory containing example datasets.
- **runtime_files/**: Directory for runtime files such as SQLite databases.
- **Images/**: Directory for storing images used in the app (e.g., logo).
- **control.py**: Script for handling UI modifications and control logic.
- **packages.txt**: List of packages for the environment.
- **requirements.txt**: List of Python dependencies for the project.
- **runner.py**: Script for handling error handling and rerun logic.
- **sqlite_implementation.py**: Script for SQLite database integration and export functionality.
- **streamlit_app.py**: Main Streamlit application script.
- **test.py**: Script for error handling and testing.

## Usage

### Launch the Streamlit app

1. **Start the app:**
   Follow the installation instructions above to start the app.

2. **Upload Your Data:**
   Use the sidebar to upload your files (CSV, Excel, JSON, SQLite).

3. **Ask Questions:**
   Enter your questions about the data in the input box.

4. **View Results:**
   See visualizations and insights generated from your data.

### Example Queries

- "Describe the dataset."
- "Show a summary of the data."
- "Generate a bar chart for sales data."

## Contributing

We welcome contributions to Nomad Analytix! To contribute:

1. **Fork the repository.**
2. **Create a new branch:**
   ```bash
   git checkout -b feature-branch
   ```
3. **Make your changes and commit them:**
   ```bash
   git commit -m "Description of changes"
   ```
4. **Push to the branch:**
   ```bash
   git push origin feature-branch
   ```
5. **Submit a pull request.**

## License

This project is licensed under the Apache-2.0 License. See the [LICENSE](LICENSE) file for details.

## Contact

For questions or feedback, please contact:

- **Email:** saijeevan2002@example.com
- **GitHub:** [Sai Jeevan Puchakayala](https://github.com/SaiJeevanPuchakayala)

---

Thank you for using Nomad Analytix! We hope this tool helps you gain valuable insights and make informed decisions from your data.