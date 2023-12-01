import random
import time
from threading import Thread
import matplotlib.pyplot as plt
import socket
import pickle
import sys
import signal
import select

HOST = "127.0.0.1"
PORT = 65435
SIZE = 1024
FORMAT = "utf-8"

client_socket = None
proxy_socket = None
server_socket = None

CLIENT_PORT = 65435
PROXY_PORT = 65436
SERVER_PORT = 65437

inputs = []
running = True

HISTORY_MAX_SIZE = 20
METRICS_UPDATE_INTERVAL_IN_SECONDS = 0.5
GRAPH_REDRAW_DELAY_IN_SECONDS = 1

# Client Packets Tracker
sender_ack_from_receiver_total_packet = 0
sender_ack_from_receiver_total_packet_history = []
sender_data_to_receiver_total_packet = 0
sender_data_to_receiver_total_packet_history = []

# Proxy Packets Tracker
proxy_ack_to_sender_total_packet = 0
proxy_ack_to_sender_total_packet_history = []
proxy_act_from_receiver_total_packet = 0
proxy_ack_from_receiver_total_packet_history = []
proxy_data_from_sender_total_packet = 0
proxy_data_from_sender_total_packet_history = []
proxy_data_to_receiver_total_packet = 0
proxy_data_to_receiver_total_packet_history = []

# Server Packets Tracker
receiver_act_to_sender_total_packet = 0
receiver_ack_to_sender_total_packet_history = []
receiver_data_from_sender_total_packet = 0
receiver_data_from_sender_total_packet_history = []


def signal_handler(sig, frame):
    global running
    print("\nUser Interruption. Shutting down server.")
    running = False
    if client_socket:
        client_socket.close()
    if server_socket:
        server_socket.close()
    if proxy_socket:
        proxy_socket.close()
    exit(0)

signal.signal(signal.SIGINT, signal_handler)


def get_total_packet_data():
    return (
        sender_ack_from_receiver_total_packet,
        sender_data_to_receiver_total_packet,
        proxy_ack_to_sender_total_packet,
        proxy_act_from_receiver_total_packet,
        proxy_data_from_sender_total_packet,
        proxy_data_to_receiver_total_packet,
        receiver_act_to_sender_total_packet,
        receiver_data_from_sender_total_packet
    )


def update_graph(ax, title, data_history):
    ax.set_title(title)
    for index, total_packet in enumerate(data_history):
        ax.plot(index, total_packet, 'o')


def update_graphs(axs):
    for row in range(4):
        for col in range(2):
            if axs[row, col]:
                axs[row, col].clear()

    update_graph(axs[0, 0], "Sender: Total of data packets sent", sender_data_to_receiver_total_packet_history)
    update_graph(axs[0, 1], "Proxy: Total of data packets received", proxy_data_from_sender_total_packet_history)

    update_graph(axs[1, 0], "Proxy: Total of data packets sent", proxy_data_to_receiver_total_packet_history)
    update_graph(axs[1, 1], "Receiver: Total of data packets received", receiver_data_from_sender_total_packet_history)
    update_graph(axs[2, 0], "Receiver: Total of ack packets sent", receiver_ack_to_sender_total_packet_history)
    update_graph(axs[2, 1], "Proxy: Total of ack packets received", proxy_ack_from_receiver_total_packet_history)

    update_graph(axs[3, 0], "Proxy: Total of ack packets sent", proxy_ack_to_sender_total_packet_history)
    update_graph(axs[3, 1], "Sender: Total of ack packets received", sender_ack_from_receiver_total_packet_history)


def show_graph():
    plt.ion()
    fig, axs = plt.subplots(4, 2)
    fig.tight_layout()

    while True:
        update_graphs(axs)
        fig.canvas.draw()
        fig.canvas.flush_events()
        time.sleep(GRAPH_REDRAW_DELAY_IN_SECONDS)


def update_list_pop_if_over_history_max_size(history_list: list, total_packets: int):
    if len(history_list) > HISTORY_MAX_SIZE:
        history_list.pop(0)
    history_list.append(total_packets)


def update_metrics_history():
    while True:
        time.sleep(METRICS_UPDATE_INTERVAL_IN_SECONDS)
        update_list_pop_if_over_history_max_size(sender_ack_from_receiver_total_packet_history,
                                                 sender_ack_from_receiver_total_packet)
        update_list_pop_if_over_history_max_size(sender_data_to_receiver_total_packet_history,
                                                 sender_data_to_receiver_total_packet)

        update_list_pop_if_over_history_max_size(proxy_ack_to_sender_total_packet_history,
                                                 proxy_ack_to_sender_total_packet)
        update_list_pop_if_over_history_max_size(proxy_ack_from_receiver_total_packet_history,
                                                 proxy_act_from_receiver_total_packet)
        update_list_pop_if_over_history_max_size(proxy_data_from_sender_total_packet_history,
                                                 proxy_data_from_sender_total_packet)
        update_list_pop_if_over_history_max_size(proxy_data_to_receiver_total_packet_history,
                                                 proxy_data_to_receiver_total_packet)

        update_list_pop_if_over_history_max_size(receiver_ack_to_sender_total_packet_history,
                                                 receiver_act_to_sender_total_packet)
        update_list_pop_if_over_history_max_size(receiver_data_from_sender_total_packet_history,
                                                 receiver_data_from_sender_total_packet)

