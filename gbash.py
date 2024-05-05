#!/usr/bin/python3
"""
This script uses Google's Generative AI API to interpret natural language commands
and generate Bash scripts for execution.

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

def generate_script(model, command, stage, attachment):
    """
    Generates a Bash script from a natural language command using a generative AI model.
    """

    self_info = execute_and_capture("cat /etc/issue | head -1")
    if len(self_info) > 5:
        self_info = "This system is: " + self_info

    prompt = f"""
    ==================================
    STAGE {stage}
    ==================================

    You are a command interpreter for a system administrator who doesn't know how to use bash. 
    - Your goal is to interpret the questions asked by the admin and help answer it perfectly
    - If you need to run shell scripts using bash, you may do so, but the answers should always be back in english.
    - Your goal is to probe the operating system the user is on and query it to get the right answer
    - You cannot make up answers, you have to let the system tell what the answer is
    - For example, 
        - if you are asked "Whats the hostname", you should help gbash to run a bash script which runs the "hostname" command to get the answer back. The answer should be something like "The hostname is XYZ".
        - if you are asked "what time it is", you should help gbash to run a bash script which runs the "date" command to extract the current date and time. The answer should be something like "The current time on this device is HH:MM:SS"
        - if you are asked "who were the last 10 users", you should first check if "last" command is available. If its available, you should execute "last | head -10" to get the answer.
    - You are NOT authorized to run "sudo" commands.
    - YOUR FINAL ANSWERS MUST ALWAYS BE READABLE ENGLISH.
    - You should avoid giving a "FINAL_ANSWER" directly without running script on the device
    - The log file format and the command outputs may differ between different flavors of linux. Please do not assume any format and use "STAGING_SCRIPT" to validate the formats before giving a FINAL_ANSWER or FINAL_SCRIPT if needed.
        - For example: the file /var/log/auth.log may have username in the first column in some servers... but it may have a datestamp on other servers. So do not assume first column has a username.

    There are three potential outcomes which are possible
    (1) Stage 1:
        - If you understand the question, but need to run a script to get more information, please respond back with “FINAL_SCRIPT” and the script starting at the next line.
        - If you understand the question, but need to run a script just to figure out how to write the “FINAL_SCRIPT” respond back with “STAGING_SCRIPT” and the actual script starting in the next line.
        - If the answer is super clear and you don’t need any script output, you can respond with “FINAL_ANSWER” and write the answer on the next line.


    (2) Stage 2: In stage you, you would be given the original problem statement, the staging script and the output of the staging output
        - Your goal is to create the “FINAL_SCRIPT” or generate the “FINAL_ANSWER”

    (3) Stage 3: In this stage, your goal is to generate “FINAL_ANSWER” based on the best information you have so far.

    Note 
    a) Every time there is a followup, I'll let you know what "Stage" of request it is. The first set of questioning will be called "Stage 1".
    If there is additional information from the follow ups, they will be documented as new Stages in the prompt. Please make sure you read the original request, and subsequent information to provide the most accurate answer.
    b) YOUR OUTPUT MUST ALWAYS start with the one of the following phrases : STAGING_SCRIPT, FINAL_SCRIPT or FINAL_ANSWER
       - THIS IS A REQUIREMENT.

    Here are some requirements
        - You cannot run any sudo commands
        - The final answer SHOULD NOT CONTAIN any bash commands... it should actually be the final answer which doesn't need any code execution. 
        - You cannot make any modifications in file system outside of /tmp/ directory
        - When sharing STAGING_SCRIPT or FINAL_SCRIPT ALWAYS start the script with “#!/bin/bash”
        - Once you generate a STAGING_SCRIPT or FINAL_SCRIPT, you MUST REVIEW IT and MAKE SURE that it will do what its expected to do... do not guess.

    To begin with, here is some basic system info for you to use to provide the answer for Stage 1
    {self_info}

    {"Attachment:" + attachment if attachment else ""}

    Command: {command}
    """  

    response = model.generate_content(
        [prompt]
    )
    script = ''
    try:
        script = response.text.replace("```bash", "").replace("```", "")
    except:
        print("Query failed - ")
        print(response.prompt_feedback)

    return script

def parse_response(response_text):
    """Parses the response from Gemini and identifies the type and content."""

    print("========")
    print(response_text)
    print("========")
    if "FINAL_SCRIPT" in response_text:
        script = re.search(r"FINAL_SCRIPT\n(.*)", response_text, re.DOTALL).group(1)
        return "script", script
    elif "STAGING_SCRIPT" in response_text:
        script = re.search(r"STAGING_SCRIPT\n(.*)", response_text, re.DOTALL).group(1)
        return "staging_script", script
    elif "REQUEST_UNCLEAR" in response_text:
        question = re.search(r"REQUEST_UNCLEAR\n(.*)", response_text, re.DOTALL).group(1)
        return "question", question
    elif "FINAL_ANSWER" in response_text:
        answer = re.search(r"FINAL_ANSWER\n(.*)", response_text, re.DOTALL).group(1)
        return "answer", answer
    else:
        return "unknown", response_text

def create_temp_file(file_content):
    """
    Creates a temporary file with the given content.

    Args:
        file_content: The content to write to the temporary file.

    Returns:
        The path to the created temporary file.
    """

    random_number = random.randint(0, 32766)
    temp_file_path = f"/tmp/gbash.{random_number}"
    with open(temp_file_path, "w") as f:
        f.write(file_content)
    return temp_file_path

def execute_and_capture(command):
    """
	Executes a shell command and returns the output as a string.

  	Args:
      command: The shell command to execute.

    Returns:
      The output of the command as a string.
    """
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    return result.stdout

def main():
    """Interacts with Gemini to process the command and get the final answer."""

    self_id=execute_and_capture("id -u");
    if self_id == 0:
        print("Please do not run as root")
        exit -1

    debug=0

    if len(sys.argv) < 2:
        print("Error: Please provide a prompt as a command-line argument.")
        sys.exit(1)

    command = sys.argv[1]

    if command == "-d":
        debug=1
        command = sys.argv[2]

    generation_config: str ={
      'temperature': 0.8,
      'top_p': 0.5,
      'top_k': 20,
      'max_output_tokens': 4048,
      'stop_sequences': [],
    }

    safety_settings : list[str] = [
        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
    ]

    if os.getenv("API_KEY") is None:
        print("API_KEY is not set... please set it and export it in your shell");
        print('Example: ');
        print(' $ API_KEY="21Ab..........."');
        print(' $ export API_KEY');
        exit()

    genai.configure(api_key=os.getenv("API_KEY"))
    model = genai.GenerativeModel(
		model_name='models/gemini-pro',
		generation_config=generation_config,
        safety_settings=safety_settings
	)
    stage = 1
    attachment = "" 
    while True:
        script = generate_script(model, command, stage, attachment)
        response_type, content = parse_response(script) 
        if response_type == "script":
            # Execute the final script and print the output 
            output = execute_and_capture(content) 
            print(output) 
            break  # We have the final answer 
        elif response_type == "staging_script": 
            # Execute the staging script, capture output, and prepare for next stage
            output = execute_and_capture(content) 
            attachment += f"\n\n== STAGING SCRIPT OUTPUT ==\n{output}"
            stage = 2 
        elif response_type == "question": 
            # Ask the user for clarification and prepare for next stage 
            clarification = input(f"Clarification needed: {content}\nYour answer: ") 
            attachment += f"\n\n== CLARIFICATION ==\n{clarification}"
            stage = 1  # We're still in the initial question stage 
        elif response_type == "answer": 
            # We have the final answer directly 
            print(content) 
            break 
        else:
            print("Error: Unknown response from Gemini.")
            break

if __name__ == "__main__":
    main()
