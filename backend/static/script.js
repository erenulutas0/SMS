let allSMS = [];
let filteredSMS = [];
let currentFilter = 'all';
let currentSMSId = null;
let refreshInterval = null;

// Sayfa yüklendiğinde
document.addEventListener('DOMContentLoaded', function() {
    loadSMS();
    loadStats();
    
    // Otomatik yenileme (her 5 saniyede bir)
    refreshInterval = setInterval(() => {
        loadSMS();
        loadStats();
    }, 5000);
    
    // Modal dışına tıklanınca kapat
    document.getElementById('smsModal').addEventListener('click', function(e) {
        if (e.target === this) {
            closeModal();
        }
    });
});

// SMS'leri yükle
async function loadSMS() {
    try {
        const response = await fetch('/api/sms');
        if (!response.ok) throw new Error('API hatası');
        
        const data = await response.json();
        console.log('API yanıtı:', data); // Debug
        
        allSMS = data.sms_list || [];
        console.log('Yüklenen SMS sayısı:', allSMS.length); // Debug
        
        // Backend zaten reverse yapıyor, tekrar yapmaya gerek yok
        // allSMS.reverse(); // Kaldırıldı
        
        filterSMS();
        updateStatusIndicator(true);
    } catch (error) {
        console.error('SMS yükleme hatası:', error);
        updateStatusIndicator(false);
        showError('SMS\'ler yüklenemedi. Backend çalışıyor mu?');
    }
}

// İstatistikleri yükle
async function loadStats() {
    try {
        const response = await fetch('/api/stats');
        if (!response.ok) throw new Error('API hatası');
        
        const data = await response.json();
        document.getElementById('statTotal').textContent = data.total || 0;
        document.getElementById('statUnread').textContent = data.unread || 0;
        document.getElementById('statRead').textContent = data.read || 0;
        document.getElementById('statRecent').textContent = data.recent_24h || 0;
    } catch (error) {
        console.error('İstatistik yükleme hatası:', error);
    }
}

// SMS'leri filtrele
function filterSMS() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    
    filteredSMS = allSMS.filter(sms => {
        const matchesFilter = 
            currentFilter === 'all' ||
            (currentFilter === 'unread' && !sms.read) ||
            (currentFilter === 'read' && sms.read);
        
        const matchesSearch = 
            !searchTerm ||
            sms.sender.toLowerCase().includes(searchTerm) ||
            sms.message.toLowerCase().includes(searchTerm);
        
        return matchesFilter && matchesSearch;
    });
    
    renderSMS();
}

// Filtre değiştir
function setFilter(filter) {
    currentFilter = filter;
    
    // Butonları güncelle
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`[data-filter="${filter}"]`).classList.add('active');
    
    filterSMS();
}

