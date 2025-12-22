import React, { useState, useEffect, useMemo } from 'react';
import { api } from './services/api';
import { cn } from './lib/utils';
import { Search, MessageSquare, Phone, Bell, Menu, RefreshCw, Smartphone } from 'lucide-react';
import { format } from 'date-fns';
import { tr } from 'date-fns/locale';

function App() {
  const [messages, setMessages] = useState([]);
  const [selectedSender, setSelectedSender] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [loading, setLoading] = useState(true);
  const [lastRefreshed, setLastRefreshed] = useState(new Date());

  const fetchData = async () => {
    setLoading(true);
    const data = await api.getMessages();
    setMessages(data);
    setLoading(false);
    setLastRefreshed(new Date());
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 5000); // Poll every 5s
    return () => clearInterval(interval);
  }, []);

  // Group messages by sender
  const conversations = useMemo(() => {
    const grouped = {};
    messages.forEach(msg => {
      if (!grouped[msg.sender]) {
        grouped[msg.sender] = [];
      }
      grouped[msg.sender].push(msg);
    });

    // Sort messages within conversation
    Object.keys(grouped).forEach(sender => {
      grouped[sender].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    });

    // Create array and sort by latest message
    return Object.entries(grouped)
      .map(([sender, msgs]) => ({
        sender,
        messages: msgs,
        lastMessage: msgs[msgs.length - 1],
        unreadCount: msgs.filter(m => !m.read).length
      }))
      .sort((a, b) => new Date(b.lastMessage.timestamp) - new Date(a.lastMessage.timestamp));
  }, [messages]);

  const filteredConversations = conversations.filter(c =>
    c.sender.toLowerCase().includes(searchTerm.toLowerCase()) ||
    c.lastMessage.message.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const activeConversation = selectedSender ? conversations.find(c => c.sender === selectedSender) : null;

  return (
    <div className="flex h-screen bg-background text-foreground overflow-hidden font-sans">
      {/* Sidebar - Contact List */}
      <div className="w-80 border-r border-border flex flex-col bg-card">
        {/* Header */}
        <div className="p-4 border-b border-border flex justify-between items-center bg-muted/20">
          <h1 className="text-xl font-bold flex items-center gap-2">
            <MessageSquare className="w-6 h-6 text-primary" />
            SMS Sync
          </h1>
          <button onClick={fetchData} className="p-2 hover:bg-accent rounded-full transition-colors">
            <RefreshCw className={cn("w-4 h-4", loading && "animate-spin")} />
          </button>
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
                  {format(new Date(conv.lastMessage.timestamp), 'HH:mm', { locale: tr })}
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
          {conversations.length} Sohbet • Son güncelleme: {format(lastRefreshed, 'HH:mm:ss')}
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
                  {selectedSender[0].toUpperCase()}
                </div>
                <div>
                  <h2 className="font-bold text-lg">{selectedSender}</h2>
                  <p className="text-xs text-muted-foreground flex items-center gap-1">
                    <Smartphone className="w-3 h-3" /> Mobil
                  </p>
                </div>
              </div>
              <div className="flex gap-2">
                <button className="p-2 hover:bg-accent rounded-full text-muted-foreground hover:text-foreground">
                  <Phone className="w-5 h-5" />
                </button>
                <button className="p-2 hover:bg-accent rounded-full text-muted-foreground hover:text-foreground">
                  <Bell className="w-5 h-5" />
                </button>
              </div>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-muted/5">
              {activeConversation?.messages.map((msg) => (
                <div key={msg.id} className="flex flex-col gap-1 items-start">
                  <div className="max-w-[70%] bg-card border border-border p-3 rounded-2xl rounded-tl-none shadow-sm">
                    <p className="text-sm leading-relaxed">{msg.message}</p>
                  </div>
                  <span className="text-[10px] text-muted-foreground ml-2">
                    {format(new Date(msg.timestamp), 'd MMM HH:mm', { locale: tr })}
                  </span>
                </div>
              ))}
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
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
