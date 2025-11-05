# app/agent_logic.py

import os
import uuid
import subprocess
import operator
import pandas as pd
from io import StringIO
from typing import TypedDict, List, Union, Optional
from typing_extensions import Annotated
from functools import partial

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.language_models.llms import LLM
from langgraph.graph import StateGraph, END
from dashscope import MultiModalConversation, Generation
from http import HTTPStatus

import base64
from openai import OpenAI
from openai import APIError, RateLimitError # 引入具体的异常类型，便于处理

# --- 0. LLM Vision Configuration ---
# doubao vision model
def encode_image_to_base64(image_path: str) -> str:
    """
    Reads an image file and encodes it into a Base64 string.
    """
    image_type = image_path.split('.')[-1].lower()
    if image_type == 'jpg':
        image_type = 'jpeg' # 标准的MIME type是jpeg
    
    with open(image_path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return f"data:image/{image_type};base64,{encoded_string}"

def vision_large_model(prompt: str, image_path: str, api_key: str, model: str, base_url: str) -> str:
    """
    Calls a Doubao Vision Language (VL) model with a local image.
    
    Args:
        prompt: The text prompt to send to the model.
        image_path: The local path to the image file.
        api_key: Your API key for the Doubao service.
        model: The model identifier.

    Returns:
        The text response from the model.
    """
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"Image file not found at: {image_path}")

    client = OpenAI(
        # 这是豆包大模型在火山引擎方舟平台上的接入点
        base_url=base_url,
        # 从参数中获取您的 API Key
        api_key=api_key
    )

    try:
        # 1. 将图片编码为 Base64 data URI
        base64_image_url = encode_image_to_base64(image_path)

        # 2. 发送请求
        response = client.chat.completions.create(
            # 指定模型 ID
            model=model,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image_url",
                            "image_url": {
                                # 使用 Base64 编码后的 data URI
                                "url": base64_image_url
                            },
                        },
                        {
                            "type": "text",
                            "text": prompt
                        },
                    ],
                }
            ]
        )

        # 3. 返回模型生成的文本内容
        print("=" * 20 + "思考过程" + "=" * 20)
        print(f"{response.choices[0].message.reasoning_content}")
        print("\n" + "=" * 20 + "完整回复" + "=" * 20)

        #print(f"{response.choices[0].message.content}")
        return response.choices[0].message.content

    except FileNotFoundError as e:
        print(f"Error: {e}")
        return "Error: Image file not found."
    except (APIError, RateLimitError) as e:
        print(f"API call failed: {e}")
        return f"Error: API call failed - {e}"
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return "Error: An unexpected error occurred."

def text_large_model(prompt: str, api_key: str, model: str,base_url: str) -> str:
    """
    使用与OpenAI API兼容的接口调用大型语言模型。

    Args:
        prompt (str): 要发送给模型的用户输入。
        api_key (str): 用于API调用的认证密钥。
        model (str): 要使用的模型的ID。

    Returns:
        str: 模型返回的文本内容。

    Raises:
        ValueError: 如果API调用失败或发生其他异常。
    """
    try:
        # 初始化OpenAI客户端
        client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )

        # 构建发送给模型的VSS
        messages = [
            {"role": "system", "content": "你是人工智能助手"},
            {"role": "user", "content": prompt}
        ]

        # 发起非流式API调用
        completion = client.chat.completions.create(
            model=model,
            messages=messages,
            stream=False,  # 确保为非流式调用
        )
        
        # 检查响应并返回结果
        if completion.choices and completion.choices[0].message:
            return completion.choices[0].message.content
        else:
            # 在某些错误情况下，choices可能为空
            raise ValueError("API响应无效：未找到有效的choices。")

    except Exception as e:
        # 捕获并抛出所有异常，以便上层调用者处理
        raise ValueError(f"调用API时发生异常: {e}")




class CustomLLM(LLM):
    """Custom LLM wrapper for models."""
    base_url: str
    api_key: str
    model_name: str
    def _call(self, prompt: str, **kwargs) -> str:
        return text_large_model(prompt, self.api_key, self.model_name,self.base_url)
    @property
    def _llm_type(self) -> str: return "text large model"

