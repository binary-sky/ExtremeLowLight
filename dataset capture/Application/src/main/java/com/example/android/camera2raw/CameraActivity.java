/*
 * Copyright 2015 The Android Open Source Project
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *       http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.example.android.camera2raw;

import android.app.Activity;
import android.content.BroadcastReceiver;
import android.content.Context;
import android.content.Intent;
import android.content.IntentFilter;
import android.database.ContentObserver;
import android.media.AudioFocusRequest;
import android.media.AudioManager;
import android.os.Bundle;
import android.os.Handler;
import android.util.Log;
import android.view.KeyEvent;
import android.widget.Toast;

/**
 * Activity displaying a fragment that implements RAW photo captures.
 */
public class CameraActivity extends Activity {

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_camera);
        takeKeyEvents(true);
        AudioManager am = (AudioManager) this.getSystemService(Context.AUDIO_SERVICE);
        int result= am.requestAudioFocus(null,AudioManager.STREAM_MUSIC,AudioManager.AUDIOFOCUS_GAIN);
        setVolumeControlStream(AudioManager.STREAM_MUSIC);

        SettingsContentObserver sco =new SettingsContentObserver(this,null);
        getApplicationContext().getContentResolver().registerContentObserver(
                android.provider.Settings.System.CONTENT_URI, true,sco);
        if (null == savedInstanceState) {
            getFragmentManager().beginTransaction()
                    .replace(R.id.container, Camera2RawFragment.newInstance())
                    .commit();

        }
    }
    // Broadcast Receiver for Music play.
    private BroadcastReceiver musicPlay = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            // TODO Auto-generated method stub
            Log.v("gaurav", "Music play started");
        }
    };

    // Broadcast Receiver for Music pause.
    private BroadcastReceiver musicPause = new BroadcastReceiver() {
        @Override
        public void onReceive(Context context, Intent intent) {
            // TODO Auto-generated method stub
            Log.v("gaurav", "Music paused");
        }
    };

}
class SettingsContentObserver extends ContentObserver {
    static boolean IFBLEPRESSED=false;

    private AudioManager audioManager;

    public SettingsContentObserver(Context context, Handler handler) {
        super(handler);
        audioManager = (AudioManager) context.getSystemService(Context.AUDIO_SERVICE);
    }

    @Override
    public boolean deliverSelfNotifications() {
        return false;
    }

    int last_vol = 0 ;
    @Override
    public void onChange(boolean selfChange) {
        int currentVolume = audioManager.getStreamVolume(AudioManager.STREAM_MUSIC);

        if(last_vol!=0&&last_vol!=currentVolume){
            if(IFBLEPRESSED==false) IFBLEPRESSED=true;
        }

        last_vol = currentVolume;

        Log.d("505030475", "Volume now " + currentVolume);
    }
}

