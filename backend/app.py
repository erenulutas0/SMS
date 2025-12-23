from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from datetime import datetime
import json
import os
import sys
import re
import winsound
import base64

# Add current directory to path for import
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from adb_manager import ADBSyncer

# Paths
if getattr(sys, 'frozen', False):
    # PyInstaller create temp folder in _MEIPASS, but we want to save data next to the EXE
    BASE_DIR = sys._MEIPASS
    EXE_DIR = os.path.dirname(sys.executable)
    FRONTEND_DIST = os.path.join(BASE_DIR, 'frontend', 'dist')
    SMS_STORAGE_FILE = os.path.join(EXE_DIR, 'sms_storage.json')
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    FRONTEND_DIST = os.path.join(os.path.dirname(BASE_DIR), 'frontend', 'dist')
    SMS_STORAGE_FILE = os.path.join(BASE_DIR, 'sms_storage.json')

app = Flask(__name__, static_folder=os.path.join(FRONTEND_DIST, 'assets'))
CORS(app)

# --- LOGGING SETUP ---
# Redirect print/stderr to a file for debugging the EXE
if getattr(sys, 'frozen', False):
    log_path = os.path.join(EXE_DIR, 'sms_debug.txt')
else:
    log_path = os.path.join(BASE_DIR, 'sms_debug.txt')

# Simple logger that writes to both file and original stdout
class Logger(object):
    def __init__(self):
        self.terminal = sys.stdout
        self.log = open(log_path, "a", encoding='utf-8', buffering=1) # Line buffering

    def write(self, message):
        try:
            self.terminal.write(message)
        except: pass
        try:
            self.log.write(message)
        except: pass

    def flush(self):
        try:
            self.terminal.flush()
            self.log.flush()
        except: pass

sys.stdout = Logger()
sys.stderr = sys.stdout

print(f"\n\n--- APP STARTED AT {datetime.now()} ---")
print(f"Base Dir: {BASE_DIR}")
print(f"Storage File: {SMS_STORAGE_FILE}")
# ---------------------

# Helper: SMS Storage
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

# Helper: Blocked Storage
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

# Helper: Normalize Sender (Aggressive)
def normalize_sender(s):
    if not s: return ""
    # Remove all non-alphanumeric characters (including spaces, hidden chars) and lowercase
    return re.sub(r'[^a-zA-Z0-9]', '', str(s)).lower()

import base64
import ctypes
import subprocess

# ... 
IS_FIRST_SYNC = True

# Flash Taskbar Icon
def flash_taskbar():
    """Flash the taskbar icon to notify user of new messages."""
    try:
        # Use ctypes to flash the window
        user32 = ctypes.windll.user32
        hwnd = user32.GetForegroundWindow()
        
        # FLASHW_ALL = 3 (flash both caption and taskbar), FLASHW_TIMERNOFG = 12
        class FLASHWINFO(ctypes.Structure):
            _fields_ = [
                ('cbSize', ctypes.c_uint),
                ('hwnd', ctypes.c_void_p),
                ('dwFlags', ctypes.c_uint),
                ('uCount', ctypes.c_uint),
                ('dwTimeout', ctypes.c_uint)
            ]
        
        # Get the console/app window handle
        kernel32 = ctypes.windll.kernel32
        
        # Try to flash all windows of this process
        fwi = FLASHWINFO()
        fwi.cbSize = ctypes.sizeof(FLASHWINFO)
        fwi.hwnd = hwnd
        fwi.dwFlags = 3 | 12  # FLASHW_ALL | FLASHW_TIMERNOFG
        fwi.uCount = 5
        fwi.dwTimeout = 0
        
        user32.FlashWindowEx(ctypes.byref(fwi))
        print("Taskbar flashed.")
    except Exception as e:
        print(f"Flash taskbar error: {e}")

