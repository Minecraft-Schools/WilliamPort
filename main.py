# RULES FOR URL DATA SENDING
# 1. Some characters are not allowed in the URL, for example: /, ?, &, =, etc.
#    To solve this, a class called ValedUrl was created.
#    To use this class, you have to pass the url as a string to the constructor.
#    It will automatically decode the url from the set rules explained later, and return the url as a string.
#    If the url is invalid, it will return None.
# 2. Continuing with url encoding/decoding, here are the different characters and their encoded versions:
#    - / -> %2F
#    - ? -> %3F
#    - & -> %26
#    - = -> %3D
#    - + -> %2B
#

import socket
import json
import threading
import base64
import os
import datetime
from datetime import timezone
import hmac, hashlib
import credentialogger
import random

class ValuedUrl:
    def __init__(self, url: str):
        self.url = url or ""
    
    def encode(self):
        return self.url.replace('/', '%2F').replace('?', '%3F').replace('&', '%26').replace('=', '%3D').replace('+', '%2B')
    def decode(self):
        return self.url.replace('%2F', '/').replace('%3F', '?').replace('%26', '&').replace('%3D', '=').replace('%2B', '+')

def makeMessage(error: bool, message: str):
    return json.dumps({
        "error": error,
        "message": message
    })

MAIN_DIR = '/Users/williamgroh/Desktop/.newfolder/http-server/dict/main/WilliamPort/'
CREDENIALS_FILE = MAIN_DIR + 'signin/credentials.json'
SESSION_FILE = MAIN_DIR + 'signin/sessions.json'

