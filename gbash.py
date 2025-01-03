"""
GBash: Natural Language to Bash Command Translator

This script uses Google's Generative AI API (Gemini) to translate natural language 
commands into Bash scripts for execution.

**Disclaimer:** This script is for educational and proof-of-concept purposes only. 
Running generated scripts without proper safeguards can be extremely risky.

https://github.com/royans/gbash/
"""

import os
import sys
import random
import subprocess
import argparse
import re
import google.generativeai as genai


def generate_bash_script(gemini_model, user_command, current_stage, previous_script_output):
    """
    Generates a Bash script from a natural language command using a generative AI model.

    Args:
        gemini_model: The initialized Google Generative AI model.
        user_command: The natural language command from the user.
        current_stage: An integer representing the current stage of the interaction (1, 2, or 3).
        previous_script_output: The output from a previously executed script (if any).

    Returns:
        A string containing the generated script or an empty string if no script is generated.
    """

    system_info = execute_command_capture_output("cat /etc/issue | head -1")
    if len(system_info) > 5:
        system_info = "This system is: " + system_info
    else:
        system_info = ""

    prompt_template = """
    ## System Administrator's Command Interpreter - Stage {current_stage}

    You are a command interpreter designed to assist a system administrator who is not familiar with Bash scripting or the `gcloud` CLI for managing Google Cloud infrastructure.

    **Your Responsibilities:**

    1. **Understand the User's Goal:** Determine the user's ultimate objective from their natural language input.
    2. **Generate Safe and Efficient Bash Scripts (If Necessary):** If a Bash script is absolutely required to fulfill the user's request, create a `FINAL_SCRIPT` that is both safe and efficient.
    3. **Prioritize Dynamic Information Gathering:** When generating scripts, prioritize commands that gather information dynamically to account for variations across Linux distributions.
    4. **Validate Script Actions:** Before presenting any script, thoroughly validate its intended actions to ensure safety and alignment with the user's goal.
    5. **Provide Clear Explanations (FINAL_ANSWER):** Deliver a clear and concise explanation of the solution in plain English, even if a script was necessary. This explanation should be formatted as `FINAL_ANSWER`. If you know what the answer is, do not ask it to run another script. Just say the answer in english.
    6. **Document the state:** Every response MUST start with what STAGE its about. Without that the answer is incorrect and incomplete.

    **References:**

    - `gcloud` Cheatsheet: [https://cloud.google.com/sdk/docs/cheatsheet](https://cloud.google.com/sdk/docs/cheatsheet)
    - `gcloud logging` Reference: [https://cloud.google.com/logging/docs/reference/tools/gcloud-logging](https://cloud.google.com/logging/docs/reference/tools/gcloud-logging)

    **Interaction Stages:**

    - **Stage 1:**
        - Understand the question and determine the best course of action.
        - If a script is needed to gather information for the final answer, respond with `FINAL_SCRIPT`.
        - If a script is needed to learn how to write the `FINAL_SCRIPT`, respond with `STAGING_SCRIPT`.
        - If the answer is clear and no script is needed, respond with `FINAL_ANSWER`.
    - **Stage 2:**
        - You will receive the original problem statement, the `STAGING_SCRIPT`, and its output.
        - Create the `FINAL_SCRIPT` or generate the `FINAL_ANSWER`.
    - **Stage 3:**
        - Generate the `FINAL_ANSWER` based on all available information.
        - The `FINAL_ANSWER` must start with "FINAL_ANSWER" on a new line, followed by the answer in plain English on the next line.

    **Important Notes:**

    - **Error Handling:** If errors occur during script execution, immediately revise the `STAGING_SCRIPT` and re-run it.
    - **Stage Awareness:** The prompt will indicate the current "Stage" of the interaction. Use this information along with the original request and subsequent outputs to provide the most accurate response.
    - **Response Format:** Your response **MUST** always begin with one of the following phrases: `STAGING_SCRIPT`, `FINAL_SCRIPT`, or `FINAL_ANSWER`.
    - **Test Before Answering:** Always test your generated scripts before providing them as a solution.
    - **Script Header:**  `STAGING_SCRIPT` and `FINAL_SCRIPT` must always begin with `#!/bin/bash`.
    - **File System Access:** You are restricted to making modifications only within the `/tmp/` directory.
    - **`sudo` Restriction:** You are **NOT** authorized to execute `sudo` commands.
    - **Readable Final Answers:** Final answers must always be in clear, understandable English and should not contain any Bash commands.
    - **`gcloud` Usage:**
        -  If a request starts with "gcloud:", use the `gcloud` command inside the shell to probe the Google Cloud infrastructure.
        - Add the following line to the bash script if gcloud is being used. This will set the default value for $PROJECT_ID.
            `PROJECT_ID=\`gcloud config get-value project\`; export PROJECT_ID`
        - Do not assume any filters, services, dates, or resource addresses.

    **Examples:**

    - **"What's the hostname?"** -> Generate a script that runs `hostname` and provide an answer like "The hostname is XYZ."
    - **"What time is it?"** -> Generate a script that runs `date` and provide an answer like "The current time on this device is HH:MM:SS."
    - **"Who were the last 10 users?"** -> Check if the `last` command is available. If it is, execute `last | head -10` to get the answer.
    - **"gcloud: Read recent ERROR logs"** -> 
        ```bash
        #!/bin/bash
        PROJECT_ID=`gcloud config get-value project`; export PROJECT_ID
        gcloud logging read "severity:ERROR" --order desc --format json | jq '.[].textPayload'
        ```

    WARNING !!! IMPORTANT REQUIREMENTS !
        - MUST HAVE REQUIREMENT: YOUR OUTPUT MUST ALWAYS start with the one of the following phrases : STAGING_SCRIPT, FINAL_SCRIPT or FINAL_ANSWER 
        - DO NOT GENERATE A "FINAL_ANSWER" without "FINAL_SCRIPT" or "STAGING_SCRIPT" 
            - Please test before you give your answer.
        - Once you generate a STAGING_SCRIPT or FINAL_SCRIPT, you MUST REVIEW IT and MAKE SURE that it will do what its expected to do... do not guess.
        - When sharing STAGING_SCRIPT or FINAL_SCRIPT ALWAYS start the script with “#!/bin/bash” 
        - You cannot make any modifications in file system outside of /tmp/ directory
        - You are NOT authorized to run "sudo" commands.
        - IF YOU HAVE ERRORS IN THE OUTPUT, YOU MUST RETRY THE REQUEST IN A DIFFERENT WAY.
        - The final answer SHOULD NOT CONTAIN any bash commands... it should actually be the final answer which doesn't need any code execution. 
        - YOUR FINAL ANSWERS MUST ALWAYS BE READABLE ENGLISH.
        - THE FINAL ANSWER MUST START WITH THE STRING "FINAL_ANSWER"
        - The log file format and the command outputs may differ between different flavors of linux. 
            - Please do not assume any format and use "STAGING_SCRIPT" to validate the formats before giving a FINAL_ANSWER or FINAL_SCRIPT if needed.
            - For example: the file /var/log/auth.log may have username in the first column in some servers... but it may have a datestamp on other servers. So do not assume first column has a username.


    **Initial System Information:**
    {system_info}

    **Previous Script Output (if any):**
    {previous_script_output}

    **User Command:** {user_command}

    **Please test and confirm your answers before responding.**
    """

    formatted_prompt = prompt_template.format(
        current_stage=current_stage,
        system_info=system_info,
        previous_script_output=previous_script_output if previous_script_output else "No previous script output.",
        user_command=user_command
    )

    #print("-----------------------------------------------------------------------")
    #print(formatted_prompt)
    response = gemini_model.generate_content([formatted_prompt])
    generated_script = ""

    try:
        generated_script = response.text.replace("`bash", "").replace("`", "")
    except Exception:
        print("Query failed -")
        print(response.prompt_feedback)

    return generated_script