def play_custom_sound():
    try:
        # Check for ringtone.mp3 in the correct directory (Frozen or Dev)
        if getattr(sys, 'frozen', False):
            if hasattr(sys, '_MEIPASS'):
                # Onefile mode
                base_dir = sys._MEIPASS
            else:
                # Onedir mode: usually in _internal or root
                base_dir = os.path.dirname(sys.executable)
                if not os.path.exists(os.path.join(base_dir, 'ringtone.mp3')):
                    # Try _internal
                    base_dir = os.path.join(base_dir, '_internal')
            
            sound_path = os.path.join(base_dir, 'ringtone.mp3')
        else:
            sound_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'frontend', 'src', 'assets', 'ringtone.mp3')
        
        # Normalize path
        sound_path = os.path.normpath(sound_path)
        print(f"Attempting to play sound: {sound_path}")
        print(f"Sound file exists: {os.path.exists(sound_path)}")
        
        if os.path.exists(sound_path):
            # Use PowerShell to play MP3 via Windows Media Player COM object
            # Escape single quotes in path for PowerShell
            escaped_path = sound_path.replace("'", "''")
            
            ps_script = f'''
Add-Type -AssemblyName presentationCore
$player = New-Object System.Windows.Media.MediaPlayer
$player.Open([System.Uri]"{escaped_path}")
$player.Volume = 1.0
$player.Play()
Start-Sleep -Seconds 3
$player.Close()
'''
            print(f"Running PowerShell to play sound...")
            result = subprocess.Popen(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                creationflags=0x08000000,  # CREATE_NO_WINDOW
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print(f"Sound command launched (PID: {result.pid})")
        else:
            print(f"Ringtone not found at: {sound_path}, using Windows beep.")
            winsound.MessageBeep()
            
    except Exception as e:
        print(f"Sound Error: {e}")
        import traceback
        traceback.print_exc()
        try: 
            winsound.MessageBeep() 
        except: 
            pass

# Callback for ADB Sync
def on_sms_received(new_sms_data_list):
    global IS_FIRST_SYNC
    current_list = load_sms()
    blocked = load_blocked()
    blocked_normalized = {normalize_sender(b) for b in blocked}
    
    # Create a quick lookup set for duplicates
    existing_keys = {f"{s.get('sender')}|{s.get('message')}" for s in current_list}
    
    updates = []
    
    for item in new_sms_data_list:
        sender_clean = item['sender'].strip()
        # Skip if blocked
        if normalize_sender(sender_clean) in blocked_normalized:
            continue
            
        key = f"{sender_clean}|{item['message']}"
        if key not in existing_keys:
            # New SMS
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
        
        # Only notify if NOT the first sync
        if not IS_FIRST_SYNC:
            # 1. Play Sound
            play_custom_sound()
            
            # 2. Flash Taskbar
            flash_taskbar()
            
    # After first execution (regardless of updates), mark first sync as done
    if IS_FIRST_SYNC:
        IS_FIRST_SYNC = False

# Initialize Syncer
syncer = ADBSyncer(app, on_sms_received)

@app.route('/api/devices', methods=['GET'])
def list_devices():
    return jsonify(syncer.get_devices())

@app.route('/api/connect', methods=['POST'])
def connect_device():
    data = request.json
    serial = data.get('serial')
    if serial:
        syncer.start_sync(serial)
        return jsonify({'success': True, 'serial': serial})
    return jsonify({'error': 'Serial required'}), 400

@app.route('/api/status', methods=['GET'])
def connection_status():
    return jsonify({
        'active': syncer.active,
        'device': syncer.device_serial
    })

@app.route('/api/sms', methods=['GET'])
def get_sms_route():
    sms_list = load_sms()
    blocked = load_blocked()
    
    # Create set of normalized blocked senders
    blocked_normalized = {normalize_sender(b) for b in blocked}
    
    # Filter out blocked (using normalized check)
    sms_list = [
        s for s in sms_list 
        if normalize_sender(s.get('sender')) not in blocked_normalized
    ]
    
    # Sort by timestamp descending
    sms_list = sorted(sms_list, key=lambda x: x.get('timestamp', '') or '', reverse=True)
    return jsonify({'sms_list': sms_list})

@app.route('/api/sms/unread', methods=['GET'])
def get_unread():
    sms_list = load_sms()
    blocked = load_blocked()
    blocked_normalized = {normalize_sender(b) for b in blocked}
    
    unread = [
        s for s in sms_list 
        if not s.get('read') 
        and normalize_sender(s.get('sender')) not in blocked_normalized
    ]
    return jsonify({'sms_list': unread})

@app.route('/api/block', methods=['POST'])
def block_sender():
    data = request.json
    sender = data.get('sender')
    if not sender: return jsonify({'error': 'Sender required'}), 400
    
    # Save the raw sender to block list just in case
    blocked = load_blocked()
    blocked.add(sender.strip())
    save_blocked(blocked)
    
    # Aggressive Normalization for Deletion
    target_norm = normalize_sender(sender)
    
    all_sms = load_sms()
    # Keep only messages that DO NOT match the normalized blocked sender
    new_sms_list = [
        s for s in all_sms 
        if normalize_sender(s.get('sender')) != target_norm
    ]
    
    deleted_count = len(all_sms) - len(new_sms_list)
    if deleted_count > 0:
        save_sms(new_sms_list)
        print(f"Deleted {deleted_count} messages from blocked sender: {sender} (norm: {target_norm})")
    
    return jsonify({'success': True, 'blocked': sender, 'deleted': deleted_count})

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
    return jsonify({
        'total': len(valid_list),
        'unread': len([s for s in valid_list if not s.get('read')])
    })

# --- Frontend Serving ---

@app.route('/')
def serve_index():
    return send_from_directory(FRONTEND_DIST, 'index.html')

@app.route('/<path:path>')
def serve_static(path):
    # Check if file exists in dist
    full_path = os.path.join(FRONTEND_DIST, path)
    if os.path.exists(full_path):
        return send_from_directory(FRONTEND_DIST, path)
    # Otherwise fallback to index (SPA routing)
    return send_from_directory(FRONTEND_DIST, 'index.html')

if __name__ == '__main__':
    import webview
    import threading
    
    def start_server():
        print("Starting SMS Desktop App...")
        app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)

    # Start Flask API in a separate thread
    t = threading.Thread(target=start_server, daemon=True)
    t.start()
    
    # Create Desktop Window
    # Create Desktop Window
    window = webview.create_window('SMS Sync', 'http://127.0.0.1:5000', width=1200, height=800)
    webview.start(debug=True)
