import axios from "axios";

const apiClient = axios.create({
  baseURL: "/api",
  withCredentials: true
});

apiClient.defaults.xsrfCookieName = "csrftoken";
apiClient.defaults.xsrfHeaderName = "X-CSRFToken";

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error("API error", error);
    return Promise.reject(error);
  }
);

export default apiClient;
