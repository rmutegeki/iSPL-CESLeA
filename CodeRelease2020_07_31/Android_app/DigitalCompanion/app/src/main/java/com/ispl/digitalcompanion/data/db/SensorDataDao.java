package com.ispl.digitalcompanion.data.db;

import androidx.room.Dao;
import androidx.room.Insert;
import androidx.room.OnConflictStrategy;
import androidx.room.Query;

import com.ispl.digitalcompanion.data.SensorData;

import java.util.List;

@Dao
public interface SensorDataDao {

    @Query("SELECT * FROM sensordata WHERE id > :reportStartTime")
    List<SensorData> getSensorsReport(long reportStartTime);

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    void insert(SensorData data);
}
