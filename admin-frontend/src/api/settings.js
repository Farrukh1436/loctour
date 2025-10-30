import apiClient from './client';

export const settingsApi = {
  // Get current settings
  getSettings: async () => {
    const response = await apiClient.get('/settings/');
    return response.data;
  },

  // Update settings
  updateSettings: async (settingsData) => {
    const response = await apiClient.put('/settings/update/', settingsData);
    return response.data;
  },

  // Create settings (if none exist)
  createSettings: async (settingsData) => {
    const response = await apiClient.post('/settings/', settingsData);
    return response.data;
  }
};
