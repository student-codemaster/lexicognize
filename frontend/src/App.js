import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { Container } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';

// Layout
import Layout from './components/Layout';

// Auth pages
import Login from './auth/Login';
import Signup from './auth/Signup';
import ForgotPassword from './auth/ForgotPassword';

// Main pages
import Dashboard from './pages/Dashboard';
import DatasetUpload from './pages/DatasetUpload';
import Training from './pages/Training';
import Evaluation from './pages/Evaluation';
import Inference from './pages/Inference';
import PDFProcessor from './pages/PDFProcessor';
import LanguageTools from './pages/LanguageTools';
import Translation from './pages/Translation';
import Profile from './pages/Profile';
import Settings from './pages/Settings';

// Components
import ProtectedRoute from './components/ProtectedRoute';
import { AuthProvider } from './auth/AuthContext';

// App component
function App() {
  return (
    <AuthProvider>
      <Router>
        <Routes>
          {/* Public routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Signup />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          
          {/* Protected routes with layout */}
          <Route path="/" element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="upload" element={<DatasetUpload />} />
            <Route path="train" element={<Training />} />
            <Route path="evaluate" element={<Evaluation />} />
            <Route path="inference" element={<Inference />} />
            <Route path="pdf-processor" element={<PDFProcessor />} />
            <Route path="language-tools" element={<LanguageTools />} />
            <Route path="translation" element={<Translation />} />
            <Route path="profile" element={<Profile />} />
            <Route path="settings" element={<Settings />} />
          </Route>
          
          {/* Admin routes */}
          <Route path="/admin/*" element={
            <ProtectedRoute requiredRole="admin">
              <Layout />
            </ProtectedRoute>
          } />
          
          {/* Catch all route */}
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </Router>
    </AuthProvider>
  );
}

export default App;