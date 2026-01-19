import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  Container,
  Row,
  Col,
  Card,
  Badge,
  Button,
  ProgressBar,
  ListGroup,
  Alert,
  Spinner
} from 'react-bootstrap';
import {
  Database,
  Cpu,
  BarChart,
  Magic,
  FilePdf,
  Translate,
  Globe,
  Clock,
  CheckCircle,
  PlayCircle,
  ExclamationTriangle,
  PersonFill,
  ArrowRight,
  PlusCircle
} from 'react-bootstrap-icons';
import { useAuth } from '../auth/AuthContext';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

function Dashboard() {
  const { user } = useAuth();
  
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({});
  const [recentJobs, setRecentJobs] = useState([]);
  const [recentDatasets, setRecentDatasets] = useState([]);
  const [systemInfo, setSystemInfo] = useState(null);
  
  useEffect(() => {
    loadDashboardData();
  }, []);
  
  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // Load user stats
      const statsResponse = await axios.get(`${API_BASE}/api/profile`);
      setStats(statsResponse.data.stats);
      
      // Load recent training jobs
      const jobsResponse = await axios.get(`${API_BASE}/api/training/jobs?limit=5`);
      setRecentJobs(jobsResponse.data.jobs || []);
      
      // Load recent datasets
      const datasetsResponse = await axios.get(`${API_BASE}/api/datasets?limit=5`);
      setRecentDatasets(datasetsResponse.data.datasets || []);
      
      // Load system info
      const systemResponse = await axios.get(`${API_BASE}/api/system-info`);
      setSystemInfo(systemResponse.data);
      
    } catch (err) {
      console.error('Error loading dashboard data:', err);
    } finally {
      setLoading(false);
    }
  };
  
  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'completed': return 'success';
      case 'running': return 'primary';
      case 'failed': return 'danger';
      case 'pending': return 'warning';
      default: return 'secondary';
    }
  };
  
  const formatFileSize = (bytes) => {
    if (!bytes) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };
  
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };
  
  if (loading) {
    return (
      <Container className="d-flex justify-content-center align-items-center" style={{ minHeight: '80vh' }}>
        <Spinner animation="border" variant="primary" />
      </Container>
    );
  }
  
  return (
    <Container className="py-4">
      {/* Welcome Section */}
      <div className="mb-4">
        <h2>
          {getGreeting()}, <span className="text-primary">{user?.username}</span>!
        </h2>
        <p className="text-muted">
          Welcome to your Legal Model Finetuner dashboard
        </p>
      </div>
      
      {/* Quick Stats */}
      <Row className="mb-4">
        <Col xl={3} lg={6} md={6} className="mb-3">
          <Card className="h-100 shadow-sm">
            <Card.Body>
              <div className="d-flex align-items-center">
                <div className="bg-primary bg-opacity-10 p-3 rounded me-3">
                  <Database size={24} className="text-primary" />
                </div>
                <div>
                  <h4 className="mb-0">{stats.total_datasets || 0}</h4>
                  <small className="text-muted">Datasets</small>
                </div>
              </div>
            </Card.Body>
            <Card.Footer className="bg-transparent border-top-0">
              <Link to="/upload" className="small text-decoration-none">
                <PlusCircle size={12} className="me-1" />
                Add dataset
              </Link>
            </Card.Footer>
          </Card>
        </Col>
        
        <Col xl={3} lg={6} md={6} className="mb-3">
          <Card className="h-100 shadow-sm">
            <Card.Body>
              <div className="d-flex align-items-center">
                <div className="bg-success bg-opacity-10 p-3 rounded me-3">
                  <Cpu size={24} className="text-success" />
                </div>
                <div>
                  <h4 className="mb-0">{stats.total_models || 0}</h4>
                  <small className="text-muted">Trained Models</small>
                </div>
              </div>
            </Card.Body>
            <Card.Footer className="bg-transparent border-top-0">
              <Link to="/train" className="small text-decoration-none">
                <PlusCircle size={12} className="me-1" />
                Train new model
              </Link>
            </Card.Footer>
          </Card>
        </Col>
        
        <Col xl={3} lg={6} md={6} className="mb-3">
          <Card className="h-100 shadow-sm">
            <Card.Body>
              <div className="d-flex align-items-center">
                <div className="bg-info bg-opacity-10 p-3 rounded me-3">
                  <BarChart size={24} className="text-info" />
                </div>
                <div>
                  <h4 className="mb-0">{stats.total_training_jobs || 0}</h4>
                  <small className="text-muted">Training Jobs</small>
                </div>
              </div>
            </Card.Body>
            <Card.Footer className="bg-transparent border-top-0">
              <Link to="/train" className="small text-decoration-none">
                <ArrowRight size={12} className="me-1" />
                View all jobs
              </Link>
            </Card.Footer>
          </Card>
        </Col>
        
        <Col xl={3} lg={6} md={6} className="mb-3">
          <Card className="h-100 shadow-sm">
            <Card.Body>
              <div className="d-flex align-items-center">
                <div className="bg-warning bg-opacity-10 p-3 rounded me-3">
                  <FilePdf size={24} className="text-warning" />
                </div>
                <div>
                  <h4 className="mb-0">{formatFileSize(stats.storage_used || 0)}</h4>
                  <small className="text-muted">Storage Used</small>
                </div>
              </div>
            </Card.Body>
            <Card.Footer className="bg-transparent border-top-0">
              <Link to="/settings" className="small text-decoration-none">
                <ArrowRight size={12} className="me-1" />
                Manage storage
              </Link>
            </Card.Footer>
          </Card>
        </Col>
      </Row>
      
      <Row>
        {/* Recent Activity */}
        <Col lg={8}>
          <Card className="shadow-sm mb-4">
            <Card.Header className="d-flex justify-content-between align-items-center">
              <span>Recent Training Jobs</span>
              <Link to="/train">
                <Button variant="outline-primary" size="sm">
                  View All
                </Button>
              </Link>
            </Card.Header>
            <Card.Body>
              {recentJobs.length === 0 ? (
                <div className="text-center py-4">
                  <Cpu size={48} className="text-muted mb-3" />
                  <h5>No Training Jobs Yet</h5>
                  <p className="text-muted mb-3">
                    Start by training your first model
                  </p>
                  <Link to="/train">
                    <Button variant="primary">
                      <PlayCircle className="me-2" />
                      Start Training
                    </Button>
                  </Link>
                </div>
              ) : (
                <ListGroup variant="flush">
                  {recentJobs.map((job) => (
                    <ListGroup.Item key={job.id} className="border-0 px-0">
                      <div className="d-flex justify-content-between align-items-center">
                        <div>
                          <h6 className="mb-1">{job.name || 'Unnamed Job'}</h6>
                          <small className="text-muted">
                            {job.model_type} • {job.task} • 
                            {new Date(job.created_at).toLocaleDateString()}
                          </small>
                        </div>
                        <div className="text-end">
                          <Badge bg={getStatusColor(job.status)} className="mb-2">
                            {job.status}
                          </Badge>
                          {job.status === 'running' && (
                            <ProgressBar
                              now={job.progress || 0}
                              label={`${job.progress || 0}%`}
                              style={{ width: '100px' }}
                            />
                          )}
                        </div>
                      </div>
                    </ListGroup.Item>
                  ))}
                </ListGroup>
              )}
            </Card.Body>
          </Card>
          
          <Card className="shadow-sm">
            <Card.Header className="d-flex justify-content-between align-items-center">
              <span>Recent Datasets</span>
              <Link to="/upload">
                <Button variant="outline-primary" size="sm">
                  View All
                </Button>
              </Link>
            </Card.Header>
            <Card.Body>
              {recentDatasets.length === 0 ? (
                <div className="text-center py-4">
                  <Database size={48} className="text-muted mb-3" />
                  <h5>No Datasets Yet</h5>
                  <p className="text-muted mb-3">
                    Upload your first legal dataset
                  </p>
                  <Link to="/upload">
                    <Button variant="primary">
                      <PlusCircle className="me-2" />
                      Upload Dataset
                    </Button>
                  </Link>
                </div>
              ) : (
                <ListGroup variant="flush">
                  {recentDatasets.map((dataset) => (
                    <ListGroup.Item key={dataset.id} className="border-0 px-0">
                      <div className="d-flex justify-content-between align-items-center">
                        <div>
                          <h6 className="mb-1">{dataset.name}</h6>
                          <small className="text-muted">
                            {dataset.metadata?.samples || 0} samples • 
                            {new Date(dataset.created_at).toLocaleDateString()}
                          </small>
                        </div>
                        <div>
                          <Badge bg="info" className="me-2">
                            {dataset.file_format || 'json'}
                          </Badge>
                          <Badge bg={dataset.is_public ? 'success' : 'secondary'}>
                            {dataset.is_public ? 'Public' : 'Private'}
                          </Badge>
                        </div>
                      </div>
                    </ListGroup.Item>
                  ))}
                </ListGroup>
              )}
            </Card.Body>
          </Card>
        </Col>
        
        {/* Quick Actions & System Info */}
        <Col lg={4}>
          <Card className="shadow-sm mb-4">
            <Card.Header>Quick Actions</Card.Header>
            <Card.Body>
              <div className="d-grid gap-2">
                <Link to="/upload" className="text-decoration-none">
                  <Button variant="outline-primary" className="w-100 text-start mb-2">
                    <Database className="me-2" />
                    Upload Dataset
                  </Button>
                </Link>
                
                <Link to="/train" className="text-decoration-none">
                  <Button variant="outline-success" className="w-100 text-start mb-2">
                    <Cpu className="me-2" />
                    Train New Model
                  </Button>
                </Link>
                
                <Link to="/pdf-processor" className="text-decoration-none">
                  <Button variant="outline-warning" className="w-100 text-start mb-2">
                    <FilePdf className="me-2" />
                    Process PDF
                  </Button>
                </Link>
                
                <Link to="/language-tools" className="text-decoration-none">
                  <Button variant="outline-info" className="w-100 text-start mb-2">
                    <Translate className="me-2" />
                    Language Tools
                  </Button>
                </Link>
                
                <Link to="/inference" className="text-decoration-none">
                  <Button variant="outline-dark" className="w-100 text-start">
                    <Magic className="me-2" />
                    Run Inference
                  </Button>
                </Link>
              </div>
            </Card.Body>
          </Card>
          
          {/* System Status */}
          <Card className="shadow-sm">
            <Card.Header>System Status</Card.Header>
            <Card.Body>
              {systemInfo && (
                <ListGroup variant="flush">
                  <ListGroup.Item className="d-flex justify-content-between align-items-center border-0 px-0">
                    <span>API Status</span>
                    <Badge bg="success">
                      <CheckCircle size={12} className="me-1" />
                      Online
                    </Badge>
                  </ListGroup.Item>
                  
                  <ListGroup.Item className="d-flex justify-content-between align-items-center border-0 px-0">
                    <span>Database</span>
                    <Badge bg="success">
                      <CheckCircle size={12} className="me-1" />
                      Connected
                    </Badge>
                  </ListGroup.Item>
                  
                  <ListGroup.Item className="d-flex justify-content-between align-items-center border-0 px-0">
                    <span>GPU Available</span>
                    <Badge bg={systemInfo.gpu_available ? 'success' : 'warning'}>
                      {systemInfo.gpu_available ? 'Yes' : 'No'}
                    </Badge>
                  </ListGroup.Item>
                  
                  <ListGroup.Item className="d-flex justify-content-between align-items-center border-0 px-0">
                    <span>CPU Usage</span>
                    <span>{systemInfo.cpu_usage || 0}%</span>
                  </ListGroup.Item>
                  
                  <ListGroup.Item className="d-flex justify-content-between align-items-center border-0 px-0">
                    <span>Memory Usage</span>
                    <span>{systemInfo.memory_usage || 0}%</span>
                  </ListGroup.Item>
                </ListGroup>
              )}
              
              <div className="mt-3">
                <small className="text-muted">
                  Last updated: {new Date().toLocaleTimeString()}
                </small>
              </div>
            </Card.Body>
          </Card>
          
          {/* Tips & Updates */}
          <Card className="shadow-sm mt-4">
            <Card.Header>Tips & Updates</Card.Header>
            <Card.Body>
              <ListGroup variant="flush">
                <ListGroup.Item className="border-0 px-0">
                  <div className="d-flex">
                    <div className="bg-primary bg-opacity-10 p-2 rounded me-3">
                      <Globe size={16} className="text-primary" />
                    </div>
                    <div>
                      <h6 className="mb-1">New: Language Translation</h6>
                      <small className="text-muted">
                        Now support Hindi, Tamil, and Kannada translation
                      </small>
                    </div>
                  </div>
                </ListGroup.Item>
                
                <ListGroup.Item className="border-0 px-0">
                  <div className="d-flex">
                    <div className="bg-success bg-opacity-10 p-2 rounded me-3">
                      <FilePdf size={16} className="text-success" />
                    </div>
                    <div>
                      <h6 className="mb-1">PDF Processing Improved</h6>
                      <small className="text-muted">
                        Better OCR and text extraction from legal PDFs
                      </small>
                    </div>
                  </div>
                </ListGroup.Item>
                
                <ListGroup.Item className="border-0 px-0">
                  <div className="d-flex">
                    <div className="bg-info bg-opacity-10 p-2 rounded me-3">
                      <ShieldLock size={16} className="text-info" />
                    </div>
                    <div>
                      <h6 className="mb-1">Security Update</h6>
                      <small className="text-muted">
                        Enhanced API key security and rate limiting
                      </small>
                    </div>
                  </div>
                </ListGroup.Item>
              </ListGroup>
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
}

export default Dashboard;