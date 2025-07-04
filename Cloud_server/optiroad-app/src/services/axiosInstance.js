import axios from "axios";
import { refreshAccessToken, refreshCSRFToken } from "./authService";
import { getCurrentUser, saveUser, removeUser } from "./storageService";

const axiosInstance = axios.create({
  baseURL: "/api", 
  withCredentials: true,
});

const getCSRFToken = () => {
  return document.cookie.split("; ")
    .find(row => row.startsWith("csrf_token="))
    ?.split("=")[1];
}

axiosInstance.interceptors.request.use(
  (config) => {
    const csrfToken = getCSRFToken();

    if(csrfToken) {
      config.headers["X-CSRF-Token"] = csrfToken;
    }     
    const user = getCurrentUser();
    if (user?.accessToken) {
      config.headers["Authorization"] = `Bearer ${user.accessToken}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

const retriedRequests = new Array();

const countRetriedRequests = (requestId) => {
  let count = 0;
  retriedRequests.forEach(requestId => {
    count ++;
  });
  return count;
}

axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    
    const requestId = `${originalRequest.method}::${originalRequest.url}::${JSON.stringify(originalRequest.data || {})}`;
    if (error.response?.status === 401 && !getCurrentUser()) {
      console.warn("Unauthorized request and no user available. Skipping refresh.");
      return Promise.reject(error);
    }

    if (countRetriedRequests(requestId) > 1) {
      console.warn("Already retried, rejecting request.");
      retriedRequests.filter(x => x !== requestId);
      removeUser(); 
      retriedRequests.length = 0;
      return Promise.reject(error);
    }

    if (error.response?.status === 401) {
      retriedRequests.push(requestId);

      try {
        const newAccessToken = await refreshAccessToken();
        if (newAccessToken) {
          originalRequest.headers["Authorization"] = `Bearer ${newAccessToken}`;
          retriedRequests.length = 0;
          return axiosInstance(originalRequest);
        }
      } catch (refreshError) {
        console.error("Refresh token failed:", refreshError);
        removeUser();
        retriedRequests.length = 0;
        return Promise.reject(refreshError);
      }
    }

    if (error.response?.status === 400) {
      if (error.response.data?.error === "Invalid CSRF Token!") {
        retriedRequests.push(requestId);
        try {
          await refreshCSRFToken();
          const csrfToken = getCSRFToken();
          if (csrfToken) {
            originalRequest.headers["X-CSRF-Token"] = csrfToken;
            retriedRequests.length = 0;
            return axiosInstance(originalRequest);
          }
        } catch (csrfError) {
          console.error("CSRF token refresh failed:", csrfError);
          retriedRequests.length = 0;
          return Promise.reject(csrfError);
        }
      }
      retriedRequests.length = 0;
      return Promise.reject(error);
    }
  }
);




export default axiosInstance;
