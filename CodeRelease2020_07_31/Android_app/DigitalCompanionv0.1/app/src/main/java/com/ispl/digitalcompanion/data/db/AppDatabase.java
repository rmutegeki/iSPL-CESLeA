package com.ispl.digitalcompanion.data.db;

import androidx.room.Database;
import androidx.room.Room;
import androidx.room.RoomDatabase;

import android.content.Context;

import com.ispl.digitalcompanion.data.SensorData;

@Database(entities = {SensorData.class}, version = 1, exportSchema = false)
public abstract class AppDatabase extends RoomDatabase {

    private static AppDatabase INSTANCE;

    public static AppDatabase getDatabase(final Context context) {
        if (INSTANCE == null) {
            synchronized (AppDatabase.class) {
                INSTANCE = Room.databaseBuilder(context.getApplicationContext(), AppDatabase.class,
                        "report.db").build();
            }
        }
        return INSTANCE;
    }

    public abstract SensorDataDao sensorDataDao();
}