# --- 2. Graph State Definition ---
class GraphState(TypedDict):
    """Represents the state of our graph, including the full script and error history."""
    messages: Annotated[List[BaseMessage], operator.add]
    user_request: str
    file_path: str
    reference_image_path: Optional[str]
    output_figure_path: str
    output_pdf_path: str
    output_code_path: str
    dataframe_head: str
    plot_plan: Optional[str]
    bypass_confirmation: bool
    full_r_script: str
    plot_image_path: Optional[str]
    error_message: Optional[str]
    qa_feedback: Optional[str]
    retry_count: int
    error_history: Annotated[List[str], operator.add]
    base_url: str
    model_name: str
    api_key: str
    vision_base_url: str
    vision_api_key: str
    vision_model: Optional[str]
    current_step: Optional[str]  # To track the current status for streaming
    max_retries: int

# --- 3. Graph Nodes (Copied directly from your script, no changes needed) ---

def qa_image_checker_node(state: GraphState) -> dict:
    print("--- Step 6: Performing QA check on the generated image...")
    user_request, image_path = state['user_request'], state['plot_image_path']
    if not image_path or not os.path.exists(image_path):
        return {"error_message": "QA Check Failed: Plot image not found for review."}
    api_key = state["vision_api_key"]
    vision_model = state["vision_model"]
    base_url = state["vision_base_url"]
    qa_prompt = f"""
## YOUR ROLE
You are a bioinformatics chart quality assurance expert.

## YOUR TASK
Compare the "User request" to the "Image" and evaluate if the image is **perfect**. A perfect chart meets two conditions:

1.  **Full Compliance with the User Request:** All elements in the chart (type, data, text) closely to match the user request. 
2.  **High Visual Quality:** Ensure all text elements (including labels, annotations, legends, and specific identifiers like gene names) in the figure are clear, fully visible, and not obscured by other graphical components (e.g., data points, shapes, or overlapping text). Verify text/genename completeness, readability, and proper spatial separation from surrounding elements across all regions of the figure. 

## OUTPUT FORMAT
Your response MUST be startwith `MATCH` or `MISMATCH:`. In brief:

- If the image is flawless, the first line must be only the word: `MATCH`
- If there is **any** issue, the first line must be `MISMATCH:` briefly explain your reasoning, point out all inconsistencies with the user request and any visual quality issues you found.

---
**THE USER REQUEST TO VERIFY:**
{user_request}

Importantly, avoid any text label being truncated, especially ensembl ID or gene name. You should know the ensembl ID or gene name, double check. Also, text lable must be kept in plot box. Check for horizontal/vertical dashed lines only, do not compare their matched x/y value with user request.
Now, analyze the attached image and generate your response in the specified format.
"""
    
    try:
        response = vision_large_model(qa_prompt, image_path, api_key, vision_model,base_url).strip()
        print(response)
        if response.upper().startswith("MATCH"):
            print("   > [SUCCESS] QA Check Passed.")
            return {"qa_feedback": None, "error_message": None}
        elif response.upper().startswith("MISMATCH:"):
            feedback = response[len("MISMATCH:"):].strip()
            print(f"   > [FAILURE] QA Check Failed. Reason: {feedback}")
            return {"qa_feedback": feedback, "error_message": f"Visual Mismatch: {feedback}"}
        else:
            print(f"   > [WARNING] QA Check returned ambiguous response: '{response}'. Assuming mismatch.")
            return {"qa_feedback": response, "error_message": f"Ambiguous QA Feedback: {response}"}
    except Exception as e:
        print(f"   > [ERROR] An exception occurred during QA check: {e}")
        return {"error_message": f"QA Vision API call failed: {e}"}

def image_understanding_node_wrapper(state: GraphState) -> dict:
    print("--- Step 0: Analyzing reference image and fusing with user request...")
    image_path, initial_prompt = state.get("reference_image_path"), state['user_request']
    api_key = state["vision_api_key"]
    vision_model = state["vision_model"]
    base_url = state["vision_base_url"]
    try:
        df_preview = pd.read_csv(StringIO(state['dataframe_head']), sep=r'\s{2,}', engine='python')
        available_columns = df_preview.columns.tolist()
    except Exception:
        available_columns = state['dataframe_head'].split('\n')[0].split()
    vision_prompt = f"""Analyze the user's text request and the reference image. Your mission is to fuse them into a structured, specific plotting specification. This specification will serve as the sole input for the next agent (the "Planning Agent") to devise a detailed, step-by-step plotting plan. Your job is to define the requirements, not to execute the plan.

**Inputs:**
- **User's Core Request:** "{initial_prompt}"
- **The Reference Image:** (attached)
- **Available Data Columns:** `{', '.join(available_columns)}`

**Output:**
A Structured Plotting Specification.

Importantly, color names should be standard R color names, use the default font in R, pay special attention to the dashed lines in the image to ensure they are not overlooked. Unless explicitly stated in user's text request, do not specify x/y-axis ranges. 
"""
    detailed_request = vision_large_model(vision_prompt, image_path, api_key, vision_model,base_url)
    print(f"   > [SUCCESS] Image and user request fused into a new, detailed plan:\n{'-'*20}\n{detailed_request}\n{'-'*20}\n")
    return {
        "user_request": detailed_request,
        "current_step": "Step 0: Fusing image and user request..."
    }

