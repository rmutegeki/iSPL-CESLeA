package com.ispl.digitalcompanion.ui.home;

import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.content.SharedPreferences;
import android.os.Build;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.annotation.RequiresApi;
import androidx.databinding.DataBindingUtil;
import androidx.fragment.app.Fragment;
import androidx.lifecycle.ViewModelProvider;
import androidx.lifecycle.ViewModelProviders;
import androidx.localbroadcastmanager.content.LocalBroadcastManager;

import com.ispl.digitalcompanion.R;
import com.ispl.digitalcompanion.databinding.HomeFragmentBinding;
import com.ispl.digitalcompanion.service.MqttService;

import java.util.Locale;
import java.util.concurrent.Executor;
import java.util.concurrent.Executors;

import static java.lang.Integer.parseInt;

public class HomeFragment extends Fragment implements SharedPreferences.OnSharedPreferenceChangeListener {

    private static final String REPORT_REQUEST_TIME = "report_request_time";
    private static final String SELECTED_INTERVAL = "selected_interval";
    private static final String[] INTERVALS = {"20", "10", "30", "40", "50", "66", "100", "1000"};
    private HomeViewModel viewModel;
    private HomeFragmentBinding binding;


    private SharedPreferences sharedPreferences;

    private Executor diskExecutor;

    private long reportStartTime = 0;
//    private long lastReportedTime = 0;
    IntentFilter filter = new IntentFilter(MqttService.ACTION_LOCATION_BROADCAST);
    private BroadcastReceiver activityLocationBroadcast;

    @RequiresApi(api = Build.VERSION_CODES.O)
    public View onCreateView(@NonNull LayoutInflater inflater,
                             ViewGroup container, Bundle savedInstanceState) {
        viewModel =
                new ViewModelProvider(this).get(HomeViewModel.class);
        View root = inflater.inflate(R.layout.fragment_home, container, false);
        binding = DataBindingUtil.bind(root);

        diskExecutor = Executors.newSingleThreadExecutor();

        binding.container.setEnabled(true);
        populateIntervalSpinner();

        viewModel.getDataReport().observe(getViewLifecycleOwner(), sensorData -> binding.setData(sensorData));

        Intent reportServiceIntent =
                new Intent(getContext(), MqttService.class);

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

        //text views that are updated via the broadcast receiver
        activityLocationBroadcast = new BroadcastReceiver() {
            @Override
            public void onReceive(Context context, Intent intent) {
                Log.d("Results from Mqtt:", "" + intent.getExtras());
                binding.activityText.setText(intent.getStringExtra(MqttService.EXTRA_ACTIVITY));
                binding.locationText.setText("(" +
                        intent.getStringExtra(MqttService.EXTRA_LOCATION_X) + ", " +
                        intent.getStringExtra(MqttService.EXTRA_LOCATION_Y) + ")");
                binding.headingText.setText(intent.getStringExtra(MqttService.EXTRA_HEADING));
                binding.stepsText.setText(intent.getStringExtra(MqttService.EXTRA_STEPS));
            }
        };

        return root;
    }

    private void set_preferences(Intent service) {
        MqttService.mIP_Address = binding.ipAddress.getText().toString();
        MqttService.mPort = binding.port.getText().toString();
        if (binding.mqttStream.isChecked()) {
            MqttService.protocol = "1";
        } else {
            MqttService.protocol = "0";
        }
        MqttService.mDeviceId = binding.deviceId.getText().toString();
        MqttService.mSubTopic = binding.subTopic.getText().toString();
        MqttService.mPubTopic = binding.pubTopic.getText().toString();
        MqttService.windowLength = (float) 2.56;
        MqttService.windowSize = (int) (1000 * MqttService.windowLength) / parseInt(INTERVALS[sharedPreferences.getInt(SELECTED_INTERVAL, 0)]);
        // Buffer size is half of the window size
        MqttService.bufferSize = (int) (1000 * MqttService.windowLength) / (parseInt(INTERVALS[sharedPreferences.getInt(SELECTED_INTERVAL, 0)]) * 2);
        Log.d("Shared", "" + MqttService.bufferSize);
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
        LocalBroadcastManager.getInstance(getActivity()).registerReceiver(activityLocationBroadcast, filter);
    }

    @Override
    public void onStop() {
        super.onStop();
        sharedPreferences.unregisterOnSharedPreferenceChangeListener(this);
        LocalBroadcastManager.getInstance(getActivity()).unregisterReceiver(activityLocationBroadcast);
    }

    @Override
    public void onSharedPreferenceChanged(SharedPreferences sharedPreferences, String s) {
        if (s.equals(MqttService.REQUESTING_REPORT)) {
            binding.setStarted(sharedPreferences.getBoolean(s, false));
        }
    }
}