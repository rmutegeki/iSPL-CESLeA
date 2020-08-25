package com.ispl.digitalcompanion.data;

import androidx.room.Embedded;
import androidx.room.Entity;
import androidx.room.PrimaryKey;

import java.time.LocalDate;

@Entity
public class SensorData {

    @PrimaryKey
    private long id;

    @Embedded(prefix = "accelerometer-")
    private Position accelerometer;

    @Embedded(prefix = "gyroscope-")
    private Position gyroscope;

    @Embedded(prefix = "magnetic-field-")
    private Position magneticField;

    @Embedded(prefix = "linear-accelerometer-")
    private Position linearAccelerometer;

//    @Embedded(prefix = "activity")
//    private String activity;
//
//    @Embedded(prefix = "location-")
//    private Location location;

    public SensorData() {

    }

    public SensorData(Position accelerometer, Position gyroscope,
                      Position magneticField, Position linearAcc) {
        this.accelerometer = accelerometer;
        this.gyroscope = gyroscope;
        this.magneticField = magneticField;
        this.linearAccelerometer = linearAcc;
    }

    public long getId() {
        return id;
    }

    public void setId(long id) {
        this.id = id;
    }

    public Position getAccelerometer() {
        return accelerometer;
    }

    public void setAccelerometer(Position accelerometer) {
        this.accelerometer = accelerometer;
    }

    public Position getGyroscope() {
        return gyroscope;
    }

    public void setGyroscope(Position gyroscope) {
        this.gyroscope = gyroscope;
    }

    public Position getMagneticField() {
        return magneticField;
    }

    public void setMagneticField(Position magneticField) {
        this.magneticField = magneticField;
    }

    public Position getLinearAccelerometer() {
        return linearAccelerometer;
    }

    public void setLinearAccelerometer(Position linearAcc) {
        this.linearAccelerometer = linearAcc;
    }

//    public String getActivity() {
//        return activity;
//    }
//
//    public void setActivity(String activity) {
//        this.activity = activity;
//    }
//
//    public void setActivity(Location location) {
//        this.location = location;
//    }
//
//    public Location getLocation() {
//        return location;
//    }

    public static class Position {

        private float x;
        private float y;
        private float z;

        public Position(float x, float y, float z) {
            this.x = x;
            this.y = y;
            this.z = z;
        }

        public float getX() {
            return x;
        }

        public void setX(float x) {
            this.x = x;
        }

        public float getY() {
            return y;
        }

        public void setY(float y) {
            this.y = y;
        }

        public float getZ() {
            return z;
        }

        public void setZ(float z) {
            this.z = z;
        }
    }

    public static class Location {
        private float x;
        private float y;

        public Location(float x, float y) {
            this.x = x;
            this.y = y;
        }

        public float getX() {
            return x;
        }

        public void setX(float x) {
            this.x = x;
        }

        public float getY() {
            return y;
        }

        public void setY(float y) {
            this.y = y;
        }

    }
}