def client_receiver():
    global client_socket, sender_ack_from_receiver_total_packet, sender_data_to_receiver_total_packet
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try: 
        client_socket.bind((HOST, CLIENT_PORT))
        client_socket.listen() 
        print(f"Socket for CLIENT listening on {HOST}:{CLIENT_PORT}")

    except OSError as e:
        print(f"Error: {e}. Server may already be running.")

    try:
        while True:
            conn, addr = client_socket.accept()
            # print(f"Connected by {addr}")

            while True:
                data = conn.recv(SIZE)
                if not data:
                    break

                # print("Data Client received!")
                received_statistics = pickle.loads(data)
                sender_data_to_receiver_total_packet = received_statistics.total_data_packets_client_sent
                sender_ack_from_receiver_total_packet = received_statistics.total_ack_packets_client_received

            conn.close()
    except KeyboardInterrupt:
        print("\nServer interrupted by user")
        server_socket.close()

def server_receiver():
    global server_socket, receiver_act_to_sender_total_packet, receiver_data_from_sender_total_packet
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try: 
        server_socket.bind((HOST, SERVER_PORT))
        server_socket.listen()
        print(f"Socket for SERVER listening on {HOST}:{SERVER_PORT}")

    except OSError as e:
        print(f"Error: {e}. Server may already be running.")

    try:
        while True:
            conn, addr = server_socket.accept()
            # print(f"Connected by {addr}")

            while True:
                data = conn.recv(SIZE)
                if not data:
                    break

                # print("Data Server received!")
                received_statistics = pickle.loads(data)
                receiver_act_to_sender_total_packet = received_statistics.total_ack_packets_server_sent
                receiver_data_from_sender_total_packet = received_statistics.total_data_packets_server_received

            conn.close()
    except KeyboardInterrupt:
        print("\nServer interrupted by user")
        server_socket.close()

def proxy_receiver():
    global proxy_socket, proxy_data_from_sender_total_packet, proxy_act_from_receiver_total_packet,proxy_data_to_receiver_total_packet,proxy_ack_to_sender_total_packet
    proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try: 
        proxy_socket.bind((HOST, PROXY_PORT))
        proxy_socket.listen() 
        print(f"Socket for PROXY listening on {HOST}:{PROXY_PORT}")

    except OSError as e:
        print(f"Error: {e}. Server may already be running.")

    try:
        while True:
            conn, addr = proxy_socket.accept()
            # print(f"Connected by {addr}")

            while True:
                data = conn.recv(SIZE)
                if not data:
                    break

                # print("Data Proxy received!")
                received_statistics = pickle.loads(data)
                proxy_data_from_sender_total_packet = received_statistics.packet_to_server
                proxy_act_from_receiver_total_packet = received_statistics.ack_from_server
                proxy_data_to_receiver_total_packet = received_statistics.packet_from_client
                proxy_ack_to_sender_total_packet = received_statistics.ack_to_client

            conn.close()
    except KeyboardInterrupt:
        print("\nServer interrupted by user")
        proxy_socket.close()

# Implement it so it updates total packet metrics from network
def receive_metrics():
    # Update these and more from network calls instead
    global sender_ack_from_receiver_total_packet, proxy_act_from_receiver_total_packet, proxy_data_from_sender_total_packet, proxy_data_to_receiver_total_packet
    while True:
        time.sleep(0.5)
        chance = random.random()
        if chance < 0.5:
            sender_ack_from_receiver_total_packet = sender_ack_from_receiver_total_packet + 1
        chance = random.random()
        if chance < 0.5:
            proxy_act_from_receiver_total_packet = proxy_act_from_receiver_total_packet + 1
        chance = random.random()
        if chance < 0.5:
            proxy_data_from_sender_total_packet = proxy_data_from_sender_total_packet + 1
        chance = random.random()
        if chance < 0.5:
            proxy_data_to_receiver_total_packet = proxy_data_to_receiver_total_packet + 1



if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Missing Address and Port for GUI")

    else:
        HOST = sys.argv[1]
        PORT = sys.argv[2]
        
        update_metrics_thread = Thread(target=update_metrics_history)
        update_metrics_thread.start()

        receive_client_metrics_thread = Thread(target=client_receiver)
        receive_client_metrics_thread.start()

        receive_server_metrics_thread = Thread(target=server_receiver)
        receive_server_metrics_thread.start()

        receive_proxy_metrics_thread = Thread(target=proxy_receiver)
        receive_proxy_metrics_thread.start()

        show_graph()
