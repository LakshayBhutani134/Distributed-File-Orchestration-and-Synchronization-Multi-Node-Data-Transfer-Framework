import socket
import threading
import sys
import os
from file_upload import handleUpload

active_conn = []

PORT = 5050
HOST = socket.gethostbyname(socket.gethostname())
SEPARATOR = '<>'
BUFFER_SIZE = 1024
FORMAT = 'utf-8'
END = "<end>"
shutdown_flag = threading.Event()

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

def authenticate(client_conn):
    # Authentication code remains the same
    client_conn.send("Enter username and password (format: username<>password): ".encode(FORMAT))
    
    try:
        credentials = client_conn.recv(BUFFER_SIZE).decode(FORMAT)
        print(f"[DEBUG] Received credentials: {credentials}")
        parts = credentials.split(SEPARATOR)
        if len(parts) != 2:
            print("[ERROR] Incorrect credentials format received.")
            return False, None

        username, password = parts

        with open("id_passwd.txt", "r") as f:
            for line in f:
                try:
                    stored_username, stored_password = line.strip().split(":")
                    if username == stored_username and password == stored_password:
                        print("[DEBUG] Authentication successful.")
                        return True, username
                except ValueError:
                    print("[ERROR] Malformed line in id_passwd.txt; expected format username:password.")
    except Exception as e:
        print(f"[ERROR] Failed to authenticate client: {e}")
    return False, None

def handle_client(client_conn, addr):
    print(f"[NEW CONNECTION] {addr} connected")
    
    # Authenticate client
    auth, username = authenticate(client_conn)
    if not auth:
        print(f"[AUTH FAILURE] {addr} authentication failed")
        client_conn.send("AUTH FAILURE".encode(FORMAT))
        client_conn.close()
        return
    client_conn.send("AUTH SUCCESS".encode(FORMAT))
    
    while True:
        try:
            # Receive the operation, filename, and filesize
            file_meta_msg = client_conn.recv(BUFFER_SIZE).decode(FORMAT)
            print(f"[DEBUG] Received file metadata: {file_meta_msg}")

            if SEPARATOR in file_meta_msg:
                operation, filename, filesize = file_meta_msg.split(SEPARATOR)
                filename = os.path.basename(filename)
                print("Base path", filename)
                filesize = int(filesize)

                if int(operation) == 1:
                    handleUpload(client_conn, filename, filesize, BUFFER_SIZE, END, FORMAT, username)
                    client_conn.send("FILE UPLOADED SUCCESSFULLY".encode(FORMAT))
                elif int(operation) == 2:
                    handleDelete(client_conn, filename, username)
                    # Remove the duplicate send here as handleDelete already sends a response
                elif int(operation) == 3:
                    handleView(client_conn, filename, username)
                elif int(operation) == 4:
                    handleListFiles(client_conn, username)
                elif int(operation) == 5:  # Assuming 5 is the operation code for downloading a file
                    handleDownload(client_conn, filename, username)

            else:
                operation = int(file_meta_msg)
                if operation == 909:
                    print("[DEBUG] CLIENT DISCONNECTED SUCCESSFULLY")
                    client_conn.close()
                    active_conn.remove(client_conn)
                    break
                elif operation == 6:
                    server_close()
                    break

        except OSError as e:
            client_conn.close()
            print("OS closed")
            break

        except Exception as e:
            print(f"[ERROR] {e}")
            client_conn.send(f"ERROR: {e}".encode(FORMAT))
            client_conn.close()
            break

        finally:
            print(f"[TASK DONE]...")
            

def handleDelete(client_conn, filename, username):
    target_dir = f'./server_storage/{username}'
    filepath = os.path.join(target_dir, filename)
    try:
        os.remove(filepath)
        print(f"[FILE DELETED] {filename}")
        client_conn.send("FILE DELETED SUCCESSFULLY".encode(FORMAT))
    except FileNotFoundError:
        print(f"[ERROR] File not found: {filename}")
        client_conn.send("FILE NOT FOUND".encode(FORMAT))
    except Exception as e:
        print(f"[ERROR] Failed to delete file: {e}")
        client_conn.send(f"ERROR: {e}".encode(FORMAT))

