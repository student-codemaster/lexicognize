import React, { useState, useEffect } from 'react';
import { 
  Form, 
  Button, 
  Card, 
  Alert, 
  ProgressBar, 
  Row, 
  Col,
  Tab,
  Tabs,
  Badge,
  ListGroup,
  Modal
} from 'react-bootstrap';
import axios from 'axios';
import { 
  Upload, 
  FileText, 
  CheckCircle, 
  XCircle,
  Download,
  BarChart,
  FilePdf
} from 'react-bootstrap-icons';
import ReactMarkdown from 'react-markdown';

const API_BASE = 'http://localhost:8000';

function PDFProcessor() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [processing, setProcessing] = useState(false);
  const [progress, setProgress] = useState(0);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');
  const [models, setModels] = useState([]);
  const [processingHistory, setProcessingHistory] = useState([]);
  const [selectedFiles, setSelectedFiles] = useState([]);
  
  const [config, setConfig] = useState({
    operations: ['extract', 'summarize', 'simplify'],
    summaryModel: '',
    simplificationModel: '',
    maxLength: 512,
    minLength: 50,
    useOCR: false
  });

  useEffect(() => {
    fetchAvailableModels();
    fetchProcessingHistory();
  }, []);

  const fetchAvailableModels = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/training/models`);
      setModels(response.data.models || []);
      
      // Set default models if available
      if (response.data.models) {
        const summaryModels = response.data.models.filter(m => 
          m.metadata?.task === 'summary' || m.name.includes('bart')
        );
        const simplificationModels = response.data.models.filter(m => 
          m.metadata?.task === 'simplify' || m.name.includes('pegasus')
        );
        
        if (summaryModels.length > 0 && !config.summaryModel) {
          setConfig(prev => ({ ...prev, summaryModel: summaryModels[0].name }));
        }
        if (simplificationModels.length > 0 && !config.simplificationModel) {
          setConfig(prev => ({ ...prev, simplificationModel: simplificationModels[0].name }));
        }
      }
    } catch (err) {
      console.error('Error fetching models:', err);
    }
  };

  const fetchProcessingHistory = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/pdf/history`);
      setProcessingHistory(response.data.history || []);
    } catch (err) {
      console.error('Error fetching history:', err);
    }
  };

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile);
      setError('');
    } else {
      setFile(null);
      setError('Please select a PDF file');
    }
  };

  const handleOperationToggle = (operation) => {
    const updatedOperations = config.operations.includes(operation)
      ? config.operations.filter(op => op !== operation)
      : [...config.operations, operation];
    
    setConfig({ ...config, operations: updatedOperations });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!file) {
      setError('Please select a PDF file');
      return;
    }

    setUploading(true);
    setProcessing(true);
    setProgress(0);
    setError('');

    const formData = new FormData();
    formData.append('file', file);
    formData.append('operations', JSON.stringify(config.operations));
    formData.append('summary_model', config.summaryModel);
    formData.append('simplification_model', config.simplificationModel);
    formData.append('max_length', config.maxLength);
    formData.append('min_length', config.minLength);

    try {
      // Simulate progress
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + 10;
        });
      }, 500);

      const response = await axios.post(`${API_BASE}/api/pdf/process`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      clearInterval(progressInterval);
      setProgress(100);
      setResult(response.data);
      fetchProcessingHistory();

      // Fetch the generated files
      if (response.data.process_id) {
        fetchProcessedFiles(response.data.process_id);
      }

    } catch (err) {
      setError(err.response?.data?.detail || 'Error processing PDF');
      console.error('Error:', err);
    } finally {
      setUploading(false);
      setTimeout(() => setProcessing(false), 1000);
    }
  };

  const fetchProcessedFiles = async (processId) => {
    try {
      const response = await axios.get(`${API_BASE}/api/pdf/results/${processId}`);
      setSelectedFiles(response.data.files || []);
    } catch (err) {
      console.error('Error fetching processed files:', err);
    }
  };

  const downloadFile = async (filename) => {
    try {
      const response = await axios.get(`${API_BASE}/api/pdf/download/${filename}`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('Error downloading file:', err);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="text-success" />;
      case 'failed':
        return <XCircle className="text-danger" />;
      case 'skipped':
        return <XCircle className="text-warning" />;
      default:
        return null;
    }
  };

  return (
    <div className="pdf-processor">
      <h2 className="mb-4">
        <FilePdf className="me-2" />
        PDF Processing
      </h2>

      <Row>
        <Col md={6}>
          <Card className="mb-4">
            <Card.Header>Upload & Configure</Card.Header>
            <Card.Body>
              <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-3">
                  <Form.Label>Select PDF File</Form.Label>
                  <Form.Control
                    type="file"
                    accept=".pdf"
                    onChange={handleFileChange}
                    disabled={uploading || processing}
                  />
                  {file && (
                    <div className="mt-2">
                      <Badge bg="info">
                        {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
                      </Badge>
                    </div>
                  )}
                </Form.Group>

                <Form.Group className="mb-3">
                  <Form.Label>Operations</Form.Label>
                  <div className="d-flex flex-wrap gap-2">
                    {['extract', 'summarize', 'simplify'].map((op) => (
                      <Button
                        key={op}
                        variant={config.operations.includes(op) ? 'primary' : 'outline-primary'}
                        onClick={() => handleOperationToggle(op)}
                        type="button"
                        size="sm"
                        disabled={uploading || processing}
                      >
                        {op.charAt(0).toUpperCase() + op.slice(1)}
                      </Button>
                    ))}
                  </div>
                </Form.Group>

                {config.operations.includes('summarize') && (
                  <Form.Group className="mb-3">
                    <Form.Label>Summary Model</Form.Label>
                    <Form.Select
                      value={config.summaryModel}
                      onChange={(e) => setConfig({ ...config, summaryModel: e.target.value })}
                      disabled={uploading || processing}
                    >
                      <option value="">Select a model</option>
                      {models
                        .filter(m => m.metadata?.task === 'summary' || m.name.includes('bart'))
                        .map(model => (
                          <option key={model.name} value={model.name}>
                            {model.name} ({model.metadata?.task || 'unknown'})
                          </option>
                        ))}
                    </Form.Select>
                  </Form.Group>
                )}

                {config.operations.includes('simplify') && (
                  <Form.Group className="mb-3">
                    <Form.Label>Simplification Model</Form.Label>
                    <Form.Select
                      value={config.simplificationModel}
                      onChange={(e) => setConfig({ ...config, simplificationModel: e.target.value })}
                      disabled={uploading || processing}
                    >
                      <option value="">Select a model</option>
                      {models
                        .filter(m => m.metadata?.task === 'simplify' || m.name.includes('pegasus'))
                        .map(model => (
                          <option key={model.name} value={model.name}>
                            {model.name} ({model.metadata?.task || 'unknown'})
                          </option>
                        ))}
                    </Form.Select>
                  </Form.Group>
                )}

                <Row>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Max Length</Form.Label>
                      <Form.Control
                        type="number"
                        value={config.maxLength}
                        onChange={(e) => setConfig({ ...config, maxLength: parseInt(e.target.value) })}
                        min="50"
                        max="1024"
                        disabled={uploading || processing}
                      />
                    </Form.Group>
                  </Col>
                  <Col md={6}>
                    <Form.Group className="mb-3">
                      <Form.Label>Min Length</Form.Label>
                      <Form.Control
                        type="number"
                        value={config.minLength}
                        onChange={(e) => setConfig({ ...config, minLength: parseInt(e.target.value) })}
                        min="10"
                        max="500"
                        disabled={uploading || processing}
                      />
                    </Form.Group>
                  </Col>
                </Row>

                {error && <Alert variant="danger">{error}</Alert>}

                <Button
                  variant="primary"
                  type="submit"
                  disabled={!file || uploading || processing}
                >
                  {uploading || processing ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                      Processing...
                    </>
                  ) : (
                    <>
                      <Upload className="me-2" />
                      Process PDF
                    </>
                  )}
                </Button>
              </Form>

              {(uploading || processing) && (
                <div className="mt-3">
                  <ProgressBar now={progress} label={`${progress}%`} />
                  <small className="text-muted">
                    {processing ? 'Processing PDF...' : 'Uploading...'}
                  </small>
                </div>
              )}
            </Card.Body>
          </Card>

          {processingHistory.length > 0 && (
            <Card>
              <Card.Header>Processing History</Card.Header>
              <Card.Body>
                <ListGroup variant="flush">
                  {processingHistory.slice(0, 5).map((item, index) => (
                    <ListGroup.Item key={index}>
                      <div className="d-flex justify-content-between align-items-center">
                        <div>
                          <small className="text-muted">
                            {new Date(item.timestamp).toLocaleString()}
                          </small>
                          <div>{item.files[0]?.split('_').slice(1).join('_')}</div>
                        </div>
                        <Button
                          size="sm"
                          variant="outline-info"
                          onClick={() => fetchProcessedFiles(item.process_id)}
                        >
                          View
                        </Button>
                      </div>
                    </ListGroup.Item>
                  ))}
                </ListGroup>
              </Card.Body>
            </Card>
          )}
        </Col>

        <Col md={6}>
          {result && (
            <Card className="mb-4">
              <Card.Header>
                Processing Results
                <Badge bg="success" className="ms-2">
                  {result.process_id?.slice(0, 8)}
                </Badge>
              </Card.Header>
              <Card.Body>
                <Tabs defaultActiveKey="results" className="mb-3">
                  <Tab eventKey="results" title="Results">
                    <div className="mt-3">
                      {result.extraction && (
                        <div className="mb-4">
                          <h5>
                            <FileText className="me-2" />
                            Text Extraction
                            {getStatusIcon(result.extraction.status)}
                          </h5>
                          {result.extraction.status === 'success' && (
                            <>
                              <Badge bg="info" className="me-2">
                                {result.extraction.text_length} characters
                              </Badge>
                              <div className="mt-2 p-2 bg-light rounded">
                                <pre className="mb-0" style={{ whiteSpace: 'pre-wrap' }}>
                                  {result.extraction.text_preview}
                                </pre>
                              </div>
                            </>
                          )}
                        </div>
                      )}

                      {result.summary && (
                        <div className="mb-4">
                          <h5>
                            <FileText className="me-2" />
                            Summary
                            {getStatusIcon(result.summary.status)}
                          </h5>
                          {result.summary.status === 'success' && (
                            <>
                              <Badge bg="info" className="me-2">
                                {result.summary.summary_length} characters
                              </Badge>
                              <Badge bg="secondary" className="me-2">
                                Model: {result.summary.model_used}
                              </Badge>
                              <div className="mt-2 p-3 bg-light rounded">
                                <ReactMarkdown>
                                  {result.summary.summary}
                                </ReactMarkdown>
                              </div>
                            </>
                          )}
                        </div>
                      )}

                      {result.simplification && (
                        <div className="mb-4">
                          <h5>
                            <FileText className="me-2" />
                            Simplified Text
                            {getStatusIcon(result.simplification.status)}
                          </h5>
                          {result.simplification.status === 'success' && (
                            <>
                              <Badge bg="info" className="me-2">
                                {result.simplification.simplified_length} characters
                              </Badge>
                              <Badge bg="secondary" className="me-2">
                                Model: {result.simplification.model_used}
                              </Badge>
                              <div className="mt-2 p-3 bg-light rounded">
                                <ReactMarkdown>
                                  {result.simplification.simplified_text}
                                </ReactMarkdown>
                              </div>
                            </>
                          )}
                        </div>
                      )}
                    </div>
                  </Tab>

                  <Tab eventKey="files" title="Generated Files">
                    <div className="mt-3">
                      <ListGroup>
                        {selectedFiles.map((file, index) => (
                          <ListGroup.Item key={index} className="d-flex justify-content-between align-items-center">
                            <div>
                              <FileText className="me-2" />
                              <span>{file.filename}</span>
                              <Badge bg="secondary" className="ms-2">
                                {file.type}
                              </Badge>
                            </div>
                            <Button
                              size="sm"
                              variant="outline-primary"
                              onClick={() => downloadFile(file.filename)}
                            >
                              <Download />
                            </Button>
                          </ListGroup.Item>
                        ))}
                      </ListGroup>
                    </div>
                  </Tab>
                </Tabs>
              </Card.Body>
            </Card>
          )}

          {!result && (
            <Card>
              <Card.Body className="text-center text-muted py-5">
                <FilePdf size={48} className="mb-3" />
                <h5>No PDF Processed Yet</h5>
                <p>Upload a PDF file to extract text, generate summaries, and create simplified versions.</p>
              </Card.Body>
            </Card>
          )}
        </Col>
      </Row>
    </div>
  );
}

export default PDFProcessor;