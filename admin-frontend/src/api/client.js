import axios from "axios";

const apiClient = axios.create({
  baseURL: "/api",
  withCredentials: true
});

apiClient.defaults.xsrfCookieName = "csrftoken";
apiClient.defaults.xsrfHeaderName = "X-CSRFToken";

// Get CSRF token from cookies
function getCsrfToken() {
  const name = 'csrftoken';
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Add CSRF token to requests
apiClient.interceptors.request.use(
  (config) => {
    const csrfToken = getCsrfToken();
    if (csrfToken) {
      config.headers['X-CSRFToken'] = csrfToken;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API error", error);
    
    // Handle authentication errors
    if (error.response?.status === 401 || error.response?.status === 403) {
      // If we're not on the login page, redirect to login
      if (!window.location.pathname.includes('/login')) {
        // Dispatch a custom event that the AuthContext can listen to
        window.dispatchEvent(new CustomEvent('auth-error'));
      }
    }
    
    return Promise.reject(error);
  }
);

export default apiClient;