def data_validator_node(state: GraphState) -> dict:
    print("--- Step 1: Validating data against user request...")
    try:
        df_preview = pd.read_csv(StringIO(state['dataframe_head']), sep=r'\s{2,}', engine='python')
        available_columns = df_preview.columns.tolist()
    except Exception:
        available_columns = state['dataframe_head'].split('\n')[0].split()
    validator_prompt = f"""You are an expert bioinformatician's assistant. Your task is to determine if the user's plotting request can be fulfilled with the provided data columns. If some column is missing, must check if the information can be preprocessed to create based on provided data.

**User's Request:**
"{state['user_request']}"

**Available Data Columns:**
`{', '.join(available_columns)}`

**CRITICAL INSTRUCTIONS:**
1.  **Be Flexible with Naming:** You MUST account for common scientific abbreviations and synonyms. Your primary goal is to verify if the *required information* exists, not to perform a strict name match. For example:
    *   `log2FC`, `logFC`, or `FoldChange` should all be considered valid for a user request asking for `log2FoldChange`.
    *   `p.adj`, `FDR`, `q-value` should all be considered valid for a request needing an adjusted p-value.
    *   `gene`, `gene_symbol`, `symbol` should all be considered valid for gene names.
2.  **Assume Derivations are Possible:** Assume that simple transformations (like calculating `-log10(FDR)` from `FDR`) are part of the plan. Do not flag these as errors.
3.  **Identify Only FUNDAMENTAL Gaps:** Only return an error if a core piece of information is completely missing and cannot be logically inferred from any of the available columns.

**OUTPUT FORMAT:**
- If all necessary information is present (considering synonyms and derivations), respond with only the word: `OK`
- If a fundamental piece of information is missing, respond with `ERROR:` followed by a brief explanation of what is missing. Example: `ERROR: The request requires a measure of statistical significance (like a p-value or FDR), which is not present in the data.`
"""
    # 1. Get text model settings from the state
    base_url = state["base_url"]
    api_key = state["api_key"]
    model_name = state["model_name"]
    
    # 2. Create a temporary, request-specific LLM instance
    llm = CustomLLM(api_key=api_key, model_name=model_name, base_url=base_url)
    response = llm.invoke(validator_prompt).strip()
    current_status = "Step 1: Validating data against user request..."
    if response.upper().startswith("ERROR:"):
        error_message = response[len("ERROR:"):].strip()
        print(f"   > [FAILURE] Data validation failed: {error_message}")
        return {"error_message": error_message, "current_step": current_status}
    else:
        print("   > [SUCCESS] Data is plausible for the request.")
        return {"current_step": current_status}

