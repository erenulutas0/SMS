package com.example.smssender

import android.Manifest
import android.annotation.SuppressLint
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.ConnectivityManager
import android.net.Uri
import android.net.wifi.WifiManager
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.os.Looper
import android.os.PowerManager
import android.provider.Settings
import android.widget.CompoundButton
import android.widget.Switch
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import java.net.Inet4Address

class MainActivity : AppCompatActivity() {

    private val PERMISSION_CODE = 101
    
    private lateinit var ipAddressText: TextView
    private lateinit var statusLabels: TextView
    private lateinit var serviceSwitch: Switch
    private lateinit var permissionSwitch: Switch
    private lateinit var backgroundSwitch: Switch

    private val handler = Handler(Looper.getMainLooper())
    private val updateRunnable = object : Runnable {
        override fun run() {
            refreshStatus()
            handler.postDelayed(this, 5000) // Refresh every 5s
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Init Views
        ipAddressText = findViewById(R.id.ipAddressText)
        statusLabels = findViewById(R.id.statusLabels)
        serviceSwitch = findViewById(R.id.serviceSwitch)
        permissionSwitch = findViewById(R.id.permissionSwitch)
        backgroundSwitch = findViewById(R.id.backgroundSwitch)

        // Listeners for Switches
        serviceSwitch.setOnCheckedChangeListener { _, isChecked ->
            if (isChecked) {
                startSmsService()
            } else {
                stopSmsService()
            }
        }

        permissionSwitch.setOnCheckedChangeListener { _, isChecked ->
            if (isChecked && !hasSmsPermission()) {
                requestSmsPermissions()
            }
            // If user unchecks, we can't really "revoke" permissions easily programmatically,
            // but we can update UI. We'll basically keep it checked if permission exists.
        }

        backgroundSwitch.setOnCheckedChangeListener { _, isChecked ->
            if (isChecked) {
                requestBatteryOptimization()
            }
            // Cannot programmatically un-ignore easily, usually user has to go to settings.
        }
        
        // Initial Check
        refreshStatus()
    }

    override fun onResume() {
        super.onResume()
        refreshStatus()
        handler.post(updateRunnable)
    }

    override fun onPause() {
        super.onPause()
        handler.removeCallbacks(updateRunnable)
    }

    private fun refreshStatus() {
        // 1. Check Permissions
        val hasPerms = hasSmsPermission()
        permissionSwitch.isChecked = hasPerms
        permissionSwitch.isEnabled = !hasPerms // Disable if already granted (can't revoke here)

        // 2. Check Battery Optimization
        val isIgnoringBattery = isIgnoringBatteryOptimizations()
        backgroundSwitch.isChecked = isIgnoringBattery
        backgroundSwitch.isEnabled = !isIgnoringBattery

        // 3. Service Status & IP
        // Getting IP
        val ip = getIpAddress()
        if (ip != "0.0.0.0" && ip != "Bilinmiyor") {
            ipAddressText.text = ip
            serviceSwitch.isEnabled = true
        } else {
            ipAddressText.text = "No Wifi"
            serviceSwitch.isChecked = false
            serviceSwitch.isEnabled = false
            statusLabels.text = "Please connect to Wifi first."
        }
        
        // We assume if IP is valid, user can try to toggle service.
        // We don't have an easy way to check if "SmsService" is actually running 
        // without binding or using ActivityManager (which is limited in new Android).
        // For now, we trust the switch state or user interaction.
        // But better: If we auto-start, we should set switch to true.
        // Let's assume if permissions are good, we WANT it running.
        
        if (hasPerms && isIgnoringBattery && serviceSwitch.isEnabled && !serviceSwitch.isChecked) {
             // Optional: Auto-start if everything is green?
             // User wanted manual control, but also "work in background".
             // Let's leave it manual but initialize correctly.
        }
    }

    private fun requestSmsPermissions() {
        val permissions = mutableListOf<String>()
        permissions.add(Manifest.permission.READ_SMS)
        permissions.add(Manifest.permission.RECEIVE_SMS)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            permissions.add(Manifest.permission.POST_NOTIFICATIONS)
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
             permissions.add(Manifest.permission.FOREGROUND_SERVICE)
        }
        ActivityCompat.requestPermissions(this, permissions.toTypedArray(), PERMISSION_CODE)
    }

    private fun hasSmsPermission(): Boolean {
         return ContextCompat.checkSelfPermission(this, Manifest.permission.READ_SMS) == PackageManager.PERMISSION_GRANTED &&
                ContextCompat.checkSelfPermission(this, Manifest.permission.RECEIVE_SMS) == PackageManager.PERMISSION_GRANTED
    }

    private fun isIgnoringBatteryOptimizations(): Boolean {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            val pm = getSystemService(POWER_SERVICE) as PowerManager
            return pm.isIgnoringBatteryOptimizations(packageName)
        }
        return true
    }

    @SuppressLint("BatteryLife")
    private fun requestBatteryOptimization() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            val pm = getSystemService(POWER_SERVICE) as PowerManager
            if (!pm.isIgnoringBatteryOptimizations(packageName)) {
                val intent = Intent()
                intent.action = Settings.ACTION_REQUEST_IGNORE_BATTERY_OPTIMIZATIONS
                intent.data = Uri.parse("package:$packageName")
                startActivity(intent)
            }
        }
    }

    private fun startSmsService() {
        try {
            val intent = Intent(this, SmsService::class.java)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                startForegroundService(intent)
            } else {
                startService(intent)
            }
            statusLabels.text = "Service Started. Running in background."
            serviceSwitch.isChecked = true
        } catch (e: Exception) {
            e.printStackTrace()
            statusLabels.text = "Error starting service: ${e.localizedMessage}"
            serviceSwitch.isChecked = false
        }
    }

    private fun stopSmsService() {
        val intent = Intent(this, SmsService::class.java)
        stopService(intent)
        statusLabels.text = "Service Stopped."
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == PERMISSION_CODE) {
             refreshStatus()
        }
    }

    private fun getIpAddress(): String {
        try {
            val connectivityManager = getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
            val linkProperties = connectivityManager.getLinkProperties(connectivityManager.activeNetwork)
            if (linkProperties != null) {
                for (linkAddress in linkProperties.linkAddresses) {
                    val address = linkAddress.address
                    if (address is Inet4Address && !address.isLoopbackAddress) {
                       return address.hostAddress
                    }
                }
            }
            val wifiManager = applicationContext.getSystemService(Context.WIFI_SERVICE) as WifiManager
            val ip = wifiManager.connectionInfo.ipAddress
            if (ip == 0) return "0.0.0.0"
            return String.format(
                "%d.%d.%d.%d",
                ip and 0xff, ip shr 8 and 0xff, ip shr 16 and 0xff, ip shr 24 and 0xff
            )
        } catch (e: Exception) {
            return "Bilinmiyor"
        }
    }
}
