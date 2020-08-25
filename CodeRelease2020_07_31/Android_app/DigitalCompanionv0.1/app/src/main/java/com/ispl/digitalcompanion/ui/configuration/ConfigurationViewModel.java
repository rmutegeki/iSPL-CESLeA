package com.ispl.digitalcompanion.ui.configuration;

import android.app.Application;

import androidx.lifecycle.AndroidViewModel;
import androidx.lifecycle.LiveData;
import androidx.lifecycle.MutableLiveData;

public class ConfigurationViewModel extends AndroidViewModel {

    private MutableLiveData<String> mText;

    public ConfigurationViewModel(Application application) {
        super(application);
        mText = new MutableLiveData<>();
        mText.setValue("Loading...");
    }

    public LiveData<String> getText() {
        return mText;
    }
}