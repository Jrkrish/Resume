import os
import http.server
import socketserver
import webbrowser

# Read the content of test_resume.html
try:
    with open('test_resume.html', 'r') as f:
        resume_content = f.read()
        template_used = "Current template"
except FileNotFoundError:
    resume_content = "<p>No resume found. Run test_resume_generation.py first.</p>"
    template_used = "None"

# Create a simple HTML page with the resume content embedded
html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Resume Preview</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background-color: white;
            padding: 30px;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }}
        h1 {{
            text-align: center;
            margin-bottom: 30px;
        }}
        .resume-container {{
            margin-top: 20px;
            border: 1px solid #eee;
            padding: 20px;
        }}
        .controls {{
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            justify-content: center;
        }}
        button {{
            background-color: #4f46e5;
            color: white;
            border: none;
            padding: 10px 15px;
            border-radius: 5px;
            cursor: pointer;
        }}
        button:hover {{
            background-color: #4338ca;
        }}
        .template-info {{
            text-align: center;
            margin-bottom: 20px;
            padding: 10px;
            background-color: #f0f9ff;
            border-radius: 5px;
            border: 1px solid #e0f2fe;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Resume Preview</h1>
        
        <div class="template-info">
            <strong>Template Used:</strong> {template_used}
        </div>
        
        <div class="controls">
            <button onclick="window.location.href='http://localhost:8000/generate'">Generate New Resume</button>
            <button onclick="window.location.href='http://127.0.0.1:5000'">Go to Main App</button>
        </div>
        
        <div class="resume-container">
            {resume_content}
        </div>
    </div>
</body>
</html>
"""

# Write the combined HTML to a file
with open('combined_resume.html', 'w') as f:
    f.write(html)

print("Created combined_resume.html with the resume embedded")
print("Opening the file in your default browser...")

# Open the file in the default browser
webbrowser.open('combined_resume.html')

# Define request handler
class ResumeSiteHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/generate':
            # Run the resume generation script
            print("Generating a new resume...")
            try:
                os.system('python test_resume_generation.py')
                # Redirect to the combined_resume.html
                self.send_response(302)
                self.send_header('Location', '/')
                self.end_headers()
            except Exception as e:
                self.send_response(500)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.wfile.write(f"<html><body><h1>Error</h1><p>{str(e)}</p></body></html>".encode())
        elif self.path == '/' or self.path == '/index.html':
            # Read the current test_resume.html
            try:
                with open('test_resume.html', 'r') as f:
                    current_resume = f.read()
            except FileNotFoundError:
                current_resume = "<p>No resume found. Run test_resume_generation.py first.</p>"
            
            # Create a fresh HTML page with the current resume
            current_html = html.replace(resume_content, current_resume)
            
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(current_html.encode())
        else:
            # Handle other files normally
            return http.server.SimpleHTTPRequestHandler.do_GET(self)

# Start server
PORT = 8000
print(f"\nStarting a server at: http://localhost:{PORT}")
print("You can generate new resumes by clicking the 'Generate New Resume' button")
print("Press Ctrl+C to stop the server")

with socketserver.TCPServer(("", PORT), ResumeSiteHandler) as httpd:
    print(f"Serving at http://localhost:{PORT}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.") 