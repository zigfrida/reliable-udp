import socket
import sys
import signal
import random
import time

SIZE = 1024
FORMAT = "utf-8"

PROXY_HOST = "127.0.0.1"  
PROXY_PORT = 65431      

SERVER_HOST = "127.0.0.1" 
SERVER_PORT = 65432  

PROB_DROPS = 0.1
PROB_DELAYS = 0.1

proxy_socket = None
server_socket = None
server_response = None

def signal_handler(sig, frame):
    print("\nUser Interruption. Stopping Proxy.")
    if(proxy_socket):
        proxy_socket.close()
    exit(0)

# Forward message and sequence number to the server
def send_to_server(client_data):
    global server_socket, server_response
    chance = random.random() 
    print(f"Chance to delay to client: {chance}")
    if chance < PROB_DELAYS:
        print("Delay packet to Server.")
        time.sleep(3)
    elif chance < PROB_DROPS:
        print("Packet dropped, not sent to Server.")
        return

    print("Sending to server")
    sequence_message = client_data.decode(FORMAT)
    
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_socket.sendto(sequence_message.encode(FORMAT), (SERVER_HOST, int(SERVER_PORT)))

    # Receive response from the server
    seq, _ = server_socket.recvfrom(SIZE)
    server_response = seq
    server_socket.close()


def send_to_client(client_addr):
    chance = random.random() 
    print(f"Chance to delay to server: {chance}")
    if chance < PROB_DELAYS:
        print("Delay packet to Client.")
        time.sleep(3)
    elif chance < PROB_DROPS:
        print("Packet dropped, not sent to Client.")
        return

    print("Sending to client.")
    proxy_socket.sendto(server_response, client_addr) # Send server's response (sequence number) back to the client


def main():
    global proxy_socket
    signal.signal(signal.SIGINT, signal_handler)

    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
    proxy_socket.bind((PROXY_HOST, int(PROXY_PORT)))
    print(f"Proxy listening on {PROXY_HOST}:{PROXY_PORT}")

    # while True:
    client_data, client_addr = proxy_socket.recvfrom(SIZE)  
    send_to_server(client_data)
    send_to_client(client_addr)

    proxy_socket.close()  # Close the proxy socket when done

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Missing required arguments.")
        print("Command: python3 proxy.py 127.0.0.1 65432 127.0.0.1 65433")
    else: 
        PROXY_HOST = sys.argv[1]
        PROXY_PORT = sys.argv[2]

        SERVER_HOST = sys.argv[3]
        SERVER_PORT = sys.argv[4]

    main()
