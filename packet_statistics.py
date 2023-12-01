import socket
import pickle

HOST = "127.0.0.1"
PORT = 65435
SIZE = 1024
FORMAT = "utf-8"

CLIENT_PORT = 65435
PROXY_PORT = 65436
SERVER_PORT = 65437

class PacketStatistics:
    def __init__(self):
        # Client Packets Tracker
        self.total_data_packets_client_sent = 0
        self.total_ack_packets_client_received = 0

        # Server Packets Tracker
        self.total_data_packets_server_received = 0
        self.total_ack_packets_server_sent = 0

        # Proxy Packets Tracker
        self.packet_to_server = 0
        self.ack_from_server = 0
        self.packet_from_client = 0
        self.ack_to_client = 0
    
    def str_client(self):
        return (f'Total of data packets: {str(self.total_data_packets_client_sent)}\n'
                f'Total of ack packets: {str(self.total_ack_packets_client_received)}\n')
    
    def str_server(self):
        return (f'Total of data packets: {str(self.total_data_packets_server_received)}\n'
                f'Total of ack packets: {str(self.total_ack_packets_server_sent)}\n')
    
    def str_proxy(self):
        return (f'Total packets sent to server: {str(self.packet_to_server)}\n'
                f'Total acks from server: {str(self.ack_from_server)}\n'
                f'Total packets from client: {str(self.packet_from_client)}\n'
                f'Total acks to client: {str(self.ack_to_client)}\n')

    # Client functions
    def increment_data_packets_client_sent(self):
        self.total_data_packets_client_sent = self.total_data_packets_client_sent + 1
        self.send_client_data_to_graph()
        self.save_client_file()

    def increment_ack_packets_client_received(self):
        self.total_ack_packets_client_received = self.total_ack_packets_client_received + 1
        self.send_client_data_to_graph()
        self.save_client_file()

    def save_client_file(self):
        with open('client_logs.txt', 'w') as f:
            print('total_data_packets_client_sent:' + str(self.total_data_packets_client_sent)
                  + ' increment_ack_packets_client_received:' + str(self.total_ack_packets_client_received), file=f
              )
            f.close()

    def save_proxy_file(self):
        with open('proxy_logs.txt', 'w') as f:
            print('packet_to_server: ' + str(self.packet_to_server) +
                  ' ack_from_server: ' + str(self.ack_from_server),
                  ' packet_from_client: ' + str(self.packet_from_client),
                  ' ack_to_client: ' + str(self.ack_to_client),
                  file=f
              )
            f.close()

    def save_server(self):
        with open('server_logs.txt', 'w') as f:
            print('total_data_packets_server_received: ' + str(self.total_data_packets_server_received) +
                  ' total_ack_packets_server_sent: ' + str(self.total_ack_packets_server_sent),
                  file=f
              )
            f.close()

    # Server functions
    def increment_data_packets_server_received(self):
        self.total_data_packets_server_received = self.total_data_packets_server_received + 1
        self.send_server_data_to_graph()
        self.save_server()

    def increment_ack_packets_server_sent(self):
        self.total_ack_packets_server_sent = self.total_ack_packets_server_sent + 1
        self.send_server_data_to_graph()
        self.save_server()

    # Proxy functions
    def inc_packet_to_server(self):
        self.packet_to_server = self.packet_to_server + 1
        self.send_proxy_data_to_graph()
        self.save_proxy_file()

    def inc_ack_from_server(self):
        self.ack_from_server = self.ack_from_server + 1
        self.send_proxy_data_to_graph()
        self.save_proxy_file()

    def inc_packet_from_client(self):
        self.packet_from_client = self.packet_from_client + 1
        self.send_proxy_data_to_graph()
        self.save_proxy_file()

    def inc_ack_to_client(self):
        self.ack_to_client = self.ack_to_client + 1
        self.send_proxy_data_to_graph()
        self.save_proxy_file()

    def send_proxy_data_to_graph(self):
        grapher_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            grapher_socket.connect((HOST, PROXY_PORT))
            # print("Proxy Connected!")
        except ConnectionRefusedError:
            print("Graphing Program is not running.")
            return
        
        try: 
            data = pickle.dumps(self)
            grapher_socket.sendall(data)
        finally:
            grapher_socket.close()

    def send_client_data_to_graph(self):
        grapher_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            grapher_socket.connect((HOST, CLIENT_PORT))
            # print("Client Connected!")
        except ConnectionRefusedError:
            print("Graphing Program is not running.")
            return
        
        try: 
            data = pickle.dumps(self)
            grapher_socket.sendall(data)
        finally:
            grapher_socket.close()

    def send_server_data_to_graph(self):
        grapher_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            grapher_socket.connect((HOST, SERVER_PORT))
            # print("Server Connected!")
        except ConnectionRefusedError:
            print("Graphing Program is not running.")
            return
        
        try: 
            data = pickle.dumps(self)
            grapher_socket.sendall(data)
        finally:
            grapher_socket.close()