import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAdmin, setIsAdmin] = useState(false);
  const [loading, setLoading] = useState(true);

  // Configure axios defaults
  // Use the same hostname as the frontend (handles localhost vs 127.0.0.1 mismatch)
  const apiHost = process.env.REACT_APP_API_URL || `${window.location.protocol}//${window.location.hostname}:5000`;
  axios.defaults.baseURL = apiHost;
  axios.defaults.withCredentials = true;

  // Global response interceptor: handle 401 errors intelligently
  axios.interceptors.response.use(
    (response) => response,
    (error) => {
      if (error.response && error.response.status === 401) {
        // Only clear auth state and redirect if we currently think the user is authenticated
        // This prevents clearing state on failed login attempts
        if (user && window.location.pathname !== '/login' && window.location.pathname !== '/register') {
          console.log('Session expired, redirecting to login');
          setUser(null);
          setIsAdmin(false);
          window.location.href = '/login';
        }
      }
      return Promise.reject(error);
    }
  );

  useEffect(() => {
    // Only check auth status on app initialization
    checkAuthStatus();
  }, []); // Empty dependency array - only run once on mount

  const checkAuthStatus = async () => {
    try {
      const response = await axios.get('/api/auth/check-auth');
      if (response.data.authenticated) {
        setUser(response.data.user);
        setIsAdmin(response.data.user.is_admin);
      } else {
        setUser(null);
        setIsAdmin(false);
      }
    } catch (error) {
      console.log('Auth check failed:', error.response?.status, error.response?.data);
      
      // Only clear auth state for actual authentication errors (401)
      if (error.response?.status === 401) {
        console.log('Authentication failed - clearing user state');
        setUser(null);
        setIsAdmin(false);
      } else {
        // For network errors, server errors, etc. - don't clear auth state
        // The user might still be authenticated, we just can't verify right now
        console.log('Non-auth error during check, keeping current auth state');
      }
    } finally {
      setLoading(false);
    }
  };

  const login = async (credentials, isAdminLogin = false) => {
    try {
      const endpoint = isAdminLogin ? '/api/auth/admin/login' : '/api/auth/login';
      const response = await axios.post(endpoint, credentials);
      
      // Set user state directly from login response - no need for additional auth check
      if (isAdminLogin) {
        setUser(response.data.user); // API returns 'user' field for both admin and regular users
        setIsAdmin(true);
      } else {
        setUser(response.data.user);
        setIsAdmin(false);
      }
      
      return { success: true, message: response.data.message };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.error || 'Login failed'
      };
    }
  };

  const register = async (userData) => {
    try {
      const response = await axios.post('/api/auth/register', userData);
      return { success: true, message: response.data.message };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.error || 'Registration failed'
      };
    }
  };

  const logout = async () => {
    try {
      await axios.post('/api/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setIsAdmin(false);
    }
  };

  const updateProfile = async (profileData) => {
    try {
      const response = await axios.put('/api/auth/profile', profileData);
      setUser(response.data.profile);
      return { success: true, message: response.data.message };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.error || 'Profile update failed'
      };
    }
  };

  const changePassword = async (passwordData) => {
    try {
      const response = await axios.post('/api/auth/change-password', passwordData);
      return { success: true, message: response.data.message };
    } catch (error) {
      return {
        success: false,
        message: error.response?.data?.error || 'Password change failed'
      };
    }
  };

  // Method to manually refresh auth when needed
  const refreshAuth = async () => {
    return checkAuthStatus();
  };

  const value = {
    user,
    isAdmin,
    loading,
    login,
    register,
    logout,
    updateProfile,
    changePassword,
    checkAuthStatus, // For backwards compatibility
    refreshAuth // New method for manual refresh
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};