def parse_gemini_response(response_text):
    """
    Parses the response from Gemini and identifies the type and content.

    Args:
        response_text: The raw text response from Gemini.

    Returns:
        A tuple containing the response type (string) and the corresponding content (string).
    """
    #print("========")
    #print(response_text)
    #print("========")

    if "FINAL_SCRIPT" in response_text:
        script_match = re.search(r"FINAL_SCRIPT\n(.*)", response_text, re.DOTALL)
        if script_match:
            return "script", script_match.group(1)
    elif "STAGING_SCRIPT" in response_text:
        script_match = re.search(r"STAGING_SCRIPT\n(.*)", response_text, re.DOTALL)
        if script_match:
            return "staging_script", script_match.group(1)
    elif "REQUEST_UNCLEAR" in response_text:
        question_match = re.search(r"REQUEST_UNCLEAR\n(.*)", response_text, re.DOTALL)
        if question_match:
            return "question", question_match.group(1)
    elif "FINAL_ANSWER" in response_text:
        answer_match = re.search(r"FINAL_ANSWER\n(.*)", response_text, re.DOTALL)
        if answer_match:
            return "answer", answer_match.group(1)

    return "unknown", response_text


def create_temp_bash_file(file_content):
    """
    Creates a temporary file with the given content, specifically for bash scripts.

    Args:
        file_content: The content to write to the temporary file.

    Returns:
        The path to the created temporary file.
    """
    temp_file_path = f"/tmp/gbash.{random.randint(0, 32766)}"
    with open(temp_file_path, "w") as temp_file:
        temp_file.write(file_content)
    return temp_file_path


