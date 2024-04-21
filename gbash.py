#!/usr/bin/python3
################ royans ##################################################
#### NOTE: This is just a proof of concept ###############################
#### NOTE: Its very very VERY risky to run this without safeguards #######
##########################################################################

import os
import sys
import random
import subprocess
import google.generativeai as genai
import json

def getScript(model, command):
  prompt = """You are a command interpretter for a system admin who doesn't know how to use bash.
  Your goal is to interpret the questions asked by the admin and convert the question into a working bash script which the user could run.
  Make sure that the script is executable and test it yourself before you give back the answer.
  The command from the admin will follow after two empty lines. The Script should start with "#!/bin/bash".


  """+command

  output = model.generate_content(prompt).text
  if output is not None:
    output = output.replace("```bash", "")
    output = output.replace("```", "")

  return(output)

def create_temp_file(file_content):
  """
  Creates a temporary file with the given content.

  Args:
    file_content: The content to write to the temporary file.

  Returns:
    The path to the created temporary file.
  """

  # Generate a random integer under 32767
  random_number = random.randint(0, 32766)

  # Create a temporary file path
  temp_file_path = f"/tmp/gbash.{random_number}"

  # Write the content to the temporary file
  with open(temp_file_path, "w") as f:
    f.write(file_content)

  return temp_file_path

def main():
  # Get prompt from command-line argument
  if len(sys.argv) < 2:
    print("Error: Please provide a prompt as a command-line argument.")
    sys.exit(1)
  command = sys.argv[1]

  genai.configure(api_key=os.getenv("API_KEY"))
  model = genai.GenerativeModel('gemini-pro')
  script_name=create_temp_file(getScript(model, command))

  # Execute the script
  os.system("bash "+script_name);

  # Cleanup
  os.system("rm "+script_name);

if __name__ == "__main__":
    main()

