import socket
import signal
import sys

from packet_statistics import PacketStatistics

HOST = "127.0.0.1"  
PORT = 65433       
SIZE = 1024
FORMAT = "utf-8"

server_socket = None
stats = PacketStatistics()

def signal_handler(sig, frame):
    print("\nUser Interruption. Shutting down server.")
    if server_socket: 
        server_socket.close()
    exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.bind((HOST, int(PORT)))
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        message_with_seq, addr = server_socket.recvfrom(SIZE) 
        if message_with_seq:
            stats.increment_data_packets_server_received()
            data, seq, client_addr = message_with_seq.decode(FORMAT).split("!")
            print(f"Message Received: {data}")
            server_response = f"{seq}!{client_addr}"
            print(f"Sending ACK: {seq}")

            server_socket.sendto(server_response.encode(FORMAT), addr)
            stats.increment_ack_packets_server_sent()
            stats.str_server()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Missing IP or port and GUI IP address")
    else:
        HOST = sys.argv[1]
        PORT = sys.argv[2]
        stats = PacketStatistics(sys.argv[3])
        main()