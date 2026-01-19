import React, { useState, useEffect } from 'react';
import { Form, Button, Card, Alert, ProgressBar, Table } from 'react-bootstrap';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

function Training() {
  const [datasets, setDatasets] = useState([]);
  const [trainingJobs, setTrainingJobs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    model_type: 'bart',
    dataset_name: '',
    task: 'summarization',
    epochs: 3,
    batch_size: 4,
    learning_rate: 5e-5,
    max_length: 1024,
    target_max_length: 256
  });

  useEffect(() => {
    fetchDatasets();
    fetchTrainingJobs();
  }, []);

  const fetchDatasets = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/datasets`);
      setDatasets(response.data.datasets);
    } catch (err) {
      console.error('Error fetching datasets:', err);
    }
  };

  const fetchTrainingJobs = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/train/jobs`);
      setTrainingJobs(response.data);
    } catch (err) {
      console.error('Error fetching training jobs:', err);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API_BASE}/api/train/start`, formData);
      alert(`Training started! Job ID: ${response.data.job_id}`);
      fetchTrainingJobs();
    } catch (err) {
      setError(err.response?.data?.detail || 'Error starting training');
    } finally {
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.type === 'number' 
        ? parseFloat(e.target.value) 
        : e.target.value
    });
  };

  return (
    <div>
      <h2>Model Training</h2>
      
      <Card className="mb-4">
        <Card.Header>Training Configuration</Card.Header>
        <Card.Body>
          <Form onSubmit={handleSubmit}>
            <Form.Group className="mb-3">
              <Form.Label>Model Type</Form.Label>
              <Form.Select 
                name="model_type" 
                value={formData.model_type}
                onChange={handleChange}
              >
                <option value="bart">BART (for Summarization)</option>
                <option value="pegasus">PEGASUS (for Simplification)</option>
              </Form.Select>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Dataset</Form.Label>
              <Form.Select 
                name="dataset_name" 
                value={formData.dataset_name}
                onChange={handleChange}
                required
              >
                <option value="">Select a dataset</option>
                {datasets.map(dataset => (
                  <option key={dataset.name} value={dataset.name}>
                    {dataset.name} ({Math.round(dataset.size / 1024)} KB)
                  </option>
                ))}
              </Form.Select>
            </Form.Group>

            <Form.Group className="mb-3">
              <Form.Label>Task</Form.Label>
              <Form.Select 
                name="task" 
                value={formData.task}
                onChange={handleChange}
              >
                <option value="summarization">Text Summarization</option>
                <option value="simplification">Text Simplification</option>
              </Form.Select>
            </Form.Group>

            <div className="row">
              <div className="col-md-3">
                <Form.Group className="mb-3">
                  <Form.Label>Epochs</Form.Label>
                  <Form.Control
                    type="number"
                    name="epochs"
                    value={formData.epochs}
                    onChange={handleChange}
                    min="1"
                    max="20"
                  />
                </Form.Group>
              </div>

              <div className="col-md-3">
                <Form.Group className="mb-3">
                  <Form.Label>Batch Size</Form.Label>
                  <Form.Control
                    type="number"
                    name="batch_size"
                    value={formData.batch_size}
                    onChange={handleChange}
                    min="1"
                    max="32"
                  />
                </Form.Group>
              </div>

              <div className="col-md-3">
                <Form.Group className="mb-3">
                  <Form.Label>Learning Rate</Form.Label>
                  <Form.Control
                    type="number"
                    name="learning_rate"
                    value={formData.learning_rate}
                    onChange={handleChange}
                    step="1e-6"
                    min="1e-6"
                    max="1e-3"
                  />
                </Form.Group>
              </div>
            </div>

            {error && <Alert variant="danger">{error}</Alert>}

            <Button 
              variant="primary" 
              type="submit" 
              disabled={loading || !formData.dataset_name}
            >
              {loading ? 'Starting Training...' : 'Start Training'}
            </Button>
          </Form>
        </Card.Body>
      </Card>

      <Card>
        <Card.Header>Training Jobs</Card.Header>
        <Card.Body>
          <Table striped bordered hover>
            <thead>
              <tr>
                <th>Job ID</th>
                <th>Model</th>
                <th>Task</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {trainingJobs.map(job => (
                <tr key={job.job_id}>
                  <td>{job.job_id.slice(0, 8)}...</td>
                  <td>{job.config.model_type}</td>
                  <td>{job.config.task}</td>
                  <td>
                    <span className={`badge ${
                      job.status === 'completed' ? 'bg-success' :
                      job.status === 'running' ? 'bg-primary' :
                      job.status === 'failed' ? 'bg-danger' : 'bg-warning'
                    }`}>
                      {job.status}
                    </span>
                  </td>
                  <td>
                    <Button 
                      variant="outline-info" 
                      size="sm"
                      onClick={() => fetchJobDetails(job.job_id)}
                    >
                      Details
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </Table>
        </Card.Body>
      </Card>
    </div>
  );
}

export default Training;