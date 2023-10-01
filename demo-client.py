import socket

HOST = "13.229.60.73"  # The server's hostname or IP address (Update appropriately for testing)
PORT = 5678  # The port used by the server

with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    s.connect((HOST, PORT))
    
    # Send "endpoint" as the first message
    s.sendall(b"get_bid")
    
    # Receive and process the response for "endpoint"
    response = s.recv(1024)
    print(f"Received response for 'get_bid': {response.decode('utf-8')}")
    
    # Send "request body" as the second message
    s.sendall(b"identifier_demo_example")
    
    # Receive and process the response for "request"
    response = s.recv(1024)
    print(f"Received response for 'identifier_example': {response.decode('utf-8')}")