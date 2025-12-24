from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from datetime import datetime
import json
import os
import sys
import re
import winsound
import threading
import webview
import pystray
from PIL import Image
import subprocess
from win11toast import toast

# Add current directory to path for import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from adb_manager import ADBSyncer

# Paths & Configuration
if getattr(sys, 'frozen', False):
    # Executable Directory (User Data goes here)
    EXE_DIR = os.path.dirname(os.path.abspath(sys.executable))
    
    # Asset Directory (Resources, might be in _internal)
    if hasattr(sys, '_MEIPASS'):
        ASSET_DIR = sys._MEIPASS
    elif os.path.exists(os.path.join(EXE_DIR, '_internal')):
        ASSET_DIR = os.path.join(EXE_DIR, '_internal')
    else:
        ASSET_DIR = EXE_DIR # Fallback for older PyInstaller or direct placement

    # Resources
    FRONTEND_DIST = os.path.join(ASSET_DIR, 'frontend', 'dist')
    ICON_PATH = os.path.join(ASSET_DIR, 'app_icon.ico')
    
    # User Data (Persistent)
    SMS_STORAGE_FILE = os.path.join(EXE_DIR, 'sms_storage.json')
    CONFIG_FILE = os.path.join(EXE_DIR, 'config.json')
    LOGS_FILE = os.path.join(EXE_DIR, 'connection_logs.json')
    LOG_PATH = os.path.join(EXE_DIR, 'sms_debug.txt')
    
else:
    # Development Mode
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    ASSET_DIR = BASE_DIR
    FRONTEND_DIST = os.path.join(os.path.dirname(BASE_DIR), 'frontend', 'dist')
    ICON_PATH = os.path.join(os.path.dirname(BASE_DIR), 'app_icon.ico')
    
    SMS_STORAGE_FILE = os.path.join(BASE_DIR, 'sms_storage.json')
    CONFIG_FILE = os.path.join(BASE_DIR, 'config.json')
    LOGS_FILE = os.path.join(BASE_DIR, 'connection_logs.json')
    LOG_PATH = os.path.join(BASE_DIR, 'sms_debug.txt')

# Ensure we can find the ringtone later
RINGTONE_PATH = os.path.join(ASSET_DIR, 'ringtone.mp3')

app = Flask(__name__, static_folder=os.path.join(FRONTEND_DIST, 'assets'))
CORS(app)

# Global variables for Window and Tray
window = None
tray_icon = None
is_running_in_tray = False

class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open(LOG_PATH, "a", encoding='utf-8', buffering=1)

    def write(self, message):
        try: self.terminal.write(message)
        except: pass
        try: self.log.write(message)
        except: pass

    def flush(self):
        try: self.terminal.flush()
        except: pass

sys.stdout = Logger()
sys.stderr = sys.stdout

# --- SMS STORAGE & LOGS ---

