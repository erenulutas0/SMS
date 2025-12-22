# Android SMS Gönderici Uygulaması

Bu Android uygulaması, telefonunuza gelen SMS'leri otomatik olarak bilgisayarınızdaki API'ye gönderir.

## 📱 Kurulum

### Gereksinimler
- Android Studio
- Android SDK (API 23+)
- SMS okuma izni

### Adımlar

1. Android Studio'da yeni bir proje oluşturun
2. `AndroidManifest.xml` dosyasına izinleri ekleyin
3. `MainActivity.java` veya `MainActivity.kt` dosyasını aşağıdaki kodla değiştirin
4. Bilgisayarınızın IP adresini kodda güncelleyin
5. Uygulamayı derleyip telefonunuza yükleyin

## 🔐 İzinler

`AndroidManifest.xml` dosyasına şu izinleri ekleyin:

```xml
<uses-permission android:name="android.permission.RECEIVE_SMS" />
<uses-permission android:name="android.permission.READ_SMS" />
<uses-permission android:name="android.permission.INTERNET" />
```

## 📝 Kod Örnekleri

Kotlin ve Java örnekleri için ilgili dosyalara bakın.

