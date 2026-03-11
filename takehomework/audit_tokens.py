import glob
import os
from jinja2 import Environment, FileSystemLoader
from litellm import token_counter

def main():
    # Path to the prompts
    prompt_dir = os.path.join("openhands", "agenthub", "codeact_agent", "prompts")
    if not os.path.exists(prompt_dir):
        print(f"Error: {prompt_dir} does not exist.")
        return

    # Initialize Jinja2 with the prompt directory
    env = Environment(loader=FileSystemLoader(prompt_dir))

    # Using your specified Gemini 3.1 model
    model_name = "gemini/gemini-3.1-pro-preview"

    # CRITICAL FOR AUDIT: Mock data to represent actual runtime variables
    # This prevents variables from being rendered as empty strings (0 tokens)
    mock_context = {
        "tools": "Tool definitions for: execute_bash, web_search, edit_file",
        "environment": "Ubuntu 22.04 with Python 3.11",
        "task": "Fix the bug in the main logic of the repository.",
        "p_philosophy": "Be concise and favor direct code execution.",
        "hints": "Look at the imports first.",
        "microagents": "Available: python_executor, file_manager"
    }

    print(f"--- OPENHANDS PROMPT AUDIT (Model: {model_name}) ---")
    print(f"{'Template Name':<40} : {'Tokens (Raw)':>12} | {'Tokens (Rendered)':>12}")
    print("-" * 85)

    j2_files = glob.glob(os.path.join(prompt_dir, "*.j2"))

    for filepath in sorted(j2_files):
        filename = os.path.basename(filepath)
        try:
            # 1. Count Raw Tokens (the .j2 file as it sits on disk)
            with open(filepath, 'r') as f:
                raw_content = f.read()
                raw_tokens = token_counter(model=model_name, text=raw_content)

            # 2. Count Rendered Tokens (as the model actually sees it)
            template = env.get_template(filename)
            rendered_content = template.render(**mock_context)

            messages = [{"role": "user", "content": rendered_content}]
            rendered_tokens = token_counter(model=model_name, messages=messages)

            print(f"{filename:<40} : {raw_tokens:>12} | {rendered_tokens:>12}")

        except Exception as e:
            print(f"{filename:<40} : Failed - {e}")

if __name__ == "__main__":
    main()
