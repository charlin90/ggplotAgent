# ggplotAgent API

This is a FastAPI wrapper for the `ggplotAgent`, a self-debugging multi-modal agent for robust and reproducible scientific visualization.

## Setup

1.  **Clone the repository.**
2.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Configure API Key:**
    Create a file named `.env` in the root directory of the project and add your Dashscope API key:
    ```
    DASHSCOPE_API_KEY="sk-your-real-api-key"
    ```
5.  **Ensure R is installed:** The agent executes R scripts, so `R` and the `Rscript` command must be installed and available in your system's PATH. You also need to have the required R libraries installed. You can install them in R with:
    ```R
    install.packages(c("tidyverse", "ggrepel"))
    ```

## Running the Server

Start the API server using Uvicorn:

```bash
uvicorn app.main:app --reload
```

The API will be available at `http://127.0.0.1:8000`. 

## How to Use the API

You can send requests to the `/generate-plot/` endpoint using tools like `curl` or a Python script.

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

Then, run the `curl` command:

```bash
curl -X POST "http://127.0.0.1:8000/generate-plot/" \
-H "accept: application/json" \
-F "prompt=Create a volcano plot. Label genes with an absolute log2FC > 2 and p_adj < 0.01." \
-F "data_file=@sample_data.csv"
```

### Example with a reference image:

```bash
# Assuming you have a reference_plot.png
curl -X POST "http://127.0.0.1:8000/generate-plot/" \
-H "accept: application/json" \
-F "prompt=Make a plot like the reference image using my data." \
-F "data_file=@sample_data.csv" \
-F "reference_image=@reference_plot.png"
```

