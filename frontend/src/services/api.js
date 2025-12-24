import axios from 'axios';

// Ensure we point to the correct port 5001 where the new backend runs
// Using absolute URL to avoid any relative path ambiguity in hybrid mode
const API_URL = 'http://127.0.0.1:5001/api';

export const api = {
    // Devices
    getDevices: async () => {
        try {
            const response = await axios.get(`${API_URL}/devices`);
            return response.data;
        } catch (error) {
            console.error("Error fetching devices:", error);
            return [];
        }
    },

    connectDevice: async (identifier, isIp = false) => {
        try {
            const payload = isIp ? { ip: identifier } : { serial: identifier };
            const response = await axios.post(`${API_URL}/connect`, payload);
            return response.data;
        } catch (error) {
            console.error("Error connecting device:", error);
            return { success: false };
        }
    },

    getStatus: async () => {
        try {
            const response = await axios.get(`${API_URL}/status`);
            return response.data;
        } catch (error) {
            return { active: false };
        }
    },

    // Get all SMS
    getMessages: async () => {
        try {
            const response = await axios.get(`${API_URL}/sms`);
            return response.data.sms_list || [];
        } catch (error) {
            console.error("Error fetching messages:", error);
            return [];
        }
    },

    // Get unread count or messages
    getUnread: async () => {
        try {
            const response = await axios.get(`${API_URL}/sms/unread`);
            return response.data.sms_list || [];
        } catch (error) {
            console.error("Error fetching unread:", error);
            return [];
        }
    },

    // Mark status
    markRead: async (id) => {
        try {
            await axios.post(`${API_URL}/sms/${id}/read`, { read: true });
            return true;
        } catch (error) {
            console.error("Error marking read:", error);
            return false;
        }
    },

    // Stats
    getStats: async () => {
        try {
            const response = await axios.get(`${API_URL}/stats`);
            return response.data;
        } catch (error) {
            console.error("Error stats:", error);
            return null;
        }
    },

    // Block Sender
    blockSender: async (sender) => {
        try {
            const response = await axios.post(`${API_URL}/block`, { sender });
            return response.data;
        } catch (error) {
            console.error("Error blocking sender:", error);
            return { success: false };
        }
    },

    // Disconnect
    disconnect: async () => {
        try {
            const response = await axios.post(`${API_URL}/disconnect`);
            return response.data;
        } catch (error) {
            console.error("Error disconnecting:", error);
            return { success: false };
        }
    },

    // Get Connection Logs
    getLogs: async () => {
        try {
            const response = await axios.get(`${API_URL}/logs`);
            return response.data.logs || [];
        } catch (error) {
            console.error("Error fetching logs:", error);
            return [];
        }
    },

    // Get Config
    getConfig: async () => {
        try {
            const response = await axios.get(`${API_URL}/config`);
            return response.data;
        } catch (error) {
            console.error("Error fetching config:", error);
            return { sound_enabled: true, notification_enabled: true };
        }
    },

    // Test Notification
    testNotification: async () => {
        try {
            const response = await axios.post(`${API_URL}/test_notification`);
            return response.data;
        } catch (error) {
            console.error("Error testing notification:", error);
            return { success: false };
        }
    },

    // Save Config
    saveConfig: async (config) => {
        try {
            const response = await axios.post(`${API_URL}/config`, config);
            return response.data;
        } catch (error) {
            console.error("Error saving config:", error);
            return { success: false };
        }
    }
};
