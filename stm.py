import socket
import threading
import requests

HOSTNAME = socket.gethostname()

HOST = socket.gethostbyname(HOSTNAME)
PORT = 5678
URL = '13.229.60.73:8000/'


def handle_client(client_socket, client_address):
    try:
        while True:
            request = client_socket.recv(1024)

            # TL;DR: Send "close" before termination connection.

            # This catches if the client or server unexpectedly closes the socket connection, exit the loop
            # To avoid this happening, make sure that the client and server are in sync on when to close the connection.
            # If we want to avoid "[WinError 10053] An established connection was aborted by the software in your host machine," use the code below

            if not request:
                pass

            request = request.decode("utf-8")

            # get_bid
            if request.lower() == "get_bid":
                response = "accepted".encode("utf-8")
                client_socket.send(response)

                # Wait for request body from the client
                while True:
                    request = client_socket.recv(1024)
                    request = request.decode("utf-8")

                    # Process the request
                    if request is not None:
                        get_bid(client_socket, request)
                        break

            # calibrate
            if request.lower() == "calibrate":
                response = "accepted".encode("utf-8")
                client_socket.send(response)

                # Wait for request body from the client
                while True:
                    request = client_socket.recv(1024)
                    request = request.decode("utf-8")

                    # Process the request
                    if request is not None:
                        request_body = request.split(',')
                        calibrate(client_socket = client_socket, data_list=request_body)
                        break

            # post_data
            if request.lower() == "post_data":
                response = "accepted".encode("utf-8")
                client_socket.send(response)

                # Wait for request body from the client
                while True:
                    request = client_socket.recv(1024)
                    request = request.decode("utf-8")

                    # Process the request
                    if request is not None:
                        request_body = request.split(',')
                        post_data(client_socket = client_socket, data_list=request_body)
                        break

            if request.lower() == "close":
                client_socket.send("closed".encode("utf-8"))
                break

    except ConnectionResetError:
        print(f"Connection to {client_address} reset by the client.")
    except Exception as e:
        print(f"An error occurred with Client {client_address}: {str(e)}")
    finally:
        client_socket.close()
        print(f"Connection to {client_address} closed")


def calibrate(client_socket, data_list):
    key_list = ['bid', 'max_height']
    data_dict = dict()

    for element, key in zip(data_list, key_list):
        data_dict[key] = element

    response = requests.post(f"{URL}/calibrate", json=data_dict)
    response_string = str(response.status_code)
    message = response.json()

    if message is not None:
        response_string += f",{message['detail']['message']}"

    client_socket.send(response_string.encode('utf-8'))


def get_bid(client_socket, identifier):
    # Make an HTTP POST request to obtain a bid
    try:
        response = requests.get(
            f"{URL}/bid/{identifier}", headers={'Accept': 'application/json'})
        response = str(response.json()["bid"]).encode("utf-8")
        client_socket.send(response)
    except Exception as e:
        print(f"Error obtaining bid: {str(e)}")


def post_data(client_socket, data_list):
    key_list = ['bid', 'gas', 'weight', 'height',
                'humidity_inside', 'humidity_outside', 'temperature']
    data_dict = dict()

    for element, key in zip(data_list, key_list):
        data_dict[key] = element

    response = requests.post(f"{URL}/data", json=data_dict)
    response_string = str(response.status_code)
    message = response.json()

    if message is not None:
        response_string += f",{message['detail']['message']}"

    client_socket.send(response_string.encode('utf-8'))


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
