from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from datetime import datetime
import json
import os

app = Flask(__name__, template_folder='templates', static_folder='static')
CORS(app)  # CORS desteği için

# SMS'leri saklamak için basit bir JSON dosyası kullanıyoruz
SMS_STORAGE_FILE = 'sms_storage.json'

def load_sms():
    """SMS'leri dosyadan yükle"""
    if os.path.exists(SMS_STORAGE_FILE):
        with open(SMS_STORAGE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_sms(sms_list):
    """SMS'leri dosyaya kaydet"""
    with open(SMS_STORAGE_FILE, 'w', encoding='utf-8') as f:
        json.dump(sms_list, f, ensure_ascii=False, indent=2)

@app.route('/api/sms', methods=['POST'])
def receive_sms():
    """Yeni SMS al"""
    try:
        data = request.json
        
        # Gerekli alanları kontrol et
        if not data or 'message' not in data or 'sender' not in data:
            return jsonify({'error': 'Eksik veri: message ve sender gerekli'}), 400
        
        # SMS objesi oluştur
        sms = {
            'id': len(load_sms()) + 1,
            'sender': data.get('sender', 'Bilinmeyen'),
            'message': data.get('message', ''),
            'timestamp': datetime.now().isoformat(),
            'read': False
        }
        
        # SMS'i kaydet
        sms_list = load_sms()
        sms_list.append(sms)
        save_sms(sms_list)
        
        print(f"Yeni SMS alındı: {sms['sender']} - {sms['message'][:50]}...")
        
        return jsonify({'success': True, 'sms': sms}), 201
        
    except Exception as e:
        print(f"Hata: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/sms', methods=['GET'])
def get_sms():
    """Tüm SMS'leri getir"""
    try:
        sms_list = load_sms()
        # En yeni önce (tarihe göre)
        sms_list = sorted(sms_list, key=lambda x: x.get('timestamp', ''), reverse=True)
        return jsonify({'sms_list': sms_list}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sms/unread', methods=['GET'])
def get_unread_sms():
    """Okunmamış SMS'leri getir"""
    try:
        sms_list = load_sms()
        unread = [sms for sms in sms_list if not sms.get('read', False)]
        unread.reverse()  # En yeni önce
        return jsonify({'sms_list': unread}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sms/<int:sms_id>/read', methods=['POST'])
def mark_as_read(sms_id):
    """SMS'i okundu olarak işaretle"""
    try:
        data = request.json or {}
        read_status = data.get('read', True)  # Varsayılan True
        
        sms_list = load_sms()
        for sms in sms_list:
            if sms['id'] == sms_id:
                sms['read'] = read_status
                save_sms(sms_list)
                return jsonify({'success': True}), 200
        return jsonify({'error': 'SMS bulunamadı'}), 404
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sms/bulk', methods=['POST'])
def receive_bulk_sms():
    """Toplu SMS al (tüm SMS'leri bir seferde)"""
    try:
        data = request.json
        
        # JSON array bekliyoruz
        if not isinstance(data, list):
            return jsonify({'error': 'JSON array bekleniyor'}), 400
        
        sms_list = load_sms()
        added_count = 0
        
        for sms_data in data:
            if not isinstance(sms_data, dict):
                continue
                
            if 'message' not in sms_data or 'sender' not in sms_data:
                continue
            
            # Duplicate kontrolü (aynı gönderen ve mesaj varsa atla)
            is_duplicate = any(
                sms.get('sender') == sms_data.get('sender') and 
                sms.get('message') == sms_data.get('message')
                for sms in sms_list
            )
            
            if not is_duplicate:
                sms = {
                    'id': len(sms_list) + 1,
                    'sender': sms_data.get('sender', 'Bilinmeyen'),
                    'message': sms_data.get('message', ''),
                    'timestamp': sms_data.get('timestamp') or datetime.now().isoformat(),
                    'read': False
                }
                sms_list.append(sms)
                added_count += 1
        
        save_sms(sms_list)
        print(f"Toplu SMS: {added_count} yeni SMS eklendi (Toplam: {len(data)})")
        
        return jsonify({
            'success': True, 
            'added': added_count,
            'total_received': len(data)
        }), 201
        
    except Exception as e:
        print(f"Hata: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/health', methods=['GET'])
def health():
    """Sağlık kontrolü"""
    return jsonify({'status': 'ok'}), 200

@app.route('/')
def index():
    """Ana sayfa - Web arayüzü"""
    return render_template('index.html')

@app.route('/test')
def test_page():
    """Test SMS gönderme sayfası"""
    return render_template('test_send.html')

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """İstatistikler"""
    try:
        sms_list = load_sms()
        total = len(sms_list)
        unread = len([sms for sms in sms_list if not sms.get('read', False)])
        read = total - unread
        
        # Son 24 saatteki SMS sayısı
        now = datetime.now()
        recent = 0
        for sms in sms_list:
            try:
                sms_time = datetime.fromisoformat(sms.get('timestamp', ''))
                if (now - sms_time).total_seconds() < 86400:  # 24 saat
                    recent += 1
            except:
                pass
        
        return jsonify({
            'total': total,
            'unread': unread,
            'read': read,
            'recent_24h': recent
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sms/<int:sms_id>', methods=['DELETE'])
def delete_sms(sms_id):
    """SMS'i sil"""
    try:
        sms_list = load_sms()
        sms_list = [sms for sms in sms_list if sms['id'] != sms_id]
        save_sms(sms_list)
        return jsonify({'success': True}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("SMS Backend API başlatılıyor...")
    print("API: http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=True)

