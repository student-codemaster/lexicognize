import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

// Create auth context
const AuthContext = createContext();

export const useAuth = () => {
  return useContext(AuthContext);
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Initialize axios interceptors
  useEffect(() => {
    // Request interceptor to add token
    const requestInterceptor = axios.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor to handle token refresh
    const responseInterceptor = axios.interceptors.response.use(
      (response) => response,
      async (error) => {
        const originalRequest = error.config;
        
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;
          
          try {
            const refreshToken = localStorage.getItem('refresh_token');
            if (refreshToken) {
              const response = await axios.post(`${API_BASE}/api/auth/refresh`, {
                refresh_token: refreshToken
              });
              
              const { access_token, refresh_token } = response.data;
              localStorage.setItem('access_token', access_token);
              localStorage.setItem('refresh_token', refresh_token);
              
              // Update axios header
              originalRequest.headers.Authorization = `Bearer ${access_token}`;
              
              // Retry original request
              return axios(originalRequest);
            }
          } catch (refreshError) {
            // Refresh token failed, logout user
            logout();
            return Promise.reject(refreshError);
          }
        }
        
        return Promise.reject(error);
      }
    );

    // Cleanup interceptors
    return () => {
      axios.interceptors.request.eject(requestInterceptor);
      axios.interceptors.response.eject(responseInterceptor);
    };
  }, []);

  // Check if user is logged in on mount
  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (token) {
        const response = await axios.get(`${API_BASE}/api/auth/me`);
        setUser(response.data);
      }
    } catch (err) {
      console.error('Auth check failed:', err);
      // Clear invalid tokens
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    } finally {
      setLoading(false);
    }
  };

  const login = async (usernameOrEmail, password, rememberMe = false) => {
    try {
      setError(null);
      const response = await axios.post(`${API_BASE}/api/auth/login`, {
        username_or_email: usernameOrEmail,
        password: password,
        remember_me: rememberMe
      });

      const { access_token, refresh_token } = response.data;
      
      // Store tokens
      localStorage.setItem('access_token', access_token);
      localStorage.setItem('refresh_token', refresh_token);
      
      // Get user info
      const userResponse = await axios.get(`${API_BASE}/api/auth/me`);
      setUser(userResponse.data);
      
      return { success: true, user: userResponse.data };
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed');
      return { success: false, error: err.response?.data?.detail || 'Login failed' };
    }
  };

  const register = async (userData) => {
    try {
      setError(null);
      const response = await axios.post(`${API_BASE}/api/auth/register`, userData);
      
      // Auto-login after registration
      const loginResult = await login(userData.email, userData.password);
      return loginResult;
    } catch (err) {
      setError(err.response?.data?.detail || 'Registration failed');
      return { success: false, error: err.response?.data?.detail || 'Registration failed' };
    }
  };

  const logout = async () => {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        await axios.post(`${API_BASE}/api/auth/logout`, {
          refresh_token: refreshToken
        });
      }
    } catch (err) {
      console.error('Logout error:', err);
    } finally {
      // Clear local storage
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      setUser(null);
    }
  };

  const logoutAll = async () => {
    try {
      await axios.post(`${API_BASE}/api/auth/logout-all`);
    } catch (err) {
      console.error('Logout all error:', err);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      setUser(null);
    }
  };

  const updateProfile = async (userData) => {
    try {
      const response = await axios.put(`${API_BASE}/api/auth/me`, userData);
      setUser(response.data);
      return { success: true, user: response.data };
    } catch (err) {
      setError(err.response?.data?.detail || 'Update failed');
      return { success: false, error: err.response?.data?.detail || 'Update failed' };
    }
  };

  const changePassword = async (currentPassword, newPassword, confirmPassword) => {
    try {
      await axios.post(`${API_BASE}/api/auth/change-password`, {
        current_password: currentPassword,
        new_password: newPassword,
        confirm_password: confirmPassword
      });
      return { success: true };
    } catch (err) {
      setError(err.response?.data?.detail || 'Password change failed');
      return { success: false, error: err.response?.data?.detail || 'Password change failed' };
    }
  };

  const forgotPassword = async (email) => {
    try {
      await axios.post(`${API_BASE}/api/auth/forgot-password`, { email });
      return { success: true };
    } catch (err) {
      setError(err.response?.data?.detail || 'Request failed');
      return { success: false, error: err.response?.data?.detail || 'Request failed' };
    }
  };

  const resetPassword = async (token, newPassword, confirmPassword) => {
    try {
      await axios.post(`${API_BASE}/api/auth/reset-password`, {
        token,
        new_password: newPassword,
        confirm_password: confirmPassword
      });
      return { success: true };
    } catch (err) {
      setError(err.response?.data?.detail || 'Password reset failed');
      return { success: false, error: err.response?.data?.detail || 'Password reset failed' };
    }
  };

  const verifyEmail = async (token) => {
    try {
      await axios.post(`${API_BASE}/api/auth/verify-email`, { token });
      await checkAuthStatus(); // Refresh user data
      return { success: true };
    } catch (err) {
      setError(err.response?.data?.detail || 'Verification failed');
      return { success: false, error: err.response?.data?.detail || 'Verification failed' };
    }
  };

  const resendVerification = async () => {
    try {
      await axios.post(`${API_BASE}/api/auth/resend-verification`);
      return { success: true };
    } catch (err) {
      setError(err.response?.data?.detail || 'Request failed');
      return { success: false, error: err.response?.data?.detail || 'Request failed' };
    }
  };

  const value = {
    user,
    loading,
    error,
    setError,
    login,
    register,
    logout,
    logoutAll,
    updateProfile,
    changePassword,
    forgotPassword,
    resetPassword,
    verifyEmail,
    resendVerification,
    checkAuthStatus
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};