import os

def handleUpload(client_conn, filename, filesize, BUFFER_SIZE, END, FORMAT, username):
    target_dir = f'./server_storage/{username}'
    os.makedirs(target_dir, exist_ok=True)
    
    filepath = os.path.join(target_dir, filename)
    
    with open(filepath, 'wb') as f:
        bytes_received = 0
        while bytes_received < filesize:
            bytes_read = client_conn.recv(BUFFER_SIZE)
            if END.encode(FORMAT) in bytes_read:
                data, _ = bytes_read.split(END.encode(FORMAT), 1)
                f.write(data)
                bytes_received += len(data)
                print("[FILE RECEIVED COMPLETELY]")
                break
            else:
                f.write(bytes_read)
                bytes_received += len(bytes_read)
    print(f"[FILE SAVED AS] {filename}")

