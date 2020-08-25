package com.ispl.labelingtool;

import android.content.Context;
import android.os.Build;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Toast;

import androidx.annotation.RequiresApi;
import androidx.appcompat.app.AppCompatActivity;

import com.hivemq.client.mqtt.datatypes.MqttQos;
import com.hivemq.client.mqtt.mqtt3.Mqtt3AsyncClient;

import java.nio.charset.StandardCharsets;
import java.util.UUID;

import static java.lang.Integer.parseInt;

public class MainActivity extends AppCompatActivity {
    // A good convention is to declare a TAG constant
    private static final String TAG = "MainActivity";

    private String mTopic = "label";
    public boolean connected = false;
    //Default user activity
    public String activity  = "0";

    private Mqtt3AsyncClient client;
    // Generate a random client id
    String clientId = UUID.randomUUID().toString();

    @RequiresApi(api = Build.VERSION_CODES.N)
    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        EditText ipAddress =  findViewById(R.id.ip_address);
        EditText port = findViewById(R.id.port);
        EditText deviceId = findViewById(R.id.device_id);
        EditText pubTopic = findViewById(R.id.pub_topic);
        EditText subTopic = findViewById(R.id.sub_topic);
        Button walking = findViewById(R.id.walking_button);
        Button standing = findViewById(R.id.standing_button);
        Button sitting = findViewById(R.id.sitting_button);
        Button lying = findViewById(R.id.lying_button);
        Button running = findViewById(R.id.running_button);
        Button idle = findViewById(R.id.idle_button);
        final Button connect = findViewById(R.id.connect_button);

        connect.setOnClickListener(view -> {
            //Start Mqtt Service
            client = com.hivemq.client.mqtt.MqttClient.builder()
                    .useMqttVersion3()
                    .identifier(clientId)
                    .serverHost(ipAddress.getText().toString())
                    .serverPort(parseInt(port.getText().toString()))
                    .buildAsync();
            connect();
            subscribe(subTopic.getText().toString());
            Toast.makeText(getApplicationContext(), "Client Connected and subscribed to: " + subTopic.getText().toString(), Toast.LENGTH_SHORT).show();

            walking.setOnClickListener(view1 -> {
                activity = "0";
                publish(pubTopic.getText().toString(), activity);
                Toast.makeText(getApplicationContext(), "WALKING: " + activity, Toast.LENGTH_SHORT).show();

            });

            standing.setOnClickListener(view2 -> {
                activity = "1";
                publish(pubTopic.getText().toString(), activity);
                Toast.makeText(getApplicationContext(), "STANDING: " + activity, Toast.LENGTH_SHORT).show();
            });

            sitting.setOnClickListener(view3 -> {
                activity = "2";
                publish(pubTopic.getText().toString(), activity);
                Toast.makeText(getApplicationContext(), "SITTING: " + activity, Toast.LENGTH_SHORT).show();
            });

            lying.setOnClickListener(view1 -> {
                activity = "3";
                publish(pubTopic.getText().toString(), activity);
                Toast.makeText(getApplicationContext(), "LYING: " + activity, Toast.LENGTH_SHORT).show();
            });

            running.setOnClickListener(view1 -> {
                activity = "4";
                publish(pubTopic.getText().toString(), activity);
                Toast.makeText(getApplicationContext(), "RUNNING: " + activity, Toast.LENGTH_SHORT).show();
            });

            idle.setOnClickListener(view1 -> {
                activity = "5";
                publish(pubTopic.getText().toString(), activity);
                Toast.makeText(getApplicationContext(), "IDLE: " + activity, Toast.LENGTH_SHORT).show();
            });
        });
    }

    @RequiresApi(api = Build.VERSION_CODES.N)
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
                    //if the message is meant for this device>>>

                })
                .send()
                .whenComplete((subAck, throwable) -> {
                    if (throwable != null) {
                        // Handle failure to subscribe
                        Log.d("MQTT", " Failed to subscribe");

                    } else {
                        // Handle successful subscription, e.g. logging or incrementing a metric
                        Log.d("MQTT", "Subscribed: " + topic);
                    }
                });

    }

    @RequiresApi(api = Build.VERSION_CODES.N)
    public void publish(String topic, String message) {
        client.publishWith()
                .topic(topic)
                .payload(message.getBytes())
                .send()
                .whenComplete((publish, throwable) -> {
                    if (throwable != null) {
                        // handle failure to publish
                        Log.d("MQTT", " Failed to send anything");
                        Toast.makeText(getApplicationContext(), "Failed to send data", Toast.LENGTH_SHORT).show();
                        throwable.printStackTrace();

                    } else {
                        // handle successful publish, e.g. logging or incrementing a metric
                        Log.d("Published", "" + new String(publish.getPayloadAsBytes(), StandardCharsets.UTF_8));
                    }
                });

    }

    @RequiresApi(api = Build.VERSION_CODES.N)
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
                        Log.d("MQTT", " client connected" );
                        connected = true;
                    }
                });
    }
}