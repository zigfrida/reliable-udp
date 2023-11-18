import socket
import signal

HOST = "127.0.0.1"  
PORT = 65432       
SIZE = 1024
FORMAT = "utf-8"

server_socket = None

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
        data, seq = message_with_seq.decode(FORMAT).split("!")

        print(f"Received message from {addr}: {data}")
        print(f"Sending ACK: {seq}")

        server_socket.sendto(seq.encode(FORMAT), addr)


if __name__ == "__main__":
    main()