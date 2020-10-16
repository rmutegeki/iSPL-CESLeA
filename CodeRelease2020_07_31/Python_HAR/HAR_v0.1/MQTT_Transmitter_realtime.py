import paho.mqtt.client as mqtt
import time, logging
import datetime
import os
import fnmatch


QOS = 1

sensor_id = 1

sub_topic = f"0"
pub_topic = f"{sensor_id}/2"
client_id = f"sub_{sensor_id}"

broker = ""
port = 1882 + sensor_id

print("sub_topic: ", sub_topic, "client_id", client_id)

CLEAN_SESSION = True
logging.basicConfig(level=logging.INFO)  # error logging

dt = datetime.datetime.now()
# RAW_DATA_FILE = f"data/raw_data_{dt.date()}_{dt.hour}-{dt.minute}-{dt.second}_sensor"
ACTION_RESULT_FILE = 'data/realtime/prediction_result.txt'
LOCATION_RESULT_FILE = 'data/realtime/localization_result.txt'


# use DEBUG,INFO,WARNING
def on_subscribe(client, userdata, mid, granted_qos):  # create function for callback
    # print("subscribed with qos",granted_qos, "\n")
    # time.sleep(0.1)
    logging.info("sub acknowledge message id=" + str(mid))
    pass


def on_disconnect(client, userdata, rc=0):
    logging.info("DisConnected result code " + str(rc))


def on_connect(client, userdata, flags, rc):
    logging.info("Connected flags" + str(flags) + "result code " + str(rc))


def on_message(client, userdata, message):
    msg = str(message.payload.decode("utf-8"))

    receive_time = int(round(time.time() * 1000))
    print(receive_time, ", ", msg)
    msg = msg.split(";")


def on_publish(client, userdata, mid):
    logging.info("message published " + str(mid))


client = mqtt.Client(client_id, False)  # create client object

# client.on_subscribe = on_subscribe  # assign function to callback
client.on_disconnect = on_disconnect  # assign function to callback
client.on_connect = on_connect  # assign function to callback
client.on_message = on_message
client.connect(broker, port)  # establish connection
time.sleep(1)
client.loop_start()
# client.subscribe(sub_topic)
client.publish(pub_topic)
count = 1

does_file_exist = False     # Whether the prediction result file exists or not

while not does_file_exist:
    try:
        with open(ACTION_RESULT_FILE, "r") as _result_file:
            does_file_exist = True
    except (FileNotFoundError, IOError, KeyboardInterrupt) as e:
        print("Error :", e)
        time.sleep(0.2)

while True:
    with open(ACTION_RESULT_FILE, "r") as _action_file, \
            open(LOCATION_RESULT_FILE, "r") as _location_file:
        while True:
            time.sleep(0.2)
            print("sending")
            line_action = _action_file.readline().strip()
            line_location = _location_file.readline().strip()
            if line_action:
                msg = f"{sensor_id};0;{line_action}"
                print("Activity: ", line_action)
                client.publish(pub_topic, msg)

            if line_location:
                msg = f"{sensor_id};1;{line_location}"
                client.publish(pub_topic, msg)


# while True:  # runs forever break with CTRL+C
#     # print("publishing on topic ",topic1)
#     # msg = "message " + str(count) + " from client B"
#     # client.publish(topic1, msg)
#     # count += 1
#
#     time.sleep(0.001)
client.disconnect()

client.loop_stop()
