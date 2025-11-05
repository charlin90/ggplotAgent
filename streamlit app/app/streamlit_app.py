# app/main.py (Now streamlit_app.py)
import os
import uuid
import pandas as pd
import shutil
import base64
import streamlit as st
from pathlib import Path

# Import your existing agent logic and configuration
from app.config import settings
from app.agent_logic import create_agent_runnable, CustomLLM, HumanMessage, AIMessage

# --- Helper Functions ---

def get_file_download_link(file_path: str, filename: str) -> str:
    """Generates a link to download a file."""
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    return f'<a href="data:application/octet-stream;base64,{b64}" download="{filename}">{filename}</a>'



# --- Session State Initialization ---
if "results" not in st.session_state:
    st.session_state.results = None
if "old_temp_dir" not in st.session_state:
    st.session_state.old_temp_dir = None

# --- Streamlit UI Configuration ---

st.set_page_config(
    page_title="ggplotAgent",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)
st.markdown("""
<style>
    /* Reduce top padding in the sidebar */
    section[data-testid="stSidebar"] > div:first-child {
        padding-top: 1rem !important;
    }

    /* Reduce top padding in the main content area */
    .block-container {
        padding-top: 2rem !important;
    }

    /* Keep the sidebar width adjustment */
    section[data-testid="stSidebar"] {
        width: 450px !important; 
    }
</style>
""", unsafe_allow_html=True)

# --- Agent Initialization (Cached) ---

@st.cache_resource
def initialize_agent():
    """
    Initializes the LLM and compiles the agent graph.
    This is cached to prevent re-initialization on every user interaction.
    """
    try:
        with st.spinner("Compiling AI Agent graph... Please wait."):
            # CORRECT: We only compile the graph structure.
            # The actual LLM instances with user-provided settings will be created 
            # on-the-fly inside the agent nodes during each run.
            agent_runnable = create_agent_runnable()
        st.success("AI Agent compiled successfully!")
        return agent_runnable
    except Exception as e:
        st.error(f"FATAL: Could not initialize LLM or compile agent. Error: {e}")
        return None

agent_runnable = initialize_agent()

# --- Main UI ---

st.title("📊 ggplotAgent")
st.markdown("""
A Self-Debugging Multi-Modal Agent for Robust and Reproducible Scientific Visualization.
Enter your request, upload your data, and let the agent generate the R code and plot for you.
**NOTE:** This application uses Docker to execute the R code in a sandboxed environment. Please ensure Docker is running.
""")

# --- Sidebar for User Inputs ---

with st.sidebar:
    st.title("📊 ggplotAgent")
    st.header("⚙️ Inputs")
    
    prompt = st.text_area(
        "**1. Plot Request**",
        height=150,
        placeholder="e.g., 'Create a volcano plot. Color significant points red, using 'p.adj' < 0.05 and |log2FC| > 1 as thresholds. Label the top 10 most significant genes.'"
    )
    
    data_file = st.file_uploader(
        "**2. Data File (CSV)**",
        type=["csv"]
    )
    
    reference_image = st.file_uploader(
        "**3. Reference Image (Optional)**",
        type=["png", "jpg", "jpeg"],
        help="Upload an image as a style reference. The agent will try to mimic its aesthetics."
    )
    
    st.markdown("---")
    
    # Use Dashscope and Doubao API keys from settings as defaults
    # In a real application, you might use st.text_input for users to provide their own keys
    # For simplicity, we'll rely on the environment variables.
    st.info(f"""
    **Models in Use:**
    - Text: `{settings.DEFAULT_MODEL}`
    - Vision: `{settings.DEFAULT_VISION_MODEL}`
    """)
    with st.expander("⚙️ Advanced Settings"):
        st.subheader("Text Model API")
        base_url = st.text_input(
            "Base URL (Text)",
            value="https://ark.cn-beijing.volces.com/api/v3",
            help="The base URL for the OpenAI-compatible text API."
        )
        model_name = st.text_input(
            "Model Name (Text)",
            value=settings.DEFAULT_MODEL,
            help="e.g., deepseek-v3-250324"
        )
        api_key = st.text_input(
            "API Key (Text)",
            type="password",
            help="Your API key for the text model."
        )
        
        st.subheader("Vision Model API")
        vision_base_url = st.text_input(
            "Base URL (Vision)",
            value="https://ark.cn-beijing.volces.com/api/v3", # 默认值可能与文本模型相同
            help="The base URL for the OpenAI-compatible vision API."
        )
        vision_model = st.text_input(
            "Model Name (Vision)",
            value=settings.DEFAULT_VISION_MODEL,
            help="e.g., doubao-1-5-thinking-vision-pro-250428"
        )
        vision_api_key = st.text_input(
            "API Key (Vision)",
            type="password",
            help="Your API key for the vision model."
        )
        st.subheader("Agent Behavior")
        max_retries_input = st.number_input(
            "Maximum Retries",
            min_value=1,
            max_value=10,
            value=3,
            step=1,
            help="The maximum number of times the agent will try to debug a failed script."
        )

    is_disabled = not all([agent_runnable, prompt, data_file])
    generate_button = st.button("Generate Plot", type="primary", use_container_width=True, disabled=is_disabled)

# --- Main Content Area for Outputs ---

