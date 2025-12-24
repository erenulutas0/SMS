# SMS Senkronizasyon (SMS Sync)

Bu proje, Android cihazınızdaki SMS'leri masaüstü bilgisayarınızla (Windows) senkronize eden, bildirimleri anlık olarak masaüstünde gösteren ve modern bir arayüz sunan kapsamlı bir uygulamadır.

## 🚀 Özellikler

*   **Çift Bağlantı Modu:**
    *   **USB (ADB):** Kablolu bağlantı ile hızlı ve kararlı senkronizasyon.
    *   **WiFi:** Aynı ağ üzerindeki cihazlar için kablosuz bağlantı.
*   **Masaüstü Bildirimleri:** Yeni mesaj geldiğinde Windows sağ alt köşesinde (Toast) bildirim gösterir.
*   **Özel Sesli Uyarı:** Mesaj geldiğinde özel zil sesi (`ringtone.mp3`) çalar (PowerShell entegrasyonu ile MP3 desteği).
*   **Modern Arayüz:** React ile hazırlanmış şık, karanlık mod destekli kullanıcı arayüzü.
*   **Arka Plan Servisi:** Uygulama penceresi kapatılsa bile sistem tepsisinde (System Tray) çalışmaya devam eder.
*   **Android Uygulaması:** Arka planda kesintisiz çalışabilen, pil optimizasyonlarını yöneten native Kotlin uygulaması.
*   **Ayarlar:** Ses ve masaüstü bildirimlerini açıp kapatma imkanı.
*   **Engelleme:** İstenmeyen göndericileri (spam) engelleme özelliği.

## 🛠️ Kurulum ve Çalıştırma

### 1. Gereksinimler
*   **Windows 10/11**
*   **Python 3.10+** (Geliştirme için)
*   **Node.js** (Frontend geliştirme için)
*   **Android Telefon** (Geliştirici seçenekleri ve USB Hata Ayıklama açık olmalıdır)

### 2. Uygulamayı Derleme (Build)
Uygulamayı tek bir `.exe` haline getirmek için hazır bir script bulunmaktadır:

```bat
build_v3.bat
```

Bu işlem:
1.  Frontend'i (`React`) derler (`npm run build`).
2.  Backend'i (`Flask`) ve gerekli tüm dosyaları `PyInstaller` ile paketler.
3.  Çıktıyı `SMSSync_Final_vX` klasörüne taşır.

### 3. Kullanım

1.  **Android Uygulaması:**
    *   Projedeki `android_app` klasörünü Android Studio ile açın ve telefonunuza yükleyin.
    *   Uygulamayı açın ve gerekli tüm izinleri (SMS okuma, Bildirim, Pil Optimizasyonu) verin.
    *   "Servisi Başlat" butonuna basın.

2.  **Masaüstü Uygulaması:**
    *   Derlenen `.exe` dosyasını çalıştırın.
    *   **USB Modu:** Telefonu USB ile bağlayın ve ADB'nin tanıdığından emin olun.
    *   **WiFi Modu:** Telefondaki IP adresini masaüstü uygulamasındaki "Cihaz Bağla" menüsüne girin.

3.  **Ayarlar:**
    *   Ayarlar menüsünden "Sesli Bildirim" ve "Masaüstü Bildirimi" seçeneklerini yönetebilirsiniz.
    *   "Test Bildirimi" butonu ile sistemin çalışıp çalışmadığını kontrol edebilirsiniz.

## 📂 Proje Yapısı

*   `android_app/`: Kotlin ile yazılmış Android istemcisi.
*   `backend/`: Python (Flask) tabanlı sunucu ve masaüstü mantığı.
    *   `app.py`: Ana uygulama döngüsü, API ve Tray yönetimi.
    *   `wifi_syncer.py` & `adb_manager.py`: Bağlantı yöneticileri.
*   `frontend/`: React tabanlı modern arayüz.
*   `build_v3.bat`: Windows için otomatik derleme scripti.

## ⚠️ Güvenlik ve Notlar

*   `config.json`, `blocked_senders.json` ve `sms_storage.json` dosyaları kullanıcının yerel verilerini tutar ve `.gitignore` ile repoya gönderilmesi engellenmiştir.
*   Uygulama yerel ağ (Localhost/LAN) üzerinde çalışır, dış internete veri göndermez.

## 🤝 Katkıda Bulunma

Pull request göndermekten çekinmeyin! Hataları `Issues` sekmesinden bildirebilirsiniz.

---
**Geliştirici:** Eren Ulutaş