def plan_generation_node(state: GraphState) -> dict:
    print("--- Step 2: Generating a full analysis and plotting plan...")
    planner_prompt = f"""You are a senior R data scientist specializing in the **Grammar of Graphics**. Create a comprehensive, two-part plan based on the user's request and data.

**User's Request:** "{state['user_request']}"
**Data Preview:** "{state['dataframe_head']}"

**Your Task:**
**Part 1: Data Preprocessing Plan**
- Detail any necessary `dplyr` or `tidyr` steps for data manipulation (e.g., filtering, mutating new columns like `-log10(pvalue)`, reshaping data).
- If no preprocessing is required, state: "No data preprocessing is needed."

**Part 2: Visualization Plan (Strictly ggplot2)**
- **Core Geometry (`geom_`):** Specify the main geom (e.g., `geom_point`, `geom_boxplot`).
- **Aesthetic Mappings (`aes()`):** Clearly define the mappings for x, y, color, size, shape, etc., using a column name from the data.
- **Layers & Annotations:** Describe any additional layers. **If text labels are requested, you MUST plan to use `ggrepel::geom_text_repel` for intelligent, non-overlapping label placement.**
- **Scales (`scale_`):** Mention any custom color scales (e.g., `scale_color_manual`) or axis transformations if necessary.
- **Theme & Labels:** Plan to use a clean theme like `theme_bw()` or `theme_classic()`. Specify the `labs()` for title, subtitle, x-axis, y-axis, and legend titles.

**CRITICAL CONSTRAINT:** Your entire plan must ONLY rely on functions from the `tidyverse` suite (which includes `ggplot2`, `dplyr`, etc.) and the `ggrepel` package. **Do not suggest any other packages like `ggpubr` or `patchwork` at this stage.** The final output must use column names present in the Data Preview.
"""
    # 1. Get text model settings from the state
    base_url = state["base_url"]
    api_key = state["api_key"]
    model_name = state["model_name"]
    
    # 2. Create a temporary, request-specific LLM instance
    llm = CustomLLM(api_key=api_key, model_name=model_name, base_url=base_url)
    plan = llm.invoke(planner_prompt)
    print("   > Full plan generated.")
    return {
        "plot_plan": plan,
        "current_step": "Step 2: Generating analysis and plotting plan..."
    }

def user_confirmation_node(state: GraphState) -> dict:
    print("\n" + "="*60 + "\n          PLEASE CONFIRM THE FULL ANALYSIS PLAN\n" + "="*60 + f"\n{state['plot_plan']}\n" + "="*60)
    if state.get("bypass_confirmation", False):
        print("\n[INFO] Confirmation bypassed by API call.")
        return {}
    # This part is for CLI and will be bypassed in API context
    while True:
        proceed = input("Do you want to proceed with this plan? (y/n): ").lower().strip()
        if proceed == 'y': return {}
        elif proceed == 'n': return {"error_message": "Task aborted by user."}

def generate_r_code_node(state: GraphState) -> dict:
    print("--- Step 4: Generating complete R script from the plan...")
    coder_system_prompt = f"""You are an expert R programmer who writes clean, efficient, and self-contained code. Your task is to convert the following plan into a complete R script.

**Confirmed Plan:** "{state['plot_plan']}"

**CRITICAL INSTRUCTIONS:**
1.  **Package Environment:** The script will be executed in an environment containing `tidyverse` and `ggrepel`. Therefore, you MUST start the script by loading these libraries:
    ```R
    library(tidyverse)
    library(ggrepel)
    ```
    **DO NOT include any other `library()` calls.**
2.  **Data Input:** Read the data using `read.csv("__INPUT_FILE__")`.
3.  **Plot Object:** The final ggplot object MUST be named `final_plot`.
4.  **Output Files:** You MUST save the final plot in TWO formats using `ggsave()`:
    - **PNG:** `ggsave("__OUTPUT_PNG_FILE__", plot = final_plot, width = 8, height = 6, dpi = 300)`
    - **PDF:** `ggsave("__OUTPUT_PDF_FILE__", plot = final_plot, width = 8, height = 6)`
5.  **Output Format:** Return ONLY the raw R code. Do not wrap it in markdown backticks (```r...```) or provide any explanations.
"""
    # 1. Get text model settings from the state
    base_url = state["base_url"]
    api_key = state["api_key"]
    model_name = state["model_name"]
    
    # 2. Create a temporary, request-specific LLM instance
    llm = CustomLLM(api_key=api_key, model_name=model_name, base_url=base_url)
    response = llm.invoke(coder_system_prompt)
    full_script = clean_r_code(response)
    print(full_script)
    print("   > Complete R script generated.")
    return {
        "full_r_script": full_script,
        "retry_count": 0,
        "error_history": [],
        "current_step": "Step 3: Generating R script..."
    }

