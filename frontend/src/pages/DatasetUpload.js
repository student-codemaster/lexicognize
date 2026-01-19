import React, { useState, useEffect } from 'react';
import { 
  Form, 
  Button, 
  Card, 
  Alert, 
  ProgressBar, 
  Table,
  Badge,
  Modal,
  Row,
  Col
} from 'react-bootstrap';
import { 
  Upload, 
  FileText, 
  CheckCircle, 
  XCircle,
  Database,
  Merge
} from 'react-bootstrap-icons';
import axios from 'axios';
import Papa from 'papaparse';

const API_BASE = 'http://localhost:8000';

function DatasetUpload() {
  const [files, setFiles] = useState([]);
  const [uploading, setUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [datasets, setDatasets] = useState([]);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [mergeOption, setMergeOption] = useState(false);
  const [datasetName, setDatasetName] = useState('');
  const [showPreview, setShowPreview] = useState(false);
  const [previewData, setPreviewData] = useState(null);

  useEffect(() => {
    fetchDatasets();
  }, []);

  const fetchDatasets = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/datasets/list`);
      setDatasets(response.data.datasets || []);
    } catch (err) {
      console.error('Error fetching datasets:', err);
    }
  };

  const handleFileChange = (e) => {
    const selectedFiles = Array.from(e.target.files);
    
    // Filter only JSON files
    const jsonFiles = selectedFiles.filter(file => 
      file.type === 'application/json' || file.name.endsWith('.json')
    );
    
    if (jsonFiles.length !== selectedFiles.length) {
      setError('Only JSON files are allowed');
    } else {
      setError('');
    }
    
    setFiles(jsonFiles);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (files.length === 0) {
      setError('Please select at least one JSON file');
      return;
    }

    setUploading(true);
    setProgress(0);
    setError('');
    setSuccess('');

    const formData = new FormData();
    files.forEach(file => {
      formData.append('files', file);
    });
    formData.append('merge', mergeOption);
    if (mergeOption && datasetName) {
      formData.append('dataset_name', datasetName);
    }

    try {
      // Simulate progress for better UX
      const progressInterval = setInterval(() => {
        setProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval);
            return prev;
          }
          return prev + 10;
        });
      }, 300);

      const response = await axios.post(
        `${API_BASE}/api/datasets/upload-multiple`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          },
          onUploadProgress: (progressEvent) => {
            const percent = Math.round(
              (progressEvent.loaded * 100) / progressEvent.total
            );
            setProgress(percent);
          }
        }
      );

      clearInterval(progressInterval);
      setProgress(100);
      
      setSuccess(response.data.message);
      setFiles([]);
      fetchDatasets();

      // Auto-generate name for merged dataset
      if (mergeOption && response.data.dataset_name) {
        setDatasetName(response.data.dataset_name);
      }

    } catch (err) {
      setError(err.response?.data?.detail || 'Error uploading files');
      console.error('Error:', err);
    } finally {
      setTimeout(() => setUploading(false), 1000);
    }
  };

  const deleteDataset = async (name) => {
    if (window.confirm(`Are you sure you want to delete dataset "${name}"?`)) {
      try {
        await axios.delete(`${API_BASE}/api/datasets/${name}`);
        fetchDatasets();
        setSuccess(`Dataset "${name}" deleted successfully`);
      } catch (err) {
        setError(err.response?.data?.detail || 'Error deleting dataset');
      }
    }
  };

  const previewDataset = async (name) => {
    try {
      const response = await axios.get(`${API_BASE}/api/datasets/stats/${name}`);
      setPreviewData(response.data);
      setShowPreview(true);
    } catch (err) {
      setError(err.response?.data?.detail || 'Error loading dataset preview');
    }
  };

  const downloadDataset = async (name) => {
    try {
      const response = await axios.get(`${API_BASE}/api/datasets/download/${name}`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${name}.json`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      console.error('Error downloading dataset:', err);
    }
  };

  const exportToCSV = (name, data) => {
    const csv = Papa.unparse(data);
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `${name}.csv`);
    document.body.appendChild(link);
    link.click();
    link.remove();
  };

  const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className="dataset-upload">
      <h2 className="mb-4">
        <Database className="me-2" />
        Dataset Management
      </h2>

      <Row>
        <Col md={6}>
          <Card className="mb-4">
            <Card.Header>Upload JSON Files</Card.Header>
            <Card.Body>
              <Form onSubmit={handleSubmit}>
                <Form.Group className="mb-3">
                  <Form.Label>Select JSON Files</Form.Label>
                  <Form.Control
                    type="file"
                    accept=".json"
                    multiple
                    onChange={handleFileChange}
                    disabled={uploading}
                  />
                  <Form.Text className="text-muted">
                    Select multiple JSON files containing legal documents with text, summary, and simplified fields.
                  </Form.Text>
                </Form.Group>

                {files.length > 0 && (
                  <div className="mb-3">
                    <h6>Selected Files ({files.length})</h6>
                    <ul className="list-group small">
                      {files.map((file, index) => (
                        <li key={index} className="list-group-item d-flex justify-content-between align-items-center">
                          <span>
                            <FileText className="me-2" />
                            {file.name}
                          </span>
                          <Badge bg="info">
                            {formatFileSize(file.size)}
                          </Badge>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                <Form.Group className="mb-3">
                  <Form.Check
                    type="checkbox"
                    label="Merge files into single dataset"
                    checked={mergeOption}
                    onChange={(e) => setMergeOption(e.target.checked)}
                    disabled={uploading}
                  />
                </Form.Group>

                {mergeOption && (
                  <Form.Group className="mb-3">
                    <Form.Label>Dataset Name (optional)</Form.Label>
                    <Form.Control
                      type="text"
                      placeholder="e.g., legal_cases_2024"
                      value={datasetName}
                      onChange={(e) => setDatasetName(e.target.value)}
                      disabled={uploading}
                    />
                    <Form.Text className="text-muted">
                      Leave blank for auto-generated name
                    </Form.Text>
                  </Form.Group>
                )}

                {error && <Alert variant="danger">{error}</Alert>}
                {success && <Alert variant="success">{success}</Alert>}

                <Button
                  variant="primary"
                  type="submit"
                  disabled={files.length === 0 || uploading}
                >
                  {uploading ? (
                    <>
                      <span className="spinner-border spinner-border-sm me-2" role="status" aria-hidden="true"></span>
                      Uploading...
                    </>
                  ) : (
                    <>
                      <Upload className="me-2" />
                      Upload Files
                    </>
                  )}
                </Button>
              </Form>

              {uploading && (
                <div className="mt-3">
                  <ProgressBar now={progress} label={`${progress}%`} />
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>

        <Col md={6}>
          <Card>
            <Card.Header className="d-flex justify-content-between align-items-center">
              <span>Available Datasets ({datasets.length})</span>
              <Button 
                variant="outline-primary" 
                size="sm"
                onClick={fetchDatasets}
              >
                Refresh
              </Button>
            </Card.Header>
            <Card.Body>
              {datasets.length === 0 ? (
                <div className="text-center text-muted py-5">
                  <Database size={48} className="mb-3" />
                  <h5>No datasets uploaded yet</h5>
                  <p>Upload JSON files to get started</p>
                </div>
              ) : (
                <Table striped hover size="sm">
                  <thead>
                    <tr>
                      <th>Name</th>
                      <th>Samples</th>
                      <th>Size</th>
                      <th>Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {datasets.map((dataset, index) => (
                      <tr key={index}>
                        <td>
                          <div className="fw-bold">{dataset.name}</div>
                          <small className="text-muted">
                            {new Date(dataset.created_at).toLocaleDateString()}
                          </small>
                        </td>
                        <td>
                          <Badge bg="info">
                            {dataset.samples?.toLocaleString()}
                          </Badge>
                        </td>
                        <td>
                          <Badge bg="secondary">
                            {formatFileSize(dataset.size)}
                          </Badge>
                        </td>
                        <td>
                          <div className="btn-group btn-group-sm">
                            <Button
                              variant="outline-info"
                              size="sm"
                              onClick={() => previewDataset(dataset.name)}
                              title="Preview"
                            >
                              <FileText />
                            </Button>
                            <Button
                              variant="outline-success"
                              size="sm"
                              onClick={() => downloadDataset(dataset.name)}
                              title="Download"
                            >
                              <Download />
                            </Button>
                            <Button
                              variant="outline-danger"
                              size="sm"
                              onClick={() => deleteDataset(dataset.name)}
                              title="Delete"
                            >
                              <XCircle />
                            </Button>
                          </div>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </Table>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>

      {/* Preview Modal */}
      <Modal show={showPreview} onHide={() => setShowPreview(false)} size="lg">
        <Modal.Header closeButton>
          <Modal.Title>
            <FileText className="me-2" />
            Dataset Preview
          </Modal.Title>
        </Modal.Header>
        <Modal.Body>
          {previewData && (
            <div>
              <h5>{previewData.dataset}</h5>
              <Row className="mb-4">
                <Col md={6}>
                  <Card>
                    <Card.Body>
                      <h6>Basic Info</h6>
                      <div className="mb-2">
                        <strong>Samples:</strong>{' '}
                        <Badge bg="info">{previewData.total_samples}</Badge>
                      </div>
                      {previewData.statistics && (
                        <>
                          <div className="mb-2">
                            <strong>Avg Text Length:</strong>{' '}
                            <Badge bg="secondary">
                              {Math.round(previewData.statistics.avg_text_length || 0)} chars
                            </Badge>
                          </div>
                          <div className="mb-2">
                            <strong>Avg Summary Length:</strong>{' '}
                            <Badge bg="secondary">
                              {Math.round(previewData.statistics.avg_summary_length || 0)} chars
                            </Badge>
                          </div>
                        </>
                      )}
                    </Card.Body>
                  </Card>
                </Col>
                <Col md={6}>
                  <Card>
                    <Card.Body>
                      <h6>Sample Document</h6>
                      {previewData.statistics?.sample_document && (
                        <div className="small">
                          <div className="mb-2">
                            <strong>Text Preview:</strong>
                            <div className="text-muted mt-1" style={{ maxHeight: '100px', overflow: 'hidden' }}>
                              {previewData.statistics.sample_document.text?.substring(0, 200)}...
                            </div>
                          </div>
                          <div className="mb-2">
                            <strong>Summary:</strong>
                            <div className="text-muted mt-1">
                              {previewData.statistics.sample_document.summary}
                            </div>
                          </div>
                        </div>
                      )}
                    </Card.Body>
                  </Card>
                </Col>
              </Row>
            </div>
          )}
        </Modal.Body>
        <Modal.Footer>
          <Button variant="secondary" onClick={() => setShowPreview(false)}>
            Close
          </Button>
          {previewData && (
            <Button 
              variant="primary"
              onClick={() => exportToCSV(previewData.dataset, previewData.statistics)}
            >
              Export to CSV
            </Button>
          )}
        </Modal.Footer>
      </Modal>
    </div>
  );
}

export default DatasetUpload;