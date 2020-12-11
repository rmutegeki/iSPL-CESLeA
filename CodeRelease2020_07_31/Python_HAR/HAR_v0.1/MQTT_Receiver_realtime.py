"""
Creates multiple Connections to a broker
and sends and receives messages.
Uses one thread per client
"""
import paho.mqtt.client as mqtt
import time
import datetime
import threading
import logging
import numpy as np
import tkinter as tk
from PIL import ImageTk, Image
import math

logging.basicConfig(level=logging.INFO)

# sub_topic: x/y: where x is device (user) ID, y is the task (1: sensor data, 2: label data)

# constants:
BROKER_IP = "123.456.78.9"

clients = [
    {"broker": BROKER_IP, "port": 1883, "name": "sub1", "sub_topic": "1/1", "pub_topic": "1"}
    # , {"broker": BROKER_IP, "port": 1883, "name": "sub2", "sub_topic": "2", "pub_topic": "2"}
    # , {"broker": BROKER_IP, "port": 1883, "name": "sub3", "sub_topic": "3", "pub_topic": "2"}
]
n_clients = len(clients)
n_users = n_clients                    # number of sensors (same with nclients)

dt = datetime.datetime.now()
RAW_DATA_FILE = f"data/realtime/raw_data"

isStarted = False               # Change when receive the start request: True (start saving data)
currentActivity = -1            # current activity: is the index of class_names

class_names = [
    "IDLE",
    "WALKING",
    "STANDING",
    "SITTING",
    "LYING",
    "RUNNING",
    "CYCLING",
    "HAND-FREE"
]

def Connect(client, broker, port, keepalive, run_forever=False):
    """Attempts connection set delay to >1 to keep trying
    but at longer intervals. If runforever flag is true then
    it will keep trying to connect or reconnect indefinetly otherwise
    gives up after 3 failed attempts"""
    connflag = False
    delay = 5
    # print("connecting ",client)
    badcount = 0  # counter for bad connection attempts
    while not connflag:
        logging.info("connecting to broker " + str(broker))
        # print("connecting to broker "+str(broker)+":"+str(port))
        print("Attempts ", str(badcount))
        time.sleep(delay)
        try:
            client.connect(broker, port, keepalive)
            connflag = True

        except:
            client.badconnection_flag = True
            logging.info("connection failed " + str(badcount))
            badcount += 1
            if badcount >= 3 and not run_forever:
                return -1
                raise SystemExit  # give up

    return 0
    #####end connecting


def wait_for(client, msgType, period=1, wait_time=10, running_loop=False):
    """Will wait for a particular event gives up after period*wait_time, Default=10
seconds.Returns True if succesful False if fails"""
    # running loop is true when using loop_start or loop_forever
    client.running_loop = running_loop  #
    wcount = 0
    while True:
        logging.info("waiting" + msgType)
        if msgType == "CONNACK":
            if client.on_connect:
                if client.connected_flag:
                    return True
                if client.bad_connection_flag:  #
                    return False

        if msgType == "SUBACK":
            if client.on_subscribe:
                if client.suback_flag:
                    return True
        if msgType == "MESSAGE":
            if client.on_message:
                if client.message_received_flag:
                    return True
        if msgType == "PUBACK":
            if client.on_publish:
                if client.puback_flag:
                    return True

        if not client.running_loop:
            client.loop(.01)  # check for messages manually
        time.sleep(period)
        wcount += 1
        if wcount > wait_time:
            print("return from wait loop taken too long")
            return False
    return True


def client_loop(client, broker, port, keepalive=60, loop_function=None, loop_delay=1, run_forever=False):
    """runs a loop that will auto reconnect and subscribe to topics
    pass topics as a list of tuples. You can pass a function to be
    called at set intervals determined by the loop_delay
    """
    client.run_flag = True
    client.broker = broker
    print("running loop ")
    client.reconnect_delay_set(min_delay=0.5, max_delay=12)

    while client.run_flag:  # loop forever

        if client.bad_connection_flag:
            break
        if not client.connected_flag:
            print("Connecting to ", broker)
            if Connect(client, broker, port, keepalive, run_forever) != -1:
                if not wait_for(client, "CONNACK"):
                    client.run_flag = False  # break no connack
            else:  # connect fails
                client.run_flag = False  # break
                print("quitting loop for  broker ", broker)

        client.loop(0.002)

        if client.connected_flag and loop_function:  # function to call
            loop_function(client, loop_delay)  # call function
    time.sleep(1)
    print("disconnecting from", broker)
    if client.connected_flag:
        client.disconnect()
        client.connected_flag = False


def on_log(client, userdata, level, buf):
    print(buf)


def on_message_REALTIME(client, userdata, message):
    global currentActivity
    msg = str(message.payload.decode("utf-8"))
    print(msg)

    # save the sensor data to raw_data file
    msg = msg.split(";")
    # receive_time = int(round(time.time() * 1000))
    for line in msg:
        if not line == "":
            data = line
            # print(data)
            with open(f"{RAW_DATA_FILE}.txt", "a") as raw_data_file:
                raw_data_file.write(data)
                raw_data_file.write("\n")


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        client.connected_flag = True  # set flag
        for c in clients:
            if client == c["client"]:
                if c["sub_topic"] != "":
                    client.subscribe(c["sub_topic"])

        print("connected OK")
    else:
        print("Bad connection Returned code=", rc)
        client.loop_stop()


def on_disconnect(client, userdata, rc):
    client.connected_flag = False  # set flag
    # print("client disconnected ok")


def on_publish(client, userdata, mid):
    time.sleep(1)
    print("In on_pub callback mid= ", mid)


def pub(client, loop_delay):
    # print("in publish")
    pass


def Create_connections():
    for i in range(n_clients):
        cname = "client" + str(i)
        t = int(time.time())
        client_id = cname + str(t)  # create unique client_id
        client = mqtt.Client(client_id)  # create new instance
        clients[i]["client"] = client
        clients[i]["client_id"] = client_id
        clients[i]["cname"] = cname
        broker = clients[i]["broker"]
        port = clients[i]["port"]
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        # client.on_publish = on_publish
        client.on_message = on_message_REALTIME
        t = threading.Thread(target=client_loop, args=(client, broker, port, 60, pub))
        threads.append(t)
        t.start()


"""
******************************* CONNECTION ******************************
"""
mqtt.Client.connected_flag = False  # create flag in class
mqtt.Client.bad_connection_flag = False  # create flag in class

threads = []
print("Creating Connections ")
no_threads = threading.active_count()
print("current threads =", no_threads)
print("Publishing ")


Create_connections()

print("All clients connected ")
no_threads = threading.active_count()
print("current threads =", no_threads)
print("starting main loop")

try:
    while True:
        time.sleep(1)
        # no_threads = threading.active_count()
        # print("current threads =", no_threads)
        for c in clients:
            if not c["client"].connected_flag:
                print("broker ", c["broker"], " is disconnected")


except KeyboardInterrupt:
    print("ending")
    for c in clients:
        c["client"].run_flag = False
time.sleep(10)
