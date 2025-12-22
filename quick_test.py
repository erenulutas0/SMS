"""
Hızlı test - Web arayüzünde görünmesi için test SMS'leri gönder
"""
import requests
import json
import time
import sys
import io

# Windows console encoding sorunu için
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

API_URL = "http://localhost:5000"

test_messages = [
    {"sender": "+905551234567", "message": "Merhaba! Bu bir test mesajidir."},
    {"sender": "Banka", "message": "Hesabiniza 1000 TL yatirildi. Iyi gunler!"},
    {"sender": "5551234567", "message": "Toplanti yarin saat 14:00'te yapilacak."},
    {"sender": "Siparis", "message": "Siparisiniz kargoya verildi. Takip no: ABC123"},
]

print("Test SMS'leri gonderiliyor...\n")

for i, msg in enumerate(test_messages, 1):
    try:
        response = requests.post(f"{API_URL}/api/sms", json=msg, timeout=5)
        if response.status_code == 201:
            print(f"[OK] {i}. SMS gonderildi: {msg['sender']}")
        else:
            print(f"[HATA] {i}. SMS gonderilemedi: {response.status_code}")
    except Exception as e:
        print(f"[HATA] {i}. Hata: {str(e)}")
    time.sleep(0.5)

print("\n[OK] Test tamamlandi! Web arayuzunu yenileyin (F5).")