// SMS'leri render et
function renderSMS() {
    const container = document.getElementById('smsList');
    
    console.log('Toplam SMS:', allSMS.length);
    console.log('Filtrelenmiş SMS:', filteredSMS.length);
    
    if (filteredSMS.length === 0) {
        if (allSMS.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-inbox"></i>
                    <p>SMS bulunamadı</p>
                    <p style="margin-top: 10px; font-size: 14px; color: var(--text-muted);">
                        Henüz SMS yok. Test SMS göndermek için:<br>
                        <a href="/test" style="color: var(--primary); text-decoration: none; margin-top: 10px; display: inline-block; padding: 8px 16px; background: var(--bg-lighter); border-radius: 8px;">
                            <i class="fas fa-paper-plane"></i> Test SMS Gönder
                        </a>
                    </p>
                </div>
            `;
        } else {
            container.innerHTML = `
                <div class="empty-state">
                    <i class="fas fa-filter"></i>
                    <p>Filtreye uygun SMS bulunamadı</p>
                    <p style="margin-top: 10px; font-size: 14px; color: var(--text-muted);">
                        Arama terimini değiştirin veya farklı bir filtre seçin.
                    </p>
                </div>
            `;
        }
        return;
    }
    
    container.innerHTML = filteredSMS.map(sms => {
        const time = formatTime(sms.timestamp);
        const initials = getInitials(sms.sender);
        const preview = sms.message && sms.message.length > 100 
            ? sms.message.substring(0, 100) + '...' 
            : (sms.message || '');
        
        return `
            <div class="sms-item ${sms.read ? '' : 'unread'}" onclick="openModal(${sms.id})">
                <div class="sms-avatar">${initials}</div>
                <div class="sms-content">
                    <div class="sms-header">
                        <span class="sms-sender">${escapeHtml(sms.sender || 'Bilinmeyen')}</span>
                        <span class="sms-time">${time}</span>
                    </div>
                    <div class="sms-message">${escapeHtml(preview)}</div>
                    ${!sms.read ? '<div class="sms-badge unread"><i class="fas fa-circle"></i> Okunmamış</div>' : ''}
                </div>
            </div>
        `;
    }).join('');
}

// Modal aç
function openModal(smsId) {
    const sms = allSMS.find(s => s.id === smsId);
    if (!sms) return;
    
    currentSMSId = smsId;
    document.getElementById('modalSender').textContent = sms.sender;
    document.getElementById('modalTime').textContent = formatTime(sms.timestamp);
    document.getElementById('modalMessage').textContent = sms.message;
    
    const statusBadge = document.getElementById('modalStatus');
    if (sms.read) {
        statusBadge.innerHTML = '<span class="sms-badge"><i class="fas fa-check"></i> Okundu</span>';
        document.getElementById('markReadBtn').textContent = 'Okunmadı İşaretle';
    } else {
        statusBadge.innerHTML = '<span class="sms-badge unread"><i class="fas fa-circle"></i> Okunmamış</span>';
        document.getElementById('markReadBtn').textContent = 'Okundu İşaretle';
    }
    
    document.getElementById('smsModal').classList.add('show');
    
    // SMS'i okundu olarak işaretle (otomatik)
    if (!sms.read) {
        markAsRead(smsId, false);
    }
}

// Modal kapat
function closeModal() {
    document.getElementById('smsModal').classList.remove('show');
    currentSMSId = null;
}

// Okundu/Okunmadı işaretle
async function toggleRead() {
    if (!currentSMSId) return;
    
    const sms = allSMS.find(s => s.id === currentSMSId);
    if (!sms) return;
    
    await markAsRead(currentSMSId, !sms.read);
    closeModal();
    loadSMS();
    loadStats();
}

// SMS'i okundu/okunmadı olarak işaretle
async function markAsRead(smsId, read) {
    try {
        const response = await fetch(`/api/sms/${smsId}/read`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ read: read })
        });
        if (!response.ok) throw new Error('İşaretleme hatası');
    } catch (error) {
        console.error('İşaretleme hatası:', error);
        showError('SMS işaretlenemedi');
    }
}

// SMS sil
async function deleteSMS() {
    if (!currentSMSId) return;
    
    if (!confirm('Bu SMS\'i silmek istediğinize emin misiniz?')) {
        return;
    }
    
    try {
        const response = await fetch(`/api/sms/${currentSMSId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) throw new Error('Silme hatası');
        
        closeModal();
        loadSMS();
        loadStats();
        showSuccess('SMS silindi');
    } catch (error) {
        console.error('Silme hatası:', error);
        showError('SMS silinemedi');
    }
}

// Yenile
function refreshSMS() {
    const btn = event.target.closest('.btn-refresh');
    if (btn) {
        btn.querySelector('i').classList.add('fa-spin');
        setTimeout(() => {
            btn.querySelector('i').classList.remove('fa-spin');
        }, 1000);
    }
    
    loadSMS();
    loadStats();
}

// Zaman formatla
function formatTime(timestamp) {
    try {
        const date = new Date(timestamp);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 60000) return 'Az önce';
        if (diff < 3600000) return `${Math.floor(diff / 60000)} dakika önce`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)} saat önce`;
        
        return date.toLocaleDateString('tr-TR', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    } catch (e) {
        return timestamp;
    }
}

// İsim baş harfleri
function getInitials(name) {
    if (!name) return '?';
    const parts = name.split(' ');
    if (parts.length >= 2) {
        return (parts[0][0] + parts[1][0]).toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
}

// HTML escape
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Durum göstergesi güncelle
function updateStatusIndicator(connected) {
    const indicator = document.getElementById('statusIndicator');
    if (connected) {
        indicator.innerHTML = '<i class="fas fa-circle"></i> Bağlı';
        indicator.querySelector('i').style.color = '#10b981';
    } else {
        indicator.innerHTML = '<i class="fas fa-circle"></i> Bağlantı Yok';
        indicator.querySelector('i').style.color = '#ef4444';
    }
}

// Hata mesajı göster
function showError(message) {
    // Basit bir toast notification (geliştirilebilir)
    console.error(message);
}

// Başarı mesajı göster
function showSuccess(message) {
    // Basit bir toast notification (geliştirilebilir)
    console.log(message);
}

