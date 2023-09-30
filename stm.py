import socket

HOST = "127.0.0.1"
PORT = 5432


def run_server():
    # Create a dictionary to store client information
    clients = {}

    while True:
        # Create a socket object
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to a specific address and port
        server.bind((HOST, PORT))
        # Listen for incoming connections
        server.listen(0)
        print(f"Listening on {HOST}:{PORT}")

        # Accept incoming connections
        client_socket, client_address = server.accept()
        print(
            f"Accepted connection from {client_address[0]}:{client_address[1]}")

        # Store client information in the dictionary
        client_id = len(clients) + 1
        clients[client_id] = {
            "socket": client_socket, "address": client_address}

        try:
            # Receive data from the client
            while True:
                request = client_socket.recv(1024)

                # This catches if the client or server unexpectedly closes the socket connection, exit the loop
                # To avoid this happening, make sure that the client and server are in sync regarding when to close the connection.
                # if not request:
                #     break

                request = request.decode("utf-8")  # Convert bytes to string

                # If we receive "close" from the client, then we break
                # out of the loop and close the connection
                if request.lower() == "close":
                    # Send response to the client which acknowledges that the
                    # connection should be closed and break out of the loop
                    client_socket.send("closed".encode("utf-8"))
                    break

                print(f"Received from Client {client_id}: {request}")

                response = "accepted".encode(
                    "utf-8")  # Convert string to bytes
                # Convert and send accept response to the client
                client_socket.send(response)
        except ConnectionResetError:
            print(f"Connection to Client {client_id} reset by the client.")
        except Exception as e:
            print(f"An error occurred with Client {client_id}: {str(e)}")
        finally:
            # Close connection socket with the client
            client_socket.close()
            print(f"Connection to Client {client_id} closed")
            # Remove the client information from the dictionary
            del clients[client_id]
            # Don't close the server socket here; it should keep listening for new connections


if __name__ == "__main__":
    run_server()
