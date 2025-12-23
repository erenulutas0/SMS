import axios from 'axios';

// In production (served by Flask), relative path works best.
// In dev (Vite), we might need a proxy or full URL.
const isDev = import.meta.env.DEV;
const API_URL = isDev ? 'http://localhost:5000/api' : '/api';

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

    connectDevice: async (serial) => {
        try {
            const response = await axios.post(`${API_URL}/connect`, { serial });
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

    // Get server config/IP (if implemented backend side, else mock/fail)
    getConfig: async () => {
        // Future proofing
        return {};
    }
};
