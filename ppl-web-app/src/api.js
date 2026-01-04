import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: API_URL,
});

// Add a request interceptor to include the JWT token
api.interceptors.request.use(
    (config) => {
        const token = localStorage.getItem('token');
        if (token) {
            config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
    },
    (error) => Promise.reject(error)
);

export const requestCode = async (email) => {
    const response = await api.post('/auth/request-code', { email });
    return response.data;
};

export const verifyCode = async (email, code) => {
    const response = await api.post('/auth/verify-code', { email, code });
    return response.data;
};

export const register = async (userData) => {
    const response = await api.post('/users/', userData);
    return response.data;
};

export const createVariable = async (variableData) => {
    const response = await api.post('/variables/', variableData);
    return response.data;
};

export const getVariables = async () => {
    const response = await api.get('/variables/');
    return response.data;
};

export const getCurrentUser = async () => {
    const response = await api.get('/users/me');
    return response.data;
};

export const updateUser = async (userData) => {
    const response = await api.put('/users/me', userData);
    return response.data;
};

export const uploadAvatar = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/users/me/avatar', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

export const getVariablePrediction = async (tag) => {
    const response = await api.get(`/variables/${tag}/prediction`);
    return response.data;
};

// --- Model APIs ---
export const getModels = async () => {
    const response = await api.get('/models/');
    return response.data;
};

export const getModel = async (id) => {
    const response = await api.get(`/models/${id}`);
    return response.data;
};

export const getModelVisualizations = async (id) => {
    const response = await api.get(`/models/${id}/visualizations`);
    return response.data;
};

export const trainModel = async (config) => {
    const response = await api.post('/models/train', config);
    return response.data;
};

export const uploadModel = async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    const response = await api.post('/models/upload', formData, {
        headers: {
            'Content-Type': 'multipart/form-data',
        },
    });
    return response.data;
};

export const createCheckoutSession = async (interval) => {
    const response = await api.post('/payment/create-checkout-session', { interval });
    return response.data;
};

export default api;
