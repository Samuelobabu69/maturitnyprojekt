import socket
from datetime import datetime

DEBUGGING = True

def resp_content_type(filename):
    """Generates the Content-Type header for an HTML response."""

    _, ext = filename.rsplit('.', 1)
    ext += ";"

    # Content-Type: text/html; charset=UTF-8
    #               ↑↑↑↑
    content_type_prefixes = [
        ("css;html;js;", "text"),
        ("inco;pg;jpg;jpeg;webp;svg;gif;", "image")
    ]

    # Content-Type: text/html; charset=UTF-8  (include only if it's different than the file extension)
    #                    ↑↑↑↑
    content_type_suffixes = [
        ("ico;", "x-icon"),
        ("jpg;", "jpeg")
    ]
    
    # Content-Type: text/html; charset=UTF-8  (include only when needed)
    #                        ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
    content_type_encodings = [  
        ("css;html;js;", "; charset=UTF-8")
    ]

    content_type_prefix, content_type_suffix, content_type_encoding = "", ext[:-1], ""
    
    for prefix in content_type_prefixes:
        if ext in prefix[0]: content_type_prefix = prefix[1]

    for suffix in content_type_suffixes:
        if ext in suffix[0]: content_type_suffix = suffix[1]

    for encoding in content_type_encodings:
        if ext in encoding[0]: content_type_encoding = encoding[1]

    content_type = content_type_prefix + "/" + content_type_suffix + content_type_encoding

    return content_type

def resp_date():
    """Generates the Date header for an HTML response."""

    date = datetime.now().strftime('%a, %d %b %Y %H:%M:%S GMT')

    return date

def resp_construct(content_type, body, status=200):
    """Generates the HTML response."""

    if status == 200:
        headers = [
            b"HTTP/1.1 200 OK",
            b"Content-Type: " + content_type.encode(),
            b"Content-Length: " + str(len(body)).encode(),
            b"Date: " + resp_date().encode(),
            b"Connection: keep-alive",
            b"",
            body
            ]
        
    elif status == 204:
        headers = [
            b"HTTP/1.1 204 No Content",
            b"Date: " + resp_date().encode(),
            b"Connection: close"
            ]
        
    elif status == 401:
        headers = [
            b"HTTP/1.1 401 Unauthorized",
            b"Content-Type: " + content_type.encode(),
            b"Content-Length: " + str(len(body)).encode(),
            b"Date: " + resp_date().encode(),
            b"Connection: close",
            b"",
            body
            ]
    
    elif status == 404:
        headers = [
            b"HTTP/1.1 404 Not Found",
            b"Date: " + resp_date().encode(),
            b"Connection: close"
            ]
        
    elif status == 409:
        headers = [
            b"HTTP/1.1 409 Conflict",
            b"Content-Type: " + content_type.encode(),
            b"Content-Length: " + str(len(body)).encode(),
            b"Date: " + resp_date().encode(),
            b"Connection: close",
            b"",
            body
            ]
    
    response = headers[0]
    for i in range(len(headers)-1):
        response += b"\r\n" + headers[i+1]

    return response

def read_file(path):
    """Reads a file... Yep."""
    with open(path, "rb") as f:

        return f.read()

def handle_request(conn, addr):
    """Handles the HTML request according to its method."""

    # If DEBUGGING variable is True, requests and responses will be printed into the terminal.
    if DEBUGGING: print('\n-----------\nGot a connection from', addr)

    request = conn.recv(1024).decode()
    
    if DEBUGGING: print("-----------\nRequest: \n", request)

    request = request.split("\r\n")
    req_method, req_path, _ = request[0].split(" ")

    if req_method == "GET":
        req_path = req_path[1:]
        if req_path == "": req_path = "index.html"
            
        content_type = resp_content_type(req_path)
        try:
            req_body = read_file(req_path)
            response = resp_construct(content_type, req_body)
        except FileNotFoundError:
            response = resp_construct(None, None, 404)

        if DEBUGGING: 
            try:
                printable_response = response.decode()

            except UnicodeDecodeError:
                printable_response = response

            if len(printable_response) > 2000:
                print("-----------\nResponse: \n", printable_response[:2000], "...")
            else:
                print("-----------\nResponse: \n", printable_response)

    if req_method == "POST":
        req_body = request[-1]
        
        data = eval(req_body)

        # If the user tries to access admin settings
        if data["type"] == "adminSettingsAccessAttempt":

            if data["data"] == ADMIN_PASSWORD:
                admin_access.append(addr[0])
                response = resp_construct("text/plain", "adminAccessGranted", 200) 

            else:
                response = resp_construct("text/plain", "adminAccessDenied", 401) 

        # If the address of the request matches with the address of the connected user:
        # (the user is authenticated and able to interact with the device)
        elif occupied_by == addr[0]:
        
            if data["type"] == "powerButton":
                if data["data"] == "press":
                    opto_input.value(1)
                    led.value(1)
                    
                elif data["data"] == "release":
                    opto_input.value(0)
                    led.value(0)
                    
            if data["type"] == "disconnected":
                occupied_by = None

            response = resp_construct(None, None, 204)
        
        # If no one is connected:
        elif not occupied_by:
            
            # If someone tries to connect:
            if data["type"] == "accessAttempt" and ACCESS_MODE == "password":
                if data["data"] == ACCESS_PASSWORD:
                    occupied_by = addr[0]
                    response = resp_construct("text/plain", "accessGranted", 200)
                else:
                    response = resp_construct("text/plain", "accessDenied", 401)
            
            if data["type"] == "accessAttempt" and ACCESS_MODE == "whitelist":
                if addr[0] in ACCESS_WHITELIST:
                    occupied_by = addr[0]
                    response = resp_construct("text/plain", "accessGranted", 200)
                else:
                    response = resp_construct("text/plain", "accessDenied", 401)
                    
        # If none of the above happens
        # (meaning that someone else is using the device)
        else:
            response = resp_construct("text/plain", "occupied", 409)
            
        
    conn.send(response)
    conn.close()

# Set up socket and start listening
s_addr = socket.getaddrinfo('0.0.0.0', 80)[0][-1]
s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(s_addr)
s.listen()

if DEBUGGING: print(f"Listening at {s_addr}")

# Main loop to listen for connections
while True:
    conn, addr = s.accept()
    handle_request(conn, addr)