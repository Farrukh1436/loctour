import { createContext, useContext, useState, useEffect } from "react";
import apiClient from "../api/client.js";

const AuthContext = createContext();

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}

export function AuthProvider({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [user, setUser] = useState(null);

  // Check authentication status on app load
  useEffect(() => {
    checkAuthStatus();
  }, []);

  // Listen for authentication errors from API calls
  useEffect(() => {
    const handleAuthError = () => {
      setIsAuthenticated(false);
      setUser(null);
    };

    window.addEventListener('auth-error', handleAuthError);
    return () => window.removeEventListener('auth-error', handleAuthError);
  }, []);

  const checkAuthStatus = async () => {
    try {
      // Try to fetch user info from Django's user endpoint
      const response = await apiClient.get("/auth/user/");
      if (response.status === 200) {
        setIsAuthenticated(true);
        setUser(response.data);
      } else {
        setIsAuthenticated(false);
        setUser(null);
      }
    } catch (error) {
      console.log("Not authenticated:", error.response?.status);
      setIsAuthenticated(false);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  };

  const login = (userData = null) => {
    setIsAuthenticated(true);
    if (userData) {
      setUser(userData);
    } else {
      checkAuthStatus();
    }
  };

  const logout = async () => {
    try {
      await apiClient.post("/auth/logout/");
    } catch (error) {
      console.error("Logout error:", error);
    } finally {
      setIsAuthenticated(false);
      setUser(null);
    }
  };

  const value = {
    isAuthenticated,
    isLoading,
    user,
    login,
    logout,
    checkAuthStatus
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}