# Function to create session ids
def create_session_id(userid: int, timestamp: str):
    # return base64.urlsafe_b64encode(os.urandom(16)).decode('utf-8')
    
    if isinstance(userid, int):
        userid = userid
    else:
        userid = int(userid)
    
    part1 = userid.to_bytes((userid.bit_length() + 7) // 8 or 1, 'big')
    part1 = base64.b64encode(part1).decode('utf-8')
    epoch = 1293840000
    part2 = int(datetime.datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S').replace(tzinfo=datetime.timezone.utc).timestamp()) - epoch
    part2 = base64.b64encode(part2.to_bytes((part2.bit_length() + 7) // 8 or 1, 'big')).decode('utf-8')
    key = f'{userid/2}r{timestamp[0:1]}'.encode('utf-8')
    message = f'Validated'.encode('utf-8')
    part3 = hmac.new(key, message, hashlib.sha256).hexdigest()
    session_id = f'{part1}.{part2}.{part3}'
    return session_id
    

# Load credentials from JSON file
def load_credentials():
    with open(CREDENIALS_FILE) as f:
        return json.load(f)

def save_credentials(credentials):
    with open(CREDENIALS_FILE, 'w') as f:
        json.dump(credentials, f, indent=4)

# Function to load sessions from the JSON file
def load_sessions():
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, 'r') as f:
            return json.load(f)
    return {}  # Return an empty dictionary if the file does not exist

# Function to save sessions to the JSON file
def save_sessions(sessions):
    with open(SESSION_FILE, 'w') as f:
        json.dump(sessions, f, indent=4)

SERVER_HOST = '0.0.0.0'
SERVER_PORT = 8080

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server_socket.bind((SERVER_HOST, SERVER_PORT))

server_socket.listen(5)

print(f'Listening on port {SERVER_PORT} ...')

# IMPORTANT: To interact with the api, for example logging in, you have to use POST requests with the path starting with /api/

while True: 
    print('ran')
    try:
        client_socket, client_address = server_socket.accept()
        print('ran2')
    except KeyboardInterrupt:
        print('KeyboardInterrupt')
        server_socket.close()
        break
    else:
        request = client_socket.recv(1500).decode()
        print("Start of request:")
        print(request)
        print("End of request")

        headers = request.split('\n')
        first_header_components = headers[0].split() or ""

        http_method = first_header_components[0] or ""
        url = first_header_components[1] or ""
        if '?' in url:
            path, query_string = url.split('?', 1)
        else:
            query_string = ''
            path = url
        
        def get_cookie_value(cookie_name):
            """Retrieve the value of a specific cookie from the headers."""
            for header in headers:
                if header.startswith('Cookie:'):
                    cookie_string = header.split(':', 1)[1].strip()
                    for cookie in cookie_string.split(';'):
                        key, value = cookie.split('=', 1)
                        if key.strip() == cookie_name:
                            return value.strip()
            return None  # Return None if the cookie is not found
        
        # Function to get the value of a query parameter
        def get_query_param(param_name):
            try:
                query_params = query_string.split('&')
                for param in query_params:
                    key, value = param.split('=')
                    value = ValuedUrl(value).decode()
                    if key == param_name:
                        return value
                return None
            except Exception as e:
                print(f"Error: {e}")
                return None

        image_content = "None"
        
        def encode_message():
            message = get_query_param('message')
            JSON_FILE = MAIN_DIR + 'special-encoder/encoded.json'
            def load():
                with open(JSON_FILE, 'r') as f:
                    c = json.load(f)
                    f.close()
                return c

            def save(file):
                with open(JSON_FILE, 'w') as f:
                    json.dump(file, f, indent=4)
            
            contents = load()
            
            if message in contents:
                return contents[message]['value']
            else:
                new_value = f"{random.randint(0,99999999):08d}"
                contents[message] = {
                    'value': new_value
                }
                save(contents)
                return new_value
            
        
        def roblox_internet():
            requested_path = get_query_param('path')
            if requested_path == 'home':
                return open(MAIN_DIR + 'roblox-internet/index.txt')
        
        if http_method == 'GET':
            if path == '/':
                fin = open(MAIN_DIR + 'index.html')
                content = fin.read()
                fin.close()
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: text/html\r\n'
                response += 'Content-Length: ' + str(len(content)) + '\r\n'
                response += '\r\n'
                response += content
            elif path == '/digclock':
                fin = open(MAIN_DIR + 'clock/new.html')
                content = fin.read()
                fin.close()
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: text/html\r\n'
                response += 'Content-Length: ' + str(len(content)) + '\r\n'
                response += '\r\n'
                response += content
            elif path == '/encoder':
                fin = open(MAIN_DIR + 'special-encoder/index.html')
                content = fin.read()
                fin.close()
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: text/html\r\n'
                response += 'Content-Length: ' + str(len(content)) + '\r\n'
                response += '\r\n'
                response += content
            elif path == '/encoder/response':
                content = encode_message()
                response = 'HTTP/1.1 200 OK \r\n'
                response += 'Content-Type: text/plain'
                response += 'Content-Length: ' + str(len(content)) + '\r\n'
                response += '\r\n'
                response += content
            elif path == '/roblox-internet':
                fin = roblox_internet()
                content = fin.read()
                fin.close()
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: text/plain\r\n'
                response += 'Content-Length: ' + str(len(content)) + '\r\n'
                response += '\r\n'
                response += content
            elif path == '/games/emulators':
                fin = open(MAIN_DIR + 'emulators.html')
                content = fin.read()
                fin.close()
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: text/html\r\n'
                response += 'Content-Length: ' + str(len(content)) + '\r\n'
                response += '\r\n'
                response += content
            elif path == '/games/emulators/android':
                fin = open(MAIN_DIR + 'emulators/Android/index.html')
                content = fin.read()
                fin.close()
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: text/html\r\n'
                response += 'Content-Length: ' + str(len(content)) + '\r\n'
                response += '\r\n'
                response += content
            elif path == '/assets/games/emulators/android/bios':
                fin = open(MAIN_DIR + 'emulators/Android/android.iso', 'rb')
                content = fin.read()
                fin.close()
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: text/html\r\n'
                response += 'Content-Length: ' + str(len(content)) + '\r\n'
                response += '\r\n'
                response += content
            elif path == '/games/emulators/gba':
                fin = open(MAIN_DIR + 'emulators/GBA/index.html')
                content = fin.read()
                fin.close()
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: text/html\r\n'
                response += 'Content-Length: ' + str(len(content)) + '\r\n'
                response += '\r\n'
                response += content
            elif path == '/assets/games/emulators/gba/pokemon-emerald.gba':
                fin = open(MAIN_DIR + 'emulators/GBA/Pokemon - Emerald Version (USA, Europe).gba', 'rb')
                content = fin.read()
                fin.close()
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: application/zip\r\n'
                response += 'Content-Length: ' + str(len(content)) + '\r\n'
                response += '\r\n'
                image_content = content
            elif path == '/games/emulators/gba/supermario4':
                fin = open(MAIN_DIR + 'emulators/GBA/super-mario-4.html')
                content = fin.read()
                fin.close()
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: text/html\r\n'
                response += 'Content-Length: ' + str(len(content)) + '\r\n'
                response += '\r\n'
                response += content
            elif path == '/games/emulators/gba/zelda':
                fin = open(MAIN_DIR + 'emulators/GBA/legend-of-zelda.html')
                content = fin.read()
                fin.close()
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: text/html\r\n'
                response += 'Content-Length: ' + str(len(content)) + '\r\n'
                response += '\r\n'
                response += content
            elif path == '/assets/games/emulators/gba/bios':
                fin = open(MAIN_DIR + 'emulators/GBA/gba_bios.bin', 'rb')
                content = fin.read()
                fin.close()
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: application/zip\r\n'
                response += 'Content-Length: ' + str(len(content)) + '\r\n'
                response += '\r\n'
                image_content = content
            elif path == '/assets/games/emulators/gba/supermario4.gba':
                fin = open(MAIN_DIR + 'emulators/GBA/Super Mario Advance 4 - Super Mario Bros. 3 (U) (V1.1).gba', 'rb')
                content = fin.read()
                fin.close()
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: application/zip\r\n'
                response += 'Content-Length: ' + str(len(content)) + '\r\n'
                response += '\r\n'
                image_content = content
            elif path == '/assets/games/emulators/gba/zelda.gba':
                fin = open(MAIN_DIR + 'emulators/GBA/Legend of Zelda, The - The Minish Cap (U).gba', 'rb')
                content = fin.read()
                fin.close()
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: application/zip\r\n'
                response += 'Content-Length: ' + str(len(content)) + '\r\n'
                response += '\r\n'
                image_content = content
            elif path == '/games/emulators/psx':
                fin = open(MAIN_DIR + 'emulators/PSX/index.html')
                content = fin.read()
                fin.close()
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: text/html\r\n'
                response += 'Content-Length: ' + str(len(content)) + '\r\n'
                response += '\r\n'
                response += content
            elif path == '/games/emulators/ps2':
                fin = open(MAIN_DIR + 'emulators/PS2/index.html')
                content = fin.read()
                fin.close()
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: text/html\r\n'
                response += 'Content-Length: ' + str(len(content)) + '\r\n'
                response += '\r\n'
                response += content
            elif path == '/games/emulators/gba/pokemon-emerald':
                fin = open(MAIN_DIR + 'emulators/GBA/pokemon-emerald.html')
                content = fin.read()
                fin.close()
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: text/html\r\n'
                response += 'Content-Length: ' + str(len(content)) + '\r\n'
                response += '\r\n'
                response += content
            elif path == '/games/emulators/psx/crashbandicoot':
                fin = open(MAIN_DIR + 'emulators/PSX/crash-bandicoot.html')
                content = fin.read()
                fin.close()
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: text/html\r\n'
                response += 'Content-Length: ' + str(len(content)) + '\r\n'
                response += '\r\n'
                response += content
            elif path == '/assets/games/emulators/psx/crashbandicoot.iso':
                fin = open(MAIN_DIR + 'emulators/PSX/Crash Bandicoot (USA).iso', 'rb')
                content = fin.read()
                fin.close()
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: application/zip\r\n'
                response += 'Content-Length: ' + str(len(content)) + '\r\n'
                response += '\r\n'
                image_content = content
            elif path == '/assets/games/emulators/psx/bios':
                fin = open(MAIN_DIR + 'emulators/PSX/scph1001.bin', 'rb')
                content = fin.read()
                fin.close()
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: application/zip\r\n'
                response += 'Content-Length: ' + str(len(content)) + '\r\n'
                response += '\r\n'
                image_content = content
            elif path == '/favicon.ico':
                with open(MAIN_DIR + 'images/favicon.ico', 'rb') as fin:
                    content = fin.read()
                fin.close()
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: image/x-icon\r\n'
                response += 'Content-Length: ' + str(len(content)) + '\r\n'
                response += '\r\n'
                image_content = content
            elif path == '/site.webmanifest':
                fin = open(MAIN_DIR + 'images/site.webmanifest')
                content = fin.read()
                fin.close()
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: application/manifest+json\r\n'
                response += 'Content-Length: ' + str(len(content)) + '\r\n'
                response += '\r\n'
                response += content
            elif path == '/favicon-16x16.png':
                fin = open(MAIN_DIR + 'images/favicon-16x16.png')
                content = fin.read()
                fin.close()
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: image/png\r\n'
                response += 'Content-Length: ' + str(len(content)) + '\r\n'
                response += '\r\n'
                image_content = content
            elif path == '/favicon-32x32.png':
                fin = open(MAIN_DIR + 'images/favicon-32x32.png')
                content = fin.read()
                fin.close()
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: image/png\r\n'
                response += 'Content-Length: ' + str(len(content)) + '\r\n'
                response += '\r\n'
                image_content = content
            elif path == '/apple-touch-icon.png':
                fin = open(MAIN_DIR + 'images/apple-touch-icon.png')
                content = fin.read()
                fin.close()
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: image/png\r\n'
                response += 'Content-Length: ' + str(len(content)) + '\r\n'
                response += '\r\n'
                image_content = content
            elif path == '/android-chrome-192x192.png':
                fin = open(MAIN_DIR + 'images/android-chrome-192x192.png')
                content = fin.read()
                fin.close()
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: image/png\r\n'
                response += 'Content-Length: ' + str(len(content)) + '\r\n'
                response += '\r\n'
                image_content = content
            elif path == '/android-chrome-512x512.png':
                fin = open(MAIN_DIR + 'images/android-chrome-512x512.png')
                content = fin.read()
                fin.close()
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: image/png\r\n'
                response += 'Content-Length: ' + str(len(content)) + '\r\n'
                response += '\r\n'
                image_content = content
            elif path == '/favicon.ico':
                fin = open(MAIN_DIR + 'images/favicon.ico')
                content = fin.read()
                fin.close()
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: image/x-icon\r\n'
                response += 'Content-Length: ' + str(len(content)) + '\r\n'
                response += '\r\n'
                image_content = content
            elif path == '/404':
                fin = open(MAIN_DIR + '404.html')
                content = fin.read()
                fin.close()
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: text/html\r\n'
                response += 'Content-Length: ' + str(len(content)) + '\r\n'
                response += '\r\n'
                response += content
            elif path == '/signup':
                fin = open(MAIN_DIR + 'signin/signup.html')
                content = fin.read()
                fin.close()
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: text/html\r\n'
                response += 'Content-Length: ' + str(len(content)) + '\r\n'
                response += '\r\n'
                response += content
            elif path == '/signin':
                fin = open(MAIN_DIR + 'signin/signin.html')
                content = fin.read()
                fin.close()
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: text/html\r\n'
                response += 'Content-Length: ' + str(len(content)) + '\r\n'
                response += '\r\n'
                response += content
            elif path == '/api/get-session-id':
                userid = get_query_param('userid')
                password = get_query_param('password')
                turbowarp = get_query_param('turbowarp') or False
                sessions = load_sessions()
                credentials = load_credentials()
                if userid in credentials and credentials[userid]['password'] == password:
                    if turbowarp == "true":
                        session_id = sessions[userid]
                        response = 'HTTP/1.1 200 OK\r\n'
                        response += 'Content-Type: text/plain; charset=utf-8\r\n'
                        response += 'Content-Length: ' + str(len(session_id)) + '\r\n'
                        response += 'Last-Modified: ' + str(datetime.datetime.now()) + '\r\n'
                        response += 'Access-Control-Allow-Origin: *\r\n'
                        response += 'Cache-Control: max-age=600\r\n'
                        response += 'x-proxy-cache: MISS\r\n'
                        response += 'Accept-Ranges: bytes\r\n'
                        response += 'Vary: Accept-Encoding\r\n'
                        response += 'Connection: keep-alive\r\n'
                        response += 'Server: Python\r\n'
                        response += '\r\n'
                        response += session_id
                    else:
                        session_id = sessions[userid]
                        response = 'HTTP/1.1 200 OK\r\n'
                        response += 'Content-Type: text/plain\r\n'
                        response += 'Content-Length: ' + str(len(session_id)) + '\r\n'
                        response += '\r\n'
                        response += session_id
                else:
                    response = 'HTTP/1.1 401 Unauthorized\r\n'
                    response += 'Content-Type: text/plain\r\n'
                    response += 'Content-Length: 16\r\n'
                    response += '\r\n'
                    response += 'Invalid Credentials'
            elif path == '/api/get-user-credentials':
                session_id = ValuedUrl(get_cookie_value('session_id')).decode()
                sessions = load_sessions()
                item_requested = get_query_param('item')
                
                for session in sessions:
                    if sessions[session] == session_id:
                        userid = session
                        credentials = load_credentials()
                        
                        if item_requested == 'userid':
                            content = userid
                        elif item_requested == 'password':
                            content = credentials[userid]['password']
                        elif item_requested == 'email':
                            content = credentials[userid]['email']
                        elif item_requested == 'all':
                            content = credentials[userid]
                        
                        response = 'HTTP/1.1 200 OK\r\n'
                        response += 'Content-Type: text/plain\r\n'
                        response += 'Content-Length: ' + str(len(userid)) + '\r\n'
                        response += '\r\n'
                        response += content
                        break
                else:
                    response = 'HTTP/1.1 401 Unauthorized\r\n'
                    response += 'Content-Type: text/plain\r\n'
                    response += 'Content-Length: 13\r\n'
                    response += '\r\n'
                    response += 'Invalid session'
            elif path == '/api/get-userid-from-username':
                username = get_query_param('username')
                credentials = load_credentials()
                turbowarp = get_query_param('turbowarp') or False
                found = False

                for userid in credentials:
                    if credentials[userid]['username'] == username:
                        if turbowarp == "true":
                            response = 'HTTP/1.1 200 OK\r\n'
                            response += 'Content-Type: text/plain; charset=utf-8\r\n'
                            response += 'Content-Length: ' + str(len(userid)) + '\r\n'
                            response += 'Last-Modified: ' + str(datetime.datetime.now()) + '\r\n'
                            response += 'Access-Control-Allow-Origin: *\r\n'
                            response += 'Cache-Control: max-age=600\r\n'
                            response += 'x-proxy-cache: MISS\r\n'
                            response += 'Accept-Ranges: bytes\r\n'
                            response += 'Vary: Accept-Encoding\r\n'
                            response += 'Connection: keep-alive\r\n'
                            response += 'Server: Python\r\n'
                            response += '\r\n'
                            response += str(userid)
                            found = True
                            break
                        else:
                            content = {'userid': str(userid)}
                            response = 'HTTP/1.1 200 OK\r\n'
                            response += 'Content-Type: application/json\r\n'
                            response += 'Content-Length: ' + str(len(str(content))) + '\r\n'
                            response += '\r\n'
                            response += json.dumps(content)
                            found = True
                            break
            
                if not found:
                    content = makeMessage(True, 'User not found')
                    response = 'HTTP/1.1 404 Not Found\r\n'
                    response += 'Content-Type: application/json\r\n'
                    response += 'Content-Length: ' + str(len(str(content))) + '\r\n'
                    response += '\r\n'
                    response += content
            elif path == '/user/dashboard':
                session_id = ValuedUrl(get_cookie_value('session_id')).decode()
                sessions = load_sessions()
                credentials = load_credentials()
                failed = True
                for session in sessions:
                    if sessions[session] == session_id:
                        role = credentials[session]['account-type']
                        if role == 'owner':
                            fin = open('person/owner/dashboard.html', 'r')
                            content = fin.read()
                            fin.close()
                            response = 'HTTP/1.1 200 OK\r\n'
                            response += 'Content-Type: text/html\r\n'
                            response += 'Content-Length: ' + str(len(content)) + '\r\n'
                            response += '\r\n'
                            response += content
                            failed = False
                            break
                        elif role == 'admin':
                            fin = open('person/admin/dashboard.html', 'r')
                            content = fin.read()
                            fin.close()
                            response = 'HTTP/1.1 200 OK\r\n'
                            response += 'Content-Type: text/html\r\n'
                            response += 'Content-Length: ' + str(len(content)) + '\r\n'
                            response += '\r\n'
                            response += content
                            failed = False
                            break
                        elif role == 'user':
                            fin = open('person/user/dashboard.html', 'r')
                            content = fin.read()
                            fin.close()
                            response = 'HTTP/1.1 200 OK\r\n'
                            response += 'Content-Type: text/html\r\n'
                            response += 'Content-Length: ' + str(len(content)) + '\r\n'
                            response += '\r\n'
                            response += content
                            failed = False
                            break
                if failed:
                    # Redirect to login page
                    response = 'HTTP/1.1 302 Found\r\n'
                    response += 'Location: /signin\r\n'
                    response += 'Content-Length: 0\r\n'
                    response += '\r\n'
                    response += ''
                    
            else:
                fin = open(MAIN_DIR + '404.html')
                content = fin.read()
                fin.close()
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: text/html\r\n'
                response += 'Content-Length: ' + str(len(content)) + '\r\n'
                response += '\r\n'
                response += content
            
        elif http_method == 'POST':
            if path == '/api/signin':
                credentials = load_credentials()
                userid = get_query_param('userid')
                password = get_query_param('password')
                
                if userid in credentials and credentials[userid]['password'] == password:
                    sessions = load_sessions()
                    session_id = create_session_id(userid, datetime.datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))
                    
                    # Store the session ID
                    sessions[userid] = session_id
                    save_sessions(sessions)

                    # Prepare the response
                    content = makeMessage(False, 'Login successful')
                    response = 'HTTP/1.1 200 OK\r\n'
                    response += 'Content-Type: application/json\r\n'
                    response += f'Set-Cookie: session_id={ValuedUrl(session_id).encode()}; HttpOnly; SameSite=Strict; Path=/; Max-Age=3600\r\n'
                    response += 'Content-Length: ' + str(len(str(content))) + '\r\n'
                    response += '\r\n'  # End of headers
                    response += content  # Body of the response
                    print(f'Session ID: {session_id}')
                else:
                    content = makeMessage(True, 'Login Failed')
                    response = 'HTTP/1.1 401 Unauthorized\r\n'
                    response += 'Content-Type: application/json\r\n'
                    response += 'Content-Length: ' + str(len(str(content))) + '\r\n'
                    response += '\r\n'  # End of headers
                    response += content  # Body of the response
            elif path == '/api/signup':
                credentials = load_credentials()
                username = get_query_param('username')
                password = get_query_param('password')
                mail_address = get_query_param('email')
                admin = get_query_param('lrt35')
                if username in credentials:
                    content = makeMessage(True, 'Username already exists')
                    response = 'HTTP/1.1 409 Conflict\r\n'
                    response += 'Content-Type: application/json\r\n'
                    response += 'Content-Length: ' + str(len(str(content))) + '\r\n'
                    response += '\r\n'  # End of headers
                    response += content  # Body of the response
                elif mail_address == None:
                    content = makeMessage(True, 'Invalid mail address')
                    response = 'HTTP/1.1 400 Bad Request\r\n'
                    response += 'Content-Type: application/json\r\n'
                    response += 'Content-Length: ' + str(len(str(content))) + '\r\n'
                    response += '\r\n'  # End of headers
                    response += content  # Body of the response
                elif username == None:
                    content = makeMessage(True, 'Invalid username')
                    response = 'HTTP/1.1 400 Bad Request\r\n'
                    response += 'Content-Type: application/json\r\n'
                    response += 'Content-Length: ' + str(len(str(content))) + '\r\n'
                    response += '\r\n'  # End of headers
                    response += content  # Body of the response
                elif password == None:
                    content = makeMessage(True, 'Invalid password')
                    response = 'HTTP/1.1 400 Bad Request\r\n'
                    response += 'Content-Type: application/json\r\n'
                    response += 'Content-Length: ' + str(len(str(content))) + '\r\n'
                    response += '\r\n'  # End of headers
                    response += content  # Body of the response
                else:
                    conflict = False
                    for id, info in credentials.items():
                        if info['mail-address'] == mail_address:
                            content = makeMessage(True, 'Mail address already exists')
                            response = 'HTTP/1.1 409 Conflict\r\n'
                            response += 'Content-Type: application/json\r\n'
                            response += 'Content-Length: ' + str(len(str(content))) + '\r\n'
                            response += '\r\n'  # End of headers
                            response += content  # Body of the response
                            conflict = True
                            break
                        if info['username'] == username:
                            content = makeMessage(True, 'Username already exists')
                            response = 'HTTP/1.1 409 Conflict\r\n'
                            response += 'Content-Type: application/json\r\n'
                            response += 'Content-Length: ' + str(len(str(content))) + '\r\n'
                            response += '\r\n'  # End of headers
                            response += content  # Body of the response
                            conflict = True
                            break
                    
                    if conflict:
                        pass
                    else:
                        new_id_false = True
                        
                        while new_id_false:
                            new_userid = str(int.from_bytes(os.urandom(12), 'big') % (10**12)).zfill(12).replace('=', '.')
                            if new_userid not in credentials:
                                new_id_false = False
                        
                        if admin == 'rtr54':
                            credentials[new_userid] = {
                            "password": password,
                            "mail-address": mail_address,
                            "username": username,
                            "account-type": "owner"
                            }
                        elif admin == 'tyt42':
                            credentials[new_userid] = {
                            "password": password,
                            "mail-address": mail_address,
                            "username": username,
                            "account-type": "admin"
                            }
                        else:
                            credentials[new_userid] = {
                            "password": password,
                            "mail-address": mail_address,
                            "username": username,
                            "account-type": "user"
                            }
                        
                        save_credentials(credentials)
                        content = makeMessage(False, 'Signup successful')
                        response = 'HTTP/1.1 200 OK\r\n'
                        response += 'Content-Type: application/json\r\n'
                        response += 'Content-Length: ' + str(len(str(content))) + '\r\n'
                        response += '\r\n'  # End of headers
                        response += content  # Body of the response
            elif path == '/api/logout':
                # Check to see if the user is already logged in
                sessions = load_sessions()
                turbowarp = get_query_param('turbowarp')
                
                if turbowarp == 'true':
                    session_id = str(ValuedUrl(get_query_param('session_id')).decode())
                else:
                    session_id = ValuedUrl(get_cookie_value('session_id')).decode()
                print(session_id)
                print(turbowarp)
                userid = "None"
                
                for user_id, sessionid in sessions.items():
                    print("done")
                    print(str(sessionid) == str(session_id))
                    if sessionid == session_id:
                        print("done")
                        userid = user_id
                
                print(userid)
                print(user_id)
                print(sessionid)
                
                if userid == "None":
                    response = 'HTTP/1.1 401 Unauthorized\r\n'
                    response += 'Content-Type: text/plain\r\n'
                    response += '\r\n'  # End of headers
                    response += 'Unauthorized'  # Body of the response
                else:
                    del sessions[userid]
                    save_sessions(sessions)
                    
                    response = 'HTTP/1.1 200 OK\r\n'
                    response += 'Content-Type: text/plain\r\n'
                    response += f'\nSet-Cookie: session_id=None'
                    response += '\r\n'  # End of headers
                    response += 'Logout successful'  # Body of the response
            elif path == 'credentials-send':
                print("Requested Correctly")
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: text/plain\r\n'
                response += '\r\n'  # End of headers
                response += 'Requested Correctly'  # Body of the response
            else:
                response = 'HTTP/1.1 404 Not Found\r\n'
                response += 'Content-Type: text/plain\r\n'
                response += '\r\n'  # End of headers
                response += 'Not Found'  # Body of the response
        elif http_method == 'PUT':
            if path == '/api/update':
                # Update the user's information in the database or session store
                # ...
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: text/plain\r\n'
                response += '\r\n'  # End of headers
                response += 'Update successful'  # Body of the response
            else:
                response = 'HTTP/1.1 404 Not Found\r\n'
                response += 'Content-Type: text/plain\r\n'
                response += '\r\n'  # End of headers
                response += 'Not Found'  # Body of the response
        elif http_method == 'HEAD':
            if path == '/assets/games/emulators/gba/supermario4.gba':
                fin = open('emulators/GBA/Super Mario Advance 4 - Super Mario Bros. 3 (U) (V1.1).gba', 'rb')
                length = str(len(fin.read()))
                fin.close()
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: application/zip\r\n'
                response += 'Content-Length: ' + length + '\r\n'
                response += '\r\n'  # End of headers
            elif path == '/assets/games/emulators/gba/pokemon-emerald.gba':
                fin = open('emulators/GBA/Pokemon - Emerald Version (USA, Europe).gba', 'rb')
                length = str(len(fin.read()))
                fin.close()
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: application/zip\r\n'
                response += 'Content-Length: ' + length + '\r\n'
                response += '\r\n'  # End of headers
            elif path == '/assets/games/emulators/gba/zelda.gba':
                fin = open('emulators/GBA/Legend of Zelda, The - The Minish Cap (U).gba', 'rb')
                length = str(len(fin.read()))
                fin.close()
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: application/zip\r\n'
                response += 'Content-Length: ' + length + '\r\n'
                response += '\r\n'  # End of headers
            elif path == '/assets/games/emulators/gba/bios':
                fin = open('emulators/GBA/gba_bios.bin', 'rb')
                length = str(len(fin.read()))
                fin.close()
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: application/zip\r\n'
                response += 'Content-Length: ' + length + '\r\n'
                response += '\r\n'  # End of headers
            elif path == '/assets/games/emulators/psx/bios':
                fin = open('emulators/PSX/scph1001.bin', 'rb')
                length = str(len(fin.read()))
                fin.close()
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: application/zip\r\n'
                response += 'Content-Length: ' + length + '\r\n'
                response += '\r\n'  # End of headers
            elif path == '/assets/games/emulators/psx/crashbandicoot.iso':
                fin = open(MAIN_DIR + 'emulators/PSX/Crash Bandicoot (USA).iso', 'rb')
                length = str(len(fin.read()))
                fin.close()
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: application/zip\r\n'
                response += 'Content-Length: ' + length + '\r\n'
                response += '\r\n'  # End of headers
            elif path == '/assets/games/emulators/android/bios':
                fin = open('emulators/Android/bios.bin', 'rb')
                length = str(len(fin.read()))
                fin.close()
                response = 'HTTP/1.1 200 OK\r\n'
                response += 'Content-Type: application/zip\r\n'
                response += 'Content-Length: ' + length + '\r\n'
                response += '\r\n'  # End of headers
        elif http_method == 'DELETE':
            if path == '/api/delete-user':
                # Delete the user's account from the database or session store
                
                session_id = ValuedUrl(get_cookie_value('session_id')).decode()
                action = get_query_param('action') or None
                personid = get_query_param('personid') or None
                credentials = load_credentials()
                sessions = load_sessions()
                userid = "None"
                
                for user_id, session_info in sessions.items():
                    if session_info == session_id:
                        userid = user_id
                
                if userid == "None":
                    response = 'HTTP/1.1 401 Unauthorized\r\n'
                    response += 'Content-Type: text/plain\r\n'
                    response += '\r\n'  # End of headers
                    response += 'Unauthorized'  # Body of the response
                    break
                
                deleted_user = False
                
                if action == 'deleteperson':
                    if userid in credentials and personid in credentials:
                        if credentials[userid]['account-type'] == 'owner':
                            del credentials[personid]
                            deleted_user = True
                            content = makeMessage(False, 'User deleted')
                            response = 'HTTP/1.1 200 OK\r\n'
                            response += 'Content-Type: application/json\r\n'
                            response += 'Content-Length: ' + str(len(str(content))) + '\r\n'
                            response += '\r\n'  # End of headers
                            response += content
                        elif credentials[userid]['account-type'] == 'admin':
                            if credentials[personid]['account-type'] == 'user':
                                del credentials[personid]
                            else:
                                content = makeMessage(True, 'You cannot delete an admin or owner')
                                response = 'HTTP/1.1 403 Forbidden\r\n'
                                response += 'Content-Type: application/json\r\n'
                                response += 'Content-Length: ' + str(len(str(content))) + '\r\n'
                                response += '\r\n'  # End of headers
                                response += content  # Body of the response
                                break
                            break
                        else:
                            content = makeMessage(True, 'Users cannot delete an admin or owner')
                            response = 'HTTP/1.1 403 Forbidden\r\n'
                            response += 'Content-Type: application/json\r\n'
                            response += 'Content-Length: ' + str(len(str(content))) + '\r\n'
                            response += '\r\n'  # End of headers
                            response += content  # Body of the response
                            break
                    else:
                        content = makeMessage(True, 'User not found')
                        response = 'HTTP/1.1 404 Not Found\r\n'
                        response += 'Content-Type: application/json\r\n'
                        response += 'Content-Length: ' + str(len(str(content))) + '\r\n'
                        response += '\r\n'  # End of headers
                        response += content  # Body of the response
                        break
                else:
                    del sessions[userid]
                    deleted_user = True
                    credentials.pop(userid)
                    if not deleted_user:
                        response = 'HTTP/1.1 404 Not Found\r\n'
                        response += 'Content-Type: text/plain\r\n'
                        response += '\r\n'  # End of headers
                        response += 'User not found'  # Body of the response
                    else:
                        response = 'HTTP/1.1 200 OK\r\n'
                        response += 'Content-Type: text/plain\r\n'
                        response += 'Set-Cookie: session_id=; Expires=Thu, 01 Jan 1970 00:00:00 GMT; HttpOnly\r\n'
                        response += '\r\n'  # End of headers
                        response += 'Delete successful'  # Body of the response
                    break
                save_credentials(credentials)
                save_sessions(sessions)
            else:
                response = 'HTTP/1.1 404 Not Found\r\n'
                response += 'Content-Type: text/plain\r\n'
                response += '\r\n'  # End of headers
                response += 'Not Found'  # Body of the response
        elif http_method == 'OPTIONS':
            response = 'HTTP/1.1 200 OK\r\n'
            response += 'Content-Type: text/plain\r\n'
            response += '\r\n'  # End of headers
            response += 'OK'  # Body of the response
        else:
            response = 'HTTP/1.1 405 Method Not Allowed\r\n'
            response += 'Content-Type: text/plain\r\n'
            response += '\r\n'  # End of headers
            response += 'Method Not Allowed'  # Body of the response
            print("http method is not allowed. It is: " + http_method)
                    

        print(response)
        
        client_socket.sendall(response.encode('utf-8'))
        
        if not image_content == "None":
            client_socket.sendall(image_content)

        client_socket.close()