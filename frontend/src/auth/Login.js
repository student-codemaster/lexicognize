import React, { useState, useEffect } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
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
  FormCheck
} from 'react-bootstrap';
import {
  PersonFill,
  LockFill,
  EyeFill,
  EyeSlashFill,
  EnvelopeFill,
  ArrowRight,
  Google,
  Github,
  Microsoft
} from 'react-bootstrap-icons';
import { useAuth } from './AuthContext';

function Login() {
  const navigate = useNavigate();
  const location = useLocation();
  const { login, user, loading: authLoading } = useAuth();
  
  const [formData, setFormData] = useState({
    usernameOrEmail: '',
    password: '',
    rememberMe: false
  });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Check if user is already logged in
  useEffect(() => {
    if (user) {
      const from = location.state?.from?.pathname || '/dashboard';
      navigate(from, { replace: true });
    }
  }, [user, navigate, location]);
  
  // Check for success message in location state
  useEffect(() => {
    if (location.state?.message) {
      setSuccess(location.state.message);
    }
    if (location.state?.registeredEmail) {
      setFormData(prev => ({
        ...prev,
        usernameOrEmail: location.state.registeredEmail
      }));
    }
  }, [location]);
  
  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');
    
    const result = await login(
      formData.usernameOrEmail,
      formData.password,
      formData.rememberMe
    );
    
    setLoading(false);
    
    if (result.success) {
      // Save remember me preference
      if (formData.rememberMe) {
        localStorage.setItem('remember_me', 'true');
      } else {
        localStorage.removeItem('remember_me');
      }
      
      // Navigate to dashboard or intended destination
      const from = location.state?.from?.pathname || '/dashboard';
      navigate(from, { replace: true });
    } else {
      setError(result.error);
    }
  };
  
  // Social login handlers
  const handleSocialLogin = (provider) => {
    // Implement social login
    console.log(`Login with ${provider}`);
    // window.location.href = `${API_BASE}/api/auth/${provider}/login`;
  };
  
  if (authLoading) {
    return (
      <Container className="d-flex justify-content-center align-items-center" style={{ minHeight: '100vh' }}>
        <Spinner animation="border" variant="primary" />
      </Container>
    );
  }
  
  return (
    <Container className="py-5">
      <Row className="justify-content-center">
        <Col md={6} lg={5} xl={4}>
          {/* Success message from registration */}
          {success && (
            <Alert variant="success" className="text-center">
              {success}
            </Alert>
          )}
          
          <Card className="shadow-sm border-0">
            <Card.Body className="p-4">
              <div className="text-center mb-4">
                <div className="bg-primary rounded-circle d-inline-flex p-3 mb-3">
                  <PersonFill size={32} className="text-white" />
                </div>
                <h3 className="fw-bold">Welcome Back</h3>
                <p className="text-muted">Sign in to your account to continue</p>
              </div>
              
              {error && (
                <Alert variant="danger" onClose={() => setError('')} dismissible>
                  {error}
                </Alert>
              )}
              
              <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-3">
                  <Form.Label>Email or Username</Form.Label>
                  <InputGroup>
                    <InputGroup.Text>
                      <EnvelopeFill />
                    </InputGroup.Text>
                    <Form.Control
                      type="text"
                      name="usernameOrEmail"
                      value={formData.usernameOrEmail}
                      onChange={handleChange}
                      placeholder="Enter email or username"
                      required
                      autoFocus
                    />
                  </InputGroup>
                </Form.Group>
                
                <Form.Group className="mb-3">
                  <Form.Label>Password</Form.Label>
                  <InputGroup>
                    <InputGroup.Text>
                      <LockFill />
                    </InputGroup.Text>
                    <Form.Control
                      type={showPassword ? 'text' : 'password'}
                      name="password"
                      value={formData.password}
                      onChange={handleChange}
                      placeholder="Enter password"
                      required
                    />
                    <Button
                      variant="outline-secondary"
                      onClick={() => setShowPassword(!showPassword)}
                    >
                      {showPassword ? <EyeSlashFill /> : <EyeFill />}
                    </Button>
                  </InputGroup>
                  <div className="d-flex justify-content-between align-items-center mt-2">
                    <FormCheck
                      type="checkbox"
                      id="rememberMe"
                      name="rememberMe"
                      checked={formData.rememberMe}
                      onChange={handleChange}
                      label="Remember me"
                    />
                    <Link to="/forgot-password" className="text-decoration-none small">
                      Forgot password?
                    </Link>
                  </div>
                </Form.Group>
                
                <Button
                  type="submit"
                  variant="primary"
                  className="w-100 py-2"
                  disabled={loading}
                >
                  {loading ? (
                    <Spinner animation="border" size="sm" className="me-2" />
                  ) : (
                    <ArrowRight className="me-2" />
                  )}
                  Sign In
                </Button>
              </Form>
              
              {/* Divider */}
              <div className="position-relative my-4">
                <hr />
                <div className="position-absolute top-50 start-50 translate-middle bg-white px-3 text-muted">
                  Or continue with
                </div>
              </div>
              
              {/* Social login buttons */}
              <div className="row g-2 mb-4">
                <div className="col">
                  <Button
                    variant="outline-primary"
                    className="w-100"
                    onClick={() => handleSocialLogin('google')}
                  >
                    <Google className="me-2" />
                    Google
                  </Button>
                </div>
                <div className="col">
                  <Button
                    variant="outline-dark"
                    className="w-100"
                    onClick={() => handleSocialLogin('github')}
                  >
                    <Github className="me-2" />
                    GitHub
                  </Button>
                </div>
                <div className="col">
                  <Button
                    variant="outline-success"
                    className="w-100"
                    onClick={() => handleSocialLogin('microsoft')}
                  >
                    <Microsoft className="me-2" />
                    Microsoft
                  </Button>
                </div>
              </div>
              
              <div className="text-center mt-4">
                <p className="mb-0">
                  Don't have an account?{' '}
                  <Link to="/register" className="text-decoration-none fw-bold">
                    Sign up
                  </Link>
                </p>
              </div>
            </Card.Body>
          </Card>
          
          {/* Demo credentials */}
          <Card className="mt-3 border-0 bg-light">
            <Card.Body className="p-3">
              <h6 className="mb-2">Demo Credentials:</h6>
              <div className="small">
                <div className="mb-1">
                  <strong>Admin:</strong> admin@example.com / password123
                </div>
                <div className="mb-1">
                  <strong>User:</strong> user@example.com / password123
                </div>
                <div>
                  <strong>Researcher:</strong> researcher@example.com / password123
                </div>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
}

export default Login;