##
# @file serial_com.py
#
# @brief Serial data logger and real-time plotter.
#
# @author ph919@ic.ac.uk

import os
import time
import queue

import numpy as np
import pandas as pd
import serial
import serial.threaded
from threading import Thread
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

dq = queue.Queue()
dt = np.dtype([("emg1_adc", "<u2"), ("emg1_volt", "<f")])
arr = np.empty(0, dtype=dt)

fig, ax = plt.subplots()
(ln,) = ax.plot([], [])


def init_plot():
    ax.set_ylim(0, 5)
    ax.set_xlim(0, 100)
    return (ln,)


def update_plot(frame):
    ln.set_data(range(len(arr["emg1_volt"][-100:])), arr["emg1_volt"][-100:])
    return (ln,)


class ReadRaw(serial.threaded.Protocol):
    def connection_made(self, transport):
        super(ReadRaw, self).connection_made(transport)
        print("port opened")

    def data_received(self, data):
        for i in data:
            dq.put(i)

    def connection_lost(self, exc):
        if exc:
            print(exc)
        print("port closed")


def log_data():
    global arr
    try:
        while True:
            packet = bytearray()
            for member in range(dt.itemsize):
                packet.append(dq.get(timeout=1))
            data = np.frombuffer(packet, dtype=dt)
            print(f"packet: {packet}, data: {data}")
            arr = np.concatenate((arr, data))
    except queue.Empty:
        print("queue empty, ending log...")
        df = pd.DataFrame(arr, columns=arr.dtype.names)
        # df.to_csv(os.path.join(os.getcwd(), str(time.time()) + "-out.csv"))
        df.to_csv(os.path.join(os.getcwd(), "tmp.csv"))
        # ani.event_source.stop()


if __name__ == "__main__":
    print("starting log...")

    # https://pyserial.readthedocs.io/en/latest/pyserial.html
    # `python -m serial.tools.list_ports` or `ls /dev/cu.*`
    clicker_port = input("Enter your TTY device:")
    ser = serial.Serial(port=clicker_port, baudrate=115200, timeout=1)

    reader = serial.threaded.ReaderThread(ser, ReadRaw)
    reader.start()

    logger = Thread(target=log_data)
    while True:
        # To stop recording, press and hold the reset button on the microcontroller board.
        command = input("Type 's' to begin:")
        if command == "s":
            # reader.write(b's')
            break
    logger.start()

    ani = FuncAnimation(fig, update_plot, interval=100, init_func=init_plot, blit=True)
    plt.show()

    logger.join()

    df = pd.DataFrame(arr, columns=arr.dtype.names)
    # df.to_csv(os.path.join(os.getcwd(), str(time.time()) + "-out.csv"))
    df.to_csv(os.path.join(os.getcwd(), "tmp.csv"))
    print("log ended.")
