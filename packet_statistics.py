import socket
import pickle

HOST = "127.0.0.1"
PORT = 65435
SIZE = 1024
FORMAT = "utf-8"

class PacketStatistics:
    def __init__(self):
        self.total_data_packets = 0
        self.total_ack_packets = 0
        self.packet_to_server = 0
        self.ack_from_server = 0
        self.packet_from_client = 0
        self.ack_to_client = 0

    def __str__(self):
        return (f'Total of data packets: {str(self.total_data_packets)}\n'
                f'Total of ack packets: {str(self.total_ack_packets)}\n')
    
    def str_client_server(self):
        return (f'Total of data packets: {str(self.total_data_packets)}\n'
                f'Total of ack packets: {str(self.total_ack_packets)}\n')
    
    def str_proxy(self):
        return (f'Total packets sent to server: {str(self.packet_to_server)}\n'
                f'Total acks from server: {str(self.ack_from_server)}\n'
                f'Total packets from client: {str(self.packet_from_client)}\n'
                f'Total acks to client: {str(self.ack_to_client)}\n')

    # Client Server functions
    def increment_data_packets(self):
        self.total_data_packets = self.total_data_packets + 1
        self.send_data_to_graph()

    def increment_ack_packets(self):
        self.total_ack_packets = self.total_ack_packets + 1
        self.send_data_to_graph()

    # Proxy functions
    def inc_packet_to_server(self):
        self.packet_to_server = self.packet_to_server + 1
        self.send_data_to_graph()

    def inc_ack_from_server(self):
        self.ack_from_server = self.ack_from_server + 1
        self.send_data_to_graph()

    def inc_packet_from_client(self):
        self.packet_from_client = self.packet_from_client + 1
        self.send_data_to_graph()

    def inc_ack_to_client(self):
        self.ack_to_client = self.ack_to_client + 1
        self.send_data_to_graph()

    def send_data_to_graph(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            server_socket.connect((HOST, PORT))
            # print("Connected!")
        except ConnectionRefusedError:
            print("Graphing Program is not running.")
            return
        
        try: 
            data = pickle.dumps(self)
            server_socket.sendall(data)
        finally:
            server_socket.close()