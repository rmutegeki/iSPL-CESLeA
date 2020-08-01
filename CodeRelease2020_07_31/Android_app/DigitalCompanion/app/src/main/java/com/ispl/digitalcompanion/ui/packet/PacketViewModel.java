package com.ispl.digitalcompanion.ui.packet;

import android.app.Application;

import androidx.lifecycle.AndroidViewModel;
import androidx.lifecycle.LiveData;
import androidx.lifecycle.MutableLiveData;

public class PacketViewModel extends AndroidViewModel {

    private MutableLiveData<String> mText;

    public PacketViewModel(Application application) {
        super(application);
        mText = new MutableLiveData<>();
        mText.setValue("Loading...");
    }

    public LiveData<String> getText() {
        return mText;
    }
}