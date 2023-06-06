import socket
import threading
import uuid


class ClientConnection(threading.Thread):
    def __init__(self, tracker_api, client_socket, ip_addr):
        super(ClientConnection, self).__init__()

        self.api = tracker_api

        self.client_socket = client_socket
        self.client_ip_addr = ip_addr
        self.client_id = str(uuid.uuid4())

        self.send_ack()

    def send_ack(self):
        """Send ACK message containing Client UUID"""
        self.client_socket.send(self.client_id.encode())

    def send_message(self, message):
        """Send a message to client"""
        self.client_socket.send(message.encode())

    def send_peer_list(self):
        return ""

    def run(self):
        while True:
            received = self.client_socket.recv(1024).decode()
            print("\nData received: ", received)

            try:
                key, value = received.split(":")

                if key == "LIST_PEERS":
                    data = self.send_peer_list()
                    # self.send_message_to_client(data)

            except Exception as e:
                print("Error occurred: ", e)


class TrackerApi:
    def __init__(self, ip, port):
        self.recv_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.recv_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.recv_socket.bind((ip, port))
        self.recv_socket.listen()

        self.client_list = []

    def create_new_client_connection(self, client_socket, ip_addr):
        client_connection = ClientConnection(self, client_socket, ip_addr)
        client_connection.daemon = True
        client_connection.start()
        return client_connection

    def start(self):
        print("\nTracker API Listening")
        while True:
            client_socket, ip_addr = self.recv_socket.accept()

            print("\nNew connection request received: ", ip_addr)
            connection = self.create_new_client_connection(client_socket, ip_addr)
            self.client_list.append(connection)
            print("Network participants: ", len(self.client_list))