def load_sms():
    if os.path.exists(SMS_STORAGE_FILE):
        try:
            with open(SMS_STORAGE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: return []
    return []

def save_sms(sms_list):
    with open(SMS_STORAGE_FILE, 'w', encoding='utf-8') as f:
        json.dump(sms_list, f, ensure_ascii=False, indent=2)

def load_logs():
    if os.path.exists(LOGS_FILE):
        try: 
            with open(LOGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: return []
    return []

def save_logs(log_entry):
    logs = load_logs()
    logs.append(log_entry)
    with open(LOGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

# ... (Blocked Logic Same as Before) ...
BLOCKED_FILE = os.path.join(os.path.dirname(SMS_STORAGE_FILE), 'blocked_senders.json')
def load_blocked():
    if os.path.exists(BLOCKED_FILE):
        try:
            with open(BLOCKED_FILE, 'r', encoding='utf-8') as f:
                return set(json.load(f))
        except: return set()
    return set()
def save_blocked(blocked_set):
    with open(BLOCKED_FILE, 'w', encoding='utf-8') as f:
        json.dump(list(blocked_set), f, ensure_ascii=False, indent=2)

def normalize_sender(s):
    if not s: return ""
    return re.sub(r'[^a-zA-Z0-9]', '', str(s)).lower()

# --- CONFIG ---
DEFAULT_CONFIG = {
    'sound_enabled': True,
    'notification_enabled': True
}

def load_config():
    print(f"Loading config from: {CONFIG_FILE}")
    if os.path.exists(CONFIG_FILE):
        try: 
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                print(f"Config loaded: {data}")
                return {**DEFAULT_CONFIG, **data}
        except Exception as e: 
            print(f"Config load error: {e}")
            return DEFAULT_CONFIG
    print("Config file not found, using defaults.")
    return DEFAULT_CONFIG

def save_config(new_config):
    print(f"Saving config to: {CONFIG_FILE} : {new_config}")
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(new_config, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Config save error: {e}")

# --- NOTIFICATION ---

def restore_window():
    global window
    if window:
        if window.minimized:
            window.restore()
        window.show()
        # Bring to front hack
        try:
            import ctypes
            hwnd = window.get_hwnd() # pywebview 5.0+? Or simply window reference
            # Note: pywebview doesn't expose HWND easily in all versions, 
            # but usually window.show() works.
        except: pass

def play_custom_sound():
    config = load_config()
    if not config.get('sound_enabled', True):
        return
        
    try:
        if os.path.exists(RINGTONE_PATH):
            print(f"Playing sound from: {RINGTONE_PATH}")
            # Normalize path for PowerShell (forward slashes are safer to avoid escape issues)
            safe_path = RINGTONE_PATH.replace('\\', '/')
            
            # Use PowerShell with MediaPlayer for MP3 support
            # Add-Type -AssemblyName PresentationCore is required for MediaPlayer
            cmd = f'''powershell -c "Add-Type -AssemblyName PresentationCore; $p = New-Object System.Windows.Media.MediaPlayer; $p.Open((New-Object System.Uri('{safe_path}'))); $p.Play(); Start-Sleep -s 5;"'''
            
            subprocess.Popen(cmd, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
        else:
            print("Ringtone not found, using default beep.")
            winsound.MessageBeep()
    except Exception as e:
        print(f"Sound Error: {e}")

@app.route('/api/test_notification', methods=['POST'])
def test_notification():
    show_notification("Test Bildirimi", "Bu bir test mesajıdır.")
    play_custom_sound()
    return jsonify({'success': True})

def show_notification(title, message):
    config = load_config()
    print(f"Triggering Notification: {title} | Config: {config}")
    
    if not config.get('notification_enabled', True):
        print("Notification disabled in config.")
        return

    # 1. Try Tray Notification first (Most reliable for tray apps)
    global tray_icon
    if tray_icon:
        try:
            print("Attempting Tray Notification...")
            tray_icon.notify(message, title)
            return
        except Exception as e:
            print(f"Tray notification failed: {e}")
    else:
        print("Tray icon not initialized, skipping tray notify.")

    # 2. Fallback to win11toast
    try:
        print("Attempting Win11Toast Notification...")
        icon_abs = os.path.abspath(ICON_PATH) if os.path.exists(ICON_PATH) else None
        
        def _notify():
            try:
                toast(
                    title, 
                    message, 
                    icon=icon_abs,
                    duration='short', 
                    app_id='SMS Sync',
                    on_click=restore_window
                )
                print("Win11Toast sent.")
            except Exception as e: print(f"Win11Toast fail: {e}")
        
        threading.Thread(target=_notify, daemon=True).start()

    except Exception as e:
        print(f"Notification Error: {e}")

IS_FIRST_SYNC = True

def on_sms_received(new_sms_data_list):
    global IS_FIRST_SYNC
    current_list = load_sms()
    blocked = load_blocked()
    blocked_normalized = {normalize_sender(b) for b in blocked}
    
    existing_keys = {f"{s.get('sender')}|{s.get('message')}" for s in current_list}
    updates = []
    
    for item in new_sms_data_list:
        sender_clean = item['sender'].strip()
        if normalize_sender(sender_clean) in blocked_normalized:
            continue
            
        key = f"{sender_clean}|{item['message']}"
        if key not in existing_keys:
            sms_obj = {
                'id': len(current_list) + len(updates) + 1,
                'sender': sender_clean,
                'message': item['message'],
                'timestamp': item['timestamp'] or datetime.now().isoformat(),
                'read': False
            }
            updates.append(sms_obj)
            existing_keys.add(key)
    
    if updates:
        current_list.extend(updates)
        save_sms(current_list)
        print(f"Synced {len(updates)} new messages.")
        
        if not IS_FIRST_SYNC:
            # Play Sound checks config inside
            play_custom_sound()
            # Show Notification checks config inside
            last_msg = updates[-1]
            show_notification(f"New SMS from {last_msg['sender']}", last_msg['message'][:50])
            
    if IS_FIRST_SYNC: IS_FIRST_SYNC = False

# --- SYNCERS ---
from wifi_syncer import WiFiSyncer
adb_syncer = ADBSyncer(app, on_sms_received)
wifi_syncer = WiFiSyncer(app, on_sms_received)
ACTIVE_MODE = "none" # none, adb, wifi
CURRENT_CONNECTION_START = None
CURRENT_IP_OR_SERIAL = None

@app.route('/api/config', methods=['GET', 'POST'])
def handle_config():
    if request.method == 'POST':
        new_conf = request.json
        save_config(new_conf)
        return jsonify({'success': True, 'config': load_config()})
    else:
        return jsonify(load_config())

@app.route('/api/connect', methods=['POST'])
def connect_device():
    global ACTIVE_MODE, CURRENT_CONNECTION_START, CURRENT_IP_OR_SERIAL
    data = request.json
    ip = data.get('ip')
    serial = data.get('serial')
    
    if ip:
        adb_syncer.stop_sync()
        wifi_syncer.start_sync(ip)
        ACTIVE_MODE = "wifi"
        CURRENT_IP_OR_SERIAL = ip
        CURRENT_CONNECTION_START = datetime.now().isoformat()
        save_logs({'type': 'connect', 'mode': 'wifi', 'target': ip, 'time': CURRENT_CONNECTION_START})
        return jsonify({'success': True, 'mode': 'wifi', 'ip': ip})

    if serial:
        wifi_syncer.stop_sync()
        adb_syncer.start_sync(serial)
        ACTIVE_MODE = "adb"
        CURRENT_IP_OR_SERIAL = serial
        CURRENT_CONNECTION_START = datetime.now().isoformat()
        save_logs({'type': 'connect', 'mode': 'adb', 'target': serial, 'time': CURRENT_CONNECTION_START})
        return jsonify({'success': True, 'mode': 'adb', 'serial': serial})

    return jsonify({'error': 'IP or Serial required'}), 400

@app.route('/api/disconnect', methods=['POST'])
def disconnect_device():
    global ACTIVE_MODE, CURRENT_CONNECTION_START, CURRENT_IP_OR_SERIAL
    
    # 1. Stop Syncers
    if ACTIVE_MODE == "wifi":
        wifi_syncer.stop_sync()
    elif ACTIVE_MODE == "adb":
        adb_syncer.stop_sync()
    
    end_time = datetime.now().isoformat()
    
    # 2. Log Disconnect
    if ACTIVE_MODE != "none":
        save_logs({
            'type': 'disconnect', 
            'mode': ACTIVE_MODE, 
            'target': CURRENT_IP_OR_SERIAL, 
            'start_time': CURRENT_CONNECTION_START,
            'end_time': end_time
        })

    ACTIVE_MODE = "none"
    CURRENT_CONNECTION_START = None
    CURRENT_IP_OR_SERIAL = None
    
    # 3. Clear Messages
    save_sms([])
    global IS_FIRST_SYNC
    IS_FIRST_SYNC = True
    
    return jsonify({'success': True})

@app.route('/api/logs', methods=['GET'])
def get_logs():
    return jsonify({'logs': load_logs()})

# ... (Original API Routes for SMS/Stats) ...
@app.route('/api/devices', methods=['GET'])
def list_devices(): return jsonify(adb_syncer.get_devices())

@app.route('/api/status', methods=['GET'])
def connection_status():
    if ACTIVE_MODE == "wifi": return jsonify(wifi_syncer.get_status())
    elif ACTIVE_MODE == "adb": return {'active': adb_syncer.active, 'device': adb_syncer.device_serial, 'type': 'adb'}
    else: return jsonify({'active': False, 'device': None, 'type': 'none'})

@app.route('/api/sms', methods=['GET'])
def get_sms_route():
    sms_list = load_sms()
    blocked = load_blocked()
    blocked_normalized = {normalize_sender(b) for b in blocked}
    sms_list = [s for s in sms_list if normalize_sender(s.get('sender')) not in blocked_normalized]
    sms_list = sorted(sms_list, key=lambda x: x.get('timestamp', '') or '', reverse=True)
    return jsonify({'sms_list': sms_list})
    
@app.route('/api/sms/unread', methods=['GET'])
def get_unread():
    # Similar impl
    sms_list = get_sms_route().get_json()['sms_list']
    unread = [s for s in sms_list if not s.get('read')]
    return jsonify({'sms_list': unread})

@app.route('/api/block', methods=['POST'])
def block_sender():
    data = request.json
    sender = data.get('sender')
    if not sender: return jsonify({'error': 'Sender required'}), 400
    blocked = load_blocked()
    blocked.add(sender.strip())
    save_blocked(blocked)
    target_norm = normalize_sender(sender)
    all_sms = load_sms()
    new_sms_list = [s for s in all_sms if normalize_sender(s.get('sender')) != target_norm]
    if len(all_sms) != len(new_sms_list): save_sms(new_sms_list)
    return jsonify({'success': True})

@app.route('/api/sms/<int:sms_id>/read', methods=['POST'])
def mark_read(sms_id):
    sms_list = load_sms()
    found = False
    for sms in sms_list:
        if sms['id'] == sms_id:
            sms['read'] = True
            found = True
            break
    if found:
        save_sms(sms_list)
        return jsonify({'success': True})
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/stats', methods=['GET'])
def stats():
    sms_list = load_sms()
    blocked = load_blocked()
    valid_list = [s for s in sms_list if s.get('sender') not in blocked]
    return jsonify({'total': len(valid_list), 'unread': len([s for s in valid_list if not s.get('read')])})

# --- FRONTEND ---
@app.route('/')
def serve_index(): return send_from_directory(FRONTEND_DIST, 'index.html')
@app.route('/<path:path>')
def serve_static(path):
    full_path = os.path.join(FRONTEND_DIST, path)
    if os.path.exists(full_path): return send_from_directory(FRONTEND_DIST, path)
    return send_from_directory(FRONTEND_DIST, 'index.html')

# --- TRAY & WINDOW MANAGEMENT ---

def setup_tray():
    global tray_icon
    try:
        if os.path.exists(ICON_PATH):
            image = Image.open(ICON_PATH)
        else:
            # Fallback (create a colored square)
            image = Image.new('RGB', (64, 64), color = (73, 109, 137))
        
        def on_exit(icon, item):
            icon.stop()
            if window: window.destroy()
            os._exit(0) # Force kill
            
        def on_open(icon, item):
            restore_window()

        menu = pystray.Menu(
            pystray.MenuItem('Open', on_open, default=True),
            pystray.MenuItem('Exit', on_exit)
        )
        
        tray_icon = pystray.Icon("SMS Sync", image, "SMS Sync", menu)
        tray_icon.run() 
    except Exception as e:
        print(f"Tray Error: {e}")

def on_closing():
    # This is called when user clicks X
    # We want to minimize to tray instead of closing
    print("Minimizing to tray...")
    window.hide()
    
    # If using pystray, we can optionally notify user
    # but win11toast handles system notifications
    return False # returning False cancels the close event in pywebview

def start_flask():
    app.run(host='127.0.0.1', port=5001, debug=False, use_reloader=False)

if __name__ == '__main__':
    # 1. Start Flask
    t = threading.Thread(target=start_flask, daemon=True)
    t.start()
    
    # 2. Start Tray (in separate thread because it blocks?)
    # pystray run() blocks, so usually we run it in a thread OR main thread.
    # pywebview start() ALSO blocks.
    # We must run tray in a thread if we want pywebview in main, or vice versa.
    # pywebview recommends main thread for GUI.
    
    tray_thread = threading.Thread(target=setup_tray, daemon=True)
    tray_thread.start()
    
    # 3. Start Window
    window = webview.create_window('SMS Sync', 'http://127.0.0.1:5001', width=1200, height=800)
    window.events.closing += on_closing
    webview.start(debug=True)
