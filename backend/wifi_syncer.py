import requests
import time
import threading
from datetime import datetime

class WiFiSyncer:
    def __init__(self, app_logger, on_sms_callback):
        self.active_ip = None
        self.is_running = False
        self.stop_event = threading.Event()
        self.logger = app_logger
        self.on_sms_received = on_sms_callback
        self.thread = None

    def start_sync(self, ip_address):
        """Start syncing with a specific IP address."""
        if self.is_running and self.active_ip == ip_address:
            return  # Already syncing this IP
        
        # Stop existing sync if any
        self.stop_sync()
        
        self.active_ip = ip_address
        self.stop_event.clear()
        self.is_running = True
        
        self.thread = threading.Thread(target=self._sync_loop, daemon=True)
        self.thread.start()
        print(f"WiFi Sync started for {ip_address}")

    def stop_sync(self):
        """Stop current sync process."""
        self.is_running = False
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=2)
        self.active_ip = None

    def get_status(self):
        return {
            "active": self.is_running,
            "device": f"WiFi ({self.active_ip})" if self.active_ip else None,
            "type": "wifi"
        }

    def _sync_loop(self):
        error_count = 0
        while not self.stop_event.is_set():
            try:
                url = f"http://{self.active_ip}:8080/sms"
                # Short timeout to keep UI responsive
                response = requests.get(url, timeout=3)
                
                if response.status_code == 200:
                    raw_data = response.json()
                    # Convert to app format
                    sms_list = []
                    for item in raw_data:
                        # Android app sends 'date' as long (millis)
                        # We need 'timestamp' as ISO string or something parseable
                        ts_val = item.get('date', 0)
                        
                        sms_list.append({
                            'sender': item.get('address', 'Unknown'),
                            'message': item.get('body', ''),
                            # Backend expects 'timestamp' key. 
                            # If it's millis, passing it as is works if frontend parses it,
                            # but let's be safe and pass as string
                            'timestamp': str(ts_val) 
                        })
                    
                    if sms_list:
                        # Send to main app logic
                        self.on_sms_received(sms_list)
                        error_count = 0
                else:
                    print(f"WiFi Error: {response.status_code}")
                    error_count += 1
            
            except Exception as e:
                print(f"WiFi Connection Error: {e}")
                error_count += 1
            
            # If too many errors, maybe pause longer?
            sleep_time = 5 if error_count > 3 else 2
            time.sleep(sleep_time)

