import socket
import threading

HOSTNAME = socket.gethostname()

HOST = socket.gethostbyname(HOSTNAME)
PORT = 5678

def handle_client(client_socket, client_address):
    try:
        while True:
            request = client_socket.recv(1024)

            # TL;DR: Send "close" before termination connection.

            # This catches if the client or server unexpectedly closes the socket connection, exit the loop
            # To avoid this happening, make sure that the client and server are in sync on when to close the connection.
            # If we want to avoid "[WinError 10053] An established connection was aborted by the software in your host machine," use the code below

            # if not request:
            #     break

            request = request.decode("utf-8")

            # Endpoints / Methods
            if request.lower() == "close":
                client_socket.send("closed".encode("utf-8"))
                break
            
            if request.lower() == "get_bid":
                # If the request is "get_bid," expect to receive an "identifier"
                identifier = client_socket.recv(1024).decode("utf-8")
                print(f"Received identifier from {client_address}: {identifier}")
                # Perform the action related to "get_bid" using the identifier

            print(f"Received from {client_address}: {request}")

            response = "accepted".encode("utf-8")
            client_socket.send(response)
    except ConnectionResetError:
        print(f"Connection to {client_address} reset by the client.")
    except Exception as e:
        print(f"An error occurred with Client {client_address}: {str(e)}")
    finally:
        client_socket.close()
        print(f"Connection to {client_address} closed")


def run_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"Listening on {HOST}:{PORT}")

    while True:
        client_socket, client_address = server.accept()
        print(
            f"Accepted connection from {client_address[0]}:{client_address[1]}")

        # Create a new thread to handle the client
        client_thread = threading.Thread(
            target=handle_client, args=(client_socket, client_address))
        client_thread.start()


if __name__ == "__main__":
    run_server()
