import socket
import schemas
import requests

hostname=socket.gethostname()
server=socket.gethostbyname(hostname)
port = 5678
baseurl = '13.229.60.73:8000/'
def calibrate(s):
    data = s.recv(1024)
    data.decode('utf-8')
    data_list = data.split(',')
    key_list = ['bid','max_height']
    data_dict = dict()
    for element, key in zip(data_list, key_list):
        data_dict[key] = element
    response = requests.post(f"{baseurl}calibrate", json=data_dict)
    


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
