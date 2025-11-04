# ggplotAgent: Web App and API

This project provides a self-debugging, multi-modal agent for robust and reproducible scientific visualization using R's `ggplot2`. It is accessible through both a user-friendly Streamlit web application and a programmatic FastAPI for developers.

## Prerequisites

1.  **Python 3.8+**
2.  **Docker:** The agent executes R code in a secure, isolated Docker container. **You must have Docker installed and running in the background** for either the web app or the API to function correctly.
3.  **Git:** For cloning the repository.

## Setup

1.  **Clone the repository:**
    ```bash
    git clone <your-repo-url>
    cd ggplotagent_fastapi
    ```

2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    A `requirements.txt` file is recommended to manage all dependencies. It should contain:
    ```txt
    fastapi
    uvicorn[standard]
    streamlit
    pandas
    langchain-core
    langgraph
    pydantic-settings
    openai
    python-multipart
    dashscope
    ```
    Install them all at once with:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Configure API Keys:**
    Create a file named `.env` in the root directory of the project. This file will store your secret API keys. Add the following, replacing the placeholder values with your actual keys:
    ```
    DASHSCOPE_API_KEY="sk-your-dashscope-api-key"
    DOUBAO_API_KEY="your-doubao-api-key"
    ```

## How to Run

You can run this project in two ways. **Make sure Docker is running before you start either one.**

### Option 1: Run the Interactive Web App (Recommended for Users)

The Streamlit app provides an easy-to-use graphical interface for generating plots without writing any code.

1.  Navigate to your project's root directory in your terminal.
2.  Run the following command:
    ```bash
    streamlit run streamlit_app.py
    ```
3.  Your browser will open a new tab at `http://localhost:8501` where you can use the application.

### Option 2: Run the API Server (For Developers)

The FastAPI server is ideal for programmatic access or integration with other services.

1.  Navigate to your project's root directory in your terminal.
2.  Start the API server using Uvicorn:
    ```bash
    uvicorn app.main:app --reload
    ```
3.  The API will be available at `http://127.0.0.1:8000`. You can access the auto-generated documentation at `http://127.0.0.1:8000/docs`.

## How to Use the API

You can send requests to the `/generate-plot/` endpoint using tools like `curl` or a Python script. The API streams status updates and the final result.

### Example with `curl`

First, create a sample data file `sample_data.csv`:
```csv
gene,log2FC,p_adj
Gene1,-2.5,0.001
Gene2,3.1,0.0002
Gene3,1.5,0.04
Gene4,-1.8,0.03
Gene5,0.5,0.6
```

Then, run the `curl` command to stream the response:
```bash
curl -X POST "http://127.0.0.1:8000/generate-plot/" \
-H "accept: application/x-ndjson" \
-F "prompt=Create a volcano plot. Label genes with an absolute log2FC > 2 and p_adj < 0.01." \
-F "data_file=@sample_data.csv"
```

### Example with a reference image:
```bash
# Assuming you have a reference_plot.png
curl -X POST "http://127.0.0.1:8000/generate-plot/" \
-H "accept: application/x-ndjson" \
-F "prompt=Make a plot like the reference image using my data." \
-F "data_file=@sample_data.csv" \
-F "reference_image=@reference_plot.png"
```

