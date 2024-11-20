# Distributed-File-Orchestration-and-Synchronization-Multi-Node-Data-Transfer-Framework
An implementation of Big Data concepts using Python, leveraging computer networks and operating systems. This distributed file system supports concurrent connections with features like user authentication, file upload/download, viewing (first 1024 bytes), deletion, and listing in user-specific directories. The system ensures scalability, data integrity, and graceful shutdown. To enable multi-device functionality, update the HOST variable in client.py to the server's IP address:

HOST = socket.gethostbyname(socket.gethostname())  # Replace with server IP  

