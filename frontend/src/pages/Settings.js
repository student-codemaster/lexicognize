import React, { useState, useEffect } from 'react';
import {
  Container,
  Row,
  Col,
  Card,
  Form,
  Button,
  Alert,
  Spinner,
  Tab,
  Tabs,
  Badge,
  ListGroup,
  Modal
} from 'react-bootstrap';
import {
  GearFill,
  BellFill,
  PaletteFill,
  Globe,
  Database,
  ShieldFill,
  TrashFill,
  Download,
  Upload,
  EyeFill,
  EyeSlashFill
} from 'react-bootstrap-icons';
import { useAuth } from '../auth/AuthContext';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

function Settings() {
  const { user, logoutAll } = useAuth();
  
  const [activeTab, setActiveTab] = useState('general');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // General settings
  const [generalSettings, setGeneralSettings] = useState({
    language: 'en',
    timezone: 'UTC',
    dateFormat: 'YYYY-MM-DD',
    timeFormat: '24h'
  });
  
  // Appearance settings
  const [appearanceSettings, setAppearanceSettings] = useState({
    theme: 'light',
    fontSize: 'medium',
    density: 'comfortable',
    animations: true
  });
  
  // Notification settings
  const [notificationSettings, setNotificationSettings] = useState({
    emailNotifications: true,
    trainingComplete: true,
    trainingFailed: true,
    newFeature: true,
    newsletter: false
  });
  
  // Data settings
  const [dataSettings, setDataSettings] = useState({
    autoSave: true,
    backupFrequency: 'daily',
    retainLogs: '30days',
    exportFormat: 'json'
  });
  
  // Modal states
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [showExportModal, setShowExportModal] = useState(false);
  const [showImportModal, setShowImportModal] = useState(false);
  const [exportData, setExportData] = useState(null);
  
  // Load settings from user preferences
  useEffect(() => {
    if (user && user.preferences) {
      setGeneralSettings(prev => ({
        ...prev,
        language: user.preferences.language || 'en'
      }));
      
      setAppearanceSettings(prev => ({
        ...prev,
        theme: user.preferences.theme || 'light'
      }));
      
      setNotificationSettings(prev => ({
        ...prev,
        emailNotifications: user.preferences.notifications !== false
      }));
    }
  }, [user]);
  
  const handleSaveSettings = async (section) => {
    setLoading(true);
    setError('');
    setSuccess('');
    
    try {
      const preferences = {
        ...user.preferences,
        language: generalSettings.language,
        theme: appearanceSettings.theme,
        notifications: notificationSettings.emailNotifications,
        autoSave: dataSettings.autoSave,
        exportFormat: dataSettings.exportFormat
      };
      
      await axios.put(`${API_BASE}/api/auth/me`, { preferences });
      setSuccess(`${section} settings saved successfully`);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to save settings');
    } finally {
      setLoading(false);
    }
  };
  
  const handleExportData = async () => {
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.get(`${API_BASE}/api/settings/export`);
      setExportData(response.data);
      setShowExportModal(true);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to export data');
    } finally {
      setLoading(false);
    }
  };
  
  const handleDownloadExport = () => {
    const dataStr = JSON.stringify(exportData, null, 2);
    const dataBlob = new Blob([dataStr], { type: 'application/json' });
    const url = URL.createObjectURL(dataBlob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `legal_models_backup_${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  };
  
  const handleDeleteAccount = async () => {
    setLoading(true);
    setError('');
    
    try {
      await axios.delete(`${API_BASE}/api/auth/me`);
      await logoutAll();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to delete account');
      setLoading(false);
    }
  };
  
  const handleImportData = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    
    setLoading(true);
    setError('');
    
    try {
      const formData = new FormData();
      formData.append('file', file);
      
      await axios.post(`${API_BASE}/api/settings/import`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      setSuccess('Data imported successfully');
      setShowImportModal(false);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to import data');
    } finally {
      setLoading(false);
    }
  };
  
  const getThemeOptions = () => [
    { value: 'light', label: 'Light', icon: '☀️' },
    { value: 'dark', label: 'Dark', icon: '🌙' },
    { value: 'auto', label: 'Auto', icon: '⚙️' }
  ];
  
  const getLanguageOptions = () => [
    { value: 'en', label: 'English' },
    { value: 'hi', label: 'Hindi' },
    { value: 'ta', label: 'Tamil' },
    { value: 'kn', label: 'Kannada' },
    { value: 'te', label: 'Telugu' },
    { value: 'ml', label: 'Malayalam' }
  ];
  
  return (
    <Container className="py-4">
      <h2 className="mb-4">
        <GearFill className="me-2" />
        Settings
      </h2>
      
      {error && (
        <Alert variant="danger" onClose={() => setError('')} dismissible>
          {error}
        </Alert>
      )}
      
      {success && (
        <Alert variant="success" onClose={() => setSuccess('')} dismissible>
          {success}
        </Alert>
      )}
      
      <Tabs
        activeKey={activeTab}
        onSelect={(k) => setActiveTab(k)}
        className="mb-4"
      >
        <Tab eventKey="general" title="General">
          <Card className="shadow-sm">
            <Card.Header>General Settings</Card.Header>
            <Card.Body>
              <Row>
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>
                      <Globe className="me-2" />
                      Language
                    </Form.Label>
                    <Form.Select
                      value={generalSettings.language}
                      onChange={(e) => setGeneralSettings({...generalSettings, language: e.target.value})}
                    >
                      {getLanguageOptions().map(option => (
                        <option key={option.value} value={option.value}>
                          {option.label}
                        </option>
                      ))}
                    </Form.Select>
                  </Form.Group>
                  
                  <Form.Group className="mb-3">
                    <Form.Label>Timezone</Form.Label>
                    <Form.Select
                      value={generalSettings.timezone}
                      onChange={(e) => setGeneralSettings({...generalSettings, timezone: e.target.value})}
                    >
                      <option value="UTC">UTC</option>
                      <option value="IST">India Standard Time (IST)</option>
                      <option value="EST">Eastern Time (EST)</option>
                      <option value="PST">Pacific Time (PST)</option>
                    </Form.Select>
                  </Form.Group>
                </Col>
                
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Date Format</Form.Label>
                    <Form.Select
                      value={generalSettings.dateFormat}
                      onChange={(e) => setGeneralSettings({...generalSettings, dateFormat: e.target.value})}
                    >
                      <option value="YYYY-MM-DD">2024-01-01</option>
                      <option value="MM/DD/YYYY">01/01/2024</option>
                      <option value="DD/MM/YYYY">01/01/2024</option>
                      <option value="MMMM D, YYYY">January 1, 2024</option>
                    </Form.Select>
                  </Form.Group>
                  
                  <Form.Group className="mb-3">
                    <Form.Label>Time Format</Form.Label>
                    <Form.Select
                      value={generalSettings.timeFormat}
                      onChange={(e) => setGeneralSettings({...generalSettings, timeFormat: e.target.value})}
                    >
                      <option value="24h">24-hour (14:30)</option>
                      <option value="12h">12-hour (2:30 PM)</option>
                    </Form.Select>
                  </Form.Group>
                </Col>
              </Row>
              
              <Button
                variant="primary"
                onClick={() => handleSaveSettings('General')}
                disabled={loading}
              >
                {loading ? (
                  <Spinner animation="border" size="sm" className="me-2" />
                ) : null}
                Save General Settings
              </Button>
            </Card.Body>
          </Card>
        </Tab>
        
        <Tab eventKey="appearance" title="Appearance">
          <Card className="shadow-sm">
            <Card.Header>
              <PaletteFill className="me-2" />
              Appearance
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={6}>
                  <Form.Group className="mb-4">
                    <Form.Label>Theme</Form.Label>
                    <div className="d-flex flex-wrap gap-3">
                      {getThemeOptions().map(option => (
                        <div
                          key={option.value}
                          className={`border rounded p-3 text-center cursor-pointer ${
                            appearanceSettings.theme === option.value
                              ? 'border-primary bg-primary bg-opacity-10'
                              : 'border-secondary'
                          }`}
                          style={{ width: '100px' }}
                          onClick={() => setAppearanceSettings({...appearanceSettings, theme: option.value})}
                        >
                          <div className="fs-4 mb-2">{option.icon}</div>
                          <div>{option.label}</div>
                        </div>
                      ))}
                    </div>
                  </Form.Group>
                  
                  <Form.Group className="mb-3">
                    <Form.Label>Font Size</Form.Label>
                    <Form.Select
                      value={appearanceSettings.fontSize}
                      onChange={(e) => setAppearanceSettings({...appearanceSettings, fontSize: e.target.value})}
                    >
                      <option value="small">Small</option>
                      <option value="medium">Medium</option>
                      <option value="large">Large</option>
                    </Form.Select>
                  </Form.Group>
                </Col>
                
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Density</Form.Label>
                    <Form.Select
                      value={appearanceSettings.density}
                      onChange={(e) => setAppearanceSettings({...appearanceSettings, density: e.target.value})}
                    >
                      <option value="compact">Compact</option>
                      <option value="comfortable">Comfortable</option>
                      <option value="spacious">Spacious</option>
                    </Form.Select>
                  </Form.Group>
                  
                  <Form.Group className="mb-4">
                    <Form.Check
                      type="switch"
                      id="animations-switch"
                      label="Enable Animations"
                      checked={appearanceSettings.animations}
                      onChange={(e) => setAppearanceSettings({...appearanceSettings, animations: e.target.checked})}
                    />
                    <Form.Text className="text-muted">
                      Smooth transitions and animations throughout the app
                    </Form.Text>
                  </Form.Group>
                </Col>
              </Row>
              
              <Button
                variant="primary"
                onClick={() => handleSaveSettings('Appearance')}
                disabled={loading}
              >
                {loading ? (
                  <Spinner animation="border" size="sm" className="me-2" />
                ) : null}
                Save Appearance Settings
              </Button>
            </Card.Body>
          </Card>
        </Tab>
        
        <Tab eventKey="notifications" title="Notifications">
          <Card className="shadow-sm">
            <Card.Header>
              <BellFill className="me-2" />
              Notifications
            </Card.Header>
            <Card.Body>
              <h5 className="mb-3">Email Notifications</h5>
              
              <Form.Group className="mb-3">
                <Form.Check
                  type="switch"
                  id="email-notifications"
                  label="Enable email notifications"
                  checked={notificationSettings.emailNotifications}
                  onChange={(e) => setNotificationSettings({...notificationSettings, emailNotifications: e.target.checked})}
                />
              </Form.Group>
              
              <div className="ms-4 mb-4">
                <Form.Group className="mb-3">
                  <Form.Check
                    type="checkbox"
                    id="training-complete"
                    label="Training job completed"
                    checked={notificationSettings.trainingComplete}
                    onChange={(e) => setNotificationSettings({...notificationSettings, trainingComplete: e.target.checked})}
                    disabled={!notificationSettings.emailNotifications}
                  />
                </Form.Group>
                
                <Form.Group className="mb-3">
                  <Form.Check
                    type="checkbox"
                    id="training-failed"
                    label="Training job failed"
                    checked={notificationSettings.trainingFailed}
                    onChange={(e) => setNotificationSettings({...notificationSettings, trainingFailed: e.target.checked})}
                    disabled={!notificationSettings.emailNotifications}
                  />
                </Form.Group>
                
                <Form.Group className="mb-3">
                  <Form.Check
                    type="checkbox"
                    id="new-feature"
                    label="New features and updates"
                    checked={notificationSettings.newFeature}
                    onChange={(e) => setNotificationSettings({...notificationSettings, newFeature: e.target.checked})}
                    disabled={!notificationSettings.emailNotifications}
                  />
                </Form.Group>
                
                <Form.Group className="mb-3">
                  <Form.Check
                    type="checkbox"
                    id="newsletter"
                    label="Newsletter and tips"
                    checked={notificationSettings.newsletter}
                    onChange={(e) => setNotificationSettings({...notificationSettings, newsletter: e.target.checked})}
                    disabled={!notificationSettings.emailNotifications}
                  />
                </Form.Group>
              </div>
              
              <h5 className="mb-3">In-App Notifications</h5>
              <p className="text-muted">
                In-app notifications are always enabled for important system messages.
              </p>
              
              <Button
                variant="primary"
                onClick={() => handleSaveSettings('Notification')}
                disabled={loading}
              >
                {loading ? (
                  <Spinner animation="border" size="sm" className="me-2" />
                ) : null}
                Save Notification Settings
              </Button>
            </Card.Body>
          </Card>
        </Tab>
        
        <Tab eventKey="data" title="Data">
          <Card className="shadow-sm">
            <Card.Header>
              <Database className="me-2" />
              Data Management
            </Card.Header>
            <Card.Body>
              <h5 className="mb-3">Data Settings</h5>
              
              <Form.Group className="mb-3">
                <Form.Check
                  type="switch"
                  id="auto-save"
                  label="Auto-save changes"
                  checked={dataSettings.autoSave}
                  onChange={(e) => setDataSettings({...dataSettings, autoSave: e.target.checked})}
                />
                <Form.Text className="text-muted">
                  Automatically save changes to datasets and models
                </Form.Text>
              </Form.Group>
              
              <Form.Group className="mb-3">
                <Form.Label>Backup Frequency</Form.Label>
                <Form.Select
                  value={dataSettings.backupFrequency}
                  onChange={(e) => setDataSettings({...dataSettings, backupFrequency: e.target.value})}
                >
                  <option value="never">Never</option>
                  <option value="daily">Daily</option>
                  <option value="weekly">Weekly</option>
                  <option value="monthly">Monthly</option>
                </Form.Select>
              </Form.Group>
              
              <Form.Group className="mb-4">
                <Form.Label>Retain Logs For</Form.Label>
                <Form.Select
                  value={dataSettings.retainLogs}
                  onChange={(e) => setDataSettings({...dataSettings, retainLogs: e.target.value})}
                >
                  <option value="7days">7 days</option>
                  <option value="30days">30 days</option>
                  <option value="90days">90 days</option>
                  <option value="1year">1 year</option>
                  <option value="forever">Forever</option>
                </Form.Select>
              </Form.Group>
              
              <h5 className="mb-3">Export/Import</h5>
              
              <div className="d-flex gap-2 mb-4">
                <Button
                  variant="outline-primary"
                  onClick={handleExportData}
                  disabled={loading}
                >
                  <Download className="me-2" />
                  Export All Data
                </Button>
                
                <Button
                  variant="outline-secondary"
                  onClick={() => setShowImportModal(true)}
                  disabled={loading}
                >
                  <Upload className="me-2" />
                  Import Data
                </Button>
              </div>
              
              <Form.Group className="mb-4">
                <Form.Label>Default Export Format</Form.Label>
                <Form.Select
                  value={dataSettings.exportFormat}
                  onChange={(e) => setDataSettings({...dataSettings, exportFormat: e.target.value})}
                >
                  <option value="json">JSON</option>
                  <option value="csv">CSV</option>
                  <option value="txt">Text</option>
                </Form.Select>
              </Form.Group>
              
              <Button
                variant="primary"
                onClick={() => handleSaveSettings('Data')}
                disabled={loading}
              >
                {loading ? (
                  <Spinner animation="border" size="sm" className="me-2" />
                ) : null}
                Save Data Settings
              </Button>
            </Card.Body>
          </Card>
        </Tab>
        
        <Tab eventKey="account" title="Account">
          <Card className="shadow-sm">
            <Card.Header>
              <ShieldFill className="me-2" />
              Account
            </Card.Header>
            <Card.Body>
              <h5 className="mb-3">Account Information</h5>
              
              <ListGroup className="mb-4">
                <ListGroup.Item className="d-flex justify-content-between align-items-center">
                  <span>Username</span>
                  <Badge bg="secondary">{user?.username}</Badge>
                </ListGroup.Item>
                
                <ListGroup.Item className="d-flex justify-content-between align-items-center">
                  <span>Email</span>
                  <Badge bg="info">{user?.email}</Badge>
                </ListGroup.Item>
                
                <ListGroup.Item className="d-flex justify-content-between align-items-center">
                  <span>Account Created</span>
                  <span>{new Date(user?.created_at).toLocaleDateString()}</span>
                </ListGroup.Item>
                
                <ListGroup.Item className="d-flex justify-content-between align-items-center">
                  <span>Last Login</span>
                  <span>{user?.last_login ? new Date(user?.last_login).toLocaleDateString() : 'Never'}</span>
                </ListGroup.Item>
                
                <ListGroup.Item className="d-flex justify-content-between align-items-center">
                  <span>Account Status</span>
                  <Badge bg={user?.status === 'active' ? 'success' : 'warning'}>
                    {user?.status}
                  </Badge>
                </ListGroup.Item>
              </ListGroup>
              
              <h5 className="mb-3">Danger Zone</h5>
              
              <Card border="danger" className="mb-3">
                <Card.Body>
                  <h6>Logout All Devices</h6>
                  <p className="text-muted mb-3">
                    Log out of all devices and revoke all active sessions.
                  </p>
                  <Button variant="outline-danger" onClick={logoutAll}>
                    Logout All Devices
                  </Button>
                </Card.Body>
              </Card>
              
              <Card border="danger">
                <Card.Body>
                  <h6>Delete Account</h6>
                  <p className="text-muted mb-3">
                    Permanently delete your account and all associated data. This action cannot be undone.
                  </p>
                  <Button variant="danger" onClick={() => setShowDeleteModal(true)}>
                    <TrashFill className="me-2" />
                    Delete Account
                  </Button>
                </Card.Body>
              </Card>
            </Card.Body>
          </Card>
        </Tab>
      </Tabs>
      
      {/* Delete Account Modal */}
      <Modal show={showDeleteModal} onHide={() => setShowDeleteModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Delete Account</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Alert variant="danger">
            <Alert.Heading>Warning: This action cannot be undone!</Alert.Heading>
            <p>
              Deleting your account will permanently remove:
            </p>
            <ul>
              <li>All your datasets</li>
              <li>All trained models</li>
              <li>Training history and logs</li>
              <li>API keys and settings</li>
            </ul>
            <p className="mb-0">
              Are you sure you want to proceed?
            </p>
          </Alert>
          
          <Form>
            <Form.Group className="mb-3">
              <Form.Label>Type "DELETE" to confirm</Form.Label>
              <Form.Control
                type="text"
                placeholder="DELETE"
                required
              />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowDeleteModal(false)}>
            Cancel
          </Button>
          <Button variant="danger" onClick={handleDeleteAccount} disabled={loading}>
            {loading ? (
              <Spinner animation="border" size="sm" className="me-2" />
            ) : null}
            Delete Account
          </Button>
        </Modal.Footer>
      </Modal>
      
      {/* Export Data Modal */}
      <Modal show={showExportModal} onHide={() => setShowExportModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>Export Data</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <p className="mb-3">
            Your data has been prepared for export. The file contains:
          </p>
          <ul>
            <li>User profile and settings</li>
            <li>All datasets and metadata</li>
            <li>Model configurations and training history</li>
            <li>API keys and usage logs</li>
          </ul>
          
          <Alert variant="info" className="mb-3">
            <Alert.Heading>Important Security Notice</Alert.Heading>
            <p className="mb-0">
              This file contains sensitive information. Keep it secure and do not share it publicly.
            </p>
          </Alert>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowExportModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" onClick={handleDownloadExport}>
            <Download className="me-2" />
            Download Export File
          </Button>
        </Modal.Footer>
      </Modal>
      
      {/* Import Data Modal */}
      <Modal show={showImportModal} onHide={() => setShowImportModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Import Data</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          <Alert variant="warning" className="mb-3">
            <Alert.Heading>Warning: Importing Data</Alert.Heading>
            <p className="mb-0">
              Importing data will merge or overwrite existing data. Make sure you have a backup before proceeding.
            </p>
          </Alert>
          
          <Form.Group>
            <Form.Label>Select backup file to import</Form.Label>
            <Form.Control
              type="file"
              accept=".json,.csv"
              onChange={handleImportData}
            />
            <Form.Text className="text-muted">
              Supported formats: JSON (recommended), CSV
            </Form.Text>
          </Form.Group>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowImportModal(false)}>
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={() => document.getElementById('import-file-input').click()}
          >
            <Upload className="me-2" />
            Browse and Import
          </Button>
          <input
            id="import-file-input"
            type="file"
            accept=".json,.csv"
            onChange={handleImportData}
            style={{ display: 'none' }}
          />
        </Modal.Footer>
      </Modal>
    </Container>
  );
}

export default Settings;