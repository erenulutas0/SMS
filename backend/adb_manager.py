import subprocess
import time
from datetime import datetime
import re
import threading

import os

class ADBSyncer:
    def __init__(self, app_context, save_callback):
        self.active = False
        self.device_serial = None
        self.thread = None
        self.save_callback = save_callback # Function to save SMS to DB
        self.app_context = app_context
    
    def _get_subprocess_kwargs(self):
        """Returns kwargs to suppress console window on Windows"""
        kwargs = {}
        if os.name == 'nt':
            # 0x08000000 is CREATE_NO_WINDOW
            kwargs['creationflags'] = 0x08000000 
        return kwargs

    def get_devices(self):
        """Returns list of connected devices"""
        try:
            result = subprocess.run(['adb', 'devices'], capture_output=True, text=True, **self._get_subprocess_kwargs())
            lines = result.stdout.splitlines()
            devices = []
            for line in lines[1:]:
                if line.strip():
                    parts = line.split()
                    if len(parts) >= 2:
                        devices.append({
                            'serial': parts[0],
                            'state': parts[1]
                        })
            return devices
        except Exception as e:
            print(f"ADB Error: {e}")
            return []

    def start_sync(self, serial):
        self.device_serial = serial
        self.active = True
        if self.thread is None or not self.thread.is_alive():
            self.thread = threading.Thread(target=self._sync_loop, daemon=True)
            self.thread.start()

    def stop_sync(self):
        self.active = False

    def _sync_loop(self):
        print(f"Starting sync for {self.device_serial}")
        while self.active:
            try:
                self._fetch_and_save()
            except Exception as e:
                print(f"Sync Error: {e}")
            
            # Sleep 
            for _ in range(50): # Check active status every 100ms
                if not self.active: break
                time.sleep(0.1)

    def get_blocked_numbers(self):
        """Fetches blocked numbers from the device"""
        blocked = set()
        # Some devices use 'original_number', others 'column1', but let's try standard provider FIRST.
        cmd = ['adb', '-s', self.device_serial, 'shell', 'content', 'query', '--uri', 'content://com.android.blockednumber/blocked', '--projection', 'original_number']
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore', **self._get_subprocess_kwargs())
            for line in result.stdout.splitlines():
                # Format: Row: 0 original_number=123456...
                # Regex to grab the number
                match = re.search(r'original_number=(.*?)($|,)', line)
                if match:
                    num = match.group(1).strip()
                    if num: blocked.add(num)
        except Exception:
            pass
        return blocked

    def _fetch_and_save(self):
        # Local import to prevent scope issues
        import re
        
        cmd = ['adb', '-s', self.device_serial, 'shell', 'content', 'query', '--uri', 'content://sms/inbox', '--projection', 'date:address:body']
        
        try:
            # 1. Get blocked numbers first
            blocked_numbers = self.get_blocked_numbers()
            # print(f"DEBUG: Found {len(blocked_numbers)} blocked numbers")

            # 2. Run ADB
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore', **self._get_subprocess_kwargs())
            if result.returncode != 0: 
                return

            output = result.stdout
            lines = output.splitlines()
            # print(f"DEBUG: ADB returned {len(lines)} lines")
            
            bulk_data = []
            
            debug_count = 0
            for i, line in enumerate(lines):
                if not line.strip(): continue
                
                # Debug first few lines
                # if debug_count < 3:
                #      print(f"DEBUG LINE: {line}")
                #      debug_count += 1
                
                if "address=" not in line: continue

                try:
                    # Extract timestamp
                    timestamp = None
                    # Use explicit re module from local import
                    date_match = re.search(r'date=([0-9]+)', line)
                    if date_match:
                        ts_millis = int(date_match.group(1))
                        try:
                            timestamp = datetime.fromtimestamp(ts_millis / 1000.0).isoformat()
                        except: pass
                    
                    # Extract Address
                    addr_match = re.search(r'address=(.*?)(, body=|, date=|$)', line)
                    
                    if not addr_match: 
                        continue

                    address = addr_match.group(1).strip()
                    if not address: continue 
                    
                    # Ensure clean string for blocking check
                    address = address.strip() 

                    # CHECK IF BLOCKED
                    if address in blocked_numbers:
                        continue
                    
                    # Extract Body
                    body_match = re.search(r'body=(.*)$', line)
                    message = ""
                    if body_match:
                        message = body_match.group(1).strip()
                    
                    bulk_data.append({
                        "sender": address,
                        "message": message or "[Boş Mesaj]",
                        "timestamp": timestamp
                    })
                except Exception as inner_e:
                    print(f"Parse Error at line {i}: {inner_e}")
                    continue
            
            # Save via Callback
            if bulk_data:
                self.save_callback(bulk_data)
                
        except Exception as e:
            import traceback
            print(f"Fetch Error: {e}")
            traceback.print_exc()
