import React, { useState, useEffect } from 'react';
import {
  Container,
  Row,
  Col,
  Card,
  Form,
  Button,
  Alert,
  Tab,
  Tabs,
  Badge,
  ListGroup,
  Modal,
  ProgressBar
} from 'react-bootstrap';
import {
  Translate,
  FileText,
  Globe,
  Download,
  Upload,
  ArrowLeftRight
} from 'react-bootstrap-icons';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

function Translation() {
  const [activeTab, setActiveTab] = useState('document');
  const [languages, setLanguages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  // Document translation state
  const [documentInput, setDocumentInput] = useState('');
  const [documentConfig, setDocumentConfig] = useState({
    targetLanguage: 'hi',
    fields: ['text', 'summary', 'simplified']
  });
  const [translatedDocument, setTranslatedDocument] = useState(null);
  
  // File upload state
  const [uploadedFile, setUploadedFile] = useState(null);
  const [uploadProgress, setUploadProgress] = useState(0);
  
  // Translate and summarize state
  const [translateSummarizeInput, setTranslateSummarizeInput] = useState('');
  const [translateSummarizeConfig, setTranslateSummarizeConfig] = useState({
    targetLanguage: 'hi',
    sourceLanguage: '',
    maxLength: 200
  });
  const [translateSummarizeResult, setTranslateSummarizeResult] = useState(null);
  
  useEffect(() => {
    fetchLanguages();
  }, []);
  
  const fetchLanguages = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/translation/languages`);
      setLanguages(response.data.languages || []);
    } catch (err) {
      console.error('Error fetching languages:', err);
    }
  };
  
  const handleDocumentTranslation = async () => {
    if (!documentInput.trim()) {
      setError('Please enter document JSON');
      return;
    }
    
    let document;
    try {
      document = JSON.parse(documentInput);
    } catch (err) {
      setError('Invalid JSON format');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post(`${API_BASE}/api/translation/translate-document`, {
        document: document,
        target_language: documentConfig.targetLanguage,
        fields: documentConfig.fields
      });
      
      setTranslatedDocument(response.data);
      setSuccess('Document translated successfully');
    } catch (err) {
      setError(err.response?.data?.detail || 'Document translation error');
    } finally {
      setLoading(false);
    }
  };
  
  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;
    
    if (!file.name.endsWith('.json')) {
      setError('Please upload a JSON file');
      return;
    }
    
    setUploadedFile(file);
    
    // Read and display file content
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const content = JSON.parse(e.target.result);
        setDocumentInput(JSON.stringify(content, null, 2));
      } catch (err) {
        setError('Invalid JSON file');
      }
    };
    reader.readAsText(file);
  };
  
  const handleTranslateAndSummarize = async () => {
    if (!translateSummarizeInput.trim()) {
      setError('Please enter text');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post(
        `${API_BASE}/api/multilingual/translate-and-summarize?text=${encodeURIComponent(translateSummarizeInput)}&target_language=${translateSummarizeConfig.targetLanguage}&max_summary_length=${translateSummarizeConfig.maxLength}`
      );
      
      setTranslateSummarizeResult(response.data);
      setSuccess('Text translated and summarized successfully');
    } catch (err) {
      setError(err.response?.data?.detail || 'Error in translate and summarize');
    } finally {
      setLoading(false);
    }
  };
  
  const downloadTranslatedDocument = () => {
    if (!translatedDocument) return;
    
    const content = JSON.stringify(translatedDocument, null, 2);
    const blob = new Blob([content], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `translated_document_${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };
  
  const getLanguageName = (code) => {
    const lang = languages.find(l => l.code === code);
    return lang ? lang.name : code;
  };
  
  const sampleDocument = {
    "case_id": "SC_2023_001",
    "text": "The Supreme Court held that the constitutional right to privacy is an intrinsic part of Article 21 of the Indian Constitution. The judgment emphasized the importance of data protection and individual autonomy in the digital age.",
    "summary": "Supreme Court recognizes right to privacy as fundamental right under Article 21.",
    "simplified": "The Supreme Court said privacy is a basic right under the Constitution. This is important for protecting personal information online.",
    "category": "constitutional_law",
    "year": 2023
  };
  
  const loadSampleDocument = () => {
    setDocumentInput(JSON.stringify(sampleDocument, null, 2));
  };
  
  return (
    <Container className="py-4">
      <h2 className="mb-4">
        <Translate className="me-2" />
        Advanced Translation Tools
      </h2>
      
      <Tabs
        activeKey={activeTab}
        onSelect={(k) => setActiveTab(k)}
        className="mb-4"
      >
        <Tab eventKey="document" title={<><FileText /> Document Translation</>}>
          <Card>
            <Card.Header className="d-flex justify-content-between align-items-center">
              <span>Legal Document Translation</span>
              <Button
                variant="outline-secondary"
                size="sm"
                onClick={loadSampleDocument}
              >
                Load Sample
              </Button>
            </Card.Header>
            <Card.Body>
              <Row>
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Upload JSON Document</Form.Label>
                    <Form.Control
                      type="file"
                      accept=".json"
                      onChange={handleFileUpload}
                      className="mb-2"
                    />
                    {uploadedFile && (
                      <Badge bg="info">
                        {uploadedFile.name} ({(uploadedFile.size / 1024).toFixed(1)} KB)
                      </Badge>
                    )}
                  </Form.Group>
                  
                  <Form.Group className="mb-3">
                    <Form.Label>Or Paste Document JSON</Form.Label>
                    <Form.Control
                      as="textarea"
                      rows={12}
                      value={documentInput}
                      onChange={(e) => setDocumentInput(e.target.value)}
                      placeholder="Paste your legal document JSON here..."
                    />
                  </Form.Group>
                </Col>
                
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Target Language</Form.Label>
                    <Form.Select
                      value={documentConfig.targetLanguage}
                      onChange={(e) => setDocumentConfig({
                        ...documentConfig,
                        targetLanguage: e.target.value
                      })}
                    >
                      {languages
                        .filter(lang => lang.is_indian)
                        .map(lang => (
                          <option key={lang.code} value={lang.code}>
                            {lang.name} ({lang.script})
                          </option>
                        ))}
                    </Form.Select>
                  </Form.Group>
                  
                  <Form.Group className="mb-3">
                    <Form.Label>Fields to Translate</Form.Label>
                    <div>
                      {['text', 'summary', 'simplified', 'title', 'description'].map(field => (
                        <Form.Check
                          key={field}
                          type="checkbox"
                          id={`field-${field}`}
                          label={field}
                          checked={documentConfig.fields.includes(field)}
                          onChange={(e) => {
                            const fields = e.target.checked
                              ? [...documentConfig.fields, field]
                              : documentConfig.fields.filter(f => f !== field);
                            setDocumentConfig({ ...documentConfig, fields });
                          }}
                          className="mb-2"
                        />
                      ))}
                    </div>
                  </Form.Group>
                  
                  <Button
                    variant="primary"
                    onClick={handleDocumentTranslation}
                    disabled={loading || !documentInput.trim()}
                    className="w-100"
                  >
                    <Translate className="me-2" />
                    Translate Document
                  </Button>
                  
                  {translatedDocument && (
                    <Button
                      variant="outline-success"
                      onClick={downloadTranslatedDocument}
                      className="w-100 mt-2"
                    >
                      <Download className="me-2" />
                      Download Translated Document
                    </Button>
                  )}
                </Col>
              </Row>
              
              {translatedDocument && (
                <div className="mt-4">
                  <Card>
                    <Card.Header>Translation Results</Card.Header>
                    <Card.Body>
                      <Tabs defaultActiveKey="original" className="mb-3">
                        <Tab eventKey="original" title="Original Document">
                          <pre className="bg-light p-3 rounded" style={{ maxHeight: '300px', overflow: 'auto' }}>
                            {JSON.stringify(translatedDocument.original_document, null, 2)}
                          </pre>
                        </Tab>
                        <Tab eventKey="translated" title="Translated Document">
                          <pre className="bg-light p-3 rounded" style={{ maxHeight: '300px', overflow: 'auto' }}>
                            {JSON.stringify(translatedDocument.translated_document, null, 2)}
                          </pre>
                        </Tab>
                        <Tab eventKey="comparison" title="Field Comparison">
                          <ListGroup>
                            {translatedDocument.translated_fields.map(field => (
                              <ListGroup.Item key={field}>
                                <h6>{field}</h6>
                                <Row>
                                  <Col md={6}>
                                    <div className="p-2 bg-light rounded mb-2">
                                      <small className="text-muted">Original:</small>
                                      <p className="mb-0">{translatedDocument.original_document[field]}</p>
                                    </div>
                                  </Col>
                                  <Col md={6}>
                                    <div className="p-2 bg-light rounded mb-2">
                                      <small className="text-muted">Translated:</small>
                                      <p className="mb-0">{translatedDocument.translated_document[`${field}_${translatedDocument.target_language}`]}</p>
                                    </div>
                                  </Col>
                                </Row>
                              </ListGroup.Item>
                            ))}
                          </ListGroup>
                        </Tab>
                      </Tabs>
                      
                      <div className="mt-3">
                        <Badge bg="primary" className="me-2">
                          Target: {getLanguageName(translatedDocument.target_language)}
                        </Badge>
                        <Badge bg="success" className="me-2">
                          {translatedDocument.translated_fields.length} fields translated
                        </Badge>
                      </div>
                    </Card.Body>
                  </Card>
                </div>
              )}
            </Card.Body>
          </Card>
        </Tab>
        
        <Tab eventKey="translate-summarize" title={<><ArrowLeftRight /> Translate & Summarize</>}>
          <Card>
            <Card.Header>Translate and Summarize in One Step</Card.Header>
            <Card.Body>
              <Row>
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Source Text</Form.Label>
                    <Form.Control
                      as="textarea"
                      rows={8}
                      value={translateSummarizeInput}
                      onChange={(e) => setTranslateSummarizeInput(e.target.value)}
                      placeholder="Enter text to translate and summarize..."
                    />
                  </Form.Group>
                  
                  <Form.Group className="mb-3">
                    <Form.Label>Source Language (Optional - Auto-detected if empty)</Form.Label>
                    <Form.Control
                      type="text"
                      value={translateSummarizeConfig.sourceLanguage}
                      onChange={(e) => setTranslateSummarizeConfig({
                        ...translateSummarizeConfig,
                        sourceLanguage: e.target.value
                      })}
                      placeholder="en, hi, ta, kn, etc. (leave empty for auto-detection)"
                    />
                  </Form.Group>
                </Col>
                
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Target Language for Summary</Form.Label>
                    <Form.Select
                      value={translateSummarizeConfig.targetLanguage}
                      onChange={(e) => setTranslateSummarizeConfig({
                        ...translateSummarizeConfig,
                        targetLanguage: e.target.value
                      })}
                    >
                      {languages
                        .filter(lang => lang.is_indian)
                        .map(lang => (
                          <option key={lang.code} value={lang.code}>
                            {lang.name}
                          </option>
                        ))}
                    </Form.Select>
                  </Form.Group>
                  
                  <Form.Group className="mb-3">
                    <Form.Label>Maximum Summary Length</Form.Label>
                    <Form.Control
                      type="number"
                      value={translateSummarizeConfig.maxLength}
                      onChange={(e) => setTranslateSummarizeConfig({
                        ...translateSummarizeConfig,
                        maxLength: parseInt(e.target.value)
                      })}
                      min="50"
                      max="500"
                    />
                  </Form.Group>
                  
                  <Button
                    variant="primary"
                    onClick={handleTranslateAndSummarize}
                    disabled={loading || !translateSummarizeInput.trim()}
                    className="w-100"
                  >
                    <ArrowLeftRight className="me-2" />
                    Translate & Summarize
                  </Button>
                </Col>
              </Row>
              
              {translateSummarizeResult && (
                <div className="mt-4">
                  <Card>
                    <Card.Header>Results</Card.Header>
                    <Card.Body>
                      <Row>
                        <Col md={4}>
                          <Card className="h-100">
                            <Card.Header>Original Text</Card.Header>
                            <Card.Body>
                              <div className="p-2 bg-light rounded" style={{ maxHeight: '200px', overflow: 'auto' }}>
                                {translateSummarizeResult.original_text}
                              </div>
                              <div className="mt-2">
                                <Badge bg="info">
                                  Source: {getLanguageName(translateSummarizeResult.source_language)}
                                </Badge>
                              </div>
                            </Card.Body>
                          </Card>
                        </Col>
                        
                        <Col md={4}>
                          <Card className="h-100">
                            <Card.Header>Translated Text</Card.Header>
                            <Card.Body>
                              <div className="p-2 bg-light rounded" style={{ maxHeight: '200px', overflow: 'auto' }}>
                                {translateSummarizeResult.translated_text}
                              </div>
                              <div className="mt-2">
                                <Badge bg="success">
                                  Target: {getLanguageName(translateSummarizeResult.target_language)}
                                </Badge>
                                {translateSummarizeResult.translation_needed && (
                                  <Badge bg="warning" className="ms-1">
                                    Translated
                                  </Badge>
                                )}
                              </div>
                            </Card.Body>
                          </Card>
                        </Col>
                        
                        <Col md={4}>
                          <Card className="h-100">
                            <Card.Header>Generated Summary</Card.Header>
                            <Card.Body>
                              <div className="p-2 bg-light rounded" style={{ maxHeight: '200px', overflow: 'auto' }}>
                                {translateSummarizeResult.summary}
                              </div>
                              <div className="mt-2">
                                <Badge bg="primary">
                                  Summary in {getLanguageName(translateSummarizeResult.target_language)}
                                </Badge>
                                {translateSummarizeResult.model_used && (
                                  <small className="d-block text-muted mt-1">
                                    Model: {translateSummarizeResult.model_used}
                                  </small>
                                )}
                              </div>
                            </Card.Body>
                          </Card>
                        </Col>
                      </Row>
                    </Card.Body>
                  </Card>
                </div>
              )}
            </Card.Body>
          </Card>
        </Tab>
      </Tabs>
      
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
      
      {/* Language Support Info */}
      <Card className="mt-4">
        <Card.Header>
          <Globe className="me-2" />
          Supported Indian Languages
        </Card.Header>
        <Card.Body>
          <Row>
            {languages
              .filter(lang => lang.is_indian)
              .map(lang => (
                <Col md={4} key={lang.code} className="mb-3">
                  <Card className="h-100">
                    <Card.Body>
                      <div className="d-flex align-items-center mb-3">
                        <div className="bg-primary text-white rounded-circle d-flex align-items-center justify-content-center" style={{ width: '40px', height: '40px' }}>
                          {lang.code.toUpperCase()}
                        </div>
                        <div className="ms-3">
                          <h5 className="mb-0">{lang.name}</h5>
                          <small className="text-muted">{lang.script} Script</small>
                        </div>
                      </div>
                      <div className="mb-2">
                        <Badge bg="info" className="me-1">Translation</Badge>
                        <Badge bg="success" className="me-1">Transliteration</Badge>
                        <Badge bg="warning">Summarization</Badge>
                      </div>
                      <p className="small text-muted mb-0">
                        Supports legal document translation with term preservation
                      </p>
                    </Card.Body>
                  </Card>
                </Col>
              ))}
          </Row>
        </Card.Body>
      </Card>
    </Container>
  );
}

export default Translation;