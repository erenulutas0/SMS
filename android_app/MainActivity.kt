package com.example.smssender

import android.Manifest
import android.content.ContentResolver
import android.content.pm.PackageManager
import android.database.Cursor
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.Telephony
import android.widget.Button
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject
import java.util.concurrent.TimeUnit

class MainActivity : AppCompatActivity() {
    
    private val SMS_PERMISSION_CODE = 100
    // ÖNEMLİ: Bilgisayarınızın IP adresini buraya yazın
    private val API_URL = "http://192.168.1.100:5000/api/sms"
    
    private val client = OkHttpClient.Builder()
        .connectTimeout(30, TimeUnit.SECONDS)
        .readTimeout(30, TimeUnit.SECONDS)
        .build()
    
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        
        val statusText = findViewById<TextView>(R.id.statusText)
        val requestPermissionButton = findViewById<Button>(R.id.requestPermissionButton)
        val syncAllButton = findViewById<Button>(R.id.syncAllButton)
        
        requestPermissionButton.setOnClickListener {
            requestSmsPermission()
        }
        
        syncAllButton.setOnClickListener {
            if (hasSmsPermission()) {
                syncAllSms()
            } else {
                statusText.text = "⚠️ Önce SMS okuma izni verin!"
            }
        }
        
        checkPermissions()
    }
    
    private fun checkPermissions() {
        val statusText = findViewById<TextView>(R.id.statusText)
        
        if (hasSmsPermission()) {
            statusText.text = "✅ İzinler verildi. SMS'ler otomatik olarak gönderilecek."
            statusText.setTextColor(ContextCompat.getColor(this, android.R.color.holo_green_dark))
        } else {
            statusText.text = "⚠️ SMS okuma izni gerekli. Lütfen izin verin."
            statusText.setTextColor(ContextCompat.getColor(this, android.R.color.holo_red_dark))
        }
    }
    
    private fun hasSmsPermission(): Boolean {
        return if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            ContextCompat.checkSelfPermission(
                this,
                Manifest.permission.RECEIVE_SMS
            ) == PackageManager.PERMISSION_GRANTED &&
            ContextCompat.checkSelfPermission(
                this,
                Manifest.permission.READ_SMS
            ) == PackageManager.PERMISSION_GRANTED
        } else {
            true
        }
    }
    
    private fun requestSmsPermission() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            ActivityCompat.requestPermissions(
                this,
                arrayOf(
                    Manifest.permission.RECEIVE_SMS,
                    Manifest.permission.READ_SMS
                ),
                SMS_PERMISSION_CODE
            )
        }
    }
    
    override fun onRequestPermissionsResult(
        requestCode: Int,
        permissions: Array<out String>,
        grantResults: IntArray
    ) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        
        if (requestCode == SMS_PERMISSION_CODE) {
            checkPermissions()
        }
    }
    
    private fun syncAllSms() {
        val statusText = findViewById<TextView>(R.id.statusText)
        statusText.text = "📤 Tüm SMS'ler gönderiliyor..."
        
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val allSms = readAllSms()
                
                if (allSms.isEmpty()) {
                    CoroutineScope(Dispatchers.Main).launch {
                        statusText.text = "ℹ️ Telefonda SMS bulunamadı."
                    }
                    return@launch
                }
                
                // Toplu gönderim için endpoint kullan
                sendBulkSms(allSms)
                
                CoroutineScope(Dispatchers.Main).launch {
                    statusText.text = "✅ ${allSms.size} SMS başarıyla gönderildi!"
                }
                
            } catch (e: Exception) {
                CoroutineScope(Dispatchers.Main).launch {
                    statusText.text = "❌ Hata: ${e.message}"
                }
            }
        }
    }
    
    private fun readAllSms(): List<Pair<String, String>> {
        val smsList = mutableListOf<Pair<String, String>>()
        
        if (!hasSmsPermission()) {
            return smsList
        }
        
        val contentResolver: ContentResolver = contentResolver
        val uri: Uri = Uri.parse("content://sms/inbox")
        
        val cursor: Cursor? = contentResolver.query(
            uri,
            arrayOf("address", "body", "date"),
            null,
            null,
            "date DESC" // En yeni önce
        )
        
        cursor?.use {
            val addressIndex = it.getColumnIndex("address")
            val bodyIndex = it.getColumnIndex("body")
            
            while (it.moveToNext()) {
                val address = if (addressIndex >= 0) it.getString(addressIndex) else "Bilinmeyen"
                val body = if (bodyIndex >= 0) it.getString(bodyIndex) else ""
                
                if (body.isNotEmpty()) {
                    smsList.add(Pair(address, body))
                }
            }
        }
        
        return smsList
    }
    
    private fun sendBulkSms(smsList: List<Pair<String, String>>) {
        try {
            val jsonArray = JSONArray()
            
            for ((sender, message) in smsList) {
                val json = JSONObject().apply {
                    put("sender", sender)
                    put("message", message)
                }
                jsonArray.put(json)
            }
            
            val requestBody = jsonArray.toString()
                .toRequestBody("application/json".toMediaType())
            
            val request = Request.Builder()
                .url("$API_URL/bulk")  // Toplu gönderim endpoint'i
                .post(requestBody)
                .build()
            
            val response = client.newCall(request).execute()
            
            if (!response.isSuccessful) {
                throw Exception("API hatası: ${response.code}")
            }
            
        } catch (e: Exception) {
            throw Exception("Gönderim hatası: ${e.message}")
        }
    }
}