def execute_command_capture_output(command):
    """
    Executes a shell command and returns the output as a string, including up to 10 lines of error output.

    Args:
        command: The shell command to execute.

    Returns:
        A string containing the combined standard output and up to 10 lines of standard error.
    """
    process_result = subprocess.run(command, shell=True, capture_output=True, text=True)
    standard_output = process_result.stdout
    standard_error = process_result.stderr

    if standard_error:
        error_lines = standard_error.splitlines()[:10]  # Capture up to 10 lines of error
        standard_output += "\n\n== ERRORS ==\n" + "\n".join(error_lines)

    return standard_output


def main():
    """
    Main function to interact with Gemini, process commands, and manage the conversation flow.
    """

    user_id = execute_command_capture_output("id -u")
    if user_id.strip() == "0":
        print("Please do not run as root")
        exit(-1)

    parser = argparse.ArgumentParser(description="Translate natural language to Bash commands.")
    parser.add_argument("-d", "--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("command", nargs="*", help="The natural language command to process")
    args = parser.parse_args()

    if not args.command:
        print("Error: Please provide a natural language command.")
        sys.exit(1)

    user_command = " ".join(args.command)

    gemini_generation_config = {
        "temperature": 0.8,
        "top_p": 0.5,
        "top_k": 20,
        "max_output_tokens": 4048,
        "stop_sequences": [],
    }

    gemini_safety_settings = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
    ]

    if os.getenv("API_KEY") is None:
        print("API_KEY environment variable is not set. Please set it before running the script.")
        print("Example:")
        print("  $ export API_KEY=\"your_api_key_here\"")
        sys.exit(1)

    genai.configure(api_key=os.getenv("API_KEY"))
    gemini_model = genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",  # Choose an appropriate model
        generation_config=gemini_generation_config,
        safety_settings=gemini_safety_settings,
    )

    interaction_stage = 1
    previous_script_output_attachment = ""
    query_count = 0
    max_queries = 5

    while query_count < max_queries:
        generated_script = generate_bash_script(
            gemini_model,
            user_command,
            interaction_stage,
            previous_script_output_attachment
        )
        query_count += 1

        response_type, response_content = parse_gemini_response(generated_script)

        if response_type == "script":
            # Execute the final script and print the output
            script_output = execute_command_capture_output(response_content)
            #print(script_output)
            # Send the output back to Gemini to create FINAL_ANSWER
            previous_script_output_attachment = f"\n\n== FINAL SCRIPT OUTPUT ==\n{script_output}"
            interaction_stage = 3
            continue  # Ask Gemini for final answer

        elif response_type == "staging_script":
            # Execute the staging script, capture output, and prepare for the next stage
            script_output = execute_command_capture_output(response_content)
            #print(script_output)
            previous_script_output_attachment = f"\n\n== STAGING SCRIPT OUTPUT ==\n{script_output}"
            interaction_stage = 2

        elif response_type == "question":
            # Ask the user for clarification and prepare for the next stage
            clarification_input = input(f"Clarification needed: {response_content}\nYour answer: ")
            previous_script_output_attachment = f"\n\n== CLARIFICATION ==\n{clarification_input}"
            interaction_stage = 1  # Reset to the initial question stage

        elif response_type == "answer":
            # We have the final answer directly
            print(response_content)
            break  # Exit the loop

        else:
            print("Error: Unknown response format from Gemini.")
            break  # Exit the loop

    if query_count >= max_queries:
        print("Error: Maximum number of queries to Gemini reached.")


if __name__ == "__main__":
    main()
