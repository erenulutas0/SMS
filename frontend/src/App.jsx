import React, { useState, useEffect, useMemo, useRef } from 'react';
import { api } from './services/api';
import { cn, parseDate, formatDate } from './lib/utils';
import { Search, MessageSquare, Phone, Bell, Menu, RefreshCw, Smartphone, Plug, CheckCircle2, XCircle, Settings, Ban, Wifi, History, Power } from 'lucide-react';

// Helper to safely parse dates moved to utils

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error("Uncaught error:", error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center h-screen bg-background text-foreground p-8">
          <h1 className="text-2xl font-bold mb-4 text-red-500">Bir hata oluştu</h1>
          <pre className="bg-muted p-4 rounded text-xs overflow-auto max-w-full mb-4 border border-border">
            {this.state.error?.toString()}
          </pre>
          <button
            onClick={() => window.location.reload()}
            className="px-4 py-2 bg-primary text-primary-foreground rounded hover:bg-primary/90"
          >
            Yeniden Yükle
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}

function App() {
  const [messages, setMessages] = useState([]);
  const [selectedSender, setSelectedSender] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [lastRefreshed, setLastRefreshed] = useState(new Date());

  // Device State
  const [showDeviceModal, setShowDeviceModal] = useState(false);
  const [devices, setDevices] = useState([]);
  const [syncStatus, setSyncStatus] = useState({ active: false, device: null });
  const [connecting, setConnecting] = useState(false);
  const [manualIp, setManualIp] = useState('');

  // Logs State
  const [showLogsModal, setShowLogsModal] = useState(false);
  const [logs, setLogs] = useState([]);

  // Settings State
  const [showSettingsModal, setShowSettingsModal] = useState(false);
  const [appConfig, setAppConfig] = useState({ sound_enabled: true, notification_enabled: true });

  const fetchData = async () => {
    setLoading(true);
    const data = await api.getMessages();
    setMessages(data);
    setLoading(false);
    setLastRefreshed(new Date());

    // Also check status
    const status = await api.getStatus();
    setSyncStatus(status);
  };

  const fetchDevices = async () => {
    const list = await api.getDevices();
    setDevices(list);
  };

  const handleConnect = async (identifier, isIp = false) => {
    setConnecting(true);
    await api.connectDevice(identifier, isIp);
    setConnecting(false);
    await fetchData(); // Refresh status
  };

  const handleDisconnect = async () => {
    if (confirm("Bağlantıyı kesmek istediğinize emin misiniz? Mevcut mesajlar temizlenecektir.")) {
      await api.disconnect();
      setMessages([]); // Clear locally immediately
      setSelectedSender(null);
      await fetchData(); // Refresh status
    }
  };

  const openLogs = async () => {
    const logData = await api.getLogs();
    setLogs(logData.reverse()); // Show newest first
    setShowLogsModal(true);
  };

  const openSettings = async () => {
    const config = await api.getConfig();
    setAppConfig(config);
    setShowSettingsModal(true);
  };

  const saveSettings = async (newConfig) => {
    // 1. Optimistic Update (Immediate Feedback)
    setAppConfig(newConfig);

    // 2. Perform Save
    const res = await api.saveConfig(newConfig);

    // 3. Revert on failure
    if (!res.success) {
      console.error("Failed to save config, reverting.");
      const old = await api.getConfig();
      setAppConfig(old);
    } else {
      setAppConfig(res.config);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000); // Poll every 5s
    return () => clearInterval(interval);
  }, []);

  // Show modal if not connected and no messages (first run)
  useEffect(() => {
    api.getStatus().then(status => {
      setSyncStatus(status);
      if (!status.active && messages.length === 0) {
        // Optionally auto-open modal, but might be annoying. Let's just rely on the button.
      }
    });
  }, [messages.length]);

  // ... inside App component

  // Sound Effect (Simple Pop)
  // Refs for scrolling
  const messagesEndRef = useRef(null);
  const chatContainerRef = useRef(null);

  // Scroll Helpers
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'auto' });
  };

  const scrollToTop = () => {
    chatContainerRef.current?.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const scrollToBottomSmooth = () => {
    chatContainerRef.current?.scrollTo({ top: chatContainerRef.current.scrollHeight, behavior: 'smooth' });
  };

  // Auto-scroll on conversation change or new message
  // Note: activeConversation is defined after conversations useMemo below
  // This effect will run after all hooks are set up
  const scrollEffectRef = useRef(false);

  useEffect(() => {
    // Will be triggered by selectedSender change
    scrollEffectRef.current = true;
  }, [selectedSender]);

  // State for tracking unread count (Title/Badge Only)
  const [prevUnreadCount, setPrevUnreadCount] = useState(0);

  // Group messages by sender
  const conversations = useMemo(() => {
    const grouped = {};
    messages.forEach(msg => {
      const key = msg.sender;
      if (!grouped[key]) {
        grouped[key] = [];
      }
      grouped[key].push(msg);
    });

    Object.keys(grouped).forEach(sender => {
      grouped[sender].sort((a, b) => parseDate(a.timestamp) - parseDate(b.timestamp));
    });

    return Object.entries(grouped)
      .map(([sender, msgs]) => ({
        sender,
        messages: msgs,
        lastMessage: msgs[msgs.length - 1],
        unreadCount: msgs.filter(m => !m.read).length
      }))
      .sort((a, b) => parseDate(b.lastMessage.timestamp) - parseDate(a.lastMessage.timestamp));
  }, [messages]);

  // Notification Effect (Title/Badge Only)
  useEffect(() => {
    const totalUnread = conversations.reduce((acc, c) => acc + c.unreadCount, 0);

    // 1. Update Title
    if (totalUnread > 0) {
      document.title = `(${totalUnread}) SMS Sync`;
    } else {
      document.title = "SMS Sync";
    }

    // 2. Update Taskbar Badge (Safety Check)
    try {
      if ('setAppBadge' in navigator && navigator.setAppBadge) {
        if (totalUnread > 0) {
          navigator.setAppBadge(totalUnread).catch(() => { }); // Silent catch
        } else {
          navigator.clearAppBadge().catch(() => { }); // Silent catch
        }
      }
    } catch (e) {
      // Ignore badge errors in non-PWA/webview contexts
    }

    setPrevUnreadCount(totalUnread);
  }, [conversations]);


  const filteredConversations = conversations.filter(c =>
    c.sender.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.lastMessage.message.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const activeConversation = selectedSender ? conversations.find(c => c.sender === selectedSender) : null;

  // Auto-scroll effect (moved here because activeConversation must be defined first)
  useEffect(() => {
    if (activeConversation && scrollEffectRef.current) {
      scrollToBottom();
      scrollEffectRef.current = false;
    }
  }, [activeConversation, selectedSender]);

  return (
    <ErrorBoundary>
      <div className="flex h-screen bg-background text-foreground overflow-hidden font-sans relative">
        {/* ... existing Render ... */}

        {/* Device Modal */}
        {showDeviceModal && (
          <div className="absolute inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
            <div className="bg-card w-full max-w-md rounded-xl border border-border shadow-2xl p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-bold flex items-center gap-2">
                  <Smartphone className="w-6 h-6 text-primary" />
                  Cihaz Bağlantısı
                </h2>
                <button
                  onClick={() => setShowDeviceModal(false)}
                  className="p-1 hover:bg-accent rounded-full"
                >
                  <XCircle className="w-6 h-6 text-muted-foreground" />
                </button>
              </div>

              <div className="space-y-6">

                {/* WiFi Connection */}
                <div className="bg-muted/30 p-4 rounded-lg border border-border">
                  <div className="flex items-center gap-2 mb-3">
                    <Wifi className="w-4 h-4 text-primary" />
                    <h3 className="font-medium text-sm">Kablosuz Bağlantı (Wi-Fi)</h3>
                  </div>
                  <p className="text-xs text-muted-foreground mb-3">
                    Telefondaki uygulamayı açın ve ekranda yazan IP adresini buraya girin.
                  </p>
                  <div className="flex gap-2">
                    <input
                      type="text"
                      placeholder="Örn: 192.168.1.35"
                      className="flex-1 p-2 rounded border border-input bg-background/50 text-sm focus:ring-1 focus:ring-primary outline-none"
                      value={manualIp}
                      onChange={(e) => setManualIp(e.target.value)}
                    />
                    <button
                      onClick={() => handleConnect(manualIp, true)}
                      disabled={connecting || !manualIp}
                      className="bg-primary hover:bg-primary/90 text-primary-foreground px-4 py-2 rounded text-sm font-medium disabled:opacity-50"
                    >
                      {connecting ? '...' : 'Bağlan'}
                    </button>
                  </div>
                </div>

                <div className="relative">
                  <div className="absolute inset-0 flex items-center"><span className="w-full border-t border-border"></span></div>
                  <div className="relative flex justify-center text-xs uppercase"><span className="bg-card px-2 text-muted-foreground">Veya USB (ADB)</span></div>
                </div>

                {/* ADB Connection */}
                <div>
                  <div className="flex justify-between items-center mb-2">
                    <h3 className="font-medium text-sm text-muted-foreground">Kablolu Cihazlar</h3>
                    <button
                      onClick={fetchDevices}
                      className="text-xs text-primary hover:underline flex items-center gap-1"
                    >
                      <RefreshCw className="w-3 h-3" /> Yenile
                    </button>
                  </div>

                  {devices.length === 0 ? (
                    <div className="p-4 bg-muted/30 rounded-lg text-center text-sm text-muted-foreground border border-dashed border-border">
                      <p>Kablolu cihaz bulunamadı.</p>
                      <p className="mt-1 text-xs opacity-70">Lütfen telefonunuzu USB ile bağlayın ve USB Hata Ayıklama modunu açın.</p>
                    </div>
                  ) : (
                    <div className="space-y-2">
                      {devices.map(dev => (
                        <div key={dev.serial} className="flex items-center justify-between p-3 bg-muted/30 rounded-lg border border-border">
                          <div className="flex items-center gap-3">
                            <Smartphone className="w-5 h-5 text-foreground" />
                            <div>
                              <p className="font-medium">{dev.serial}</p>
                              <p className="text-xs text-muted-foreground capitalize">{dev.state}</p>
                            </div>
                          </div>
                          <button
                            onClick={() => handleConnect(dev.serial, false)}
                            disabled={syncStatus.active && syncStatus.device === dev.serial}
                            className={cn(
                              "px-3 py-1.5 rounded-md text-sm font-medium transition-all",
                              syncStatus.active && syncStatus.device === dev.serial
                                ? "bg-green-500/10 text-green-500 cursor-default"
                                : "bg-primary text-primary-foreground hover:bg-primary/90"
                            )}
                          >
                            {syncStatus.active && syncStatus.device === dev.serial ? 'Bağlı' : 'Bağlan'}
                          </button>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-border">
                <div className="flex items-center gap-2 text-sm text-muted-foreground">
                  {syncStatus.active ? (
                    <>
                      {syncStatus.type === 'wifi' ? (
                        <Wifi className="w-4 h-4 text-green-500" />
                      ) : (
                        <CheckCircle2 className="w-4 h-4 text-green-500" />
                      )}
                      <span>
                        {syncStatus.type === 'wifi' ? 'Wi-Fi Senkronizasyon: ' : 'USB Senkronizasyon: '}
                        <span className="text-foreground font-medium">{syncStatus.device}</span>
                      </span>
                    </>
                  ) : (
                    <>
                      <Plug className="w-4 h-4" />
                      <span>Aktif bağlantı yok.</span>
                    </>
                  )}
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Logs Modal */}
        {showLogsModal && (
          <div className="absolute inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
            <div className="bg-card w-full max-w-2xl rounded-xl border border-border shadow-2xl p-6 h-[80vh] flex flex-col">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-bold flex items-center gap-2">
                  <History className="w-6 h-6 text-primary" />
                  Bağlantı Kayıtları
                </h2>
                <button
                  onClick={() => setShowLogsModal(false)}
                  className="p-1 hover:bg-accent rounded-full"
                >
                  <XCircle className="w-6 h-6 text-muted-foreground" />
                </button>
              </div>

              <div className="flex-1 overflow-y-auto border border-border rounded-lg">
                <table className="w-full text-sm text-left">
                  <thead className="bg-muted text-muted-foreground">
                    <tr>
                      <th className="p-3 font-medium">Tür</th>
                      <th className="p-3 font-medium">Mod</th>
                      <th className="p-3 font-medium">Hedef</th>
                      <th className="p-3 font-medium">Zaman</th>
                    </tr>
                  </thead>
                  <tbody>
                    {logs.length === 0 ? (
                      <tr>
                        <td colSpan={4} className="p-8 text-center text-muted-foreground">Kayıt bulunamadı.</td>
                      </tr>
                    ) : (
                      logs.map((log, idx) => (
                        <tr key={idx} className="border-b border-border/50 hover:bg-muted/20">
                          <td className="p-3">
                            <span className={cn(
                              "px-2 py-0.5 rounded text-xs font-bold uppercase",
                              log.type === 'connect' ? "bg-green-500/10 text-green-600" : "bg-red-500/10 text-red-600"
                            )}>
                              {log.type === 'connect' ? 'Bağlandı' : 'Ayrıldı'}
                            </span>
                          </td>
                          <td className="p-3 uppercase text-xs">{log.mode}</td>
                          <td className="p-3 font-mono text-xs">{log.target}</td>
                          <td className="p-3 text-muted-foreground">
                            {log.type === 'connect' ? formatDate(log.time, 'd MMM HH:mm:ss') : formatDate(log.end_time || log.time, 'd MMM HH:mm:ss')}
                          </td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}


        {/* Settings Modal */}
        {showSettingsModal && (
          <div className="absolute inset-0 z-50 bg-black/50 flex items-center justify-center p-4">
            <div className="bg-card w-full max-w-sm rounded-xl border border-border shadow-2xl p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-bold flex items-center gap-2">
                  <Settings className="w-6 h-6 text-primary" />
                  Ayarlar
                </h2>
                <button
                  onClick={() => setShowSettingsModal(false)}
                  className="p-1 hover:bg-accent rounded-full"
                >
                  <XCircle className="w-6 h-6 text-muted-foreground" />
                </button>
              </div>

              <div className="space-y-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium">Sesli Bildirim</h3>
                    <p className="text-xs text-muted-foreground">Yeni mesaj gelince özel sesi çal.</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      className="sr-only peer"
                      checked={appConfig.sound_enabled}
                      onChange={(e) => setAppConfig({ ...appConfig, sound_enabled: e.target.checked })}
                    />
                    <div className="w-11 h-6 bg-muted peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-primary rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                  </label>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="font-medium">Masaüstü Bildirimi</h3>
                    <p className="text-xs text-muted-foreground">Uygulama arka plandayken bildirim göster.</p>
                  </div>
                  <label className="relative inline-flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      className="sr-only peer"
                      checked={appConfig.notification_enabled}
                      onChange={(e) => setAppConfig({ ...appConfig, notification_enabled: e.target.checked })}
                    />
                    <div className="w-11 h-6 bg-muted peer-focus:outline-none peer-focus:ring-2 peer-focus:ring-primary rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-primary"></div>
                  </label>
                </div>

                <div className="pt-4 flex justify-between gap-2">
                  <button
                    onClick={() => api.testNotification()}
                    className="px-4 py-2 text-sm font-medium border border-input hover:bg-muted rounded-md transition-colors"
                  >
                    Test Bildirimi
                  </button>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setShowSettingsModal(false)}
                      className="px-4 py-2 text-sm font-medium hover:bg-muted rounded-md transition-colors"
                    >
                      Vazgeç
                    </button>
                    <button
                      onClick={() => saveSettings(appConfig).then(() => setShowSettingsModal(false))}
                      className="px-4 py-2 text-sm font-medium bg-primary text-primary-foreground hover:bg-primary/90 rounded-md transition-colors shadow"
                    >
                      Kaydet
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )
        }

        {/* Sidebar - Contact List */}
        <div className="w-80 border-r border-border flex flex-col bg-card">
          {/* Header */}
          <div className="p-4 border-b border-border flex justify-between items-center bg-muted/20">
            <h1 className="text-xl font-bold flex items-center gap-2">
              <MessageSquare className="w-6 h-6 text-primary" />
              SMS Sync
            </h1>
            <div className="flex gap-1">
              <button
                onClick={() => { setShowDeviceModal(true); fetchDevices(); }}
                className={cn("p-2 hover:bg-accent rounded-full transition-colors", !syncStatus.active && "animate-pulse text-yellow-500")}
                title="Cihaz Bağla"
              >
                <Smartphone className="w-4 h-4" />
              </button>
              <button
                onClick={openSettings}
                className="p-2 hover:bg-accent rounded-full transition-colors"
                title="Ayarlar"
              >
                <Settings className="w-4 h-4" />
              </button>
              <button onClick={fetchData} className="p-2 hover:bg-accent rounded-full transition-colors">
                <RefreshCw className={cn("w-4 h-4", loading && "animate-spin")} />
              </button>
              <button onClick={openLogs} className="p-2 hover:bg-accent rounded-full transition-colors" title="Bağlantı Kayıtları">
                <History className="w-4 h-4" />
              </button>
              {syncStatus.active && (
                <button
                  onClick={handleDisconnect}
                  className="p-2 hover:bg-red-500/10 text-red-500 rounded-full transition-colors"
                  title="Bağlantıyı Kes"
                >
                  <Power className="w-4 h-4" />
                </button>
              )}
            </div>
          </div>

          {/* Search */}
          <div className="p-3">
            <div className="relative">
              <Search className="absolute left-3 top-2.5 h-4 w-4 text-muted-foreground" />
              <input
                type="text"
                placeholder="Ara..."
                className="w-full pl-9 pr-4 py-2 bg-muted/50 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-ring"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>

          {/* List */}
          <div className="flex-1 overflow-y-auto">
            {conversations.length === 0 && !loading && (
              <div className="flex flex-col items-center justify-center h-48 text-muted-foreground p-4 text-center">
                <p className="mb-2">Görüntülenecek mesaj yok.</p>
                <button
                  onClick={() => { setShowDeviceModal(true); fetchDevices(); }}
                  className="text-primary hover:underline text-sm"
                >
                  Cihaz Bağla
                </button>
              </div>
            )}
            {filteredConversations.map((conv) => (
              <div
                key={conv.sender}
                onClick={() => setSelectedSender(conv.sender)}
                className={cn(
                  "p-4 border-b border-border/50 cursor-pointer hover:bg-accent/50 transition-all",
                  selectedSender === conv.sender && "bg-accent border-l-4 border-l-primary"
                )}
              >
                <div className="flex justify-between items-start mb-1">
                  <span className="font-semibold truncate max-w-[180px]">{conv.sender}</span>
                  <span className="text-xs text-muted-foreground">
                    {formatDate(conv.lastMessage.timestamp, 'HH:mm')}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <p className={cn(
                    "text-sm truncate max-w-[220px]",
                    conv.unreadCount > 0 ? "text-foreground font-medium" : "text-muted-foreground"
                  )}>
                    {conv.lastMessage.message}
                  </p>
                  {conv.unreadCount > 0 && (
                    <span className="bg-primary text-primary-foreground text-xs font-bold px-2 py-0.5 rounded-full ml-2">
                      {conv.unreadCount}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>

          <div className="p-3 border-t border-border text-xs text-center text-muted-foreground bg-muted/10">
            {conversations.length} Sohbet • Son güncelleme: {formatDate(lastRefreshed, 'HH:mm:ss')}
          </div>
        </div>

        {/* Main Chat Area */}
        <div className="flex-1 flex flex-col bg-background/50 relative">
          {selectedSender ? (
            <>
              {/* Header */}
              <div className="p-4 border-b border-border flex justify-between items-center bg-card shadow-sm z-10">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-br from-primary to-purple-600 flex items-center justify-center text-white font-bold text-lg shadow-lg">
                    {selectedSender[0]?.toUpperCase() || '?'}
                  </div>
                  <div>
                    <h2 className="font-bold text-lg">{selectedSender}</h2>
                    <p className="text-xs text-muted-foreground flex items-center gap-1">
                      <Smartphone className="w-3 h-3" /> Mobil
                    </p>
                  </div>
                </div>
                <div className="flex gap-2">
                  <button
                    onClick={async () => {
                      if (confirm(`${selectedSender} engellensin mi? Bu kişiden gelen mesajlar artık görünmeyecek.`)) {
                        await api.blockSender(selectedSender);
                        setSelectedSender(null);
                        fetchData();
                      }
                    }}
                    className="p-2 hover:bg-red-500/10 hover:text-red-500 rounded-full text-muted-foreground transition-all"
                    title="Numarayı Engelle"
                  >
                    <Ban className="w-5 h-5" />
                  </button>
                  <button className="p-2 hover:bg-accent rounded-full text-muted-foreground hover:text-foreground">
                    <Phone className="w-5 h-5" />
                  </button>
                  <button className="p-2 hover:bg-accent rounded-full text-muted-foreground hover:text-foreground">
                    <Bell className="w-5 h-5" />
                  </button>
                </div>
              </div>

              {/* Messages */}
              <div ref={chatContainerRef} className="flex-1 overflow-y-auto p-4 space-y-4 bg-muted/5 relative scroll-smooth">
                {activeConversation?.messages.map((msg) => (
                  <div key={msg.id} className="flex flex-col gap-1 items-start">
                    <div className="max-w-[70%] bg-card border border-border p-3 rounded-2xl border-l-4 border-l-primary shadow-sm">
                      <p className="text-sm leading-relaxed whitespace-pre-wrap">{msg.message}</p>
                    </div>
                    <span className="text-[10px] text-muted-foreground ml-2">
                      {formatDate(msg.timestamp, 'd MMM HH:mm')}
                    </span>
                  </div>
                ))}
                <div ref={messagesEndRef} />

                {/* Floating Scroll Buttons */}
                <div className="fixed right-6 bottom-24 flex flex-col gap-2 z-20">
                  <button
                    onClick={scrollToTop}
                    className="p-2 bg-primary/80 hover:bg-primary text-white rounded-full shadow-lg backdrop-blur-sm transition-all"
                    title="En Üste Git"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m18 15-6-6-6 6" /></svg>
                  </button>
                  <button
                    onClick={scrollToBottomSmooth}
                    className="p-2 bg-primary/80 hover:bg-primary text-white rounded-full shadow-lg backdrop-blur-sm transition-all"
                    title="En Alta Git"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m6 9 6 6 6-6" /></svg>
                  </button>
                </div>
              </div>

              {/* Input Placeholder (Read Only for now) */}
              <div className="p-4 border-t border-border bg-card">
                <div className="flex gap-2">
                  <input
                    disabled
                    placeholder="Bu sürümde cevap yazılamaz (Sadece Okuma)"
                    className="flex-1 p-3 rounded-lg border border-input bg-muted/50 text-sm cursor-not-allowed opacity-70"
                  />
                </div>
              </div>
            </>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-muted-foreground">
              <div className="w-24 h-24 bg-primary/10 rounded-full flex items-center justify-center mb-6 animate-pulse">
                <MessageSquare className="w-10 h-10 text-primary" />
              </div>
              <h3 className="text-2xl font-bold text-foreground mb-2">SMS Senkronizasyon</h3>
              <p>Mesajlarınızı görüntülemek için soldan bir sohbet seçin.</p>
              {devices.length > 0 && !syncStatus.active && (
                <button
                  onClick={() => { setShowDeviceModal(true); }}
                  className="mt-4 text-primary font-medium hover:underline"
                >
                  Bağlantıyı Başlat
                </button>
              )}
            </div>
          )}
        </div>
      </div >
    </ErrorBoundary >
  );
}

export default App;
