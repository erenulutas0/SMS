# 📱 Android Uygulaması Kurulum Kılavuzu

Telefonunuzdaki SMS'leri bilgisayarınıza aktarmak için Android uygulamasını kurmanız gerekiyor.

## 🚀 Hızlı Kurulum (Android Studio ile)

### 1. Android Studio'yu İndirin ve Kurun
- [Android Studio](https://developer.android.com/studio) indirin
- Kurulumu tamamlayın

### 2. Projeyi Açın
1. Android Studio'yu açın
2. "Open an Existing Project" seçin
3. `android_app` klasörünü seçin
4. Proje yüklenecek (ilk seferinde biraz zaman alabilir)

### 3. IP Adresini Güncelleyin
**ÖNEMLİ:** Bilgisayarınızın IP adresini bulun:

**Windows'ta:**
```bash
ipconfig
```
"IPv4 Address" satırındaki değeri kullanın (örn: `192.168.1.102`)

**Şu dosyalardaki IP adresini güncelleyin:**
- `android_app/SmsReceiver.kt` (satır 21)
- `android_app/MainActivity.kt` (satır 30)

```kotlin
private val API_URL = "http://BURAYA_IP_ADRESINIZI_YAZIN:5000/api/sms"
```

### 4. Uygulamayı Derleyin ve Yükleyin
1. Telefonunuzu USB ile bilgisayara bağlayın
2. Telefonunuzda "USB Debugging" özelliğini açın:
   - Ayarlar → Telefon Hakkında → Yapı Numarası'na 7 kez tıklayın
   - Ayarlar → Geliştirici Seçenekleri → USB Hata Ayıklama'yı açın
3. Android Studio'da yeşil "Run" butonuna tıklayın (▶️)
4. Telefonunuzu seçin ve uygulama yüklenecek

### 5. İzinleri Verin
1. Uygulama açıldığında "SMS Okuma İzni Ver" butonuna tıklayın
2. İzinleri verin
3. "Tüm SMS'leri Gönder" butonuna tıklayarak mevcut SMS'leri gönderebilirsiniz

## 📲 Alternatif: APK Oluşturma

Android Studio olmadan APK oluşturmak için:

1. Android Studio'da: **Build → Build Bundle(s) / APK(s) → Build APK(s)**
2. Oluşan APK dosyasını telefonunuza aktarın
3. Telefonunuzda "Bilinmeyen Kaynaklardan Yükleme" iznini verin
4. APK'yı yükleyin

## 🔧 Sorun Giderme

### SMS'ler gönderilmiyor
1. **IP Adresi Kontrolü:**
   - Bilgisayarınızın IP adresini kontrol edin: `ipconfig`
   - Android uygulamasındaki IP adresinin aynı olduğundan emin olun
   - Telefon ve bilgisayar aynı Wi-Fi ağında olmalı

2. **İzinler:**
   - Uygulama ayarlarından SMS okuma izninin verildiğini kontrol edin
   - Android 6.0+ için runtime izinleri gereklidir

3. **Backend Kontrolü:**
   - Backend'in çalıştığından emin olun: `http://localhost:5000`
   - Windows Firewall'da port 5000'in açık olduğundan emin olun

4. **Log Kontrolü:**
   - Android Studio'da Logcat sekmesini açın
   - "SmsReceiver" filtresi ile logları kontrol edin
   - Hata mesajlarını kontrol edin

### Yeni SMS'ler gelmiyor
- Android 8.0+ için BroadcastReceiver'ın doğru kayıtlı olduğundan emin olun
- Uygulamanın arka planda çalışmasına izin verin
- Pil optimizasyonlarını kapatın (Ayarlar → Uygulamalar → SMS Bildirici → Pil Optimizasyonu)

## 🎯 Test Etme

1. Backend'in çalıştığından emin olun
2. Android uygulamasını açın
3. İzinleri verin
4. "Tüm SMS'leri Gönder" butonuna tıklayın
5. Bilgisayarınızda `http://localhost:5000` adresini açın
6. SMS'lerin göründüğünü kontrol edin

## 📝 Notlar

- **Otomatik Gönderim:** Yeni gelen SMS'ler otomatik olarak gönderilir
- **Manuel Gönderim:** "Tüm SMS'leri Gönder" butonu ile mevcut SMS'leri gönderebilirsiniz
- **Ağ:** Telefon ve bilgisayar aynı Wi-Fi ağında olmalıdır
- **Güvenlik:** Production kullanımı için authentication ekleyin

