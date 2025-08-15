# app/main.py
import os
import uuid
import pandas as pd
import shutil
import base64  # <-- ADDED
from typing import Optional

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, Header
from pydantic import BaseModel  # <-- ADDED
from starlette.requests import Request
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .agent_logic import create_agent_runnable, CustomLLM, HumanMessage

# Create FastAPI app instance
app = FastAPI(
    title="ggplot2agent API",
    description="A Self-Debugging Multi-Modal Agent for Robust and Reproducible Scientific Visualization.",
    version="1.0"
)


# --- 2. ADD THE CORS MIDDLEWARE ---
# This section should be placed right after you define the `app` instance.
# It allows requests from any origin, which is suitable for development.
# For production, you should restrict the origins to your frontend's domain.

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
    "http://127.0.0.1",
    "http://127.0.0.1:8080",
    "http://127.0.0.1:3000",
    # You can add the specific URL of your deployed frontend here
    # e.g., "https://your-frontend-domain.com"
    "*" # Using a wildcard is convenient for open APIs or local development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # List of origins that are allowed to make requests
    allow_credentials=True, # Allow cookies to be included in requests
    allow_methods=["*"],    # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],    # Allow all headers
)


# --- Define the Response Model ---
class PlotResponse(BaseModel):
    """
    Defines the successful JSON response structure containing the
    R code and the base64-encoded plot image.
    """
    status: str = "success"
    r_code: str
    image_base64: str
    image_mime_type: str = "image/png"
    pdf_base64: str
    pdf_mime_type: str = "application/pdf"


# --- App State and Lifespan Events (No changes here) ---
@app.on_event("startup")
async def startup_event():
    """On startup, initialize the LLM and compile the agent graph."""
    print("--- Initializing application and compiling agent graph... ---")
    try:
        llm = CustomLLM(api_key=settings.DASHSCOPE_API_KEY, model_name=settings.DEFAULT_MODEL)
        llm.invoke("ping")
        app.state.agent_runnable = create_agent_runnable(llm, settings.MAX_RETRIES)
        print("--- Agent graph compiled successfully. Application is ready. ---")
    except Exception as e:
        print(f"FATAL: Could not initialize LLM or compile agent. Error: {e}")
        app.state.agent_runnable = None
        app.state.startup_error = str(e)


# --- API Endpoint (Modified) ---
@app.post("/generate-plot/", response_model=PlotResponse) # <-- MODIFIED
async def generate_plot(
    request: Request,
    prompt: str = Form(..., description="The detailed request for the plot."),
    data_file: UploadFile = File(..., description="Input CSV data file."),
    reference_image: Optional[UploadFile] = File(None, description="Optional reference image for the plot style."),
    token: Optional[str] = Header(None, description="Dashscope API Key. Overrides server default."),
):
    """
    Generate an R plot from a data file and a prompt.
    Returns a JSON object with the generated R script and a base64-encoded plot image.
    """
    if not app.state.agent_runnable:
        raise HTTPException(status_code=503, detail=f"Service Unavailable: Agent could not be initialized. Error: {app.state.startup_error}")

    api_token = token or settings.DASHSCOPE_API_KEY
    if not api_token:
        raise HTTPException(status_code=401, detail="Dashscope API key not provided in header or server configuration.")

    api_token_a1 = settings.DOUBAO_API_KEY
    if not api_token_a1:
        raise HTTPException(status_code=401, detail="DOUBAO API key not provided in header or server configuration.")

    request_id = str(uuid.uuid4())
    temp_dir_request = os.path.join(settings.TEMP_DIR, request_id)
    os.makedirs(temp_dir_request)
    
    try:
        # 1. Save uploaded files (No changes here)
        data_file_path = os.path.join(temp_dir_request, data_file.filename)
        with open(data_file_path, "wb") as f:
            shutil.copyfileobj(data_file.file, f)

        ref_image_path = None
        if reference_image:
            ref_image_path = os.path.join(temp_dir_request, reference_image.filename)
            with open(ref_image_path, "wb") as f:
                shutil.copyfileobj(reference_image.file, f)
        
        # 2. Prepare initial state (No changes here)
        try:
            df_head_str = pd.read_csv(data_file_path).head().to_string()
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error reading provided CSV file: {e}")

        output_figure_path = os.path.join(temp_dir_request, "output_figure.png")
        output_pdf_path = os.path.join(temp_dir_request, "output_figure.pdf")
        output_code_path = os.path.join(temp_dir_request, "output_script.R")

        initial_state = {
            "messages": [HumanMessage(content=prompt)],
            "user_request": prompt,
            "file_path": os.path.abspath(data_file_path),
            "reference_image_path": os.path.abspath(ref_image_path) if ref_image_path else None,
            "dataframe_head": df_head_str,
            "output_code_path": os.path.abspath(output_code_path),
            "output_figure_path": os.path.abspath(output_figure_path),
            "output_pdf_path": os.path.abspath(output_pdf_path),
            "retry_count": 0,
            "bypass_confirmation": True,
            "error_history": [],
            "api_token": api_token,
            "api_token_a1": api_token_a1,
            "vision_model": settings.DEFAULT_VISION_MODEL
        }

        # 3. Invoke the agent graph (No changes here)
        final_state = request.app.state.agent_runnable.invoke(initial_state)

        # 4. Check for success and prepare response OR handle failure
        if os.path.exists(output_figure_path) and os.path.exists(output_code_path) and os.path.exists(output_pdf_path):
            # SUCCESS PATH: Agent completed and generated all files.
            print("--- Agent finished successfully. Preparing response. ---")
            
            with open(output_code_path, "r", encoding="utf-8") as f:
                r_code_content = f.read()

            with open(output_figure_path, "rb") as f:
                image_bytes = f.read()
            image_base64_str = base64.b64encode(image_bytes).decode("utf-8")
            
            with open(output_pdf_path, "rb") as f:
                pdf_bytes = f.read()
            pdf_base64_str = base64.b64encode(pdf_bytes).decode("utf-8")
            
            return PlotResponse(
                r_code=r_code_content,
                image_base64=image_base64_str,
                pdf_base64=pdf_base64_str
            )
        else:
            # FAILURE PATH: Agent did not generate the expected output files.
            # This means the graph ended at `handle_error_node`.
            print("--- Agent finished with an error. Preparing error response. ---")
            
            # The user-friendly message is the last message generated by the handle_error_node.
            error_detail = "Agent execution failed, and no specific error message was generated. Please check the server logs."
            if final_state.get('messages'):
                # The last message in the state is the user-friendly one we want to show.
                error_detail = final_state.get('messages')[-1].content
            
            # We use HTTP 400 Bad Request, as it's most likely an issue with the user's
            # data or prompt that the agent couldn't resolve. This is more informative
            # than a generic 500 Internal Server Error.
            raise HTTPException(status_code=400, detail=error_detail)

        

    finally:
        # 6. Clean up temporary directory (No changes here)
        if os.path.exists(temp_dir_request):
            shutil.rmtree(temp_dir_request)
