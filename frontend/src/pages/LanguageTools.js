import React, { useState, useEffect } from 'react';
import {
  Container,
  Row,
  Col,
  Card,
  Form,
  Button,
  Alert,
  Badge,
  Tab,
  Tabs,
  Spinner,
  ListGroup,
  ProgressBar
} from 'react-bootstrap';
import {
  Translate,
  Type,
  Globe,
  FileText,
  Download,
  Upload
} from 'react-bootstrap-icons';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

function LanguageTools() {
  const [activeTab, setActiveTab] = useState('translation');
  const [supportedLanguages, setSupportedLanguages] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [result, setResult] = useState(null);
  
  // Translation state
  const [translationInput, setTranslationInput] = useState('');
  const [translationConfig, setTranslationConfig] = useState({
    sourceLanguage: '',
    targetLanguage: 'hi',
    detectLanguage: true,
    maxLength: 1024
  });
  
  // Transliteration state
  const [transliterationInput, setTransliterationInput] = useState('');
  const [transliterationConfig, setTransliterationConfig] = useState({
    sourceLanguage: 'en',
    targetLanguage: 'hi',
    preserveTerms: true
  });
  
  // Language detection state
  const [detectionInput, setDetectionInput] = useState('');
  const [detectionResult, setDetectionResult] = useState(null);
  
  // Batch processing state
  const [batchInput, setBatchInput] = useState('');
  const [batchResults, setBatchResults] = useState([]);
  
  useEffect(() => {
    fetchSupportedLanguages();
  }, []);
  
  const fetchSupportedLanguages = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/translation/languages`);
      setSupportedLanguages(response.data.languages || []);
      
      // Set default source language to auto-detect
      setTranslationConfig(prev => ({
        ...prev,
        sourceLanguage: ''
      }));
    } catch (err) {
      console.error('Error fetching languages:', err);
    }
  };
  
  const handleTranslate = async () => {
    if (!translationInput.trim()) {
      setError('Please enter text to translate');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post(`${API_BASE}/api/translation/translate`, {
        text: translationInput,
        source_language: translationConfig.sourceLanguage || null,
        target_language: translationConfig.targetLanguage,
        detect_language: translationConfig.detectLanguage,
        max_length: translationConfig.maxLength
      });
      
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Translation error');
    } finally {
      setLoading(false);
    }
  };
  
  const handleTransliterate = async () => {
    if (!transliterationInput.trim()) {
      setError('Please enter text to transliterate');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post(`${API_BASE}/api/transliteration/transliterate`, {
        text: transliterationInput,
        source_language: transliterationConfig.sourceLanguage,
        target_language: transliterationConfig.targetLanguage,
        preserve_terms: transliterationConfig.preserveTerms
      });
      
      setResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Transliteration error');
    } finally {
      setLoading(false);
    }
  };
  
  const handleDetectLanguage = async () => {
    if (!detectionInput.trim()) {
      setError('Please enter text to detect language');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post(`${API_BASE}/api/translation/detect-language`, detectionInput, {
        headers: { 'Content-Type': 'text/plain' }
      });
      
      setDetectionResult(response.data);
    } catch (err) {
      setError(err.response?.data?.detail || 'Detection error');
    } finally {
      setLoading(false);
    }
  };
  
  const handleBatchTranslation = async () => {
    const texts = batchInput.split('\n').filter(text => text.trim());
    if (texts.length === 0) {
      setError('Please enter texts (one per line)');
      return;
    }
    
    setLoading(true);
    setError('');
    
    try {
      const response = await axios.post(`${API_BASE}/api/translation/translate-batch`, {
        texts: texts,
        target_language: translationConfig.targetLanguage,
        detect_language: true
      });
      
      setBatchResults(response.data.results || []);
    } catch (err) {
      setError(err.response?.data?.detail || 'Batch translation error');
    } finally {
      setLoading(false);
    }
  };
  
  const downloadResult = () => {
    if (!result) return;
    
    const content = JSON.stringify(result, null, 2);
    const blob = new Blob([content], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `language_result_${Date.now()}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };
  
  const getLanguageName = (code) => {
    const lang = supportedLanguages.find(l => l.code === code);
    return lang ? lang.name : code;
  };
  
  const getIndianLanguages = () => {
    return supportedLanguages.filter(lang => lang.is_indian);
  };
  
  return (
    <Container className="py-4">
      <h2 className="mb-4">
        <Globe className="me-2" />
        Language Tools
      </h2>
      
      <Tabs
        activeKey={activeTab}
        onSelect={(k) => setActiveTab(k)}
        className="mb-4"
      >
        <Tab eventKey="translation" title={<><Translate /> Translation</>}>
          <Card>
            <Card.Header>Text Translation</Card.Header>
            <Card.Body>
              <Row>
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Source Text</Form.Label>
                    <Form.Control
                      as="textarea"
                      rows={8}
                      value={translationInput}
                      onChange={(e) => setTranslationInput(e.target.value)}
                      placeholder="Enter text to translate..."
                    />
                  </Form.Group>
                </Col>
                
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Target Language</Form.Label>
                    <Form.Select
                      value={translationConfig.targetLanguage}
                      onChange={(e) => setTranslationConfig({
                        ...translationConfig,
                        targetLanguage: e.target.value
                      })}
                    >
                      {getIndianLanguages().map(lang => (
                        <option key={lang.code} value={lang.code}>
                          {lang.name} ({lang.script})
                        </option>
                      ))}
                    </Form.Select>
                  </Form.Group>
                  
                  <Form.Group className="mb-3">
                    <Form.Check
                      type="checkbox"
                      label="Auto-detect source language"
                      checked={translationConfig.detectLanguage}
                      onChange={(e) => setTranslationConfig({
                        ...translationConfig,
                        detectLanguage: e.target.checked,
                        sourceLanguage: e.target.checked ? '' : 'en'
                      })}
                    />
                  </Form.Group>
                  
                  {!translationConfig.detectLanguage && (
                    <Form.Group className="mb-3">
                      <Form.Label>Source Language</Form.Label>
                      <Form.Select
                        value={translationConfig.sourceLanguage}
                        onChange={(e) => setTranslationConfig({
                          ...translationConfig,
                          sourceLanguage: e.target.value
                        })}
                      >
                        <option value="">Select source language</option>
                        {supportedLanguages.map(lang => (
                          <option key={lang.code} value={lang.code}>
                            {lang.name}
                          </option>
                        ))}
                      </Form.Select>
                    </Form.Group>
                  )}
                  
                  <Button
                    variant="primary"
                    onClick={handleTranslate}
                    disabled={loading || !translationInput.trim()}
                    className="w-100"
                  >
                    {loading ? (
                      <Spinner animation="border" size="sm" className="me-2" />
                    ) : (
                      <Translate className="me-2" />
                    )}
                    Translate
                  </Button>
                </Col>
              </Row>
              
              {result && (
                <div className="mt-4">
                  <Card>
                    <Card.Header className="d-flex justify-content-between align-items-center">
                      <span>Translation Result</span>
                      <Button
                        variant="outline-primary"
                        size="sm"
                        onClick={downloadResult}
                      >
                        <Download /> Download
                      </Button>
                    </Card.Header>
                    <Card.Body>
                      <Row>
                        <Col md={6}>
                          <h6>Original</h6>
                          <div className="p-3 bg-light rounded">
                            <p className="mb-0">{result.original_text}</p>
                            {result.source_language && (
                              <small className="text-muted">
                                Language: {getLanguageName(result.source_language)}
                                {result.confidence && ` (${(result.confidence * 100).toFixed(1)}% confidence)`}
                              </small>
                            )}
                          </div>
                        </Col>
                        <Col md={6}>
                          <h6>Translated</h6>
                          <div className="p-3 bg-light rounded">
                            <p className="mb-0">{result.translated_text}</p>
                            <small className="text-muted">
                              Language: {getLanguageName(result.target_language)}
                            </small>
                          </div>
                        </Col>
                      </Row>
                      
                      <div className="mt-3">
                        <Badge bg="info" className="me-2">
                          Source: {getLanguageName(result.source_language)}
                        </Badge>
                        <Badge bg="success" className="me-2">
                          Target: {getLanguageName(result.target_language)}
                        </Badge>
                        {result.translation_needed !== undefined && (
                          <Badge bg={result.translation_needed ? 'warning' : 'secondary'}>
                            {result.translation_needed ? 'Translation Applied' : 'No Translation Needed'}
                          </Badge>
                        )}
                      </div>
                    </Card.Body>
                  </Card>
                </div>
              )}
            </Card.Body>
          </Card>
        </Tab>
        
        <Tab eventKey="transliteration" title={<><Type /> Transliteration</>}>
          <Card>
            <Card.Header>Text Transliteration</Card.Header>
            <Card.Body>
              <Row>
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Source Text</Form.Label>
                    <Form.Control
                      as="textarea"
                      rows={8}
                      value={transliterationInput}
                      onChange={(e) => setTransliterationInput(e.target.value)}
                      placeholder="Enter text to transliterate..."
                    />
                  </Form.Group>
                </Col>
                
                <Col md={6}>
                  <Form.Group className="mb-3">
                    <Form.Label>Source Language/Script</Form.Label>
                    <Form.Select
                      value={transliterationConfig.sourceLanguage}
                      onChange={(e) => setTransliterationConfig({
                        ...transliterationConfig,
                        sourceLanguage: e.target.value
                      })}
                    >
                      <option value="en">English (Latin)</option>
                      <option value="hi">Hindi (Devanagari)</option>
                      <option value="ta">Tamil (Tamil)</option>
                      <option value="kn">Kannada (Kannada)</option>
                      <option value="te">Telugu (Telugu)</option>
                      <option value="ml">Malayalam (Malayalam)</option>
                    </Form.Select>
                  </Form.Group>
                  
                  <Form.Group className="mb-3">
                    <Form.Label>Target Language/Script</Form.Label>
                    <Form.Select
                      value={transliterationConfig.targetLanguage}
                      onChange={(e) => setTransliterationConfig({
                        ...transliterationConfig,
                        targetLanguage: e.target.value
                      })}
                    >
                      <option value="hi">Hindi (Devanagari)</option>
                      <option value="ta">Tamil (Tamil)</option>
                      <option value="kn">Kannada (Kannada)</option>
                      <option value="en">English (Latin)</option>
                      <option value="te">Telugu (Telugu)</option>
                      <option value="ml">Malayalam (Malayalam)</option>
                    </Form.Select>
                  </Form.Group>
                  
                  <Form.Group className="mb-3">
                    <Form.Check
                      type="checkbox"
                      label="Preserve legal terms and formatting"
                      checked={transliterationConfig.preserveTerms}
                      onChange={(e) => setTransliterationConfig({
                        ...transliterationConfig,
                        preserveTerms: e.target.checked
                      })}
                    />
                  </Form.Group>
                  
                  <Button
                    variant="primary"
                    onClick={handleTransliterate}
                    disabled={loading || !transliterationInput.trim()}
                    className="w-100"
                  >
                    {loading ? (
                      <Spinner animation="border" size="sm" className="me-2" />
                    ) : (
                      <Type className="me-2" />
                    )}
                    Transliterate
                  </Button>
                </Col>
              </Row>
              
              {result && (
                <div className="mt-4">
                  <Card>
                    <Card.Header>Transliteration Result</Card.Header>
                    <Card.Body>
                      <Row>
                        <Col md={6}>
                          <h6>Original</h6>
                          <div className="p-3 bg-light rounded">
                            <p className="mb-0">{result.original_text}</p>
                            <small className="text-muted">
                              Script: {result.source_script}
                            </small>
                          </div>
                        </Col>
                        <Col md={6}>
                          <h6>Transliterated</h6>
                          <div className="p-3 bg-light rounded">
                            <p className="mb-0">{result.transliterated_text}</p>
                            <small className="text-muted">
                              Script: {result.target_script}
                            </small>
                          </div>
                        </Col>
                      </Row>
                      
                      {result.preserved_sections && result.preserved_sections.length > 0 && (
                        <div className="mt-3">
                          <h6>Preserved Sections</h6>
                          <ListGroup>
                            {result.preserved_sections.map((section, idx) => (
                              <ListGroup.Item key={idx}>
                                <Badge bg="info" className="me-2">
                                  {section[0]}
                                </Badge>
                                {section[1]}
                              </ListGroup.Item>
                            ))}
                          </ListGroup>
                        </div>
                      )}
                    </Card.Body>
                  </Card>
                </div>
              )}
            </Card.Body>
          </Card>
        </Tab>
        
        <Tab eventKey="detection" title={<><Globe /> Language Detection</>}>
          <Card>
            <Card.Header>Language Detection</Card.Header>
            <Card.Body>
              <Form.Group className="mb-3">
                <Form.Label>Enter Text</Form.Label>
                <Form.Control
                  as="textarea"
                  rows={6}
                  value={detectionInput}
                  onChange={(e) => setDetectionInput(e.target.value)}
                  placeholder="Enter text to detect language..."
                />
              </Form.Group>
              
              <Button
                variant="primary"
                onClick={handleDetectLanguage}
                disabled={loading || !detectionInput.trim()}
              >
                {loading ? (
                  <Spinner animation="border" size="sm" className="me-2" />
                ) : (
                  <Globe className="me-2" />
                )}
                Detect Language
              </Button>
              
              {detectionResult && (
                <div className="mt-4">
                  <Card>
                    <Card.Header>Detection Result</Card.Header>
                    <Card.Body>
                      <Row>
                        <Col md={6}>
                          <div className="p-3 bg-light rounded mb-3">
                            <p className="mb-0">{detectionResult.text}</p>
                          </div>
                        </Col>
                        <Col md={6}>
                          <ListGroup>
                            <ListGroup.Item className="d-flex justify-content-between align-items-center">
                              <span>Detected Language</span>
                              <Badge bg="primary">
                                {detectionResult.language_name}
                              </Badge>
                            </ListGroup.Item>
                            <ListGroup.Item className="d-flex justify-content-between align-items-center">
                              <span>Language Code</span>
                              <Badge bg="secondary">
                                {detectionResult.detected_language}
                              </Badge>
                            </ListGroup.Item>
                            <ListGroup.Item className="d-flex justify-content-between align-items-center">
                              <span>Confidence</span>
                              <ProgressBar
                                now={detectionResult.confidence * 100}
                                label={`${(detectionResult.confidence * 100).toFixed(1)}%`}
                                style={{ width: '150px' }}
                              />
                            </ListGroup.Item>
                            <ListGroup.Item className="d-flex justify-content-between align-items-center">
                              <span>Script</span>
                              <Badge bg="info">
                                {detectionResult.script}
                              </Badge>
                            </ListGroup.Item>
                            <ListGroup.Item className="d-flex justify-content-between align-items-center">
                              <span>Indian Language</span>
                              <Badge bg={detectionResult.is_indian ? 'success' : 'warning'}>
                                {detectionResult.is_indian ? 'Yes' : 'No'}
                              </Badge>
                            </ListGroup.Item>
                          </ListGroup>
                        </Col>
                      </Row>
                    </Card.Body>
                  </Card>
                </div>
              )}
            </Card.Body>
          </Card>
        </Tab>
        
        <Tab eventKey="batch" title={<><FileText /> Batch Processing</>}>
          <Card>
            <Card.Header>Batch Translation</Card.Header>
            <Card.Body>
              <Form.Group className="mb-3">
                <Form.Label>Enter Texts (one per line)</Form.Label>
                <Form.Control
                  as="textarea"
                  rows={10}
                  value={batchInput}
                  onChange={(e) => setBatchInput(e.target.value)}
                  placeholder="Enter multiple texts, one per line..."
                />
                <Form.Text className="text-muted">
                  Each line will be processed as a separate text
                </Form.Text>
              </Form.Group>
              
              <Form.Group className="mb-3">
                <Form.Label>Target Language</Form.Label>
                <Form.Select
                  value={translationConfig.targetLanguage}
                  onChange={(e) => setTranslationConfig({
                    ...translationConfig,
                    targetLanguage: e.target.value
                  })}
                >
                  {getIndianLanguages().map(lang => (
                    <option key={lang.code} value={lang.code}>
                      {lang.name}
                    </option>
                  ))}
                </Form.Select>
              </Form.Group>
              
              <Button
                variant="primary"
                onClick={handleBatchTranslation}
                disabled={loading || !batchInput.trim()}
                className="mb-3"
              >
                {loading ? (
                  <Spinner animation="border" size="sm" className="me-2" />
                ) : (
                  <Translate className="me-2" />
                )}
                Translate Batch
              </Button>
              
              {batchResults.length > 0 && (
                <div className="mt-4">
                  <h5>Results ({batchResults.length} texts)</h5>
                  <ListGroup>
                    {batchResults.map((result, idx) => (
                      <ListGroup.Item key={idx}>
                        <div className="d-flex justify-content-between align-items-start">
                          <div style={{ flex: 1 }}>
                            <div className="mb-1">
                              <strong>Original:</strong> {result.original_text.substring(0, 100)}...
                            </div>
                            <div className="mb-1">
                              <strong>Translated:</strong> {result.translated_text.substring(0, 100)}...
                            </div>
                            {result.detected_language && (
                              <small className="text-muted">
                                Detected: {getLanguageName(result.detected_language)}
                                {result.confidence && ` (${(result.confidence * 100).toFixed(1)}%)`}
                              </small>
                            )}
                          </div>
                          <Badge bg="info" className="ms-2">
                            #{idx + 1}
                          </Badge>
                        </div>
                      </ListGroup.Item>
                    ))}
                  </ListGroup>
                  
                  <Button
                    variant="outline-primary"
                    className="mt-3"
                    onClick={() => {
                      const content = JSON.stringify(batchResults, null, 2);
                      const blob = new Blob([content], { type: 'application/json' });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement('a');
                      a.href = url;
                      a.download = `batch_translation_${Date.now()}.json`;
                      document.body.appendChild(a);
                      a.click();
                      document.body.removeChild(a);
                      URL.revokeObjectURL(url);
                    }}
                  >
                    <Download /> Download Results
                  </Button>
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
      
      {/* Supported Languages Info */}
      <Card className="mt-4">
        <Card.Header>Supported Languages</Card.Header>
        <Card.Body>
          <Row>
            {supportedLanguages.map(lang => (
              <Col md={3} key={lang.code} className="mb-3">
                <Card>
                  <Card.Body className="text-center">
                    <h5>{lang.name}</h5>
                    <Badge bg="secondary" className="me-2">
                      {lang.code}
                    </Badge>
                    <Badge bg="info">
                      {lang.script}
                    </Badge>
                    {lang.is_indian && (
                      <div className="mt-2">
                        <Badge bg="success">Indian Language</Badge>
                      </div>
                    )}
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

export default LanguageTools;