package com.ispl.digitalcompanion.ui.home;

import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.os.Build;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;

import androidx.annotation.NonNull;
import androidx.annotation.RequiresApi;
import androidx.databinding.DataBindingUtil;
import androidx.fragment.app.Fragment;
import androidx.lifecycle.ViewModelProviders;

import com.ispl.digitalcompanion.R;
import com.ispl.digitalcompanion.data.db.AppDatabase;
import com.ispl.digitalcompanion.data.db.SensorDataDao;
import com.ispl.digitalcompanion.databinding.HomeFragmentBinding;
import com.ispl.digitalcompanion.service.MqttService;

import java.util.concurrent.Executor;
import java.util.concurrent.Executors;

public class HomeFragment extends Fragment implements SharedPreferences.OnSharedPreferenceChangeListener {

    private HomeViewModel viewModel;

    private static final String REPORT_REQUEST_TIME = "report_request_time";
    private static final String SELECTED_INTERVAL = "selected_interval";

    private static final String[] INTERVALS = {"20", "10", "30", "40", "50", "66", "100", "1000"};
    private HomeFragmentBinding binding;


    private SharedPreferences sharedPreferences;

    private Executor diskExecutor;

    private long reportStartTime = 0;
//    private long lastReportedTime = 0;

    @RequiresApi(api = Build.VERSION_CODES.O)
    public View onCreateView(@NonNull LayoutInflater inflater,
                             ViewGroup container, Bundle savedInstanceState) {
        viewModel =
                ViewModelProviders.of(this).get(HomeViewModel.class);
        View root = inflater.inflate(R.layout.fragment_home, container, false);
        binding = DataBindingUtil.bind(root);

        diskExecutor = Executors.newSingleThreadExecutor();

        binding.container.setEnabled(true);
        populateIntervalSpinner();

        viewModel.getDataReport().observe(getViewLifecycleOwner(), sensorData -> binding.setData(sensorData));

        Intent reportServiceIntent =
                new Intent(getContext(), MqttService.class);

        SensorDataDao sensorDataDao = AppDatabase.getDatabase(this.getContext()).sensorDataDao();

        sharedPreferences = this.getActivity().getSharedPreferences("pref", Context.MODE_PRIVATE);

        boolean reportRequested = sharedPreferences
                .getBoolean(MqttService.REQUESTING_REPORT, false);
        binding.setStarted(reportRequested);

        if (reportRequested) {
            reportStartTime = sharedPreferences
                    .getLong(REPORT_REQUEST_TIME, System.currentTimeMillis());
        }

        binding.startButton.setOnClickListener(view -> {
            set_preferences(reportServiceIntent);
            reportStartTime = System.currentTimeMillis();
            getActivity().startForegroundService(reportServiceIntent);
            sharedPreferences.edit().putLong(REPORT_REQUEST_TIME, reportStartTime).apply();
        });

        binding.stopButton.setOnClickListener((View view) -> {
            getActivity().stopService(reportServiceIntent);
            diskExecutor.execute(() -> {
                sharedPreferences.edit().putBoolean(MqttService.REQUESTING_REPORT, false).apply();
            });
        });

        return root;
    }

    private void set_preferences(Intent service) {
        service.putExtra("ip_address", binding.ipAddress.getText().toString());
        service.putExtra("port", binding.port.getText().toString());
        binding.mqttStream.setClickable(false);
        if (binding.mqttStream.isChecked()){
            service.putExtra("protocol", "1");
        } else {
            service.putExtra("protocol", "0");
        }
        service.putExtra("id", binding.deviceId.getText().toString());
        service.putExtra("sub_topic", binding.subTopic.getText().toString());
        service.putExtra("pub_topic", binding.pubTopic.getText().toString());
    }

    private void populateIntervalSpinner() {
        ArrayAdapter<String> adapter = new ArrayAdapter<>(this.getContext(),
                android.R.layout.simple_spinner_dropdown_item, INTERVALS);
        binding.reportInterval.setAdapter(adapter);
        binding.reportInterval.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            @Override
            public void onItemSelected(AdapterView<?> adapterView, View view, int i, long l) {
                viewModel.setReportInterval(Long.parseLong(INTERVALS[i]));
                sharedPreferences.edit().putInt(SELECTED_INTERVAL, i).apply();
            }

            @Override
            public void onNothingSelected(AdapterView<?> adapterView) {
                binding.reportInterval.setSelection(sharedPreferences.getInt(SELECTED_INTERVAL, 0));
            }
        });
    }

    @Override
    public void onStart() {
        super.onStart();
        sharedPreferences.registerOnSharedPreferenceChangeListener(this);
    }

    @Override
    public void onStop() {
        sharedPreferences.unregisterOnSharedPreferenceChangeListener(this);
        super.onStop();
    }

    @Override
    public void onSharedPreferenceChanged(SharedPreferences sharedPreferences, String s) {
        if (s.equals(MqttService.REQUESTING_REPORT)) {
            binding.setStarted(sharedPreferences.getBoolean(s, false));
        }
    }
}