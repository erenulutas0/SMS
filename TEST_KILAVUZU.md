# 🧪 Test Kılavuzu

## Adım Adım Test

### 1. Backend'i Başlatın

```bash
python backend/app.py
```

Veya Windows'ta:
```bash
start_backend.bat
```

Backend başladığında şunu görmelisiniz:
```
SMS Backend API başlatılıyor...
API: http://localhost:5000
 * Running on http://0.0.0.0:5000
```

### 2. Bağlantıyı Test Edin

Yeni bir terminal açın ve:

```bash
python test_connection.py
```

Başarılı olursa:
```
✅ API çalışıyor!
✅ Test SMS başarıyla gönderildi!
✅ X SMS bulundu
🎉 Tüm testler başarılı!
```

### 3. Desktop Bildirim Uygulamasını Başlatın

Yeni bir terminal açın:

```bash
python desktop_app/sms_notifier.py
```

Veya Windows'ta:
```bash
start_desktop_app.bat
```

### 4. Android Uygulamasını Test Edin

#### Seçenek A: Android Studio ile

1. Android Studio'yu açın
2. `android_app/` klasörünü proje olarak açın
3. `SmsReceiver.kt` ve `MainActivity.kt` dosyalarındaki IP adresini kontrol edin (192.168.56.1)
4. Uygulamayı telefonunuza yükleyin
5. SMS okuma izni verin
6. "Tüm SMS'leri Gönder" butonuna basın

#### Seçenek B: Manuel Test (Telefon Yoksa)

Telefonunuz yoksa, test için API'ye manuel SMS gönderebilirsiniz:

```bash
python test_api.py
```

### 5. Yeni SMS Testi

1. Backend çalışıyor olmalı
2. Desktop uygulaması çalışıyor olmalı
3. Android uygulaması yüklü ve izin verilmiş olmalı
4. Telefonunuza test SMS'i gönderin
5. Bilgisayarınızda bildirim görünmeli

## 🔍 Sorun Giderme

### Backend başlamıyor

- Python yüklü mü? `python --version`
- Bağımlılıklar yüklü mü? `pip install -r requirements.txt`
- Port 5000 kullanımda mı? Başka bir uygulama kullanıyor olabilir

### Bağlantı hatası

- **Windows Firewall**: Port 5000'i açın
  - Windows Defender Firewall → Gelen Kurallar → Yeni Kural
  - Port → TCP → 5000 → İzin Ver

- **IP Adresi**: Doğru IP adresini kullandığınızdan emin olun
  ```bash
  ipconfig
  ```

- **Ağ**: Telefon ve bilgisayar aynı Wi-Fi ağında olmalı

### Android uygulaması SMS göndermiyor

- SMS okuma izni verildi mi?
- IP adresi doğru mu? (192.168.56.1)
- Backend çalışıyor mu?
- Aynı ağda mısınız?

### Bildirimler görünmüyor

- Desktop uygulaması çalışıyor mu?
- Windows bildirim ayarları açık mı?
- Backend'de SMS'ler var mı? `http://localhost:5000/api/sms` adresini tarayıcıda açın

## 📱 IP Adresi Kontrolü

IP adresiniz değiştiyse:

1. Windows'ta IP adresinizi bulun:
   ```bash
   ipconfig
   ```

2. Şu dosyalardaki IP adresini güncelleyin:
   - `android_app/SmsReceiver.kt` (satır 21)
   - `android_app/MainActivity.kt` (satır 18)
   - `test_connection.py` (satır 7)

3. Android uygulamasını yeniden derleyin ve yükleyin

## ✅ Başarı Kriterleri

Sistem düzgün çalışıyorsa:

- ✅ Backend başlatıldığında hata yok
- ✅ `test_connection.py` başarılı
- ✅ Desktop uygulaması çalışıyor
- ✅ Android uygulaması izin veriyor
- ✅ Yeni SMS geldiğinde bildirim görünüyor
- ✅ "Tüm SMS'leri Gönder" butonu çalışıyor

