import random
import time
from threading import Thread
import matplotlib.pyplot as plt

HISTORY_MAX_SIZE = 20
METRICS_UPDATE_INTERVAL_IN_SECONDS = 0.5
GRAPH_REDRAW_DELAY_IN_SECONDS = 1

sender_ack_from_receiver_total_packet = 0
sender_ack_from_receiver_total_packet_history = []
sender_data_to_receiver_total_packet = 0
sender_data_to_receiver_total_packet_history = []

proxy_ack_to_sender_total_packet = 0
proxy_ack_to_sender_total_packet_history = []
proxy_act_from_receiver_total_packet = 0
proxy_ack_from_receiver_total_packet_history = []
proxy_data_from_sender_total_packet = 0
proxy_data_from_sender_total_packet_history = []
proxy_data_to_receiver_total_packet = 0
proxy_data_to_receiver_total_packet_history = []

receiver_act_to_sender_total_packet = 0
receiver_ack_to_sender_total_packet_history = []
receiver_data_from_sender_total_packet = 0
receiver_data_from_sender_total_packet_history = []


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


# Implement it so it updates total packet metrics from network
def receive_metrics():
    # Update these from network call
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
    update_metrics_thread = Thread(target=update_metrics_history)
    update_metrics_thread.start()

    receive_metrics_thread = Thread(target=receive_metrics)
    receive_metrics_thread.start()

    show_graph()
