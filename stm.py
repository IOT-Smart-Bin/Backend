import socket
import threading
import requests

HOSTNAME = socket.gethostname()

HOST = socket.gethostbyname(HOSTNAME)
PORT = 5678
URL = 'http://13.229.60.73:8000'

# Create a list to keep track of active client threads
active_threads = []
# Track complete event for each thread
thread_complete_event = threading.Event()


def handle_client(client_socket, client_address):
    try:
        while True:
            endpoint = client_socket.recv(1024)

            # TL;DR: Send "close" before termination connection.

            # This catches if the client or server unexpectedly closes the socket connection, exit the loop
            # To avoid this happening, make sure that the client and server are in sync on when to close the connection.
            # If we want to avoid "[WinError 10053] An established connection was aborted by the software in your host machine," use the code below

            if not endpoint:
                break

            endpoint = endpoint.decode("utf-8")

            # get_bid
            if endpoint.lower() == "get_bid":
                response = "accepted".encode("utf-8")
                client_socket.send(response)

                request_body = client_socket.recv(1024)
                formatted_request_body = request_body.decode("utf-8")

                get_bid(client_socket=client_socket,
                        identifier=formatted_request_body)

            # calibrate
            if endpoint.lower() == "calibrate":
                response = "accepted".encode("utf-8")
                client_socket.send(response)

                request_body = client_socket.recv(1024)
                formatted_request_body = request_body.decode(
                    "utf-8").split(',')

                calibrate(client_socket=client_socket,
                          data_list=formatted_request_body)

            # post_data
            if endpoint.lower() == "post_data":
                response = "accepted".encode("utf-8")
                client_socket.send(response)

                request_body = client_socket.recv(1024)
                formatted_request_body = request_body.decode(
                    "utf-8").split(',')

                post_data(client_socket=client_socket,
                          data_list=formatted_request_body)

            if endpoint.lower() == "close":
                client_socket.send("closed".encode("utf-8"))
                break

    except ConnectionResetError:
        print(f"Connection to {client_address} reset by the client.")
    except Exception as e:
        print(f"An error occurred with Client {client_address}: {str(e)}")
    finally:
        client_socket.close()
        print(f"Connection to {client_address} closed")

        # Set the thread_complete_event to notify the monitor_thread
        thread_complete_event.set()


def calibrate(client_socket, data_list):
    key_list = ['bid', 'max_height']
    data_dict = dict()

    for element, key in zip(data_list, key_list):
        data_dict[key] = element

    try:
        response = requests.put(f"{URL}/calibrate", json=data_dict)
        response_string = str(response.status_code)
        message = response.json()

        if message is not None:
            response_string += f",{message['detail']['message']}"

        client_socket.send(response_string.encode('utf-8'))
    except Exception as e:
        print(f"Error calibrating: {str(e)}")
        client_socket.send("error".encode("utf-8"))


def get_bid(client_socket, identifier):
    try:
        response = requests.get(f"{URL}/bid/{identifier}")
        response_string = str(response.json()["bid"])
        client_socket.send(response_string.encode('utf-8'))
    except Exception as e:
        print(f"Error obtaining bid: {str(e)}")
        client_socket.send("error".encode("utf-8"))


def post_data(client_socket, data_list):
    key_list = ['bid', 'gas', 'weight', 'height',
                'humidity_inside', 'humidity_outside', 'temperature']
    data_dict = dict()

    for element, key in zip(data_list, key_list):
        data_dict[key] = element

    try:
        response = requests.post(f"{URL}/data", json=data_dict)
        response_string = str(response.status_code)
        message = response.json()

        if message is not None:
            response_string += f",{message['detail']['message']}"

        client_socket.send(response_string.encode('utf-8'))
    except Exception as e:
        print(f"Error posting data: {str(e)}")
        client_socket.send("error".encode("utf-8"))


def monitor_thread():
    while True:
        # Wait for the event to be set (a thread has completed its work)
        thread_complete_event.wait()

        # Clear the event
        thread_complete_event.clear()

        # Clean up threads that have finished their tasks
        for thread in active_threads:
            if not thread.is_alive():
                print("Removed thread", thread)

                thread.join()
                active_threads.remove(thread)

def run_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen(5)
    print(f"Listening on {HOST}:{PORT}")

    client_thread = threading.Thread(
        target=monitor_thread)
    client_thread.start()

    while True:
        client_socket, client_address = server.accept()
        print(
            f"Accepted connection from {client_address[0]}:{client_address[1]}")

        # Create a new thread to handle the client
        client_thread = threading.Thread(
            target=handle_client, args=(client_socket, client_address))
        client_thread.start()

        # Add the thread to the active_threads list
        active_threads.append(client_thread)


if __name__ == "__main__":
    run_server()
