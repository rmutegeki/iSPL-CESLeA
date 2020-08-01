package com.ispl.digitalcompanion;

import java.io.IOException;
import java.io.UnsupportedEncodingException;

import static com.ispl.digitalcompanion.service.MqttService.mPacket;
import static com.ispl.digitalcompanion.service.MqttService.mSocket;

public class UDPThread {

    public UDPThread() {

    }

    public static void send(String data) {
        byte bytes[];


        try {
            bytes = data.getBytes("UTF-8");

            if(mPacket != null && mSocket != null){
            	mPacket.setData(bytes);
				mPacket.setLength(bytes.length);


				mSocket.send(mPacket);
            }
        } catch (UnsupportedEncodingException | NullPointerException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
            //Log.e("Error", "SendBlock");
            return;
        } catch (IOException e) {
            // TODO Auto-generated catch block
            e.printStackTrace();
            //Log.e("Error", "SendBlock");
            return;
        }

    }
}