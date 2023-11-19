import random
import time
from threading import Thread
from queue import Queue
import matplotlib.pyplot as plt
import numpy as np

HISTORY_MAX_SIZE = 30

GRAPH_REDRAW_DELAY_IN_SECONDS = 1

sender_ack_from_receiver_total_packet = 0
sender_ack_from_receiver_total_packet_history = []
sender_data_to_receiver_total_packet = 0
sender_data_to_receiver_total_packet_history = []

proxy_ack_to_sender_total_packet = 0
proxy_ack_to_sender_total_packet_history = []
proxy_act_from_receiver_total_packet = 0
proxy_act_from_receiver_total_packet_history = []
proxy_data_from_sender_total_packet = 0
proxy_data_from_sender_total_packet_history = []
proxy_data_to_receiver_total_packet = 0
proxy_data_to_receiver_total_packet_history = []

receiver_act_to_sender_total_packet = 0
receiver_act_to_sender_total_packet_history = []
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

def update_graph(axs):
    x = np.linspace(0, 2 * np.pi, 400)
    y = np.sin(x ** 2)

    if axs[0, 0]:
        axs[0, 0].clear()

    for row in range(4):
        for col in range(2):
            if axs[row, col]:
                axs[row, col].clear()

    axs[0, 0].plot(x, y)
    axs[0, 0].set_title("Sender: Total of data packets sent")

    axs[0, 1].plot(x, y ** 2)
    axs[0, 1].set_title("Proxy: Total of data packets received")

    axs[1, 0].plot(x + 1, y + 1)
    axs[1, 0].set_title("Proxy: Total of data packets sent")
    axs[1, 1].plot(x + 2, y + 2)
    axs[1, 1].set_title("Receiver: Total of data packets received")

    axs[2, 0].plot(x, y)
    axs[2, 0].set_title("Receiver: Total of ack packets sent")
    axs[2, 1].plot(x, y)
    axs[2, 1].set_title("Proxy: Total of ack packets received")

    axs[3, 0].plot(x, y)
    axs[3, 0].set_title("Proxy: Total of ack packets sent")
    axs[3, 1].plot(x, y ** random.random())
    axs[3, 1].set_title("Sender: Total of ack packets received")



def show_graph():
    plt.ion()

    fig, axs = plt.subplots(4, 2)
    fig.tight_layout()

    while True:
        update_graph(axs)
        # drawing updated values
        fig.canvas.draw()
        # This will run the GUI event
        # loop until all UI events
        # currently waiting have been processed
        fig.canvas.flush_events()
        time.sleep(GRAPH_REDRAW_DELAY_IN_SECONDS)

def update_metrics():
    time.sleep(0.5)


if __name__ == "__main__":
    update_metrics_thread = Thread(target=update_metrics)
    update_metrics_thread.start()

    update_metrics_thread = Thread(target=update_metrics)
    update_metrics_thread.start()

    show_graph()
