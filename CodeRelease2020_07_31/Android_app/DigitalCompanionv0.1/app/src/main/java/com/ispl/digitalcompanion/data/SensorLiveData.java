package com.ispl.digitalcompanion.data;

import android.annotation.SuppressLint;

import androidx.lifecycle.LiveData;

import android.content.Context;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.os.CountDownTimer;

public class SensorLiveData extends LiveData<SensorData> implements
        SensorEventListener {

    private static SensorLiveData instance;

    private SensorManager sensorManager;

    private Sensor accelerometerSensor;
    private Sensor gyroscopeSensor;
    private Sensor magneticFieldSensor;
    private Sensor linearAccelerationSensor;

    private CountDownTimer timer;

    private boolean isDelivered;

    private SensorData sensorData;

    private SensorLiveData(Context context) {
        sensorManager = (SensorManager) context.getSystemService(Context.SENSOR_SERVICE);
        accelerometerSensor = sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER);
        gyroscopeSensor = sensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE);
        magneticFieldSensor = sensorManager.getDefaultSensor(Sensor.TYPE_MAGNETIC_FIELD);
        linearAccelerationSensor = sensorManager.getDefaultSensor(Sensor.TYPE_LINEAR_ACCELERATION);

        initTimer(1000);

        sensorData = new SensorData();
    }

    public static SensorLiveData getInstance(Context context) {
        if (instance == null) {
            instance = new SensorLiveData(context.getApplicationContext());
        }
        return instance;
    }

    public SensorLiveData reportInterval(long interval) {
        timer.cancel();
        initTimer(interval);
        timer.start();
        return this;
    }

    private void initTimer(long interval) {
        timer = new CountDownTimer(3600000, interval) {
            @Override
            public void onTick(long l) {
                isDelivered = false;
            }

            @Override
            public void onFinish() {

            }
        };
    }

    @SuppressLint("MissingPermission")
    @Override
    protected void onActive() {
        super.onActive();
        sensorManager.registerListener(this, accelerometerSensor,
                SensorManager.SENSOR_DELAY_GAME);
        sensorManager.registerListener(this, gyroscopeSensor,
                SensorManager.SENSOR_DELAY_GAME);
        sensorManager.registerListener(this, magneticFieldSensor,
                SensorManager.SENSOR_DELAY_GAME);
        sensorManager.registerListener(this, linearAccelerationSensor,
                SensorManager.SENSOR_DELAY_GAME);
        timer.start();
    }

    @SuppressLint("MissingPermission")
    @Override
    protected void onInactive() {
        super.onInactive();
        sensorManager.unregisterListener(this);
        timer.cancel();
    }

    @Override
    public void onSensorChanged(SensorEvent sensorEvent) {
        float[] values = sensorEvent.values;

        SensorData.Position data = new SensorData.Position(values[0], values[1], values[2]);

        switch (sensorEvent.sensor.getType()) {

            case Sensor.TYPE_ACCELEROMETER:
                sensorData.setAccelerometer(data);
                break;

            case Sensor.TYPE_GYROSCOPE:
                sensorData.setGyroscope(data);
                break;

            case Sensor.TYPE_MAGNETIC_FIELD:
                sensorData.setMagneticField(data);
                break;

            case Sensor.TYPE_LINEAR_ACCELERATION:
                sensorData.setLinearAccelerometer(data);
                break;

            default:
                break;
        }
        if (!isDelivered) {
            sensorData.setId(System.currentTimeMillis());
            setValue(sensorData);
            isDelivered = true;
        }
    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int i) {

    }
}
