import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  Container,
  Row,
  Col,
  Card,
  Form,
  Button,
  Alert,
  Spinner,
  InputGroup,
  ProgressBar,
  Tooltip,
  OverlayTrigger
} from 'react-bootstrap';
import {
  PersonFill,
  EnvelopeFill,
  LockFill,
  EyeFill,
  EyeSlashFill,
  CheckCircleFill,
  XCircleFill,
  InfoCircle
} from 'react-bootstrap-icons';
import { useAuth } from './AuthContext';

function Signup() {
  const navigate = useNavigate();
  const { register, user } = useAuth();
  
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    fullName: '',
    password: '',
    confirmPassword: ''
  });
  
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [passwordStrength, setPasswordStrength] = useState(0);
  const [passwordCriteria, setPasswordCriteria] = useState({
    length: false,
    uppercase: false,
    lowercase: false,
    number: false
  });
  
  // Check if user is already logged in
  useEffect(() => {
    if (user) {
      navigate('/dashboard', { replace: true });
    }
  }, [user, navigate]);
  
  // Check password strength
  useEffect(() => {
    const criteria = {
      length: formData.password.length >= 8,
      uppercase: /[A-Z]/.test(formData.password),
      lowercase: /[a-z]/.test(formData.password),
      number: /\d/.test(formData.password)
    };
    
    setPasswordCriteria(criteria);
    
    // Calculate strength (0-100)
    const met = Object.values(criteria).filter(Boolean).length;
    setPasswordStrength((met / 4) * 100);
  }, [formData.password]);
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  const validateForm = () => {
    const errors = [];
    
    if (!formData.email) errors.push('Email is required');
    if (!formData.username) errors.push('Username is required');
    if (!formData.password) errors.push('Password is required');
    if (formData.password !== formData.confirmPassword) {
      errors.push('Passwords do not match');
    }
    
    // Email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (formData.email && !emailRegex.test(formData.email)) {
      errors.push('Invalid email format');
    }
    
    // Username validation
    const usernameRegex = /^[a-zA-Z0-9_-]+$/;
    if (formData.username && !usernameRegex.test(formData.username)) {
      errors.push('Username can only contain letters, numbers, underscores, and hyphens');
    }
    
    // Password strength
    if (passwordStrength < 100) {
      errors.push('Password does not meet all requirements');
    }
    
    return errors;
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    const errors = validateForm();
    if (errors.length > 0) {
      setError(errors.join(', '));
      setLoading(false);
      return;
    }
    
    const result = await register({
      email: formData.email,
      username: formData.username,
      full_name: formData.fullName,
      password: formData.password,
      confirm_password: formData.confirmPassword
    });
    
    setLoading(false);
    
    if (result.success) {
      // Redirect to dashboard with success message
      navigate('/dashboard', {
        state: {
          message: 'Registration successful! Welcome to Legal Model Finetuner.'
        }
      });
    } else {
      setError(result.error);
    }
  };
  
  const getPasswordStrengthColor = () => {
    if (passwordStrength < 25) return 'danger';
    if (passwordStrength < 50) return 'warning';
    if (passwordStrength < 75) return 'info';
    return 'success';
  };
  
  const renderTooltip = (props) => (
    <Tooltip id="password-tooltip" {...props}>
      <div className="text-start">
        <div><CheckCircleFill size={12} className="me-1" /> At least 8 characters</div>
        <div><CheckCircleFill size={12} className="me-1" /> One uppercase letter</div>
        <div><CheckCircleFill size={12} className="me-1" /> One lowercase letter</div>
        <div><CheckCircleFill size={12} className="me-1" /> One number</div>
      </div>
    </Tooltip>
  );
  
  return (
    <Container className="py-5">
      <Row className="justify-content-center">
        <Col md={8} lg={6}>
          <Card className="shadow-sm border-0">
            <Card.Body className="p-4">
              <div className="text-center mb-4">
                <div className="bg-primary rounded-circle d-inline-flex p-3 mb-3">
                  <PersonFill size={32} className="text-white" />
                </div>
                <h3 className="fw-bold">Create Account</h3>
                <p className="text-muted">Sign up to start using Legal Model Finetuner</p>
              </div>
              
              {error && (
                <Alert variant="danger" onClose={() => setError('')} dismissible>
                  {error}
                </Alert>
              )}
              
              <Form onSubmit={handleSubmit}>
                <Row>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Full Name (Optional)</Form.Label>
                      <InputGroup>
                        <InputGroup.Text>
                          <PersonFill />
                        </InputGroup.Text>
                        <Form.Control
                          type="text"
                          name="fullName"
                          value={formData.fullName}
                          onChange={handleChange}
                          placeholder="Enter your full name"
                        />
                      </InputGroup>
                    </Form.Group>
                  </Col>
                  
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Username *</Form.Label>
                      <InputGroup>
                        <InputGroup.Text>
                          <PersonFill />
                        </InputGroup.Text>
                        <Form.Control
                          type="text"
                          name="username"
                          value={formData.username}
                          onChange={handleChange}
                          placeholder="Choose a username"
                          required
                        />
                      </InputGroup>
                      <Form.Text className="text-muted">
                        Letters, numbers, underscores, and hyphens only
                      </Form.Text>
                    </Form.Group>
                  </Col>
                </Row>
                
                <Form.Group className="mb-3">
                  <Form.Label>Email Address *</Form.Label>
                  <InputGroup>
                    <InputGroup.Text>
                      <EnvelopeFill />
                    </InputGroup.Text>
                    <Form.Control
                      type="email"
                      name="email"
                      value={formData.email}
                      onChange={handleChange}
                      placeholder="Enter your email"
                      required
                    />
                  </InputGroup>
                  <Form.Text className="text-muted">
                    We'll send a verification email to this address
                  </Form.Text>
                </Form.Group>
                
                <Row>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>
                        Password *
                        <OverlayTrigger
                          placement="top"
                          overlay={renderTooltip}
                        >
                          <InfoCircle className="ms-2" size={14} />
                        </OverlayTrigger>
                      </Form.Label>
                      <InputGroup>
                        <InputGroup.Text>
                          <LockFill />
                        </InputGroup.Text>
                        <Form.Control
                          type={showPassword ? 'text' : 'password'}
                          name="password"
                          value={formData.password}
                          onChange={handleChange}
                          placeholder="Create password"
                          required
                        />
                        <Button
                          variant="outline-secondary"
                          onClick={() => setShowPassword(!showPassword)}
                        >
                          {showPassword ? <EyeSlashFill /> : <EyeFill />}
                        </Button>
                      </InputGroup>
                      
                      {/* Password strength indicator */}
                      {formData.password && (
                        <div className="mt-2">
                          <ProgressBar
                            now={passwordStrength}
                            variant={getPasswordStrengthColor()}
                            className="mb-2"
                          />
                          <div className="small">
                            <div className={`d-flex align-items-center ${passwordCriteria.length ? 'text-success' : 'text-danger'}`}>
                              {passwordCriteria.length ? <CheckCircleFill size={12} /> : <XCircleFill size={12} />}
                              <span className="ms-1">At least 8 characters</span>
                            </div>
                            <div className={`d-flex align-items-center ${passwordCriteria.uppercase ? 'text-success' : 'text-danger'}`}>
                              {passwordCriteria.uppercase ? <CheckCircleFill size={12} /> : <XCircleFill size={12} />}
                              <span className="ms-1">One uppercase letter</span>
                            </div>
                            <div className={`d-flex align-items-center ${passwordCriteria.lowercase ? 'text-success' : 'text-danger'}`}>
                              {passwordCriteria.lowercase ? <CheckCircleFill size={12} /> : <XCircleFill size={12} />}
                              <span className="ms-1">One lowercase letter</span>
                            </div>
                            <div className={`d-flex align-items-center ${passwordCriteria.number ? 'text-success' : 'text-danger'}`}>
                              {passwordCriteria.number ? <CheckCircleFill size={12} /> : <XCircleFill size={12} />}
                              <span className="ms-1">One number</span>
                            </div>
                          </div>
                        </div>
                      )}
                    </Form.Group>
                  </Col>
                  
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Confirm Password *</Form.Label>
                      <InputGroup>
                        <InputGroup.Text>
                          <LockFill />
                        </InputGroup.Text>
                        <Form.Control
                          type={showConfirmPassword ? 'text' : 'password'}
                          name="confirmPassword"
                          value={formData.confirmPassword}
                          onChange={handleChange}
                          placeholder="Confirm password"
                          required
                        />
                        <Button
                          variant="outline-secondary"
                          onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        >
                          {showConfirmPassword ? <EyeSlashFill /> : <EyeFill />}
                        </Button>
                      </InputGroup>
                      {formData.confirmPassword && formData.password !== formData.confirmPassword && (
                        <Form.Text className="text-danger">
                          Passwords do not match
                        </Form.Text>
                      )}
                    </Form.Group>
                  </Col>
                </Row>
                
                <Form.Group className="mb-4">
                  <Form.Check
                    type="checkbox"
                    id="terms"
                    label={
                      <>
                        I agree to the{' '}
                        <Link to="/terms" className="text-decoration-none">
                          Terms of Service
                        </Link>{' '}
                        and{' '}
                        <Link to="/privacy" className="text-decoration-none">
                          Privacy Policy
                        </Link>
                      </>
                    }
                    required
                  />
                </Form.Group>
                
                <Button
                  type="submit"
                  variant="primary"
                  className="w-100 py-2"
                  disabled={loading || passwordStrength < 100}
                >
                  {loading ? (
                    <Spinner animation="border" size="sm" className="me-2" />
                  ) : null}
                  Create Account
                </Button>
              </Form>
              
              <div className="text-center mt-4">
                <p className="mb-0">
                  Already have an account?{' '}
                  <Link to="/login" className="text-decoration-none fw-bold">
                    Sign in
                  </Link>
                </p>
              </div>
            </Card.Body>
          </Card>
          
          {/* Account types info */}
          <Card className="mt-3 border-0 bg-light">
            <Card.Body className="p-3">
              <h6 className="mb-2">Account Types:</h6>
              <div className="small">
                <div className="mb-1">
                  <strong>User:</strong> Upload datasets, train models, generate summaries
                </div>
                <div className="mb-1">
                  <strong>Researcher:</strong> All user features + advanced model training
                </div>
                <div>
                  <strong>Legal Professional:</strong> Specialized legal document processing
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
}

export default Signup;