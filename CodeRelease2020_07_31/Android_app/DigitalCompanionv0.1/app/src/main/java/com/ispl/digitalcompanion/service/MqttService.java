package com.ispl.digitalcompanion.service;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.net.ConnectivityManager;
import android.net.Network;
import android.net.NetworkInfo;
import android.os.Build;
import android.os.PowerManager;
import android.os.PowerManager.WakeLock;
import android.util.Log;

import androidx.lifecycle.LifecycleService;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;

import com.hivemq.client.mqtt.datatypes.MqttQos;
import com.hivemq.client.mqtt.mqtt3.Mqtt3AsyncClient;
import com.ispl.digitalcompanion.MainActivity;
import com.ispl.digitalcompanion.R;
import com.ispl.digitalcompanion.data.SensorData;
import com.ispl.digitalcompanion.data.SensorLiveData;

import java.io.IOException;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketException;
import java.net.UnknownHostException;
import java.nio.charset.StandardCharsets;
import java.util.Collections;
import java.util.LinkedList;
import java.util.List;
import java.util.Locale;
import java.util.UUID;
import java.util.concurrent.Executor;
import java.util.concurrent.Executors;
import java.util.stream.Collectors;

import static java.lang.Float.parseFloat;
import static java.lang.Integer.parseInt;

public class MqttService extends LifecycleService {
    public static final String REQUESTING_REPORT = "requesting_report";
    // A good convention is to declare a TAG constant
    private static final String TAG = "MqttService";
    private static final int NOTIFICATION_ID = 1002;
    private static final String CHANNEL_ID = "channel_01";
    //Mqtt Client Config
    public Mqtt3AsyncClient client;
    // To keep the CPU on so we can send our data
    PowerManager powerManager;
    public static String mIP_Address;
    public static String mPort;
    public static String mDeviceId;
    public static String mPubTopic;
    public static String mSubTopic;
    public static String protocol;
    public static float windowLength;
    public static int windowSize;
    public static int bufferSize;
    WakeLock wakeLock;
    // Generate a random client id
    String clientId = UUID.randomUUID().toString();
    private Executor mqttExecutor;
    private Executor udpExecutor;
    private Executor dataExecutor;
    private BroadcastReceiver broadcastReceiver;
    private int qos = 1;
    private SensorData msensorData;
    //Data object for sensor data
    private List sensorDataBuffer;
    private boolean firstRound = true;
    private int windowEnd = bufferSize;
    private DatagramSocket mSocket = null;
    private DatagramPacket mPacket = null;
    public static final String
            ACTION_LOCATION_BROADCAST = MqttService.class.getName() + "ActivityLocationBroadcast",
            EXTRA_ACTIVITY = "extra_activity",
            EXTRA_LOCATION_X = "extra_location_x",
            EXTRA_LOCATION_Y = "extra_location_y",
            EXTRA_HEADING = "extra_heading",
            EXTRA_STEPS = "extra_steps";
    private String locx = "-";
    private String locy = "-";
    private String activity = "IDLE";
    private String heading = "-";
    private String steps = "-";

