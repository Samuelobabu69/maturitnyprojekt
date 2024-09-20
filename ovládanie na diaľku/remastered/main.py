from flask import Flask, request
from flask_cors import CORS
import pyautogui as pag, io, base64, http.server, socketserver, threading, socket, os, time
from tkinter import *
from PIL import Image

# html stránka
http_port = 56789   
directory = '.'  # This will serve files from the current directory
handler = http.server.SimpleHTTPRequestHandler
httpd = socketserver.TCPServer(("", http_port), handler)

# povolenie pyautogui pohybovanie sa v rohoch obrazovky
pag.FAILSAFE = False

# flask aplikacia
app = Flask(__name__)

# CORS sprostosť
CORS(app)

start_x, start_y = None, None
occupiedBy = None

# heslo
password = ""

root = Tk()

root.title("Easy Remote")
root.iconbitmap("assets/easy-remote.ico")
root.geometry("340x100")

tk_row1 = 10
tk_row2 = 50
tk_row3 = 90
tk_row4 = 130

def read_file(path):
    """Reads a file... Yep."""
    with open(path, "rb") as f:

        return f.read()
    
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

    current_time = time.gmtime()

    date = "{:s}, {:02d} {:s} {:d} {:02d}:{:02d}:{:02d} GMT".format(
        ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][current_time[6]],
        current_time[2],
        ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][current_time[1] - 1],
        current_time[0],
        current_time[3],
        current_time[4],
        current_time[5]
    )
    
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

def startFlaskServer():
    app.run(host="0.0.0.0", port=5000)

def clearScreen():

    for i in root.winfo_children():
        i.destroy()

def tkScreen1():

    global entry_pass

    clearScreen()

    label_passinput = Label(root, text="Create password:")
    label_passinput.place(x=20, y=tk_row1)

    entry_pass = Entry(root, show="•")
    entry_pass.place(x=150, y=tk_row1+3)

    button_start = Button(root, text="Start", width=7, command=start)
    button_start.place(x=248, y=tk_row2)

    root.mainloop()

def tkScreen2():

    clearScreen()

    label_starting = Label(root, text="Starting server...")
    label_starting.place(x=105, y=tk_row1)

def tkScreen3():

    clearScreen()

    global entry_serverpass, label_stopserverinfo

    root.geometry("340x210")

    label_serverurl = Label(root, text="URL:")
    label_serverurl.place(x=20, y=tk_row1)

    entry_serverurl = Entry(root)
    entry_serverurl.insert(0, f"{socket.gethostbyname(socket.gethostname())}:{http_port}")
    entry_serverurl.config(state="readonly")
    entry_serverurl.place(x=60, y=tk_row1+2)

    label_serverpass = Label(root, text="Password:")
    label_serverpass.place(x=20, y=tk_row2)

    entry_serverpass = Entry(root, show="•")
    entry_serverpass.insert(0, password)
    entry_serverpass.config(state="readonly")
    entry_serverpass.place(x=95, y=tk_row2+2)

    button_showpass = Button(root, text="👁")
    button_showpass.place(x=260, y=tk_row2-2)
    button_showpass.bind("<ButtonPress>", showPassword)
    button_showpass.bind("<ButtonRelease>", hidePassword)

    label_stopserverinfo = Label(root, text="To connect to this computer, type the URL \nabove into a web browser on a phone. \nClose this app to stop. If the app takes too \nlong to close, try refreshing the client's web \nbrowser.", justify=LEFT)
    label_stopserverinfo.place(x=20, y=tk_row3)

    root.protocol("WM_DELETE_WINDOW", onClose)

def showPassword(event):

    entry_serverpass.config(show="")

def hidePassword(event):

    entry_serverpass.config(show="•")

