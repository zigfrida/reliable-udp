import socket
import sys
import signal
import random
import time
from threading import Thread
from packet_statistics import PacketStatistics

SIZE = 1024
FORMAT = "utf-8"

PROXY_HOST = "127.0.0.1"  
PROXY_PORT = 65432      

SERVER_HOST = "127.0.0.1" 
SERVER_PORT = 65433  

PROB_DROPS = 0.5
PROB_DELAYS = 0.5

proxy_socket = None
server_socket = None
server_response = None

stats = PacketStatistics()

def signal_handler(sig, frame):
    print("\nUser Interruption. Stopping Proxy.")
    if(proxy_socket):
        proxy_socket.close()
    if(server_socket):
        server_socket.close()
    exit(0)

def proxy_prob():
    delay_chance = random.random()
    print(f"Delay chance: {delay_chance}")
    if delay_chance < PROB_DELAYS:
        print("Pakcet Delayed")
        time.sleep(3)
        return True
    
    drop_chance = random.random()
    if drop_chance < PROB_DROPS:
        print("Packet Dropped")
        return False
    
    return True

def send_to_server():
    while True:
        print("Waiting for data from client")
        client_data, client_addr = proxy_socket.recvfrom(SIZE)
        if client_data:
            stats.inc_packet_from_client()
            print("Got data from client")
            if proxy_prob():
                print("Sending to server")
                stats.inc_packet_to_server()
                sequence_message = client_data.decode(FORMAT)
                print(f"Message sending to server: {sequence_message}")
                server_socket.sendto(client_data, (SERVER_HOST, int(SERVER_PORT)))
            stats.str_proxy()

def send_to_client():
    while True:
        print("Waiting for data from server")
        data, _ = server_socket.recvfrom(SIZE)
        if data:
            stats.inc_ack_from_server()
            print("Got sequence number from server")
            if proxy_prob():
                stats.inc_ack_to_client()
                seq, client_addr = data.decode(FORMAT).split("!")
                host, port = client_addr.split(":")
                print(f"Sending to client: {client_addr}")
                proxy_socket.sendto(seq.encode(FORMAT), (host, int(port)))
            stats.str_proxy()
            


def main():
    global proxy_socket, server_socket
    signal.signal(signal.SIGINT, signal_handler)

    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  
    proxy_socket.bind((PROXY_HOST, int(PROXY_PORT)))
    print(f"Proxy listening on {PROXY_HOST}:{PROXY_PORT}")

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # start Send to server thread
    t1 = Thread(target=send_to_server)
    t1.start()
    # start Send to client thread
    t2 = Thread(target=send_to_client)
    t2.start()



if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("Missing required arguments.")
        print("Command: python3 proxy.py PROXY_HOST PORT SERVER_HOST PORT")
    else: 
        PROXY_HOST = sys.argv[1]
        PROXY_PORT = sys.argv[2]

        SERVER_HOST = sys.argv[3]
        SERVER_PORT = sys.argv[4]

    main()
