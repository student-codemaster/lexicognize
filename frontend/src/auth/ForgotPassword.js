import React, { useState, useEffect } from 'react';
import { useNavigate, Link, useSearchParams } from 'react-router-dom';
import {
  Container,
  Row,
  Col,
  Card,
  Form,
  Button,
  Alert,
  Spinner,
  InputGroup
} from 'react-bootstrap';
import {
  EnvelopeFill,
  LockFill,
  EyeFill,
  EyeSlashFill,
  CheckCircleFill
} from 'react-bootstrap-icons';
import { useAuth } from './AuthContext';

function ForgotPassword() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const { forgotPassword, resetPassword, user } = useAuth();
  
  const [step, setStep] = useState(1); // 1: request reset, 2: reset password
  const [formData, setFormData] = useState({
    email: '',
    token: '',
    newPassword: '',
    confirmPassword: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Check for token in URL
  useEffect(() => {
    const token = searchParams.get('token');
    if (token) {
      setFormData(prev => ({ ...prev, token }));
      setStep(2);
    }
  }, [searchParams]);
  
  // Check if user is already logged in
  useEffect(() => {
    if (user) {
      navigate('/dashboard', { replace: true });
    }
  }, [user, navigate]);
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  const handleRequestReset = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess('');
    
    const result = await forgotPassword(formData.email);
    
    setLoading(false);
    
    if (result.success) {
      setSuccess('If an account exists with this email, you will receive a password reset link.');
      setFormData(prev => ({ ...prev, email: '' }));
    } else {
      setError(result.error);
    }
  };
  
  const handleResetPassword = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    if (formData.newPassword !== formData.confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }
    
    const result = await resetPassword(
      formData.token,
      formData.newPassword,
      formData.confirmPassword
    );
    
    setLoading(false);
    
    if (result.success) {
      setSuccess('Password reset successful! You can now sign in with your new password.');
      setTimeout(() => {
        navigate('/login', {
          state: { message: 'Password reset successful! Please sign in.' }
        });
      }, 3000);
    } else {
      setError(result.error);
    }
  };
  
  return (
    <Container className="py-5">
      <Row className="justify-content-center">
        <Col md={6} lg={5}>
          <Card className="shadow-sm border-0">
            <Card.Body className="p-4">
              <div className="text-center mb-4">
                <div className="bg-primary rounded-circle d-inline-flex p-3 mb-3">
                  <LockFill size={32} className="text-white" />
                </div>
                <h3 className="fw-bold">
                  {step === 1 ? 'Reset Password' : 'Set New Password'}
                </h3>
                <p className="text-muted">
                  {step === 1 
                    ? 'Enter your email to receive a reset link' 
                    : 'Enter your new password'}
                </p>
              </div>
              
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
              
              {step === 1 ? (
                <Form onSubmit={handleRequestReset}>
                  <Form.Group className="mb-4">
                    <Form.Label>Email Address</Form.Label>
                    <InputGroup>
                      <InputGroup.Text>
                        <EnvelopeFill />
                      </InputGroup.Text>
                      <Form.Control
                        type="email"
                        name="email"
                        value={formData.email}
                        onChange={handleChange}
                        placeholder="Enter your email address"
                        required
                      />
                    </InputGroup>
                    <Form.Text className="text-muted">
                      We'll send a password reset link to this email
                    </Form.Text>
                  </Form.Group>
                  
                  <Button
                    type="submit"
                    variant="primary"
                    className="w-100 py-2"
                    disabled={loading}
                  >
                    {loading ? (
                      <Spinner animation="border" size="sm" className="me-2" />
                    ) : null}
                    Send Reset Link
                  </Button>
                </Form>
              ) : (
                <Form onSubmit={handleResetPassword}>
                  <Form.Group className="mb-3">
                    <Form.Label>New Password</Form.Label>
                    <InputGroup>
                      <InputGroup.Text>
                        <LockFill />
                      </InputGroup.Text>
                      <Form.Control
                        type={showPassword ? 'text' : 'password'}
                        name="newPassword"
                        value={formData.newPassword}
                        onChange={handleChange}
                        placeholder="Enter new password"
                        required
                      />
                      <Button
                        variant="outline-secondary"
                        onClick={() => setShowPassword(!showPassword)}
                      >
                        {showPassword ? <EyeSlashFill /> : <EyeFill />}
                      </Button>
                    </InputGroup>
                    <Form.Text className="text-muted">
                      Minimum 8 characters with uppercase, lowercase, and number
                    </Form.Text>
                  </Form.Group>
                  
                  <Form.Group className="mb-4">
                    <Form.Label>Confirm New Password</Form.Label>
                    <InputGroup>
                      <InputGroup.Text>
                        <LockFill />
                      </InputGroup.Text>
                      <Form.Control
                        type={showConfirmPassword ? 'text' : 'password'}
                        name="confirmPassword"
                        value={formData.confirmPassword}
                        onChange={handleChange}
                        placeholder="Confirm new password"
                        required
                      />
                      <Button
                        variant="outline-secondary"
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                      >
                        {showConfirmPassword ? <EyeSlashFill /> : <EyeFill />}
                      </Button>
                    </InputGroup>
                    {formData.confirmPassword && formData.newPassword !== formData.confirmPassword && (
                      <Form.Text className="text-danger">
                        Passwords do not match
                      </Form.Text>
                    )}
                  </Form.Group>
                  
                  <Button
                    type="submit"
                    variant="primary"
                    className="w-100 py-2"
                    disabled={loading}
                  >
                    {loading ? (
                      <Spinner animation="border" size="sm" className="me-2" />
                    ) : null}
                    Reset Password
                  </Button>
                </Form>
              )}
              
              <div className="text-center mt-4">
                <p className="mb-0">
                  Remember your password?{' '}
                  <Link to="/login" className="text-decoration-none fw-bold">
                    Sign in
                  </Link>
                </p>
                {step === 2 && (
                  <p className="mb-0 mt-2">
                    Need a new reset link?{' '}
                    <Button
                      variant="link"
                      className="p-0 fw-bold"
                      onClick={() => setStep(1)}
                    >
                      Request another
                    </Button>
                  </p>
                )}
              </div>
            </Card.Body>
          </Card>
          
          {/* Security tips */}
          <Card className="mt-3 border-0 bg-light">
            <Card.Body className="p-3">
              <h6 className="mb-2">
                <CheckCircleFill className="me-2 text-success" />
                Security Tips:
              </h6>
              <div className="small">
                <div className="mb-1">• Use a strong, unique password</div>
                <div className="mb-1">• Don't reuse passwords across sites</div>
                <div className="mb-1">• Reset links expire in 24 hours</div>
                <div>• Contact support if you need help</div>
              </div>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
}

export default ForgotPassword;