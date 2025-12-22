package com.example.smssender

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.provider.Telephony
import android.util.Log
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject
import java.util.concurrent.TimeUnit

class SmsReceiver : BroadcastReceiver() {
    
    // ÖNEMLİ: Bilgisayarınızın IP adresini buraya yazın (ipconfig ile bulabilirsiniz)
    private val API_URL = "http://192.168.1.100:5000/api/sms"
    
    private val client = OkHttpClient.Builder()
        .connectTimeout(10, TimeUnit.SECONDS)
        .readTimeout(10, TimeUnit.SECONDS)
        .build()
    
    override fun onReceive(context: Context, intent: Intent) {
        if (Telephony.Sms.Intents.SMS_RECEIVED_ACTION == intent.action) {
            val messages = Telephony.Sms.Intents.getMessagesFromIntent(intent)
            
            for (message in messages) {
                val sender = message.displayOriginatingAddress
                val body = message.messageBody
                
                Log.d("SmsReceiver", "SMS alındı: $sender - $body")
                
                // API'ye gönder
                sendSmsToApi(sender, body)
            }
        }
    }
    
    private fun sendSmsToApi(sender: String, message: String) {
        CoroutineScope(Dispatchers.IO).launch {
            try {
                val json = JSONObject().apply {
                    put("sender", sender)
                    put("message", message)
                }
                
                val requestBody = json.toString()
                    .toRequestBody("application/json".toMediaType())
                
                val request = Request.Builder()
                    .url(API_URL)
                    .post(requestBody)
                    .build()
                
                val response = client.newCall(request).execute()
                
                if (response.isSuccessful) {
                    Log.d("SmsReceiver", "SMS başarıyla gönderildi")
                } else {
                    Log.e("SmsReceiver", "Hata: ${response.code} - ${response.message}")
                }
                
            } catch (e: Exception) {
                Log.e("SmsReceiver", "API gönderim hatası: ${e.message}")
            }
        }
    }
}