def debug_r_code_node(state: GraphState) -> dict:
    print(f"--- Debugging Attempt {state['retry_count'] + 1}: Analyzing error...")
    qa_feedback = state.get("qa_feedback")
    if qa_feedback:
        error_type_intro = f"The script ran, but a QA check failed: '{qa_feedback}'"
        history_for_prompt = f"VISUAL QA FAILED\n--- FEEDBACK ---\n{qa_feedback}\n\n--- FAULTY SCRIPT ---\n{state['full_r_script']}"
    else:
        error_type_intro = "An R script you wrote failed to execute. Analyze the script, error, and history to provide a corrected, complete script."
        history_for_prompt = "\n\n".join(state['error_history'])

    debugger_prompt = f"""You are an elite R debugger. {error_type_intro}

**Original Plan:** "{state['plot_plan']}"
**Data Preview:** {state['dataframe_head']}
**ERROR/FEEDBACK HISTORY:**
---
{history_for_prompt}
---
**EXECUTION ENVIRONMENT:** Remember, the R script runs in a Docker container with ONLY the `tidyverse` and `ggrepel` packages installed. Your proposed fix MUST NOT require any other libraries.

**YOUR TASK:**
1.  **Analyze the failure critically.** In a `<thinking>` block, explain your analysis of the error or QA feedback.
2.  **Decide on the action:**
    *   **If you determine the `Visual QA Feedback` is WRONG and the script is already correct:** Explain why in your thinking, and then after the thinking block, you MUST respond with ONLY the exact phrase: `NO_CHANGE_NEEDED`
    *   **If the script genuinely needs fixing (due to a script error OR valid QA feedback):** Explain your fix in your thinking, and then rewrite the entire, complete R script from `library()` to `ggsave()`, adhering strictly to the available packages.

**OUTPUT FORMAT:**
<thinking>
My analysis of the failure and my correction strategy.
</thinking>
# If fixing, the complete R script goes here.
# If QA is wrong, the phrase NO_CHANGE_NEEDED goes here.
"""
    # 1. Get text model settings from the state
    base_url = state["base_url"]
    api_key = state["api_key"]
    model_name = state["model_name"]
    
    # 2. Create a temporary, request-specific LLM instance
    llm = CustomLLM(api_key=api_key, model_name=model_name, base_url=base_url)
    response = llm.invoke(debugger_prompt)
    thought = ""
    if "<thinking>" in response:
        thought = response.split("<thinking>")[1].split("</thinking>")[0].strip()
        print(f"   > Debugger's thought process: {thought}")
    
    fixed_script_or_signal = clean_r_code(response)

    current_status = f"Step 6: Debugging R script (Attempt {state['retry_count'] + 1})..."
    if fixed_script_or_signal.strip() == "NO_CHANGE_NEEDED":
        print("   > [INFO] Debugger determined the code is correct and is overriding the QA feedback.")
        return {"qa_feedback": None, "error_message": "QA_OVERRIDE", "current_step": current_status}
    else:
        print("   > A new, improved full script has been generated for re-execution.")
        return {
            "full_r_script": fixed_script_or_signal,
            "retry_count": state["retry_count"] + 1,
            "error_message": None,
            "qa_feedback": None,
            "current_step": current_status
        }


def clean_r_code(code_string: str) -> str:
    if not isinstance(code_string, str): return ""
    if "<thinking>" in code_string:
        code_string = code_string.split("</thinking>", 1)[-1]
    if "```r" in code_string:
        code_string = code_string.split("```r")[1].split("```")[0]
    elif code_string.strip().startswith("```"):
        code_string = "\n".join(code_string.strip().split('\n')[1:-1])
    return code_string.strip()
