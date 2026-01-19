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
  ProgressBar,
  Image,
  Modal
} from 'react-bootstrap';
import {
  PersonFill,
  EnvelopeFill,
  CalendarFill,
  Building,
  BriefcaseFill,
  PhoneFill,
  GeoAltFill,
  Globe,
  ShieldLock,
  KeyFill,
  ClockFill,
  Database,
  Cpu,
  FileText,
  BarChart,
  PencilFill,
  Upload,
  CheckCircleFill
} from 'react-bootstrap-icons';
import { useAuth } from '../auth/AuthContext';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

function Profile() {
  const { user, updateProfile, changePassword, loading: authLoading } = useAuth();
  
  const [activeTab, setActiveTab] = useState('overview');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [stats, setStats] = useState(null);
  const [apiKeys, setApiKeys] = useState([]);
  
  // Profile form
  const [profileForm, setProfileForm] = useState({
    fullName: '',
    organization: '',
    position: '',
    bio: '',
    phoneNumber: '',
    address: '',
    country: '',
    avatarUrl: ''
  });
  
  // Password form
  const [passwordForm, setPasswordForm] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });
  
  // API key form
  const [apiKeyForm, setApiKeyForm] = useState({
    name: '',
    scopes: ['read', 'write'],
    rateLimit: 100
  });
  
  // Show/hide states
  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [showApiKeyModal, setShowApiKeyModal] = useState(false);
  const [newApiKey, setNewApiKey] = useState(null);
  
  // Load user stats
  useEffect(() => {
    if (user) {
      loadUserData();
      setProfileForm({
        fullName: user.full_name || '',
        organization: user.organization || '',
        position: user.position || '',
        bio: user.bio || '',
        phoneNumber: user.phone_number || '',
        address: user.address || '',
        country: user.country || '',
        avatarUrl: user.avatar_url || ''
      });
    }
  }, [user]);
  
  const loadUserData = async () => {
    try {
      // Load stats
      const statsResponse = await axios.get(`${API_BASE}/api/profile`);
      setStats(statsResponse.data.stats);
      
      // Load API keys
      const keysResponse = await axios.get(`${API_BASE}/api/auth/api-keys`);
      setApiKeys(keysResponse.data);
    } catch (err) {
      console.error('Error loading user data:', err);
    }
  };
  
  const handleProfileUpdate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');
    
    const result = await updateProfile(profileForm);
    
    setLoading(false);
    
    if (result.success) {
      setSuccess('Profile updated successfully');
    } else {
      setError(result.error);
    }
  };
  
  const handlePasswordChange = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');
    
    if (passwordForm.newPassword !== passwordForm.confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }
    
    const result = await changePassword(
      passwordForm.currentPassword,
      passwordForm.newPassword,
      passwordForm.confirmPassword
    );
    
    setLoading(false);
    
    if (result.success) {
      setSuccess('Password changed successfully');
      setPasswordForm({
        currentPassword: '',
        newPassword: '',
        confirmPassword: ''
      });
      setShowPasswordModal(false);
    } else {
      setError(result.error);
    }
  };
  
  const handleCreateApiKey = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post(`${API_BASE}/api/auth/api-keys`, apiKeyForm);
      setNewApiKey(response.data);
      setApiKeyForm({ name: '', scopes: ['read', 'write'], rateLimit: 100 });
      loadUserData(); // Refresh API keys list
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create API key');
    } finally {
      setLoading(false);
    }
  };
  
  const handleRevokeApiKey = async (apiKeyId) => {
    if (window.confirm('Are you sure you want to revoke this API key?')) {
      try {
        await axios.delete(`${API_BASE}/api/auth/api-keys/${apiKeyId}`);
        loadUserData(); // Refresh list
        setSuccess('API key revoked successfully');
      } catch (err) {
        setError(err.response?.data?.detail || 'Failed to revoke API key');
      }
    }
  };
  
  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    setSuccess('Copied to clipboard!');
  };
  
  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };
  
  const getRoleBadgeColor = (role) => {
    switch (role) {
      case 'admin': return 'danger';
      case 'researcher': return 'info';
      case 'legal_professional': return 'warning';
      default: return 'primary';
    }
  };
  
  if (authLoading) {
    return (
      <Container className="d-flex justify-content-center align-items-center" style={{ minHeight: '100vh' }}>
        <Spinner animation="border" variant="primary" />
      </Container>
    );
  }
  
  return (
    <Container className="py-4">
      <Row>
        <Col lg={4} md={5}>
          {/* Profile Card */}
          <Card className="shadow-sm mb-4">
            <Card.Body className="text-center">
              <div className="mb-3">
                {profileForm.avatarUrl ? (
                  <Image
                    src={profileForm.avatarUrl}
                    roundedCircle
                    style={{ width: '120px', height: '120px', objectFit: 'cover' }}
                  />
                ) : (
                  <div
                    className="rounded-circle bg-primary d-flex align-items-center justify-content-center mx-auto"
                    style={{ width: '120px', height: '120px' }}
                  >
                    <PersonFill size={48} className="text-white" />
                  </div>
                )}
              </div>
              
              <h4 className="mb-1">{user?.full_name || user?.username}</h4>
              <p className="text-muted mb-2">{user?.email}</p>
              
              <Badge bg={getRoleBadgeColor(user?.role)} className="mb-3">
                {user?.role?.toUpperCase()}
              </Badge>
              
              <div className="text-start mt-4">
                <div className="d-flex align-items-center mb-2">
                  <CalendarFill className="me-2 text-muted" />
                  <small>Joined {new Date(user?.created_at).toLocaleDateString()}</small>
                </div>
                
                {user?.last_login && (
                  <div className="d-flex align-items-center mb-2">
                    <ClockFill className="me-2 text-muted" />
                    <small>Last login: {new Date(user?.last_login).toLocaleDateString()}</small>
                  </div>
                )}
                
                {user?.email_verified_at ? (
                  <div className="d-flex align-items-center mb-2 text-success">
                    <CheckCircleFill className="me-2" />
                    <small>Email verified</small>
                  </div>
                ) : (
                  <div className="d-flex align-items-center mb-2 text-warning">
                    <ShieldLock className="me-2" />
                    <small>Email not verified</small>
                  </div>
                )}
              </div>
            </Card.Body>
          </Card>
          
          {/* Quick Stats */}
          <Card className="shadow-sm">
            <Card.Header>
              <BarChart className="me-2" />
              Quick Stats
            </Card.Header>
            <Card.Body>
              <ListGroup variant="flush">
                <ListGroup.Item className="d-flex justify-content-between align-items-center">
                  <span>
                    <Database className="me-2" />
                    Datasets
                  </span>
                  <Badge bg="primary">{stats?.total_datasets || 0}</Badge>
                </ListGroup.Item>
                
                <ListGroup.Item className="d-flex justify-content-between align-items-center">
                  <span>
                    <Cpu className="me-2" />
                    Models
                  </span>
                  <Badge bg="success">{stats?.total_models || 0}</Badge>
                </ListGroup.Item>
                
                <ListGroup.Item className="d-flex justify-content-between align-items-center">
                  <span>
                    <FileText className="me-2" />
                    Training Jobs
                  </span>
                  <Badge bg="info">{stats?.total_training_jobs || 0}</Badge>
                </ListGroup.Item>
                
                <ListGroup.Item className="d-flex justify-content-between align-items-center">
                  <span>
                    <Upload className="me-2" />
                    Storage Used
                  </span>
                  <Badge bg="warning">{formatFileSize(stats?.storage_used || 0)}</Badge>
                </ListGroup.Item>
              </ListGroup>
            </Card.Body>
          </Card>
        </Col>
        
        <Col lg={8} md={7}>
          <Tabs
            activeKey={activeTab}
            onSelect={(k) => setActiveTab(k)}
            className="mb-4"
          >
            <Tab eventKey="overview" title="Overview">
              <Card className="shadow-sm">
                <Card.Header className="d-flex justify-content-between align-items-center">
                  <span>Profile Information</span>
                  <Button
                    variant="outline-primary"
                    size="sm"
                    onClick={() => setActiveTab('edit')}
                  >
                    <PencilFill className="me-1" />
                    Edit Profile
                  </Button>
                </Card.Header>
                <Card.Body>
                  <Row>
                    <Col md={6}>
                      <div className="mb-3">
                        <h6 className="text-muted mb-1">
                          <PersonFill className="me-2" />
                          Full Name
                        </h6>
                        <p className="mb-0">{user?.full_name || 'Not set'}</p>
                      </div>
                      
                      <div className="mb-3">
                        <h6 className="text-muted mb-1">
                          <EnvelopeFill className="me-2" />
                          Email
                        </h6>
                        <p className="mb-0">{user?.email}</p>
                      </div>
                      
                      <div className="mb-3">
                        <h6 className="text-muted mb-1">
                          <Building className="me-2" />
                          Organization
                        </h6>
                        <p className="mb-0">{user?.organization || 'Not set'}</p>
                      </div>
                      
                      <div className="mb-3">
                        <h6 className="text-muted mb-1">
                          <BriefcaseFill className="me-2" />
                          Position
                        </h6>
                        <p className="mb-0">{user?.position || 'Not set'}</p>
                      </div>
                    </Col>
                    
                    <Col md={6}>
                      <div className="mb-3">
                        <h6 className="text-muted mb-1">
                          <PhoneFill className="me-2" />
                          Phone
                        </h6>
                        <p className="mb-0">{user?.phone_number || 'Not set'}</p>
                      </div>
                      
                      <div className="mb-3">
                        <h6 className="text-muted mb-1">
                          <GeoAltFill className="me-2" />
                          Address
                        </h6>
                        <p className="mb-0">{user?.address || 'Not set'}</p>
                      </div>
                      
                      <div className="mb-3">
                        <h6 className="text-muted mb-1">
                          <Globe className="me-2" />
                          Country
                        </h6>
                        <p className="mb-0">{user?.country || 'Not set'}</p>
                      </div>
                      
                      <div className="mb-3">
                        <h6 className="text-muted mb-1">Bio</h6>
                        <p className="mb-0">{user?.bio || 'No bio provided'}</p>
                      </div>
                    </Col>
                  </Row>
                </Card.Body>
              </Card>
              
              {/* Account Preferences */}
              <Card className="shadow-sm mt-4">
                <Card.Header>Account Preferences</Card.Header>
                <Card.Body>
                  <Row>
                    <Col md={6}>
                      <div className="mb-3">
                        <h6>Theme</h6>
                        <Badge bg="light" text="dark">
                          {user?.preferences?.theme || 'light'}
                        </Badge>
                      </div>
                      
                      <div className="mb-3">
                        <h6>Language</h6>
                        <Badge bg="info">
                          {user?.preferences?.language || 'en'}
                        </Badge>
                      </div>
                    </Col>
                    
                    <Col md={6}>
                      <div className="mb-3">
                        <h6>Notifications</h6>
                        <Badge bg={user?.preferences?.notifications ? 'success' : 'secondary'}>
                          {user?.preferences?.notifications ? 'Enabled' : 'Disabled'}
                        </Badge>
                      </div>
                      
                      <div className="mb-3">
                        <h6>Default Model</h6>
                        <Badge bg="primary">
                          {user?.preferences?.default_model || 'bart'}
                        </Badge>
                      </div>
                    </Col>
                  </Row>
                </Card.Body>
              </Card>
            </Tab>
            
            <Tab eventKey="edit" title="Edit Profile">
              <Card className="shadow-sm">
                <Card.Header>Edit Profile</Card.Header>
                <Card.Body>
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
                  
                  <Form onSubmit={handleProfileUpdate}>
                    <Row>
                      <Col md={6}>
                        <Form.Group className="mb-3">
                          <Form.Label>Full Name</Form.Label>
                          <Form.Control
                            type="text"
                            value={profileForm.fullName}
                            onChange={(e) => setProfileForm({...profileForm, fullName: e.target.value})}
                            placeholder="Enter your full name"
                          />
                        </Form.Group>
                        
                        <Form.Group className="mb-3">
                          <Form.Label>Organization</Form.Label>
                          <Form.Control
                            type="text"
                            value={profileForm.organization}
                            onChange={(e) => setProfileForm({...profileForm, organization: e.target.value})}
                            placeholder="Enter your organization"
                          />
                        </Form.Group>
                        
                        <Form.Group className="mb-3">
                          <Form.Label>Position</Form.Label>
                          <Form.Control
                            type="text"
                            value={profileForm.position}
                            onChange={(e) => setProfileForm({...profileForm, position: e.target.value})}
                            placeholder="Enter your position"
                          />
                        </Form.Group>
                      </Col>
                      
                      <Col md={6}>
                        <Form.Group className="mb-3">
                          <Form.Label>Phone Number</Form.Label>
                          <Form.Control
                            type="text"
                            value={profileForm.phoneNumber}
                            onChange={(e) => setProfileForm({...profileForm, phoneNumber: e.target.value})}
                            placeholder="Enter your phone number"
                          />
                        </Form.Group>
                        
                        <Form.Group className="mb-3">
                          <Form.Label>Country</Form.Label>
                          <Form.Control
                            type="text"
                            value={profileForm.country}
                            onChange={(e) => setProfileForm({...profileForm, country: e.target.value})}
                            placeholder="Enter your country"
                          />
                        </Form.Group>
                        
                        <Form.Group className="mb-3">
                          <Form.Label>Avatar URL</Form.Label>
                          <Form.Control
                            type="text"
                            value={profileForm.avatarUrl}
                            onChange={(e) => setProfileForm({...profileForm, avatarUrl: e.target.value})}
                            placeholder="Enter avatar image URL"
                          />
                        </Form.Group>
                      </Col>
                    </Row>
                    
                    <Form.Group className="mb-4">
                      <Form.Label>Bio</Form.Label>
                      <Form.Control
                        as="textarea"
                        rows={3}
                        value={profileForm.bio}
                        onChange={(e) => setProfileForm({...profileForm, bio: e.target.value})}
                        placeholder="Tell us about yourself"
                      />
                    </Form.Group>
                    
                    <Button
                      type="submit"
                      variant="primary"
                      disabled={loading}
                    >
                      {loading ? (
                        <Spinner animation="border" size="sm" className="me-2" />
                      ) : null}
                      Update Profile
                    </Button>
                  </Form>
                </Card.Body>
              </Card>
            </Tab>
            
            <Tab eventKey="security" title="Security">
              <Card className="shadow-sm">
                <Card.Header>Security Settings</Card.Header>
                <Card.Body>
                  <div className="mb-4">
                    <h5>Change Password</h5>
                    <p className="text-muted mb-3">
                      Use a strong password that you don't use elsewhere
                    </p>
                    <Button
                      variant="outline-primary"
                      onClick={() => setShowPasswordModal(true)}
                    >
                      Change Password
                    </Button>
                  </div>
                  
                  <div className="mb-4">
                    <h5>Two-Factor Authentication</h5>
                    <p className="text-muted mb-3">
                      Add an extra layer of security to your account
                    </p>
                    <Button variant="outline-secondary" disabled>
                      Coming Soon
                    </Button>
                  </div>
                  
                  <div>
                    <h5>Session Management</h5>
                    <p className="text-muted mb-3">
                      Manage your active sessions
                    </p>
                    <Button variant="outline-danger">
                      Logout All Devices
                    </Button>
                  </div>
                </Card.Body>
              </Card>
            </Tab>
            
            <Tab eventKey="api-keys" title="API Keys">
              <Card className="shadow-sm">
                <Card.Header className="d-flex justify-content-between align-items-center">
                  <span>API Keys</span>
                  <Button
                    variant="primary"
                    size="sm"
                    onClick={() => setShowApiKeyModal(true)}
                  >
                    <KeyFill className="me-1" />
                    Create API Key
                  </Button>
                </Card.Header>
                <Card.Body>
                  {apiKeys.length === 0 ? (
                    <div className="text-center py-4">
                      <KeyFill size={48} className="text-muted mb-3" />
                      <h5>No API Keys</h5>
                      <p className="text-muted">
                        Create your first API key to access the API
                      </p>
                    </div>
                  ) : (
                    <ListGroup variant="flush">
                      {apiKeys.map((apiKey) => (
                        <ListGroup.Item key={apiKey.id}>
                          <div className="d-flex justify-content-between align-items-center">
                            <div>
                              <h6 className="mb-1">{apiKey.name}</h6>
                              <small className="text-muted">
                                Key: {apiKey.key}
                                <br />
                                Created: {new Date(apiKey.created_at).toLocaleDateString()}
                                {apiKey.last_used && (
                                  <>
                                    <br />
                                    Last used: {new Date(apiKey.last_used).toLocaleDateString()}
                                  </>
                                )}
                              </small>
                              <div className="mt-2">
                                {apiKey.scopes.map((scope, idx) => (
                                  <Badge key={idx} bg="info" className="me-1">
                                    {scope}
                                  </Badge>
                                ))}
                                <Badge bg="secondary" className="me-1">
                                  Limit: {apiKey.rate_limit}/hour
                                </Badge>
                                <Badge bg={apiKey.is_active ? 'success' : 'danger'}>
                                  {apiKey.is_active ? 'Active' : 'Revoked'}
                                </Badge>
                              </div>
                            </div>
                            <div>
                              {apiKey.is_active && (
                                <Button
                                  variant="outline-danger"
                                  size="sm"
                                  onClick={() => handleRevokeApiKey(apiKey.id)}
                                >
                                  Revoke
                                </Button>
                              )}
                            </div>
                          </div>
                        </ListGroup.Item>
                      ))}
                    </ListGroup>
                  )}
                </Card.Body>
              </Card>
            </Tab>
          </Tabs>
        </Col>
      </Row>
      
      {/* Change Password Modal */}
      <Modal show={showPasswordModal} onHide={() => setShowPasswordModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Change Password</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {error && (
            <Alert variant="danger" onClose={() => setError('')} dismissible>
              {error}
            </Alert>
          )}
          
          <Form onSubmit={handlePasswordChange}>
            <Form.Group className="mb-3">
              <Form.Label>Current Password</Form.Label>
              <Form.Control
                type="password"
                value={passwordForm.currentPassword}
                onChange={(e) => setPasswordForm({...passwordForm, currentPassword: e.target.value})}
                required
              />
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>New Password</Form.Label>
              <Form.Control
                type="password"
                value={passwordForm.newPassword}
                onChange={(e) => setPasswordForm({...passwordForm, newPassword: e.target.value})}
                required
              />
            </Form.Group>
            
            <Form.Group className="mb-4">
              <Form.Label>Confirm New Password</Form.Label>
              <Form.Control
                type="password"
                value={passwordForm.confirmPassword}
                onChange={(e) => setPasswordForm({...passwordForm, confirmPassword: e.target.value})}
                required
              />
            </Form.Group>
            
            <Button type="submit" variant="primary" disabled={loading}>
              {loading ? (
                <Spinner animation="border" size="sm" className="me-2" />
              ) : null}
              Change Password
            </Button>
          </Form>
        </Modal.Body>
      </Modal>
      
      {/* Create API Key Modal */}
      <Modal show={showApiKeyModal} onHide={() => setShowApiKeyModal(false)}>
        <Modal.Header closeButton>
          <Modal.Title>Create API Key</Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {newApiKey ? (
            <div>
              <Alert variant="success">
                <Alert.Heading>API Key Created!</Alert.Heading>
                <p>
                  <strong>Key:</strong> {newApiKey.key}
                </p>
                <p className="mb-0">
                  <strong>Important:</strong> Save this key now. You won't be able to see it again!
                </p>
              </Alert>
              <Button
                variant="outline-primary"
                onClick={() => copyToClipboard(newApiKey.key)}
                className="me-2"
              >
                Copy Key
              </Button>
              <Button
                variant="primary"
                onClick={() => {
                  setNewApiKey(null);
                  setShowApiKeyModal(false);
                }}
              >
                Close
              </Button>
            </div>
          ) : (
            <Form onSubmit={handleCreateApiKey}>
              <Form.Group className="mb-3">
                <Form.Label>Key Name</Form.Label>
                <Form.Control
                  type="text"
                  value={apiKeyForm.name}
                  onChange={(e) => setApiKeyForm({...apiKeyForm, name: e.target.value})}
                  placeholder="e.g., Production Key"
                  required
                />
              </Form.Group>
              
              <Form.Group className="mb-3">
                <Form.Label>Scopes</Form.Label>
                <div>
                  {['read', 'write', 'train', 'admin'].map((scope) => (
                    <Form.Check
                      key={scope}
                      type="checkbox"
                      id={`scope-${scope}`}
                      label={scope}
                      checked={apiKeyForm.scopes.includes(scope)}
                      onChange={(e) => {
                        const scopes = e.target.checked
                          ? [...apiKeyForm.scopes, scope]
                          : apiKeyForm.scopes.filter(s => s !== scope);
                        setApiKeyForm({...apiKeyForm, scopes});
                      }}
                      className="mb-2"
                    />
                  ))}
                </div>
              </Form.Group>
              
              <Form.Group className="mb-4">
                <Form.Label>Rate Limit (requests per hour)</Form.Label>
                <Form.Control
                  type="number"
                  value={apiKeyForm.rateLimit}
                  onChange={(e) => setApiKeyForm({...apiKeyForm, rateLimit: parseInt(e.target.value)})}
                  min="1"
                  max="10000"
                />
              </Form.Group>
              
              <Button type="submit" variant="primary" disabled={loading}>
                {loading ? (
                  <Spinner animation="border" size="sm" className="me-2" />
                ) : null}
                Create API Key
              </Button>
            </Form>
          )}
        </Modal.Body>
      </Modal>
    </Container>
  );
}

export default Profile;