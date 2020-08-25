package com.ispl.digitalcompanion.ui.packet;

import android.os.Bundle;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.fragment.app.Fragment;
import androidx.lifecycle.Observer;
import androidx.lifecycle.ViewModelProviders;

import com.ispl.digitalcompanion.R;

public class PacketFragment extends Fragment {

    private PacketViewModel packetViewModel;

    public View onCreateView(@NonNull LayoutInflater inflater,
                             ViewGroup container, Bundle savedInstanceState) {
        packetViewModel =
                ViewModelProviders.of(this).get(PacketViewModel.class);
        View root = inflater.inflate(R.layout.fragment_packet, container, false);
        final TextView textView = root.findViewById(R.id.text_packet);
        packetViewModel.getText().observe(getViewLifecycleOwner(), new Observer<String>() {
            @Override
            public void onChanged(@Nullable String s) {
                textView.setText(s);
            }
        });
        return root;
    }
}