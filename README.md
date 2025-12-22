# 📱 SMS Sync: Android to Desktop

**SMS Sync** is a modern, open-source application that bridges your Android phone and Windows desktop. It synchronizes your SMS messages in real-time using **ADB (Android Debug Bridge)** and displays them in a sleek, **Dark Mode React UI**.

![Project Screenshot](https://via.placeholder.com/1200x600?text=SMS+Sync+Dashboard)

## ✨ Features

*   **⚡ Real-Time Sync**: Instantly fetches messages from your phone via USB (ADB).
*   **🎨 Modern UI**: Beautiful, responsive dashboard built with **React**, **Vite**, and **Tailwind CSS**.
*   **🌑 Dark Mode**: Easy on the eyes with a premium dark theme.
*   **🔍 Search**: Quickly find messages by sender or content.
*   **🔒 Privacy Focused**: Data is stored locally on your machine. No external servers involved.
*   **📦 Zero-App Dependency**: Uses ADB directly, so you don't strictly *need* to install an APK on your phone if USB debugging is enabled.

## 🛠️ Tech Stack

*   **Frontend**: React.js, Vite, Tailwind CSS, Lucide Icons
*   **Backend**: Python, Flask
*   **Sync**: Python (ADB Shell)

## 🚀 Getting Started

### Prerequisites

*   **Python 3.8+** installed.
*   **Node.js** (for the frontend).
*   **ADB (Android Debug Bridge)** installed and added to your system PATH.
    *   *Windows*: [Download Platform Tools](https://developer.android.com/studio/releases/platform-tools)
*   **Android Phone** with **USB Debugging** enabled.

### 📥 Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/erenulutas0/SMS.git
    cd SMS
    ```

2.  **Setup the Backend**:
    ```bash
    # Create virtual environment
    python -m venv venv
    
    # Activate script (Windows)
    .\venv\Scripts\activate
    
    # Install dependencies
    pip install -r requirements.txt
    ```

3.  **Setup the Frontend**:
    ```bash
    cd frontend
    npm install
    cd ..
    ```

## 🎮 Usage

You can run the entire system with a single script, or run components individually.

### Option 1: One-Click Start (Recommended)

1.  Connect your Android phone via USB.
2.  Double-click **`start_modern_app.bat`** to start the Backend and Web UI.
3.  Double-click **`start_adb_sync.bat`** to start the SMS extraction engine.
4.  Open your browser at **http://localhost:5173**.

### Option 2: Manual Start

**1. Start Backend:**
```bash
python backend/app.py
```

**2. Start Frontend:**
```bash
cd frontend
npm run dev
```

**3. Start Syncing:**
```bash
python adb_sync.py
```

## ⚠️ Important Notes

*   **USB Debugging**: You must accept the USB Debugging prompt on your phone when you first connect it.
*   **Sensitive Data**: Messages are stored in `backend/sms_storage.json`. This file is **ignored** in git to protect your privacy. Do not commit it manually.

## 🤝 Contributing

Contributions are welcome! Feel free to open issues or submit pull requests.

## 📄 License

This project is licensed under the MIT License.