from pathlib import Path
def execute_r_code_node(state: GraphState) -> dict:
    attempt_num = state.get('retry_count', 0)
    print(f"--- Step 5 (Execution Attempt {attempt_num + 1})...")
    full_script = state.get('full_r_script')
    if not full_script: return {"error_message": "No R script was generated."}
    
    project_root_host = Path.cwd()
    project_root_container = Path("/work")
    file_path_relative = Path(state['file_path']).relative_to(project_root_host)
    output_figure_path_relative = Path(state['output_figure_path']).relative_to(project_root_host)
    output_pdf_path_relative = Path(state['output_pdf_path']).relative_to(project_root_host)
    
    script_with_paths = full_script.replace("__INPUT_FILE__", file_path_relative.as_posix())
    script_with_paths = script_with_paths.replace("__OUTPUT_PNG_FILE__", output_figure_path_relative.as_posix())
    script_with_paths = script_with_paths.replace("__OUTPUT_PDF_FILE__", output_pdf_path_relative.as_posix())
    
    temp_dir = Path(state['output_figure_path']).parent
    script_path_host = temp_dir / f"temp_script_{uuid.uuid4()}.R"
    script_path_relative = script_path_host.relative_to(project_root_host)
    with open(script_path_host, "w", encoding='utf-8') as f: f.write(script_with_paths)


    # R命令：先安装ggrepel（如果不存在），然后执行我们的目标脚本
    # `repos`参数指定了CRAN镜像，可以加快下载速度
    r_command = f"if(!require('ggrepel', quietly = TRUE)) install.packages('ggrepel'); source('{script_path_relative.as_posix()}')"
    current_status = f"Step 4: Executing R script (Attempt {attempt_num + 1})..."    
    try:
        #result = subprocess.run(["Rscript", script_path], capture_output=True, text=True, check=False)
        workdir_path_str = project_root_container.as_posix() # This will be the string "/work"
        
        # Construct the volume mapping string
        volume_mapping = f"{project_root_host}:{workdir_path_str}"
        result = subprocess.run(
            [
                "docker", "run", "--rm",
                f"--volume={volume_mapping}",
                f"--workdir={workdir_path_str}", # This now passes the pure string "/work"
                "docker.io/rocker/tidyverse:latest",                                      
                "R", "-e", r_command                            
            ],
            capture_output=True, encoding='utf-8', check=False, errors='replace'
        )
        #print(result)
        if result.returncode != 0:
            error_msg = result.stderr.strip()
            print(f"   > [FAILURE] Attempt {attempt_num + 1} failed.")
            history_entry = f"ATTEMPT {attempt_num + 1} FAILED\n--- SCRIPT ---\n{full_script}\n--- ERROR ---\n{error_msg}"
            return {"error_message": error_msg, "error_history": [history_entry],"current_step": current_status}
        else:
            print(f"   > [SUCCESS] Script executed on attempt {attempt_num + 1}.")
            return {"plot_image_path": state['output_figure_path'], "error_message": None,"current_step": current_status}
    except FileNotFoundError:
        return {"error_message": "Rscript command not found. Ensure R is installed and in your system's PATH.","current_step": current_status}
    finally:
        pass

def interpret_error_for_user(state: GraphState) -> str:
    """
    Uses an LLM to interpret the final error and provide actionable advice to the user.
    """
    user_request = state['user_request']
    dataframe_head = state['dataframe_head']
    final_error = state.get('error_message', 'Unknown error.')
    full_script = state.get('full_r_script')

    prompt = f"""
You are a helpful and empathetic AI assistant for a tool called `ggplotagent`. Your user has encountered an error that the agent could not fix automatically. Your task is to explain the problem clearly and provide actionable suggestions.

**Context:**
- **User's Original Request:** "{user_request}"
- **Data Columns Available:** `{dataframe_head.splitlines()[0]}`
- **The Final Error Message:** "{final_error}"
- **The R Script that Failed (if any):** 
```R
{full_script or "No script was generated (error occurred before code generation)."}
```

**Your Mission:**
Based on all the context, generate a user-friendly error message. Follow these rules:
1.  **Start with a clear, apologetic statement:** "I'm sorry, but I ran into a problem I couldn't solve."
2.  **Diagnose the likely root cause in simple terms.** Avoid technical jargon.
    - If the error is about a missing column (e.g., "object not found"), point it out directly.
    - If it's a more complex R error, try to simplify its meaning (e.g., "It seems there was an issue with how the data was structured for the plot.").
    - If the error came from data validation, reiterate that message.
3.  **Provide concrete, actionable suggestions.** This is the most important part.
    - Suggest checking column names for typos.
    - Suggest ensuring the data format matches the request (e.g., "Does your file contain the 'pvalue' column needed for the volcano plot?").
    - Suggest rephrasing the request to be more specific.
4.  **Keep it concise and structured.** Use bullet points for suggestions.

**Example Output:**
"I'm sorry, but I ran into a problem I couldn't solve after a few tries.

**Likely Issue:**
The R code failed because it couldn't find the column named `logFC` in your data.

**Here's what you can try:**
*   Please double-check your uploaded file to ensure a column with fold change information exists.
*   The column might have a different name (e.g., `log2FoldChange`, `FoldChange`). If so, please mention the correct column name in your next request.
*   You could rephrase your request like: 'Create a volcano plot using log2FoldChange for the x-axis and p.adj for the y-axis'."

Importantly, Output should be startwith `I'm sorry`.
"""
    try:
        # 1. Get text model settings from the state
        base_url = state["base_url"]
        api_key = state["api_key"]
        model_name = state["model_name"]
    
        # 2. Create a temporary, request-specific LLM instance
        llm = CustomLLM(api_key=api_key, model_name=model_name, base_url=base_url)
        user_friendly_error = llm.invoke(prompt)
        return user_friendly_error
    except Exception as e:
        print(f"Error while interpreting error for user: {e}")
        return f"I'm sorry, I encountered an unrecoverable error. The final technical error was: {final_error}. Please check your data and request, paying close attention to column names."


