package com.ispl.digitalcompanion.ui.home;

import android.app.Application;

import androidx.lifecycle.AndroidViewModel;
import androidx.lifecycle.LiveData;
import androidx.lifecycle.MutableLiveData;
import androidx.lifecycle.Transformations;

import com.ispl.digitalcompanion.data.SensorData;
import com.ispl.digitalcompanion.data.SensorLiveData;

public class HomeViewModel extends AndroidViewModel {

    private final LiveData<SensorData> dataReport;
    private MutableLiveData<Long> reportInterval = new MutableLiveData<>();

    public HomeViewModel(Application application) {
        super(application);

        dataReport = Transformations.switchMap(reportInterval, input ->
                SensorLiveData.getInstance(application).reportInterval(input));
    }

    LiveData<SensorData> getDataReport() {
        return dataReport;
    }

    void setReportInterval(long reportInterval) {
        this.reportInterval.setValue(reportInterval);
    }
}