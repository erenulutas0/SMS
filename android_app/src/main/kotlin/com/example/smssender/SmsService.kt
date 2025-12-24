package com.example.smssender

import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Context
import android.content.Intent
import android.net.wifi.WifiManager
import android.os.Build
import android.os.IBinder
import android.os.PowerManager
import androidx.core.app.NotificationCompat
import fi.iki.elonen.NanoHTTPD
import org.json.JSONArray
import org.json.JSONObject
import java.io.IOException
import java.util.*

class SmsService : Service() {

    private var server: SmsServer? = null
    private val PORT = 8080
    private val CHANNEL_ID = "SmsServiceChannel"
    
    private var wakeLock: PowerManager.WakeLock? = null
    private var wifiLock: WifiManager.WifiLock? = null

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
        
        // Acquire WakeLock (Keep CPU running)
        val powerManager = getSystemService(Context.POWER_SERVICE) as PowerManager
        wakeLock = powerManager.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "SmsSender::Wakelock")
        wakeLock?.acquire()

        // Acquire WifiLock (Keep WiFi active for incoming connections)
        val wifiManager = applicationContext.getSystemService(Context.WIFI_SERVICE) as WifiManager
        // WIFI_MODE_FULL_HIGH_PERF is recommended for low latency apps, though deprecated in some versions it's best for servers
        wifiLock = wifiManager.createWifiLock(WifiManager.WIFI_MODE_FULL_HIGH_PERF, "SmsSender::WifiLock")
        wifiLock?.acquire()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        try {
            val notification = createNotification()
            // We need to call startForeground immediately
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                try {
                     startForeground(1, notification, android.content.pm.ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC)
                } catch (e: Exception) {
                     // Fallback if specific type fails (e.g. on mixed OS versions or if permission missing in manifest logic)
                     startForeground(1, notification)
                }
            } else {
                startForeground(1, notification)
            }
            
            startServer()
        } catch (e: Exception) {
            e.printStackTrace()
        }

        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? {
        return null
    }

    override fun onDestroy() {
        super.onDestroy()
        server?.stop()
        
        try {
            if (wakeLock?.isHeld == true) wakeLock?.release()
            if (wifiLock?.isHeld == true) wifiLock?.release()
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val serviceChannel = NotificationChannel(
                CHANNEL_ID,
                "SMS Service Channel",
                NotificationManager.IMPORTANCE_DEFAULT
            )
            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(serviceChannel)
        }
    }

    private fun createNotification(): Notification {
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("SMS Servisi Aktif")
            .setContentText("Wifi ve CPU uyanık tutuluyor. IP'den bağlanılabilir.")
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .build()
    }

    private fun startServer() {
        try {
            if (server == null || server?.isAlive == false) {
                server = SmsServer()
                server?.start()
            }
        } catch (e: IOException) {
            e.printStackTrace()
        }
    }

    private inner class SmsServer : NanoHTTPD(PORT) {
        override fun serve(session: IHTTPSession): Response {
            // Keep permissions check internal or trust 
            // the system since we are running as an app with permissions
            
            if (session.uri == "/sms") {
                return try {
                    val json = readSmsToJson()
                    newFixedLengthResponse(Response.Status.OK, "application/json", json)
                } catch (e: Exception) {
                    newFixedLengthResponse(Response.Status.INTERNAL_ERROR, "text/plain", "Error: ${e.message}")
                }
            }
            if (session.uri == "/") {
                  return newFixedLengthResponse("<html><body><h1>SMS Server Calisiyor</h1></body></html>")
            }
            return newFixedLengthResponse(Response.Status.NOT_FOUND, "text/plain", "Not Found")
        }
    }

    private fun readSmsToJson(): String {
        val jsonArray = JSONArray()
        val uri = android.net.Uri.parse("content://sms/inbox")
        // Sorted by date desc
        val cursor = contentResolver.query(uri, arrayOf("address", "body", "date"), null, null, "date DESC LIMIT 50")

        cursor?.use {
            val idxAddress = it.getColumnIndex("address")
            val idxBody = it.getColumnIndex("body")
            val idxDate = it.getColumnIndex("date")

            while (it.moveToNext()) {
                val jsonObj = JSONObject()
                jsonObj.put("address", if (idxAddress >= 0) it.getString(idxAddress) else "Unknown")
                jsonObj.put("body", if (idxBody >= 0) it.getString(idxBody) else "")
                jsonObj.put("date", if (idxDate >= 0) it.getLong(idxDate) else 0L)
                jsonArray.put(jsonObj)
            }
        }
        return jsonArray.toString()
    }
}
