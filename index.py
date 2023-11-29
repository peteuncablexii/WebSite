import http.server
import socketserver
import os
import cgi

PORT = 8000
UPLOAD_FOLDER = "WaitingSubmission"

logged_ips = set()  # Set to store logged IPs

class CustomHandler(http.server.SimpleHTTPRequestHandler):
    def log_ip(self):
        ip = self.client_address[0]
        if ip not in logged_ips:
            logged_ips.add(ip)
            with open("ip_log.txt", "a") as log_file:
                log_file.write(f"IP Address: {ip}\n")
    
    def do_POST(self):
        form = cgi.FieldStorage(
            fp=self.rfile,
            headers=self.headers,
            environ={'REQUEST_METHOD': 'POST'}
        )
        
        self.log_ip()  # Log client's IP
        
        filename_input = form.getvalue('filenameInput')
        file_item = form['fileInput']
        
        if file_item.file and filename_input:
            # Get the original filename
            original_filename = file_item.filename
            
            # Extract the file extension
            file_extension = os.path.splitext(original_filename)[-1]
            
            # Create a new filename combining user-provided filename and original extension
            new_filename = f"{filename_input}{file_extension}"
            
            file_content = file_item.file.read()
            file_path = os.path.join(UPLOAD_FOLDER, new_filename)
            
            with open(file_path, 'wb') as new_file:
                new_file.write(file_content)
            
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b'File uploaded successfully!')
        else:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Error: File upload failed!')

Handler = CustomHandler

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"Serving HTTP server at port {PORT}")
    httpd.serve_forever()