def handleView(client_conn, filename, username):
    target_dir = f'./server_storage/{username}'
    filepath = os.path.join(target_dir, filename)
    try:
        with open(filepath, 'rb') as f:
            preview = f.read(BUFFER_SIZE)
            client_conn.send(preview)
        print(f"[FILE PREVIEW SENT] {filename}")
    except FileNotFoundError:
        print(f"[ERROR] File not found: {filename}")
        client_conn.send("FILE NOT FOUND".encode(FORMAT))
    except Exception as e:
        print(f"[ERROR] Failed to send file preview: {e}")
        client_conn.send(f"ERROR: {e}".encode(FORMAT))

def handleListFiles(client_conn, username):
    """Handle listing files in the client's directory."""
    target_dir = f'./server_storage/{username}'
    
    try:
        # Create directory if it doesn't exist
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            
        # Get list of files
        files = os.listdir(target_dir)
        
        if not files:
            response = "No files found in your directory."
        else:
            # Create formatted list of files with sizes
            file_list = []
            for file in files:
                file_path = os.path.join(target_dir, file)
                size = os.path.getsize(file_path)
                file_list.append(f"{file} ({size} bytes)")
            response = "\n".join(file_list)
        
        # Send the response
        client_conn.send(response.encode(FORMAT))
        print(f"[FILES LISTED] for user {username}")
        
    except Exception as e:
        error_msg = f"Error listing files: {str(e)}"
        client_conn.send(error_msg.encode(FORMAT))
        print(f"[ERROR] {error_msg}")

def handleDownload(client_conn, filename, username):
    """Handle downloading files for the client."""
    target_dir = f'./server_storage/{username}'
    filepath = os.path.join(target_dir, filename)
    print(filepath)
    
    try:
        # Check if the file exists
        if not os.path.exists(filepath):
            print(f"[ERROR] File not found: {filename}")
            client_conn.send("FILE NOT FOUND".encode(FORMAT))
            return
        
        # Get the file size and send metadata to the client
        filesize = os.path.getsize(filepath)
        client_conn.send(f"{filename}{SEPARATOR}{filesize}".encode(FORMAT))
        
        # Open and send the file in chunks
        with open(filepath, 'rb') as f:
            while True:
                bytes_read = f.read(BUFFER_SIZE)
                if not bytes_read:
                    break
                client_conn.send(bytes_read)
        
        # Send END marker to indicate completion
        client_conn.send(END.encode(FORMAT))
        print(f"[FILE SENT] {filename} ({filesize} bytes)")
    
    except Exception as e:
        error_msg = f"[ERROR] Failed to send file: {e}"
        print(error_msg)
        client_conn.send(f"ERROR: {e}".encode(FORMAT))


def signal_handler(client_conn):
    active_conn.remove(client_conn)
    client_conn.close()
    print("[EXITING]...")
    sys.exit(0)

def server_close():
    
    shutdown_flag.set()

    for conn in active_conn:
        try:
            conn.send("Close".encode(FORMAT))
            print("Closed")
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()
        except OSError as e:
            print("Connection error")

    active_conn.clear()

    server.close()
    

def start():
    server.listen()
    print(f'[LISTENING] at {HOST} on {PORT}')
    try:
        while not shutdown_flag.is_set(): 
            client_conn, addr = server.accept()
            active_conn.append(client_conn)
            print(f"[NEW CONNECTION] {addr} accepted")
            thread = threading.Thread(target=handle_client, args=(client_conn, addr))
            thread.start()
            print(len(active_conn))
            print(f"ACTIVE CONNECTIONS: {threading.active_count()-1}")
    except Exception as e:
        print("Server closed")
        sys.exit(0)
    except KeyboardInterrupt:
        server_close()
        
start()