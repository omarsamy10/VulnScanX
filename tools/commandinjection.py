import subprocess
import re
import os
import json

import os
import json

def save_to_json(vulnerability, directory):
    """
    Appends a vulnerability to a JSON file inside the specified directory if it's not already present.

    :param vulnerability: A dictionary containing vulnerability details.
    :param directory: The directory where the JSON file will be saved.
    """
    filename = os.path.join(directory, "vulnerabilities.json")
    
    try:
        # Try to load existing data from the file
        with open(filename, "r") as file:
            data = json.load(file)
    except FileNotFoundError:
        # If the file doesn't exist, initialize with an empty list
        data = []

    # Check if the vulnerability is already in the list
    if vulnerability not in data:
        data.append(vulnerability)

    # Save the updated data back to the file
    with open(filename, "w") as file:
        json.dump(data, file, indent=4)


def commandinjection(url_file,url_directory):
    """
    Run Commix on a list of URLs, extract parameters and payloads, and save results to a JSON file.
    """
    try:
        # Read URLs from the file
        with open(url_file, "r") as f:
            urls = f.readlines()

        # Iterate through each URL
        for url in urls:
            url = url.strip()  # Remove leading/trailing whitespace
            if not url:
                continue  # Skip empty lines

            print(f"Testing URL: {url}")

            # Run Commix for the current URL
            command = ["commix", "--url", url, "--batch"]
            result = subprocess.run(command, capture_output=True, text=True)

            # Prepare the result data
            if result.returncode != 0:
                print(f"Error testing {url}: {result.stderr}")
                # Save an error as a vulnerability with a description
                error_data = {
                    "vulnerability": "Command Injection",
                    "severity": "Critical",
                    "url": url,
                    "description": f"Error encountered: {result.stderr}"
                }
                save_to_json(error_data,url_directory)
            else:
                # Extract parameters and payloads
                parameter_payload_pairs = []

                for line in result.stdout.splitlines():
                    # Extract vulnerable parameters
                    if "injectable" in line:
                        param_match = re.search(r"Parameter '(.+?)' seems injectable", line)
                        if param_match:
                            parameter = param_match.group(1)

                            # Look for a payload on the following lines
                            payload_match = re.search(r"Payload : (.+)", line)
                            payload = payload_match.group(1) if payload_match else "N/A"

                            # Add the parameter-payload pair to the list
                            parameter_payload_pairs.append((parameter, payload))
                        break

                # If parameter-payload pairs are found, save them as results
                if parameter_payload_pairs:
                    description = "\n".join([f"Parameter: {param}, Payload: {payload}" for param, payload in parameter_payload_pairs])
                    description += "\n <strong>Recommended Action : <a href=\"http://127.0.0.1/blog?post=command-injection\"> command injection Blog </a></strong>"
                    data = {
                        "vulnerability": "Command Injection",
                        "severity": "Critical",  # Fixed severity for command injection
                        "url": url,
                        "description": description
                    }
                    save_to_json(data,url_directory)

    except Exception as e:
        error_data = {
            "vulnerability": "Command Injection",
            "severity": "Critical",
            "url": "N/A",
            "description": f"Error: {str(e)}"
        }
        save_to_json(error_data,url_directory)