def startSite():

    # logika pre POST requesty

    @app.route("/", methods=["POST"])
    def post():
        global start_x, start_y, occupiedBy

        data = request.get_json()

        if occupiedBy == request.remote_addr:
            if data["type"] == "browser refresh":
                if request.remote_addr == occupiedBy:
                    occupiedBy = None
                    return "refresh true"
                
                else:
                    return "refresh false"
                
            if data["type"] == "mousepadTouch":
                start_x, start_y = pag.position()
                return "empty"
            
            if data["type"] == "mousepadMove":
                if start_x and start_y:
                    offset_x, offset_y = data["data"].split("/")
                    new_x = start_x + float(offset_x)
                    new_y = start_y + float(offset_y)
                    pag.moveTo(new_x, new_y)
                return "empty"
            
            if data["type"] == "mousepadRelease":
                end_x, end_y = pag.position()
                if end_x == start_x and end_y == start_y:
                    pag.click()
                return "empty" 
        
            if data["type"] == "hotkeyPress":
                if data["data"] == "Backspace":
                    pag.press("backspace")
                elif data["data"] == "Enter":
                    pag.press("enter")
                elif data["data"] == "Esc":
                    pag.press("esc")
                elif data["data"] == "Caps Lock":
                    pag.press("capslock")
                return "empty"
            
            if data["type"] == "textWrite":
                pag.write(data["data"])
                return "empty"
            
            if data["type"] == "showScreen":
                screenshot = pag.screenshot()

                cursor_x, cursor_y = pag.position()
                cursor_image = Image.open("assets/cursor_mod.png")
                screenshot.paste(cursor_image, (cursor_x, cursor_y), cursor_image)
                
                screenshot_bytes = io.BytesIO()
                screenshot.thumbnail((800, 800))
                screenshot.save(screenshot_bytes, format="PNG")
                screenshot_base64 = base64.b64encode(screenshot_bytes.getvalue()).decode('utf-8')
                return screenshot_base64

            if data["type"] == "inactive dc" or data["type"] == "dc":
                occupiedBy = None
                return "empty"
            
        elif not occupiedBy:

            if data["type"] == "connect":
                if data["data"] == password:
                    occupiedBy = request.remote_addr
                    return "connect success"
                
                else:
                    return "connect failed"
                
            else:
                return "unverified"
            
        else:
            return "occupied"

    # zakázanie GET requestov            
    @app.route("/", methods=["GET"])
    def get():
        return "'GET' requests not allowed"
    
    global http_thread, flask_thread

    # hostovanie stránky
    http_thread = threading.Thread(target=httpd.serve_forever)
    http_thread.start()

    # hostovanie flasku
    flask_thread = threading.Thread(target=startFlaskServer)
    flask_thread.start()
    
    tkScreen3()

def handle_request(conn, addr):
    """Handles the HTML request according to its method."""
    
    # If DEBUGGING variable is True, requests and responses will be printed into the terminal.
    
    if DEBUGGING: print("handling request...")
    
    if DEBUGGING: print('\n-----------\nGot a connection from', addr)

    request = conn.recv(1024).decode()
    
    if DEBUGGING: print("-----------\nRequest: \n", request)

    request = request.split("\r\n")
    req_method, req_path, _ = request[0].split(" ")

    if req_method == "GET":

        # TODO: Screen share

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

        if occupiedBy == addr[0]:
            if data["type"] == "browserRefresh":
                occupiedBy = None
                return resp_construct(None, None, 204)

        if data["type"] == "mousepadTouch":
                start_x, start_y = pag.position()
                return resp_construct(None, None, 204)
            
        if data["type"] == "mousepadMove":
            if start_x and start_y:
                offset_x, offset_y = data["data"].split("/")
                new_x = start_x + float(offset_x)
                new_y = start_y + float(offset_y)
                pag.moveTo(new_x, new_y)
            return resp_construct(None, None, 204)
        
        if data["type"] == "mousepadRelease":
            end_x, end_y = pag.position()
            if end_x == start_x and end_y == start_y:
                pag.click()
            return resp_construct(None, None, 204)
    
        if data["type"] == "hotkeyPress":
            if data["data"] == "Backspace":
                pag.press("backspace")
            elif data["data"] == "Enter":
                pag.press("enter")
            elif data["data"] == "Esc":
                pag.press("esc")
            elif data["data"] == "Caps Lock":
                pag.press("capslock")
            return resp_construct(None, None, 204)
        
        if data["type"] == "textWrite":
            pag.write(data["data"])
            return resp_construct(None, None, 204)
        
        if data["type"] == "disconnectForInactivity" or data["type"] == "disconnect":
            occupiedBy = None
            return "empty"

    elif not occupiedBy:

        if data["type"] == "connect":
            if data["data"] == password:
                occupiedBy = request.remote_addr
                return resp_construct(None, None, 200)
            
            else:
                return "connect failed"
            
        else:
            return resp_construct(None, None, 401)
        
    else:
        return resp_construct(None, None, 409)
        
    conn.send(response)
    conn.close()

def onClose():
    
    httpd.shutdown()
    root.destroy()
    os._exit(0)

def start():

    global password, startSite_thread

    password = entry_pass.get().strip()

    startSite_thread = threading.Thread(target=startSite)
    startSite_thread.start()

    tkScreen2()

if __name__ == "__main__":
    tkScreen1()