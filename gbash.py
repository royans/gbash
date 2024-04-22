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

import google.generativeai as genai


def generate_script(model, command):
    """
    Generates a Bash script from a natural language command using a generative AI model.

    Args:
        model: The Generative AI model instance.
        command: The natural language command to interpret.

    Returns:
        The generated Bash script as a string.
    """

    self_info=execute_and_capture("cat /etc/issue | grep -v ^$; uname -a;");

    prompt = f"""You are a command interpreter for a system administrator who doesn't know how to use bash. 
    Your goal is to interpret the questions asked by the admin and convert the question into a working bash script which the user could run.
    Make sure that the script is executable and test it yourself before you give back the answer.

    The command from the admin will follow after two empty lines. The Script should start with "#!/bin/bash".
    It should be possible to execute that script without any errors. Please test before you generate the script.


    """ + command

    print(prompt)

    response = model.generate_content(prompt)
    script = response.text.replace("```bash", "").replace("```", "")
    return script


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
    """
    Interprets a command-line argument as a natural language command,
    generates a Bash script, executes it, and cleans up.
    """


    debug=0

    if len(sys.argv) < 2:
        print("Error: Please provide a prompt as a command-line argument.")
        sys.exit(1)

    command = sys.argv[1]

    if command == "-d":
        debug=1
        command = sys.argv[2]

    genai.configure(api_key=os.getenv("API_KEY"))
    model = genai.GenerativeModel('gemini-pro')
    script = generate_script(model, command)
    temp_file_path = create_temp_file(script)

    try:
        if debug==1:
            print("================================")   
            subprocess.run(["cat", temp_file_path], check=True)
            print("\n================================\n")   
        subprocess.run(["bash", temp_file_path], check=True)
    finally:
        os.remove(temp_file_path)


if __name__ == "__main__":
    main()