    @Override
    public void onCreate() {
        super.onCreate();
        // Initializing our data array list
        sensorDataBuffer = Collections.synchronizedList(new LinkedList<String>());

        //Let's provide the default activity, location, heading and steps
        sendBroadcastMessage(activity, locx, locy, heading, steps);

        // Check if the IP and other parameters are set defaults
        if (mIP_Address.isEmpty() || mIP_Address == null) {
            Log.d("Parameters:", "IP address is empty:" + mIP_Address);
            mIP_Address = "155.230.15.110";
        }
        if (mPort.isEmpty() || mIP_Address == null) {
            Log.d("Parameters:", "Port is empty:" + mPort);
            mPort = "1883";
        }
        if (mDeviceId.isEmpty() || mDeviceId == null) {
            Log.d("Parameters:", "Device ID is empty:" + mDeviceId);
            mDeviceId = "1";
        }
        if (mSubTopic.isEmpty() || mSubTopic == null) {
            Log.d("Parameters:", "IP address is empty:" + mSubTopic);
            mSubTopic = "all";
        }
        if (mPubTopic.isEmpty() || mPubTopic == null) {
            Log.d("Parameters:", "IP address is empty:" + mPubTopic);
            mPubTopic = "device/1";
        }
        if (protocol.isEmpty() || protocol == null) {
            Log.d("Parameters:", "No protocol has been selected:" + protocol);
            protocol = "0";
        }

        udpExecutor = Executors.newSingleThreadExecutor();
        mqttExecutor = Executors.newSingleThreadExecutor();
        dataExecutor = Executors.newSingleThreadExecutor();

        //Let's execute our data processing function
        dataExecutor.execute(this::process_data);

        if (protocol.equals("0")) {
            if(start_UDP_Stream()){
                Log.d("UDP Stream", "Started");
            }
        }

        //Start Mqtt Service
        client = com.hivemq.client.mqtt.MqttClient.builder()
                .useMqttVersion3()
                .identifier(clientId)
                .serverHost(mIP_Address)
                .serverPort(parseInt(mPort))
                .buildAsync();
        connect();
        subscribe(mSubTopic);

        this.getApplication().getSharedPreferences("pref", Context.MODE_PRIVATE)
                .edit()
                .putBoolean(REQUESTING_REPORT, true)
                .apply();

        SensorLiveData.getInstance(this).observe(this, sensorData -> {
            if (sensorData == null) {
                return;
            }
            String data = sensorData.getId() + "," +
                    mDeviceId + "," +
                    sensorData.getAccelerometer().getX() + "," +
                    sensorData.getAccelerometer().getY() + "," +
                    sensorData.getAccelerometer().getZ() + "," +
                    sensorData.getGyroscope().getX() + "," +
                    sensorData.getGyroscope().getY() + "," +
                    sensorData.getGyroscope().getZ() + "," +
                    sensorData.getMagneticField().getX() + "," +
                    sensorData.getMagneticField().getY() + "," +
                    sensorData.getMagneticField().getZ() + "," +
                    sensorData.getLinearAccelerometer().getX() + "," +
                    sensorData.getLinearAccelerometer().getY() + "," +
                    sensorData.getLinearAccelerometer().getZ() + "," +
                    sensorData.getBarometer() + ";";
            sensorDataBuffer.add(data);

        });

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationManager notificationManager = (NotificationManager)
                    getSystemService(NOTIFICATION_SERVICE);
            NotificationChannel notificationChannel = new NotificationChannel(CHANNEL_ID,
                    getString(R.string.app_name),
                    NotificationManager.IMPORTANCE_DEFAULT);
            notificationManager.createNotificationChannel(notificationChannel);
        }

