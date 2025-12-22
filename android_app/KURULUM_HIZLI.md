# ⚡ Hızlı Kurulum (5 Dakika)

## 1. IP Adresini Bul
Bilgisayarınızda terminal açın:
```bash
ipconfig
```
**IPv4 Address** değerini not edin (örn: `192.168.1.102`)

## 2. Android Studio'da IP'yi Güncelle

**Dosya 1:** `SmsReceiver.kt` (satır 21)
```kotlin
private val API_URL = "http://192.168.1.102:5000/api/sms"  // IP'nizi yazın
```

**Dosya 2:** `MainActivity.kt` (satır 30)
```kotlin
private val API_URL = "http://192.168.1.102:5000/api/sms"  // IP'nizi yazın
```

## 3. Uygulamayı Çalıştır
1. Telefonu USB ile bağla
2. Android Studio'da ▶️ (Run) butonuna tıkla
3. Telefonu seç ve yükle

## 4. İzinleri Ver
1. Uygulama açıldığında "SMS Okuma İzni Ver" butonuna tıkla
2. İzinleri ver
3. "Tüm SMS'leri Gönder" butonuna tıkla

## 5. Kontrol Et
Bilgisayarında `http://localhost:5000` aç - SMS'ler görünmeli! 🎉

---

**Sorun mu var?** `ANDROID_KURULUM.md` dosyasına bakın.