def handle_error_node(state: GraphState) -> dict:
    """
    Handles final errors by interpreting them for the user and returning a friendly message.
    """
    error_msg_for_user = interpret_error_for_user(state)
    print(f"\n--- Task Ended with an Unrecoverable Error ---\nUser-Facing Message:\n{error_msg_for_user}")
    
    return {
        "messages": [AIMessage(content=error_msg_for_user)],
        "current_step": "Task Failed. Preparing final error message."
    }



def save_and_finish_node(state: GraphState) -> dict:
    print("\n--- Task Finished Successfully ---")
    with open(state['output_code_path'], "w", encoding='utf-8') as f: f.write(state['full_r_script'])
    print(f"   > Final R script saved to '{state['output_code_path']}'.")
    return {
        "messages": [AIMessage(content="Task complete!")],
        "current_step": "Task Finished Successfully."
    }


# --- 4. Graph Builder ---
def create_agent_runnable():
    """Builds and compiles the langgraph agent."""
    workflow = StateGraph(GraphState)

    # Add nodes
    workflow.add_node("image_analyzer", image_understanding_node_wrapper)
    workflow.add_node("data_validator", data_validator_node)
    workflow.add_node("plan_generator", plan_generation_node)
    workflow.add_node("user_confirmer", user_confirmation_node)
    workflow.add_node("code_generator", generate_r_code_node)
    workflow.add_node("code_executor", execute_r_code_node)
    workflow.add_node("qa_image_checker", qa_image_checker_node)
    workflow.add_node("code_debugger", debug_r_code_node)
    workflow.add_node("save_and_finish", save_and_finish_node)
    workflow.add_node("handle_error", handle_error_node)

    # Define routing logic
    def initial_router(state: GraphState) -> str:
        return "image_analyzer" if state.get("reference_image_path") else "data_validator"
    def route_after_validation(state: GraphState):
        return "handle_error" if state.get("error_message") else "plan_generator"
    def route_after_confirmation(state: GraphState):
        return "handle_error" if state.get("error_message") else "code_generator"
    def route_after_execution(state: GraphState) -> str:
        max_retries = state.get("max_retries", 3)
        if state.get("error_message"):
            return "handle_error" if state.get("retry_count", 0) >= max_retries else "code_debugger"
        return "qa_image_checker"
    def route_after_qa(state: GraphState) -> str:
        max_retries = state.get("max_retries", 3)
        if not state.get("qa_feedback"): return "save_and_finish"
        return "handle_error" if state.get("retry_count", 0) >= max_retries else "code_debugger"

    # NEW routing function to handle the debugger's decision
    def route_from_debugger(state: GraphState) -> str:
        """If QA was overridden, finish. Otherwise, re-run the code."""
        if state.get("error_message") == "QA_OVERRIDE":
            return "save_and_finish"
        return "code_executor"

    # Set entry point and define workflow
    workflow.set_conditional_entry_point(initial_router, {"image_analyzer": "image_analyzer", "data_validator": "data_validator"})
    workflow.add_edge("image_analyzer", "data_validator")
    workflow.add_conditional_edges("data_validator", route_after_validation, {"plan_generator": "plan_generator", "handle_error": "handle_error"})
    workflow.add_edge("plan_generator", "user_confirmer")
    workflow.add_conditional_edges("user_confirmer", route_after_confirmation, {"code_generator": "code_generator", "handle_error": "handle_error"})
    workflow.add_edge("code_generator", "code_executor")
    workflow.add_conditional_edges("code_executor", route_after_execution, {"code_debugger": "code_debugger", "qa_image_checker": "qa_image_checker", "handle_error": "handle_error"})
    workflow.add_conditional_edges("qa_image_checker", route_after_qa, {"save_and_finish": "save_and_finish", "code_debugger": "code_debugger", "handle_error": "handle_error"})
    workflow.add_conditional_edges("code_debugger", route_from_debugger, {
        "code_executor": "code_executor",
        "save_and_finish": "save_and_finish"
    })
    workflow.add_edge("save_and_finish", END)
    workflow.add_edge("handle_error", END)
    
    return workflow.compile()