        startForeground(NOTIFICATION_ID, makeNotification());
    }

    @Override
    public int onStartCommand(Intent intent, int flags, int startId) {
        super.onStartCommand(intent, flags, startId);
        //Let's acquire a wake lock
        powerManager = (PowerManager) getSystemService(POWER_SERVICE);
        wakeLock = powerManager.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "DigitalCompanion::MyWakelockTag");
        wakeLock.acquire(60 * 60 * 1000L /*60 minutes*/);

        return START_STICKY;
    }

    @Override
    public void onDestroy() {
        stop_UDP_Stream();
        client.unsubscribeWith().topicFilter(mSubTopic).send();

        this.getApplicationContext().getSharedPreferences("pref", MODE_PRIVATE)
                .edit()
                .putBoolean(REQUESTING_REPORT, false)
                .apply();
        //Let's also release the wake lock to save battery
        wakeLock.release();

        super.onDestroy();
    }

    private Notification makeNotification() {
        Intent notificationIntent = new Intent(this, MainActivity.class);
        PendingIntent pendingIntent =
                PendingIntent.getActivity(this, 0, notificationIntent, 0);

        Notification.Builder notificationBuilder = new Notification.Builder(this)
                .setSmallIcon(R.mipmap.ic_launcher)
                .setContentTitle(getString(R.string.notification_title))
                .setOngoing(true)
                .setContentIntent(pendingIntent);
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            notificationBuilder.setChannelId(CHANNEL_ID);
        }
        return notificationBuilder.build();
    }

    private boolean isNetworkAvailable() {
        ConnectivityManager connMgr = (ConnectivityManager) getSystemService(Context.CONNECTIVITY_SERVICE);
        boolean isWifiConn = false;
        boolean isMobileConn = false;
        for (Network network : connMgr.getAllNetworks()) {
            NetworkInfo networkInfo = connMgr.getNetworkInfo(network);
            if (networkInfo.getType() == ConnectivityManager.TYPE_WIFI) {
                isWifiConn |= networkInfo.isConnected();
            }
            if (networkInfo.getType() == ConnectivityManager.TYPE_MOBILE) {
                isMobileConn |= networkInfo.isConnected();
            }
        }
        return isWifiConn || isMobileConn;
    }

    private boolean start_UDP_Stream() {
        if (!isNetworkAvailable()) {
            Log.d("UDP", "No network");
            return false;
        }

        InetAddress client_adress = null;
        try {
            client_adress = InetAddress.getByName(mIP_Address);
        } catch (UnknownHostException e) {
            Log.d("UDP", "Invalid Address");
            return false;
        }
        try {
            mSocket = new DatagramSocket();
            mSocket.setReuseAddress(true);
        } catch (SocketException e) {
            mSocket = null;
            Log.d("UDP", "Network Error");
            return false;
        }

        byte[] buf = new byte[256];

        int port;
        try {
            port = parseInt(mPort);
            mPacket = new DatagramPacket(buf, buf.length, client_adress, port);
        } catch (Exception e) {
            mSocket.close();
            mSocket = null;
            Log.d("UDP", "No network");
            return false;
        }

        return true;
    }

    private void stop_UDP_Stream() {
        if (mSocket != null)
            mSocket.close();
        mSocket = null;
        mPacket = null;
    }

    public void subscribe(String topic) {

        client.subscribeWith()
                .topicFilter(topic)
                .qos(MqttQos.AT_MOST_ONCE)
                .callback(publish -> {
                    // Process the received message
                    String message = new String(publish.getPayloadAsBytes(), StandardCharsets.UTF_8);
                    Log.d("MQTT", "Received a message: " + message);
                    // Message of the form device_id;activity;location_x,location_y
                    String[] values = message.split(";", 0);
                    try {
                        //Check if the message is meant for this device>>>
                        if (values.length > 0 && values[0].equals(mDeviceId)) {
                            // deviceId = values[0]; we don't use this one anywhere
                            if (values.length > 1) {
                                if (values[1].equals("0") && values.length > 2) {
                                    activity = values[2];
                                    Log.d("Received", "Activity: " + activity);
                                } else if (values[1].equals("1") && values.length > 2) {
                                    // Structure: locx,locy,heading,number_steps
                                    String[] location_data = values[2].split(",", 4);
                                    locx = String.format(Locale.ENGLISH, "%.2f", parseFloat(location_data[0]));
                                    locy = String.format(Locale.ENGLISH, "%.2f", parseFloat(location_data[1]));
                                    heading = String.format(Locale.ENGLISH, "%.2f", parseFloat(location_data[2]));
                                    steps = location_data[3];

                                    Log.d("Received", "Location : (" + locx + ", " + locy + ")");
                                    Log.d("Received", "Heading: " + heading);
                                    Log.d("Received", "Steps: " + steps);
                                }

                                sendBroadcastMessage(activity, locx, locy, heading, steps);
                            } else {
                                Log.d("Mqtt_Sub", "No activity or location specific data provided" + values);
                            }
                        } else {
                            Log.d("Mqtt_Sub", "No device specific data provided" + values);
                        }
                    } catch (ArrayIndexOutOfBoundsException ex) {
                        ex.printStackTrace();
                        sendBroadcastMessage(activity, locx, locy, heading, steps);
                    }
                })
                .send()
                .whenComplete((subAck, throwable) -> {
                    if (throwable != null) {
                        // Handle failure to subscribe
                        Log.d("MQTT", " Failed to subscribe");

                    } else {
                        // Handle successful subscription, e.g. logging or incrementing a metric
                        Log.d("MQTT", "Subscribed: " + mSubTopic);
                    }
                });

    }

    public void publish(String topic, String message) {
        client.publishWith()
                .topic(topic)
                .payload(message.getBytes())
                .send()
                .whenComplete((publish, throwable) -> {
                    if (throwable != null) {
                        // handle failure to publish
                        Log.d("MQTT", " Failed to send anything");
                        throwable.printStackTrace();

                    } else {
                        // handle successful publish, e.g. logging or incrementing a metric
//                        Log.d("Published", "" + new String(publish.getPayloadAsBytes(), StandardCharsets.UTF_8));

                    }
                });

    }

    public void connect() {
        client.connectWith()
                .send()
                .whenComplete((connAck, throwable) -> {
                    if (throwable != null) {
                        //handle failure
                        Log.d("MQTT", " nope" + throwable);
                        throwable.printStackTrace();
                    } else {
                        //setup subscribes or start publishing
                        Log.d("MQTT", " client connected:" + mIP_Address + ":" + mPort);
                    }
                });
    }

    private void process_data() {
        String sample = "";
        while (true) {
            try {
                if (sensorDataBuffer.size() < bufferSize) {
                    //Do nothing when the data is not enough
                    continue;
                }
                //if (firstRound && sensorDataBuffer.size() >= bufferSize || sensorDataBuffer.size() == windowEnd + bufferSize) {
                if (sensorDataBuffer.size() >= bufferSize) {
                    // We've gotten enough data for this buffer
                    Log.d("Buffer", "At least " + bufferSize + " values of data have been obtained. Data Count: " + sensorDataBuffer.size());
                    firstRound = false;
                    windowEnd = sensorDataBuffer.size();
                    // we are only interested in the current buffer's elements

                    try {
                        //Log.d("Before", "" + sensorDataBuffer.size());
                        sample = (String) sensorDataBuffer.subList(0, bufferSize).stream().map(Object::toString).collect(Collectors.joining(""));
                        //Log.d("Still Before", "" + sensorDataBuffer.size());
                        sensorDataBuffer.subList(0, bufferSize).clear();
                        //Log.d("After", "" + sensorDataBuffer.size());
                    } catch (Exception ex) {
                        Log.d("Data Issue", "Issue with sample: " + sample);
                        ex.printStackTrace();
                        continue;
                    }

                    String finalSample = sample;
                    //Log.d("data", finalSample);
                    if (protocol.equals("0")) {
                        udpExecutor.execute(() ->
                                send(finalSample)
                        );
                    } else {
                        mqttExecutor.execute(() ->
                                publish(mPubTopic, finalSample)
                        );
                    }
                }
            } catch (Exception ex) {
                System.out.println("An Exception occured");
                ex.printStackTrace();
            }
        }
    }

    private void sendBroadcastMessage(String _activity, String location_x, String location_y, String _heading, String _steps) {
        Log.d("Brodcast", "Brodcast Initiated: " + _activity + ", (" + location_x + "," + location_y + ")");
        if (_activity != null && location_x != null && location_y != null && _heading != null && _steps != null) {
            Intent intent = new Intent(ACTION_LOCATION_BROADCAST);
            intent.putExtra(EXTRA_ACTIVITY, _activity);
            intent.putExtra(EXTRA_LOCATION_X, location_x);
            intent.putExtra(EXTRA_LOCATION_Y, location_y);
            intent.putExtra(EXTRA_HEADING, _heading);
            intent.putExtra(EXTRA_STEPS, _steps);
            LocalBroadcastManager.getInstance(this).sendBroadcast(intent);
        }
    }

    private void send(String data) {
        byte[] bytes;
        try {
            bytes = data.getBytes("UTF-8");
            if (mPacket != null && mSocket != null) {
                mPacket.setData(bytes);
                mPacket.setLength(bytes.length);
                mSocket.send(mPacket);
            }
        } catch (NullPointerException | IOException e) {
            e.printStackTrace();
        }
    }
}
