"""
API'yi test etmek için basit bir script
"""
import requests
import json

API_URL = "http://localhost:5000"

def test_send_sms():
    """Test SMS gönder"""
    data = {
        "sender": "+905551234567",
        "message": "Bu bir test mesajıdır. SMS bildirici sistemi çalışıyor!"
    }
    
    try:
        response = requests.post(f"{API_URL}/api/sms", json=data)
        if response.status_code == 201:
            print("✅ SMS başarıyla gönderildi!")
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print(f"❌ Hata: {response.status_code}")
            print(response.text)
    except requests.exceptions.ConnectionError:
        print("❌ API'ye bağlanılamıyor. Backend çalışıyor mu?")
    except Exception as e:
        print(f"❌ Hata: {str(e)}")

def test_get_sms():
    """Tüm SMS'leri getir"""
    try:
        response = requests.get(f"{API_URL}/api/sms")
        if response.status_code == 200:
            data = response.json()
            sms_list = data.get('sms_list', [])
            print(f"\n📨 Toplam {len(sms_list)} SMS bulundu:\n")
            for sms in sms_list[:5]:  # İlk 5'ini göster
                print(f"Gönderen: {sms['sender']}")
                print(f"Mesaj: {sms['message'][:50]}...")
                print(f"Tarih: {sms['timestamp']}")
                print("-" * 50)
        else:
            print(f"❌ Hata: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ API'ye bağlanılamıyor. Backend çalışıyor mu?")
    except Exception as e:
        print(f"❌ Hata: {str(e)}")

if __name__ == '__main__':
    print("SMS API Test Scripti\n")
    print("1. Test SMS gönderiliyor...")
    test_send_sms()
    print("\n2. SMS'ler getiriliyor...")
    test_get_sms()