if generate_button:
    # Clean up the previous run's temporary directory if it exists
    if st.session_state.old_temp_dir and st.session_state.old_temp_dir.exists():
        shutil.rmtree(st.session_state.old_temp_dir, ignore_errors=True)
    st.session_state.results = None # Reset results for the new run
    # Validate inputs
    if not prompt:
        st.warning("Please enter a plot request.")
    elif not data_file:
        st.warning("Please upload a CSV data file.")
    else:
        # --- Prepare for Agent Run ---
        # 1. Create a temporary directory for this request
        request_id = str(uuid.uuid4())
        temp_dir_request = Path(settings.TEMP_DIR) / request_id
        temp_dir_request.mkdir(parents=True, exist_ok=True)
        st.session_state.old_temp_dir = temp_dir_request

        try:
            # 2. Save uploaded files
            data_file_path = temp_dir_request / data_file.name
            with open(data_file_path, "wb") as f:
                f.write(data_file.getvalue())

            ref_image_path = None
            if reference_image:
                ref_image_path = temp_dir_request / reference_image.name
                with open(ref_image_path, "wb") as f:
                    f.write(reference_image.getvalue())
            
            # 3. Prepare Initial State
            try:
                df_head_str = pd.read_csv(data_file_path).head().to_string()
            except Exception as e:
                st.error(f"Error reading provided CSV file: {e}")
                # Stop execution if CSV is invalid
                st.stop()
            
            output_figure_path = temp_dir_request / "output_figure.png"
            output_pdf_path = temp_dir_request / "output_figure.pdf"
            output_code_path = temp_dir_request / "output_script.R"

            initial_state = {
                "messages": [HumanMessage(content=prompt)],
                "user_request": prompt,
                "file_path": str(data_file_path.absolute()),
                "reference_image_path": str(ref_image_path.absolute()) if ref_image_path else None,
                "dataframe_head": df_head_str,
                "output_code_path": str(output_code_path.absolute()),
                "output_figure_path": str(output_figure_path.absolute()),
                "output_pdf_path": str(output_pdf_path.absolute()),
                "retry_count": 0,
                "bypass_confirmation": True,
                "error_history": [],
                "base_url": base_url,
                "model_name": model_name,
                "api_key": api_key or settings.DASHSCOPE_API_KEY,
                "vision_api_key": vision_api_key or settings.DOUBAO_API_KEY,
                "vision_model": settings.DEFAULT_VISION_MODEL,
                "vision_base_url": vision_base_url,
                "max_retries": max_retries_input
            }

            # --- Stream Agent Execution ---
            final_state = {}
            with st.status("Agent is working...", expanded=True) as status:
                st.write("🚀 Agent initiated. Starting process...")
                
                # The .stream() method yields a dictionary for each step, 
                # with the key being the node name and the value being its output.
                for state_chunk in agent_runnable.stream(initial_state):
                    # state_chunk is typically like {'node_name': {'messages': [...], 'current_step': '...'}}
                    
                    # Check if the final state is in the current chunk
                    if "__end__" in state_chunk:
                        final_state = state_chunk["__end__"]
                    
                    # We iterate through the values of the chunk. Usually there's only one.
                    for node_output in state_chunk.values():
                        # Ensure the output is a dictionary before trying to access it
                        if isinstance(node_output, dict):
                            # Check for the progress update message
                            current_step_desc = node_output.get("current_step")
                            if current_step_desc:
                                status.update(label=current_step_desc)
                                st.write(f"🔄 {current_step_desc}")

                # After the loop, update the status based on the final outcome
                if output_figure_path.exists():
                     status.update(label="✅ Plot generated successfully!", state="complete", expanded=False)
                else:
                     status.update(label="❌ Agent failed to generate the plot.", state="error", expanded=True)

            
            if output_figure_path.exists():
                with open(output_code_path, "r", encoding="utf-8") as f:
                    r_code = f.read()
                
                st.session_state.results = {
                    "figure_path": str(output_figure_path),
                    "pdf_path": str(output_pdf_path),
                    "code": r_code,
                    "success": True
                }
            else:
                error_message = "An unknown error occurred."
                if final_state and final_state.get('messages'):
                     error_message = final_state.get('messages')[-1].content
                st.session_state.results = {
                    "error": error_message,
                    "success": False
                }            
        except Exception as e:
            st.error(f"Error processing your request: {e}")

                
# --- Display results if they exist in session state ---
if st.session_state.results:
    st.subheader("Results")
    
    if st.session_state.results["success"]:
        st.success("Plot generated successfully!")
        
        left_spacer, image_col, right_spacer = st.columns([1, 3, 1])
        with image_col:
            st.image(st.session_state.results["figure_path"], caption="Generated Plot", use_container_width='auto')
        
        r_code = st.session_state.results["code"]
        with st.expander("View Generated R Code"):
            st.code(r_code, language='r')
        
        st.markdown("### 📥 Downloads")
        col1, col2, col3 = st.columns(3)
        with col1:
            with open(st.session_state.results["figure_path"], "rb") as file:
                st.download_button(
                    label="Download PNG",
                    data=file,
                    file_name="generated_plot.png",
                    mime="image/png",
                    use_container_width=True
                )
        with col2:
             with open(st.session_state.results["pdf_path"], "rb") as file:
                st.download_button(
                    label="Download PDF",
                    data=file,
                    file_name="generated_plot.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        with col3:
            st.download_button(
                label="Download R Script",
                data=r_code,
                file_name="plotting_script.R",
                mime="text/plain",
                use_container_width=True
            )
    else:
        st.error("The agent failed to generate the plot.")
        st.text_area("Error Details", st.session_state.results["error"], height=200)