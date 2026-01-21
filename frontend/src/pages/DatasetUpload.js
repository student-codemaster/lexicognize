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
  ProgressBar,
  Badge,
  Tab,
  Tabs,
  Modal,
  ListGroup,
  InputGroup
} from 'react-bootstrap';
import {
  Upload,
  Database,
  Search,
  Download,
  Globe,
  FileText,
  CheckCircle,
  XCircle,
  ArrowRight,
  CloudDownload,
  InfoCircle
} from 'react-bootstrap-icons';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

function DatasetUpload() {
  const [activeTab, setActiveTab] = useState('upload');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // File upload state
  const [files, setFiles] = useState([]);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [uploadConfig, setUploadConfig] = useState({
    merge: false,
    datasetName: '',
    description: '',
    isPublic: false
  });
  
  // Hugging Face import state
  const [hfDatasets, setHfDatasets] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedTask, setSelectedTask] = useState('');
  const [selectedDataset, setSelectedDataset] = useState(null);
  const [importConfig, setImportConfig] = useState({
    split: 'train',
    sampleSize: 1000,
    datasetName: '',
    description: '',
    isPublic: false
  });
  const [showImportModal, setShowImportModal] = useState(false);
  const [importing, setImporting] = useState(false);
  
  // Load available Hugging Face datasets
  useEffect(() => {
    loadHuggingFaceDatasets();
  }, [searchQuery, selectedTask]);
  
  const loadHuggingFaceDatasets = async () => {
    try {
      const params = {};
      if (searchQuery) params.search = searchQuery;
      if (selectedTask) params.task = selectedTask;
      
      const response = await axios.get(`${API_BASE}/api/datasets/huggingface/available`, { params });
      setHfDatasets(response.data.datasets || []);
    } catch (err) {
      console.error('Error loading Hugging Face datasets:', err);
    }
  };
  
  const handleFileUpload = async (e) => {
    e.preventDefault();
    
    if (files.length === 0) {
      setError('Please select files to upload');
      return;
    }
    
    setLoading(true);
    setError('');
    setSuccess('');
    
    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });
    formData.append('merge', uploadConfig.merge);
    formData.append('dataset_name', uploadConfig.datasetName);
    formData.append('description', uploadConfig.description);
    formData.append('is_public', uploadConfig.isPublic);
    
    try {
      const response = await axios.post(`${API_BASE}/api/datasets/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          const percent = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          setUploadProgress(percent);
        }
      });
      
      setSuccess('Dataset uploaded successfully!');
      setFiles([]);
      setUploadProgress(0);
      setUploadConfig({
        merge: false,
        datasetName: '',
        description: '',
        isPublic: false
      });
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Upload failed');
    } finally {
      setLoading(false);
    }
  };
  
  const handleHuggingFaceImport = async () => {
    if (!selectedDataset) {
      setError('Please select a dataset to import');
      return;
    }
    
    setImporting(true);
    setError('');
    
    try {
      const response = await axios.post(`${API_BASE}/api/datasets/huggingface/import`, {
        dataset_id: selectedDataset.id,
        split: importConfig.split,
        sample_size: importConfig.sampleSize,
        dataset_name: importConfig.datasetName || selectedDataset.name,
        description: importConfig.description || `Imported from Hugging Face: ${selectedDataset.name}`,
        is_public: importConfig.isPublic
      });
      
      setSuccess('Dataset import started in background!');
      setShowImportModal(false);
      setSelectedDataset(null);
      setImportConfig({
        split: 'train',
        sampleSize: 1000,
        datasetName: '',
        description: '',
        isPublic: false
      });
      
    } catch (err) {
      setError(err.response?.data?.detail || 'Import failed');
    } finally {
      setImporting(false);
    }
  };
  
  const viewDatasetInfo = async (dataset) => {
    try {
      const response = await axios.get(`${API_BASE}/api/datasets/huggingface/${dataset.id}/info`);
      setSelectedDataset({
        ...dataset,
        details: response.data
      });
      setShowImportModal(true);
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to load dataset info');
    }
  };
  
  const getTaskColor = (task) => {
    switch (task) {
      case 'summarization': return 'primary';
      case 'simplification': return 'success';
      case 'translation': return 'info';
      case 'classification': return 'warning';
      default: return 'secondary';
    }
  };
  
  return (
    <Container className="py-4">
      <h2 className="mb-4">
        <Database className="me-2" />
        Dataset Management
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
        {/* Local File Upload Tab */}
        <Tab eventKey="upload" title="Upload Files">
          <Card className="shadow-sm">
            <Card.Header>Upload Local Files</Card.Header>
            <Card.Body>
              <Form onSubmit={handleFileUpload}>
                <Form.Group className="mb-3">
                  <Form.Label>Select JSON Files</Form.Label>
                  <Form.Control
                    type="file"
                    accept=".json"
                    multiple
                    onChange={(e) => setFiles(Array.from(e.target.files))}
                    disabled={loading}
                  />
                  <Form.Text className="text-muted">
                    Upload JSON files containing legal documents with text, summary, and simplified fields
                  </Form.Text>
                </Form.Group>
                
                {files.length > 0 && (
                  <div className="mb-3">
                    <h6>Selected Files ({files.length})</h6>
                    <ListGroup>
                      {files.map((file, index) => (
                        <ListGroup.Item key={index} className="d-flex justify-content-between align-items-center">
                          <span>
                            <FileText className="me-2" />
                            {file.name}
                          </span>
                          <Badge bg="info">
                            {(file.size / 1024).toFixed(1)} KB
                          </Badge>
                        </ListGroup.Item>
                      ))}
                    </ListGroup>
                  </div>
                )}
                
                <Form.Group className="mb-3">
                  <Form.Check
                    type="checkbox"
                    label="Merge files into single dataset"
                    checked={uploadConfig.merge}
                    onChange={(e) => setUploadConfig({...uploadConfig, merge: e.target.checked})}
                    disabled={loading}
                  />
                </Form.Group>
                
                <Row>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Dataset Name</Form.Label>
                      <Form.Control
                        type="text"
                        value={uploadConfig.datasetName}
                        onChange={(e) => setUploadConfig({...uploadConfig, datasetName: e.target.value})}
                        placeholder="Enter dataset name"
                        disabled={loading}
                      />
                    </Form.Group>
                  </Col>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Description</Form.Label>
                      <Form.Control
                        type="text"
                        value={uploadConfig.description}
                        onChange={(e) => setUploadConfig({...uploadConfig, description: e.target.value})}
                        placeholder="Enter description"
                        disabled={loading}
                      />
                    </Form.Group>
                  </Col>
                </Row>
                
                <Form.Group className="mb-4">
                  <Form.Check
                    type="checkbox"
                    label="Make dataset public"
                    checked={uploadConfig.isPublic}
                    onChange={(e) => setUploadConfig({...uploadConfig, isPublic: e.target.checked})}
                    disabled={loading}
                  />
                  <Form.Text className="text-muted">
                    Public datasets can be seen by other users
                  </Form.Text>
                </Form.Group>
                
                <Button
                  type="submit"
                  variant="primary"
                  disabled={loading || files.length === 0}
                >
                  {loading ? (
                    <Spinner animation="border" size="sm" className="me-2" />
                  ) : (
                    <Upload className="me-2" />
                  )}
                  Upload Dataset
                </Button>
                
                {uploadProgress > 0 && (
                  <div className="mt-3">
                    <ProgressBar now={uploadProgress} label={`${uploadProgress}%`} />
                  </div>
                )}
              </Form>
            </Card.Body>
          </Card>
        </Tab>
        
        {/* Hugging Face Import Tab */}
        <Tab eventKey="huggingface" title="Hugging Face">
          <Card className="shadow-sm">
            <Card.Header className="d-flex justify-content-between align-items-center">
              <span>Import from Hugging Face</span>
              <Badge bg="info">
                {hfDatasets.length} datasets available
              </Badge>
            </Card.Header>
            <Card.Body>
              {/* Search and Filter */}
              <div className="mb-4">
                <Row>
                  <Col md={8}>
                    <InputGroup>
                      <InputGroup.Text>
                        <Search />
                      </InputGroup.Text>
                      <Form.Control
                        type="text"
                        placeholder="Search datasets..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                      />
                    </InputGroup>
                  </Col>
                  <Col md={4}>
                    <Form.Select
                      value={selectedTask}
                      onChange={(e) => setSelectedTask(e.target.value)}
                    >
                      <option value="">All Tasks</option>
                      <option value="summarization">Summarization</option>
                      <option value="simplification">Simplification</option>
                      <option value="translation">Translation</option>
                      <option value="classification">Classification</option>
                    </Form.Select>
                  </Col>
                </Row>
              </div>
              
              {/* Dataset List */}
              {hfDatasets.length === 0 ? (
                <div className="text-center py-5">
                  <Globe size={48} className="text-muted mb-3" />
                  <h5>No Datasets Found</h5>
                  <p className="text-muted">
                    Try a different search or check your connection
                  </p>
                </div>
              ) : (
                <div className="row row-cols-1 row-cols-md-2 g-4">
                  {hfDatasets.map((dataset) => (
                    <div key={dataset.id} className="col">
                      <Card className="h-100">
                        <Card.Body>
                          <div className="d-flex justify-content-between align-items-start mb-3">
                            <div>
                              <h5 className="mb-1">{dataset.name.split('/').pop()}</h5>
                              <small className="text-muted">by {dataset.name.split('/')[0]}</small>
                            </div>
                            <Badge bg={getTaskColor(dataset.task)}>
                              {dataset.task}
                            </Badge>
                          </div>
                          
                          <p className="small text-muted mb-3" style={{ minHeight: '60px' }}>
                            {dataset.description.length > 150
                              ? `${dataset.description.substring(0, 150)}...`
                              : dataset.description}
                          </p>
                          
                          <div className="mb-3">
                            <small className="text-muted">Languages:</small>
                            <div className="d-flex flex-wrap gap-1 mt-1">
                              {dataset.languages?.map((lang) => (
                                <Badge key={lang} bg="secondary">
                                  {lang}
                                </Badge>
                              ))}
                            </div>
                          </div>
                          
                          <div className="d-flex justify-content-between align-items-center">
                            <small className="text-muted">
                              <CloudDownload className="me-1" />
                              {dataset.size || 'Unknown size'}
                            </small>
                            <div>
                              <Button
                                variant="outline-primary"
                                size="sm"
                                onClick={() => viewDatasetInfo(dataset)}
                                className="me-2"
                              >
                                <InfoCircle className="me-1" />
                                Details
                              </Button>
                              <Button
                                variant="primary"
                                size="sm"
                                onClick={() => {
                                  setSelectedDataset(dataset);
                                  setShowImportModal(true);
                                }}
                              >
                                <Download className="me-1" />
                                Import
                              </Button>
                            </div>
                          </div>
                        </Card.Body>
                      </Card>
                    </div>
                  ))}
                </div>
              )}
            </Card.Body>
          </Card>
        </Tab>
      </Tabs>
      
      {/* Hugging Face Import Modal */}
      <Modal show={showImportModal} onHide={() => setShowImportModal(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>
            Import Dataset: {selectedDataset?.name}
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {selectedDataset?.details && (
            <div className="mb-4">
              <h6>Dataset Details</h6>
              <p className="text-muted">{selectedDataset.details.description}</p>
              
              <div className="row mb-3">
                <div className="col-md-6">
                  <small className="text-muted">Task:</small>
                  <div>
                    <Badge bg={getTaskColor(selectedDataset.details.task)}>
                      {selectedDataset.details.task}
                    </Badge>
                  </div>
                </div>
                <div className="col-md-6">
                  <small className="text-muted">Languages:</small>
                  <div className="d-flex flex-wrap gap-1">
                    {selectedDataset.details.languages?.map((lang) => (
                      <Badge key={lang} bg="secondary">
                        {lang}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
              
              {selectedDataset.details.stats && (
                <Card className="mb-3">
                  <Card.Body className="py-2">
                    <small>
                      <strong>Sample fields:</strong>{' '}
                      {selectedDataset.details.stats.fields?.join(', ')}
                    </small>
                  </Card.Body>
                </Card>
              )}
            </div>
          )}
          
          <h6>Import Configuration</h6>
          <Form>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Dataset Name</Form.Label>
                  <Form.Control
                    type="text"
                    value={importConfig.datasetName || selectedDataset?.name.split('/').pop()}
                    onChange={(e) => setImportConfig({...importConfig, datasetName: e.target.value})}
                    placeholder="Enter dataset name"
                  />
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>Split</Form.Label>
                  <Form.Select
                    value={importConfig.split}
                    onChange={(e) => setImportConfig({...importConfig, split: e.target.value})}
                  >
                    <option value="train">Train</option>
                    <option value="validation">Validation</option>
                    <option value="test">Test</option>
                  </Form.Select>
                </Form.Group>
              </Col>
            </Row>
            
            <Form.Group className="mb-3">
              <Form.Label>Sample Size (optional)</Form.Label>
              <Form.Control
                type="number"
                value={importConfig.sampleSize}
                onChange={(e) => setImportConfig({...importConfig, sampleSize: parseInt(e.target.value) || 0})}
                placeholder="Leave empty for all samples"
                min="1"
                max="100000"
              />
              <Form.Text className="text-muted">
                Number of samples to import. Leave empty to import entire dataset.
              </Form.Text>
            </Form.Group>
            
            <Form.Group className="mb-3">
              <Form.Label>Description</Form.Label>
              <Form.Control
                as="textarea"
                rows={2}
                value={importConfig.description || `Imported from Hugging Face: ${selectedDataset?.name}`}
                onChange={(e) => setImportConfig({...importConfig, description: e.target.value})}
                placeholder="Enter description"
              />
            </Form.Group>
            
            <Form.Group className="mb-4">
              <Form.Check
                type="checkbox"
                label="Make dataset public"
                checked={importConfig.isPublic}
                onChange={(e) => setImportConfig({...importConfig, isPublic: e.target.checked})}
              />
            </Form.Group>
          </Form>
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowImportModal(false)}>
            Cancel
          </Button>
          <Button
            variant="primary"
            onClick={handleHuggingFaceImport}
            disabled={importing}
          >
            {importing ? (
              <Spinner animation="border" size="sm" className="me-2" />
            ) : (
              <Download className="me-2" />
            )}
            Start Import
          </Button>
        </Modal.Footer>
      </Modal>
    </Container>
  );
}

export default DatasetUpload;