import React, { useState, useEffect } from 'react';
import { Form, Badge, OverlayTrigger, Tooltip } from 'react-bootstrap';
import { Globe, InfoCircle } from 'react-bootstrap-icons';
import axios from 'axios';

const API_BASE = 'http://localhost:8000';

function LanguageSelector({
  value,
  onChange,
  label = "Language",
  showIndianOnly = false,
  showScript = true,
  disabled = false,
  size = "md"
}) {
  const [languages, setLanguages] = useState([]);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchLanguages();
  }, []);
  
  const fetchLanguages = async () => {
    try {
      const response = await axios.get(`${API_BASE}/api/translation/languages`);
      let langList = response.data.languages || [];
      
      if (showIndianOnly) {
        langList = langList.filter(lang => lang.is_indian);
      }
      
      setLanguages(langList);
    } catch (err) {
      console.error('Error fetching languages:', err);
    } finally {
      setLoading(false);
    }
  };
  
  const getLanguageInfo = (langCode) => {
    const lang = languages.find(l => l.code === langCode);
    if (!lang) return null;
    
    return (
      <div className="d-flex align-items-center">
        <Globe className="me-2" />
        <div>
          <strong>{lang.name}</strong>
          {showScript && (
            <div className="small text-muted">Script: {lang.script}</div>
          )}
          {lang.is_indian && (
            <Badge bg="success" size="sm" className="mt-1">Indian Language</Badge>
          )}
        </div>
      </div>
    );
  };
  
  if (loading) {
    return (
      <Form.Group>
        <Form.Label>{label}</Form.Label>
        <Form.Control as="select" disabled>
          <option>Loading languages...</option>
        </Form.Control>
      </Form.Group>
    );
  }
  
  return (
    <Form.Group>
      <Form.Label className="d-flex align-items-center">
        {label}
        <OverlayTrigger
          placement="top"
          overlay={
            <Tooltip>
              Select target language for translation/transliteration
            </Tooltip>
          }
        >
          <InfoCircle className="ms-2" size={14} />
        </OverlayTrigger>
      </Form.Label>
      <Form.Select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        disabled={disabled}
        size={size}
      >
        <option value="">Select a language</option>
        {languages.map(lang => (
          <option key={lang.code} value={lang.code}>
            {lang.name} {showScript && `(${lang.script})`}
          </option>
        ))}
      </Form.Select>
      
      {value && (
        <div className="mt-2 p-2 bg-light rounded">
          {getLanguageInfo(value)}
        </div>
      )}
    </Form.Group>
  );
}

export default LanguageSelector;