import axios from 'axios';

const API_URL = 'http://localhost:5000/api';

export const api = {
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

    // Get server config/IP (if implemented backend side, else mock/fail)
    getConfig: async () => {
        // Future proofing
        return {};
    }
};
