package com.ispl.digitalcompanion;

import androidx.databinding.BindingAdapter;
import android.widget.Spinner;

public class BindingAdapters {

    @BindingAdapter("spinnerEnabled")
    public static void enabled(Spinner spinner, boolean enabled) {
        spinner.setEnabled(enabled);
    }
}
