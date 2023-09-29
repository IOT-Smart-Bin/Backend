import socket

hostname=socket.gethostname()
server=socket.gethostbyname(hostname)
port = 5678
if __name__ == "__main__":
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        s.bind((server, port))
    except socket.error as e:
        print(str(e))

    s.listen(2)
    print("Waiting for a connection, Server Started")

    while True:
        conn, addr = s.accept()
        