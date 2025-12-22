"""
Bağlantıyı test etmek için basit bir script
IP adresinizi kontrol edin ve API'ye bağlanabildiğinizi test edin
"""
import requests
import sys

# IP adresinizi buraya yazın
API_URL = "http://192.168.56.1:5000"

def test_connection():
    """API bağlantısını test et"""
    print("🔍 API bağlantısı test ediliyor...")
    print(f"📡 URL: {API_URL}\n")
    
    try:
        # Health check
        print("1. Health check yapılıyor...")
        response = requests.get(f"{API_URL}/api/health", timeout=5)
        
        if response.status_code == 200:
            print("✅ API çalışıyor!")
            print(f"   Yanıt: {response.json()}\n")
        else:
            print(f"❌ API yanıt vermiyor: {response.status_code}\n")
            return False
            
        # Test SMS gönder
        print("2. Test SMS gönderiliyor...")
        test_data = {
            "sender": "+905551234567",
            "message": "Bu bir test mesajıdır! Bağlantı başarılı."
        }
        
        response = requests.post(f"{API_URL}/api/sms", json=test_data, timeout=5)
        
        if response.status_code == 201:
            print("✅ Test SMS başarıyla gönderildi!")
            print(f"   Yanıt: {response.json()}\n")
        else:
            print(f"❌ SMS gönderilemedi: {response.status_code}")
            print(f"   Hata: {response.text}\n")
            return False
        
        # SMS'leri getir
        print("3. SMS'ler getiriliyor...")
        response = requests.get(f"{API_URL}/api/sms", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            sms_count = len(data.get('sms_list', []))
            print(f"✅ {sms_count} SMS bulundu\n")
            
            if sms_count > 0:
                print("📨 Son SMS'ler:")
                for sms in data['sms_list'][:3]:
                    print(f"   - {sms['sender']}: {sms['message'][:50]}...")
        else:
            print(f"❌ SMS'ler getirilemedi: {response.status_code}\n")
            return False
        
        print("\n🎉 Tüm testler başarılı! Sistem çalışıyor.")
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Bağlantı hatası!")
        print("\n🔧 Kontrol edin:")
        print("   1. Backend çalışıyor mu? (python backend/app.py)")
        print("   2. IP adresi doğru mu? (192.168.56.1)")
        print("   3. Telefon ve bilgisayar aynı ağda mı?")
        print("   4. Windows Firewall port 5000'i engelliyor mu?")
        return False
        
    except Exception as e:
        print(f"❌ Hata: {str(e)}")
        return False

if __name__ == '__main__':
    print("=" * 50)
    print("SMS API Bağlantı Testi")
    print("=" * 50)
    print()
    
    if len(sys.argv) > 1:
        # IP adresi argüman olarak verilmişse kullan
        API_URL = f"http://{sys.argv[1]}:5000"
        print(f"📡 Özel IP kullanılıyor: {API_URL}\n")
    
    success = test_connection()
    sys.exit(0 if success else 1)

