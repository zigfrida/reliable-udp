class PacketStatistics:
    def __init__(self):
        self.total_data_packets = 0
        self.total_ack_packets = 0

    def __str__(self):
        return (f'Total of data packets: {str(self.total_data_packets)}\n'
                f'Total of ack packets: {str(self.total_ack_packets)}')

    def increment_data_packets(self):
        self.total_data_packets = self.total_data_packets + 1

    def increment_ack_packets(self):
        self.total_ack_packets = self.total_ack_packets + 1

    def increment_data_packets_by(self, number_of_packets: int):
        self.total_data_packets = self.total_data_packets + number_of_packets

    def increment_ack_packets_by(self, number_of_packets: int):
        self.total_ack_packets = self.total_ack_packets + number_of_packets