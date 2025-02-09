from flask import Flask, jsonify,render_template,request
import subprocess
import json
from tools import commandinjection,dalfox,sqlinjection
import os



flask_app=Flask(__name__)


urls_path="urls.txt"
scan_finished=False

#homepage
@flask_app.route("/",methods=["GET","POST"])
def home():
            return render_template("index.html",
                                title="/")
        


# Start-scan route
@flask_app.route("/start-scan", methods=["POST"])
def start_scan():
    url = request.form.get("url")
    headers = request.form.get("headers")
    scan_type = request.form.get("scan-type") 
    subdomain_enum = request.form.get("subdomain-enum")
    crawling=request.form.get("crawling")
    xss = request.form.get("xss") 
    sqli = request.form.get("sql-injection") 
    commandinj = request.form.get("command-injection")
    try:
        if scan_type == "full":
            full_scan(url, headers)
        elif scan_type == "custom":
            custom_scan(url, headers, subdomain_enum,crawling, xss, sqli, commandinj)
        return "Scan initiated."
    except Exception as e:
        return


#results
@flask_app.route("/results",methods=["GET","POST"])
def results():
            return render_template("results.html",
                                title="/results")
    



#blog
# List of available blog posts
BLOG_POSTS = [
    {"id": "command-injection", "title": "Command Injection"},
    {"id": "sql-injection", "title": "SQL Injection"},
    {"id": "xss", "title": "Cross-Site Scripting (XSS)"}
]

@flask_app.route("/blog", methods=["GET"])
def blog():
    # Check if a specific post is requested
    if "post" in request.args:
        post_id = request.args["post"]
        # Render the corresponding post template
        if post_id == "command-injection":
            return render_template("command-injection.html", title="Command Injection")
        elif post_id == "sql-injection":
            return render_template("sql-injection.html", title="SQL Injection")
        elif post_id == "xss":
            return render_template("xss.html", title="XSS")
        else:
            return "Post not found", 404
    else:
        # Render the list of available posts
        return render_template("blog.html", posts=BLOG_POSTS, title="Blog")
            
    


@flask_app.route("/getresults", methods=["GET"])
def get_results():
    results_file = "vulnerabilities.json"
    
    if not os.path.exists(results_file):
        return jsonify({"error": "Results file not found", "scan_finish": False})
    
    with open(results_file, "r") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            return jsonify({"error": "Invalid JSON format", "scan_finish": False})

    return jsonify({**data, "scan_finish": scan_finished})





def full_scan(url,headers):
    global scan_finished
    subdomain_enum=True
    recon(url,subdomain_enum)
    dalfox.run_dalfox_on_url(urls_path)
    commandinjection.commandinjection(urls_path)
    sqlinjection.sql_injection_test(urls_path,headers,level="1",risk="1")
    scan_finished=True


def custom_scan(url,headers,subdomain_enum,crawling,xss,sqli,commandinj):
    global scan_finished
    if crawling=="on" or subdomain_enum=="on":
        recon(url,subdomain_enum)
    else:
        with open("urls.txt", "a") as file:
            # Append the new URL to the file, followed by a newline
            file.write(url + "\n")
        

    if(xss =="on"):
        dalfox.run_dalfox_on_url(urls_path)
    if(commandinj =="on"):
        commandinjection.commandinjection(urls_path)
    if(sqli =="on"):
        sqlinjection.sql_injection_test(urls_path,headers,level="1",risk="1")
    scan_finished=True


#recon function is a bash script that automates subdomain enum & passive and active crawling     
def recon(url,subdomain_enum):
    try:
        if subdomain_enum == "on":
            sub="-sub"
        else:
            sub=""

        # Run the bash script
        result = subprocess.run(
            ["/tools/automate.sh"] + url +sub,  # Path to the bash script
            capture_output=True,  # Capture stdout and stderr
            text=True,            # Return output as a string
            check=True            # Raise an error if the script fails
        )
            
    except subprocess.CalledProcessError as e:
        # Handle errors (e.g., script returns a non-zero exit code)
        return {
            "error": str(e),
            "stdout": e.stdout,
            "stderr": e.stderr,
            "returncode": e.returncode
        }    


# Run the app with debug mode
if __name__ == '__main__':
    flask_app.run(host='127.0.0.1', port=5000, debug=True)  # Enable debug mode here
