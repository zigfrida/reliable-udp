class ProxyPacketStatistics:
    def __init__(self):
        self.packet_to_server = 0
        self.ack_from_server = 0
        self.packet_from_client = 0
        self.ack_to_client = 0

    def __str__(self):
        return (f'Total packets sent to server: {str(self.packet_to_server)}\n'
                f'Total acks from server: {str(self.ack_from_server)}\n'
                f'Total packets sent to client: {str(self.packet_from_client)}\n'
                f'Total acks to client: {str(self.ack_to_client)}\n')

    def inc_packet_to_server(self):
        self.packet_to_server = self.packet_to_server + 1

    def inc_ack_from_server(self):
        self.ack_from_server = self.ack_from_server + 1

    def inc_packet_from_client(self, number_of_packets: int):
        self.packet_from_client = self.packet_from_client + number_of_packets

    def inc_ack_to_client(self, number_of_packets: int):
        self.ack_to_client = self.ack_to_client + number_of_packets