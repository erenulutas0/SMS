import subprocess
import requests
import json
import time
from datetime import datetime

API_URL = "http://localhost:5000/api/sms/bulk"

def get_sms_from_adb():
    try:
        # ADB command to query SMS
        # We fetch address (sender), body, and date
        cmd = ['adb', 'shell', 'content', 'query', '--uri', 'content://sms/inbox', '--projection', 'address:body:date', '--sort', 'date DESC', '--limit', '50']
        
        # Run command
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
        
        if result.returncode != 0:
            print(f"ADB Error: {result.stderr}")
            return []
            
        output = result.stdout
        if not output:
             print("No SMS found or empty output")
             return []

        # Parse output
        # Output format is usually: Row: 0 address=... body=... date=...
        sms_list = []
        
        for line in output.splitlines():
            if not line.startswith("Row:"):
                continue
                
            try:
                # Naive parsing - this depends on the output format of 'content query' which can vary slightly
                # usually space separated key=value, but body can contain spaces.
                # Regex is safer.
                import re
                
                # Extract address
                address_match = re.search(r'address=(.*?),', line)
                body_match = re.search(r'body=(.*?),', line) # This is risky if body has commas
                date_match = re.search(r'date=(.*?)(,|$)', line)
                
                # Better approach: split by ", " but body might contain it.
                # Let's try to extract known fields.
                
                parts = line.split(", ")
                sender = "Unknown"
                message = ""
                timestamp = ""
                
                for part in parts:
                    if part.startswith("address="):
                        sender = part.replace("address=", "")
                    elif part.startswith("date="):
                         timestamp = part.replace("date=", "")
                    # Body is the hardest because it's last or in middle and can contain anything
                
                # Let's try a safer ADB strategy: JSON output if possible, or simpler separator
                # But 'content' command doesn't support json easily.
                # Let's rely on the user confirming if this works, or use a better python generic approach.
                pass 
            except Exception as e:
                pass

        # Alternative: Use simple pulling of all data and requests
        return []

    except Exception as e:
        print(f"Error: {e}")
        return []

def sync_via_adb():
    print("Syncing SMS via ADB...")
    
    # Check if device is connected
    check = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
    if "device\n" not in check.stdout and "device\r" not in check.stdout:
        print("Waiting for device...")
        return

    cmd = ['adb', 'shell', 'content', 'query', '--uri', 'content://sms/inbox', '--projection', 'date:address:body']
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    except Exception as e:
        print(f"ADB Execution Error: {e}")
        return

    if result.returncode != 0:
        print(f"ADB Error: {result.stderr}")
        return
        
    output = result.stdout
    
    bulk_data = []
    import re
    
    lines = output.splitlines()
    debug_count = 0
    
    for line in lines:
        if "Row:" not in line:
            continue
            
        if debug_count < 3:
            print(f"DEBUG LINE: {line}")
            debug_count += 1
            
        try:
            # New Projection: date, address, body
            # Expected formatting: Row: 0 date=173..., address=..., body=...
            
            # Extract Date first (safest)
            timestamp = None
            date_match = re.search(r'date=([0-9]+)', line)
            if date_match:
                try:
                    ts_millis = int(date_match.group(1))
                    timestamp = datetime.fromtimestamp(ts_millis / 1000.0).isoformat()
                except:
                    pass
            
            # Extract Address
            # It should be after date=... so we search for address=...
            addr_match = re.search(r'address=(.*?)(, body=|$)', line)
            if not addr_match: continue
            address = addr_match.group(1).strip()
            
            # Extract Body
            # It is usually last
            body_match = re.search(r'body=(.*)$', line)
            message = ""
            if body_match:
                message = body_match.group(1).strip()
                # Remove trailing comma if it exists (artifacts from split or whatever)
                # But 'body' is typically the rest of the line.
            
            if address:
                bulk_data.append({
                    "sender": address,
                    "message": message or "[Boş Mesaj]",
                    "timestamp": timestamp
                })
        except Exception as e:
            print(f"Parse Error on line: {e}")
            continue

    if bulk_data:
        try:
            print(f"Sending {len(bulk_data)} SMS to backend...")
            resp = requests.post(API_URL, json=bulk_data)
            if resp.status_code == 201:
                print("Successfully synced SMS!")
            else:
                 print(f"Failed to sync. Backend responded: {resp.status_code}")
        except Exception as e:
            print(f"API Connection Error: {e}")
            print("Make sure the backend is running at http://localhost:5000")
            
    else:
        print("No SMS found or parsed.")

if __name__ == "__main__":
    print("ADB Sync Tool Started")
    print("Press Ctrl+C to stop")
    while True:
        sync_via_adb()
        time.sleep(10)
