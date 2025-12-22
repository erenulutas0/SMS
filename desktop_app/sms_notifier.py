import requests
import time
import json
import os
from datetime import datetime
from plyer import notification
import threading

# API ayarları
API_URL = "http://localhost:5000"
CHECK_INTERVAL = 2  # Saniye cinsinden kontrol aralığı

# Son kontrol edilen SMS ID'sini sakla
LAST_CHECKED_FILE = 'last_checked.json'

def load_last_checked():
    """Son kontrol edilen SMS ID'sini yükle"""
    if os.path.exists(LAST_CHECKED_FILE):
        with open(LAST_CHECKED_FILE, 'r') as f:
            data = json.load(f)
            return data.get('last_id', 0)
    return 0

def save_last_checked(sms_id):
    """Son kontrol edilen SMS ID'sini kaydet"""
    with open(LAST_CHECKED_FILE, 'w') as f:
        json.dump({'last_id': sms_id}, f)

def show_notification(sender, message):
    """Sistem bildirimi göster"""
    try:
        # Mesajı kısalt (çok uzunsa)
        short_message = message[:100] + "..." if len(message) > 100 else message
        
        notification.notify(
            title=f"SMS: {sender}",
            message=short_message,
            timeout=10,  # 10 saniye göster
            app_name="SMS Bildirici"
        )
        print(f"Bildirim gösterildi: {sender} - {short_message[:50]}...")
    except Exception as e:
        print(f"Bildirim hatası: {str(e)}")

def check_new_sms():
    """Yeni SMS'leri kontrol et"""
    try:
        response = requests.get(f"{API_URL}/api/sms", timeout=5)
        if response.status_code == 200:
            data = response.json()
            sms_list = data.get('sms_list', [])
            
            last_checked_id = load_last_checked()
            new_sms_count = 0
            
            # Yeni SMS'leri bul (son kontrol edilenden sonra gelenler)
            for sms in sms_list:
                if sms['id'] > last_checked_id:
                    show_notification(sms['sender'], sms['message'])
                    new_sms_count += 1
                    # En yeni ID'yi kaydet
                    if sms['id'] > last_checked_id:
                        last_checked_id = sms['id']
            
            if new_sms_count > 0:
                save_last_checked(last_checked_id)
                print(f"{new_sms_count} yeni SMS bulundu ve bildirim gösterildi.")
            
            return True
        else:
            print(f"API hatası: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("API'ye bağlanılamıyor. Backend çalışıyor mu?")
        return False
    except Exception as e:
        print(f"Hata: {str(e)}")
        return False

def main_loop():
    """Ana döngü - sürekli kontrol et"""
    print("SMS Bildirici başlatıldı...")
    print(f"API: {API_URL}")
    print(f"Kontrol aralığı: {CHECK_INTERVAL} saniye")
    print("Çıkmak için Ctrl+C basın\n")
    
    while True:
        check_new_sms()
        time.sleep(CHECK_INTERVAL)

if __name__ == '__main__':
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\n\nSMS Bildirici kapatılıyor...")
    except Exception as e:
        print(f"Kritik hata: {str(e)}")

