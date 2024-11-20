import socket
import sys
import os

PORT = 5050
HOST = "10.20.200.203"
SEPARATOR = '<>'
BUFFER_SIZE = 1024
FORMAT = 'utf-8'
END = "<end>"

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))

def signal_handler(operation):
    client.send(f"{operation}".encode(FORMAT))
    print("[DISCONNECTING]...")
    # client.close()
    sys.exit(0)

try:
    # Authentication Phase
    auth_prompt = client.recv(BUFFER_SIZE).decode(FORMAT)
    print(auth_prompt)  # Prompt from server

    # Send username and password
    username = input("Enter username: ")
    password = input("Enter password: ")
    credentials = f"{username}{SEPARATOR}{password}"
    client.send(credentials.encode(FORMAT))

    # Wait for authentication response
    auth_response = client.recv(BUFFER_SIZE).decode(FORMAT)
    print(auth_response)  # Should be either "AUTH SUCCESS" or "AUTH FAILURE"

    if auth_response == "AUTH SUCCESS":
        # Authentication succeeded, proceed with operations
        while True:
            operation = input("Enter operation (1 to upload file, 2 to delete file, 3 to view file, 4 to list all files, 5 to download, 909 to disconnect): ")

            try:
                if int(operation) == 1:
                    filename = input("Enter the filename to upload: ")
                    
                    try:
                        filesize = os.path.getsize(filename)
                    except FileNotFoundError:
                        print("File not found.")
                        continue

                    # Send operation, filename, and filesize to server
                    client.send(f"{operation}{SEPARATOR}{filename}{SEPARATOR}{filesize}".encode(FORMAT))

                    # Send file content
                    try:
                        with open(filename, 'rb') as f:
                            while True:
                                bytes_read = f.read(BUFFER_SIZE)
                                if not bytes_read:
                                    break
                                client.send(bytes_read)
                    except Exception as e:
                        print(f"Error during file transmission: {e}")
                        continue

                    # Send END marker to indicate file upload completion
                    client.send(END.encode(FORMAT))
                    
                    # Receive and print server response for file upload
                    flag = client.recv(BUFFER_SIZE).decode(FORMAT)
                    print(flag)

                elif int(operation) == 2:
                    filename = input("Enter the filename to delete: ")
                    client.send(f"{operation}{SEPARATOR}{filename}{SEPARATOR}0".encode(FORMAT))
                    response = client.recv(BUFFER_SIZE).decode(FORMAT)
                    print(response)

                elif int(operation) == 3:
                    filename = input("Enter the filename to view: ")
                    client.send(f"{operation}{SEPARATOR}{filename}{SEPARATOR}0".encode(FORMAT))
                    preview = client.recv(BUFFER_SIZE)
                    print(f"\n{preview.decode(FORMAT)}")
            
                elif int(operation) == 4:
                    # Send list files request
                    client.send(f"4{SEPARATOR}list{SEPARATOR}0".encode(FORMAT))
                    # Receive and display the file list
                    file_list = client.recv(BUFFER_SIZE).decode(FORMAT)
                    print("\nFiles in your directory:")
                    print(file_list)
                    print()

                elif int(operation) == 5:
                    filename = input("Enter the filename to download: ")
                    
                    # Send the download request to the server
                    client.send(f"{operation}{SEPARATOR}{filename}{SEPARATOR}0".encode(FORMAT))
                    
                    # Receive the response metadata (filename and filesize)
                    metadata = client.recv(BUFFER_SIZE).decode(FORMAT)
                    
                    if metadata == "FILE NOT FOUND":
                        print("File not found on the server.")
                        continue
                    
                    # Parse metadata
                    received_filename, filesize = metadata.split(SEPARATOR)
                    filesize = int(filesize)
                    print(f"Downloading file: {received_filename} ({filesize} bytes)")
                    
                    # Open a file to write the received data
                    with open(received_filename, 'wb') as f:
                        bytes_received = 0
                        
                        while bytes_received < filesize:
                            bytes_read = client.recv(BUFFER_SIZE)
                            
                            # Check for END marker
                            if END.encode(FORMAT) in bytes_read:
                                data, _ = bytes_read.split(END.encode(FORMAT), 1)
                                f.write(data)
                                bytes_received += len(data)
                                print("[DOWNLOAD COMPLETE]")
                                break
                            else:
                                f.write(bytes_read)
                                bytes_received += len(bytes_read)
                    
                    print(f"File downloaded successfully: {received_filename}")

                elif int(operation) == 6:
                    client.send(f"{operation}".encode(FORMAT))
                    print("[DISCONNECTING]...")
                    print(client.recv(BUFFER_SIZE).decode(FORMAT))
                    client.close()
                    sys.exit(0)
                    
                elif int(operation) == 909:
                    signal_handler(operation)
                    
                

                else:
                    print("Invalid Operation")


            except ConnectionResetError:
                print("Server shut down")
                break
            except Exception as e:
                print("Invalid input: ", e)
                continue
    else:
        # Authentication failed, disconnect
        print("Authentication failed. Closing connection.")
        client.close()

except KeyboardInterrupt:
    signal_handler(909)


