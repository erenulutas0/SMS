# Android Uygulaması Dağıtım Rehberi 🚀

Uygulamanızı USB kablosu olmadan dağıtmak için iki ana yöntem vardır.

## Yöntem 1: APK Dosyası Paylaşmak (Hızlı & Ücretsiz)
Bu yöntemle hemen bir dosya oluşturup WhatsApp/Drive üzerinden arkadaşlarınıza atabilirsiniz.

### 1. APK Oluşturma
1.  **Android Studio**'yu açın ve `android_app` klasörünü proje olarak seçin.
2.  Üst menüden **Build > Build Bundle(s) / APK(s) > Build APK(s)** seçeneğine tıklayın.
3.  İşlem bitince sağ altta "APK(s) generated successfully" uyarısı çıkacak. **Locate** butonuna basın.
4.  `app-debug.apk` dosyasını göreceksiniz. Bu dosyayı `SMSSync.apk` olarak yeniden adlandırabilirsiniz.

### 2. Paylaşma
*   Bu dosyayı Google Drive, WeTransfer veya kendi web sitenize yükleyin.
*   Linkini kullanıcıya gönderin.

### 3. Kullanıcı Nasıl Yükler?
1.  Linke tıklar ve dosyayı indirir.
2.  "Bu dosya zararlı olabilir" uyarısına "Yine de indir" der.
3.  Açarken "Bilinmeyen kaynaklardan yüklemeye izin ver" der ve yükler.
4.  Uygulama açılır, izinleri verir ve IP adresi ekranda belirir.

---

## Yöntem 2: Google Play Store (Profesyonel)
Bu yöntem son kullanıcı için en kolayıdır ancak sizin hazırlık yapmanız gerekir.

1.  **Google Play Console** hesabı açın (Tek seferlik $25 ücreti var).
2.  Android Studio'da **Build > Generate Signed Bundle / APK** diyerek "Android App Bundle (.aab)" oluşturun.
3.  Google Play Console'a girip yeni uygulama oluşturun ve bu dosyayı yükleyin.
4.  Uygulama incelenip onaylandıktan sonra (yaklaşık 1 hafta), herkes Play Store'dan indirebilir.

## Özet
*   **Hemen test etmek için:** Yöntem 1 (APK)
*   **Genele açmak için:** Yöntem 2 (Play Store)
