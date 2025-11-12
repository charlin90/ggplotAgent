# ggplotAgent Streamlit App

This project provides a self-debugging, multi-modal agent for robust and reproducible scientific visualization using R's `ggplot2`. This repository contains the user-friendly Streamlit application for generating plots through a simple graphical interface.
<img width="1865" height="1023" alt="image" src="https://github.com/user-attachments/assets/b42d0c91-57c9-4e58-bafb-355ea1d729c1" />


## Prerequisites

1.  **Python 3.9+**
2.  ⚠️ **Docker Desktop:** The agent executes R code in a secure, isolated Docker container. **You must install and run Docker Desktop** for the app to function correctly.
3.  **Git:** For cloning the repository from the command line.

## ⚠️ Important: Docker Setup

Before launching the application, you must prepare the Docker environment. This is a one-time setup.

1.  **Install Docker Desktop:** Download and install Docker Desktop for your operating system (Windows, macOS, or Linux) from the [official Docker website](https://www.docker.com/products/docker-desktop/).

2.  **Start Docker Desktop:** Launch the application. Ensure it is running in the background. You should see the Docker whale icon in your system tray or menu bar.

3.  **Pull the R Environment Image:** The agent relies on a specific Docker image that contains R, `ggplot2`, and all necessary libraries. Open your terminal and run the following command to download it:

    ```bash
    docker pull rocker/tidyverse:latest
    ```
    This command will download the image from Docker Hub. Please wait for the download to complete before proceeding.

## Local Deployment Instructions

Follow these steps to set up and run the application on your local machine.

### Step 1: Clone the Repository

Open your terminal and run the following command to download the project files:

```bash
git clone https://github.com/charlin90/ggplotAgent
cd ggplotAgent/streamlit app/
```

### Step 2: Create a Virtual Environment

It is highly recommended to use a virtual environment to manage dependencies. The following instructions use `conda`.

```bash
# Create the environment
conda create -n ggplotagent python=3.9

# Activate the environment
conda activate ggplotagent
```

### Step 3: Install Dependencies

With your `conda` environment activated, install all the required Python packages using `pip`:
```bash
pip install -r requirements.txt
```

## 🚀 Running the Application

**Ensure Docker Desktop is running and you have successfully pulled the `rocker/tidyverse` image before starting the app.**

1.  Navigate to your project's root directory in your terminal (if you're not already there).
2.  Run the following command:

    ```bash
    python -m streamlit run app/streamlit_app.py
    ```

3.  Your default web browser will automatically open a new tab at `http://localhost:8501`. The application is now ready to use!

## How to Use the App

The interface is designed to be straightforward:

1.  **Plot Request:** In the sidebar, describe the plot you want to create in the text area (e.g., "Create a volcano plot...").
2.  **Data File:** Upload your data in CSV format.
3.  **Reference Image (Optional):** Upload a PNG or JPG image as a style guide for the agent to follow.
4.  🔑 **Configure API Keys (Mandatory):** The AI agent requires API keys to work and supports any OpenAI-compatible API service. The default settings are configured for models available through **Volcano Engine (火山引擎)**. 
    *   You can obtain the necessary API keys, Base URL, and Model Names by registering at [volcengine.com](https://www.volcengine.com/).
    *   In the sidebar, find and expand the **"⚙️ Advanced Settings"** section.
    *   You **must** fill in the `API Key (Text)` and `API Key (Vision)` fields with your valid API keys from your provider.
    *   The `Base URL` and `Model Name` fields are pre-filled with Volcano Engine defaults but can be changed if you use a different service.
5.  **Generate Plot:** Once all inputs and API keys are provided, click the "Generate Plot" button. The agent will show its progress and display the final plot, code, and download links upon completion.
