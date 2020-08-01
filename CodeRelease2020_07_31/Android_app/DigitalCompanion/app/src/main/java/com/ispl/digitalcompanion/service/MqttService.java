package com.ispl.digitalcompanion.service;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import androidx.lifecycle.LifecycleService;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.net.ConnectivityManager;
import android.net.Network;
import android.net.NetworkInfo;
import android.os.Build;
import android.util.Log;

import com.ispl.digitalcompanion.MainActivity;
import com.ispl.digitalcompanion.R;
import com.ispl.digitalcompanion.UDPThread;
import com.ispl.digitalcompanion.data.SensorLiveData;
import com.ispl.digitalcompanion.data.db.AppDatabase;
import com.ispl.digitalcompanion.data.db.SensorDataDao;

import org.eclipse.paho.android.service.MqttAndroidClient;
import org.eclipse.paho.client.mqttv3.IMqttActionListener;
import org.eclipse.paho.client.mqttv3.IMqttDeliveryToken;
import org.eclipse.paho.client.mqttv3.IMqttToken;
import org.eclipse.paho.client.mqttv3.MqttAsyncClient;
import org.eclipse.paho.client.mqttv3.MqttCallback;
import org.eclipse.paho.client.mqttv3.MqttClient;
import org.eclipse.paho.client.mqttv3.MqttException;
import org.eclipse.paho.client.mqttv3.MqttMessage;

import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.SocketException;
import java.net.UnknownHostException;
import java.util.concurrent.Executor;
import java.util.concurrent.Executors;

import static java.lang.Integer.parseInt;

public class MqttService extends LifecycleService {
    // A good convention is to declare a TAG constant
    private static final String TAG = "MqttService";

    public static final String REQUESTING_REPORT = "requesting_report";

    private static final int NOTIFICATION_ID = 1002;
    private static final String CHANNEL_ID = "channel_01";

    private SensorDataDao sensorDataDao;

    private Executor diskExecutor;
    private Executor mqttExecutor;
    private Executor udpExecutor;

    private BroadcastReceiver broadcastReceiver;

    private String mIP_Address = "155.230.15.110";
    private String mPort = "5500";

    private String mDeviceId = "1";
    private String mPubTopic = "device/1";
    private String mSubTopic = "all";

    public static DatagramSocket mSocket = null;
    public static DatagramPacket mPacket = null;

    private String protocol = "0";

    // Generate a random client id
    String clientId = MqttClient.generateClientId();
    private int qos = 0;

    public MqttService(){

    }

    @Override
    public void onCreate() {
        super.onCreate();

        diskExecutor = Executors.newSingleThreadExecutor();
        udpExecutor = Executors.newSingleThreadExecutor();
        mqttExecutor = Executors.newSingleThreadExecutor();
        start_UDP_Stream();

        // Instantiate our client and connect to it
        // create an instance of an Android MQTT client that binds to the Paho Android Service
        MqttAndroidClient client =
                new MqttAndroidClient(getApplicationContext(), "tcp://" + mIP_Address + ":" + mPort , clientId);
        client.setCallback(new MqttCallback() {
            @Override
            public void connectionLost(Throwable cause) {
                System.out.println("Connection was lost!");

            }

            @Override
            public void messageArrived(String topic, MqttMessage message) throws Exception {
                System.out.println("Message Arrived!: " + topic + ": " + new String(message.getPayload()));

            }

            @Override
            public void deliveryComplete(IMqttDeliveryToken token) {
                System.out.println("Delivery Complete!");
            }
        });

        this.getApplication().getSharedPreferences("pref", Context.MODE_PRIVATE)
                .edit()
                .putBoolean(REQUESTING_REPORT, true)
                .apply();

        sensorDataDao = AppDatabase.getDatabase(this).sensorDataDao();
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
                    sensorData.getLinearAccelerometer().getZ();

            diskExecutor.execute(() -> sensorDataDao.insert(sensorData));
            if (protocol.equals("0")) {
                udpExecutor.execute(() -> UDPThread.send(data));
            } else {
                mqttExecutor.execute(() -> {
//                    try {
//                        IMqttToken token = client.connect();
//                        token.setActionCallback(new IMqttActionListener() {
//                            @Override
//                            public void onSuccess(IMqttToken asyncActionToken) {
//                                MqttMessage message = new MqttMessage(data.getBytes());
//                                message.setQos(qos);
//                                try {
//                                    client.publish(mPubTopic, message);
//                                } catch (MqttException e) {
//                                    e.printStackTrace();
//                                }
//                                Log.d(TAG, "Published:");
//                            }
//
//                            @Override
//                            public void onFailure(IMqttToken asyncActionToken, Throwable exception) {
//                                Log.d(TAG, "Failed to publish");
//                            }
//                        });
//                    } catch (MqttException e) {
//                        e.printStackTrace();
//                    }
                });
            }
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
        this.mIP_Address = intent.getStringExtra("ip_address");
        this.mPort = intent.getStringExtra("port");
        this.protocol = intent.getStringExtra("protocol");
        this.mDeviceId = intent.getStringExtra("id");
        this.mSubTopic = intent.getStringExtra("sub_topic");
        this.mPubTopic = intent.getStringExtra("pub_topic");
        return START_STICKY;
    }

    @Override
    public void onDestroy() {
        stop_UDP_Stream();

        this.getApplicationContext().getSharedPreferences("pref",MODE_PRIVATE)
                .edit()
                .putBoolean(REQUESTING_REPORT, false)
                .apply();

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
}
