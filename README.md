# TOS Analyzer - Legal Document Risk Assessment Platform

A sophisticated Flask-based web application that analyzes Terms of Service documents for legal risks and dark patterns using advanced Natural Language Processing. The system provides comprehensive risk assessments, transparency scoring, and actionable recommendations without sending data to external services.

## 🚀 Features

### Core Analysis Capabilities
- **Dual Analysis Engine**: Machine Learning (LegalBERT) + Enhanced Pattern Matching
- **Risk Scoring**: 0-100 scale with weighted category scoring
- **Dark Pattern Detection**: 6 categories of manipulative tactics
- **Positive Indicator Recognition**: User-friendly practice detection
- **Transparency Scoring**: Document clarity and readability assessment
- **Executive Summary**: AI-generated actionable recommendations

### Advanced Features
- **Document Comparison**: Side-by-side analysis of multiple documents
- **Analysis History**: Track and revisit previous assessments
- **Data Export**: JSON format with complete analysis metadata
- **File Deduplication**: SHA-256 hashing prevents duplicate processing
- **Multi-format Support**: PDF and text file processing

## 📋 Table of Contents
- [Installation](#installation)
- [Architecture Overview](#architecture-overview)
- [Analysis Engine Details](#analysis-engine-details)
- [Risk Scoring Methodology](#risk-scoring-methodology)
- [API Documentation](#api-documentation)
- [Development Guide](#development-guide)
- [Deployment](#deployment)
- [Configuration](#configuration)

## 🛠 Installation

### Prerequisites
- Python 3.11+
- 16MB+ RAM for document processing
- SQLite support (included in Python)

### Quick Start
```bash
# Clone the repository
git clone <repository-url>
cd tos-analyzer

# Install dependencies
pip install -r requirements.txt

# Initialize database
python -c "from app import app, db; app.app_context().push(); db.create_all()"

# Run development server
python main.py
```

### Production Deployment
```bash
# Install production server
pip install gunicorn

# Run with Gunicorn
gunicorn --bind 0.0.0.0:5000 --workers 4 main:app
```

## 🏗 Architecture Overview

### System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Analysis      │
│                 │    │                 │    │   Engine        │
│ • Bootstrap 5   │◄──►│ • Flask 3.1.1   │◄──►│ • NLP Analyzer  │
│ • JavaScript    │    │ • SQLAlchemy    │    │ • ML Classifier │
│ • Drag & Drop   │    │ • Session Mgmt  │    │ • Pattern Match │
│ • Charts.js     │    │ • File Upload   │    │ • Risk Scoring  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │   Data Layer    │
                       │                 │
                       │ • SQLite DB     │
                       │ • File Storage  │
                       │ • Cache Layer   │
                       └─────────────────┘
```

### Component Breakdown

#### Frontend Layer (`/templates`, `/static`)
- **Responsive Design**: Bootstrap 5 with custom CSS variables
- **Interactive Upload**: Drag-and-drop file interface with progress indicators
- **Data Visualization**: Chart.js for risk breakdown and transparency scoring
- **Real-time Feedback**: JavaScript-powered file validation and processing updates

#### Backend Layer (`app.py`, `routes.py`, `models.py`)
- **Flask Application**: WSGI-compatible web framework with proxy support
- **SQLAlchemy ORM**: Database abstraction with connection pooling
- **Session Management**: Secure session handling with configurable keys
- **File Processing**: Multi-format document handling with size limits

#### Analysis Engine (`nlp_analyzer.py`, `ml_analyzer.py`, `enhanced_patterns.py`)
- **Dual Classification**: ML-based semantic analysis + pattern-based detection
- **Risk Assessment**: Weighted scoring across 6 risk categories
- **Language Processing**: Legal document-specific text analysis
- **Confidence Scoring**: ML-powered certainty metrics for each detection

#### Data Layer (`models.py`, SQLite)
- **Analysis Results**: JSON-serialized analysis data with metadata
- **File Deduplication**: SHA-256 content hashing
- **History Tracking**: Timestamped analysis records
- **Export Capabilities**: Structured data export functionality

## 🧠 Analysis Engine Details

### Machine Learning Classification

#### LegalBERT Integration
```python
# Model: nlpaueb/legal-bert-base-uncased
# Pre-trained on legal documents for domain-specific understanding

class LegalMLAnalyzer:
    def __init__(self):
        self.model = AutoModel.from_pretrained("nlpaueb/legal-bert-base-uncased")
        self.tokenizer = AutoTokenizer.from_pretrained("nlpaueb/legal-bert-base-uncased")
        
    def analyze_text_ml(self, text):
        # 1. Tokenize legal text with 512 token limit
        # 2. Generate sentence embeddings using CLS token
        # 3. Compare against pre-computed clause category embeddings
        # 4. Calculate cosine similarity for classification
        # 5. Apply 0.7 threshold for positive classification
        # 6. Return confidence scores (0.7-0.95 range)
```

#### Enhanced Pattern Fallback
When ML libraries are unavailable, the system uses sophisticated pattern matching:

```python
class EnhancedPatternAnalyzer:
    def __init__(self):
        self.advanced_patterns = {
            'data_sharing_specific': {
                'patterns': [
                    r'(?i)(?:share|sell|transfer).*?(?:personal|user).*?(?:information|data).*?(?:third parties|partners)',
                    # 20+ advanced regex patterns per category
                ],
                'weight': 25,
                'confidence_base': 0.9
            }
        }
        
    def _calculate_pattern_confidence(self, sentence, matches, pattern_data):
        # Confidence calculation based on:
        # - Pattern specificity (longer matches = higher confidence)
        # - Legal language indicators (formal terms boost confidence)
        # - Multiple pattern matches (overlapping evidence)
        # - Context analysis (surrounding legal terminology)
```

### Risk Categories and Weights

#### Critical Risk Categories (High Impact)
1. **Data Sharing with Third Parties** (Weight: 25)
   - Personal information sold to advertisers
   - Data shared with business partners
   - Corporate sale/merger data transfers

2. **Arbitration Waiver** (Weight: 20)
   - Mandatory binding arbitration clauses
   - Class action waivers
   - Jury trial right forfeiture

#### Moderate Risk Categories
3. **Unilateral Changes** (Weight: 15)
   - Terms modification without notice
   - Immediate effectiveness upon posting
   - Continued use implies acceptance

4. **Account Termination** (Weight: 15)
   - Termination without cause or notice
   - Immediate access revocation
   - Sole discretion suspension rights

5. **Liability Limitation** (Weight: 12)
   - Broad damage exclusions
   - Maximum liability caps
   - "As-is" service disclaimers

6. **Auto-Renewal/Billing** (Weight: 10)
   - Automatic subscription renewals
   - Hidden recurring charges
   - Complex cancellation requirements

### Dark Pattern Detection

#### Manipulative Tactics Identified
```python
dark_patterns = {
    'auto_renewal': {
        'description': 'Hidden automatic billing/renewal',
        'patterns': [
            r'(?i)automatic.*?renewal.*?unless.*?cancel',
            r'(?i)trial.*?ends.*?automatic.*?billing'
        ]
    },
    'hidden_costs': {
        'description': 'Undisclosed fees and charges',
        'patterns': [
            r'(?i)additional.*?fees.*?may.*?apply',
            r'(?i)excluding.*?processing.*?fees'
        ]
    },
    'opt_out_difficulty': {
        'description': 'Complex cancellation processes',
        'patterns': [
            r'(?i)cancellation.*?requires.*?30.*?days',
            r'(?i)written.*?notice.*?required'
        ]
    }
}
```

### Positive Indicator Recognition

#### User-Friendly Practices Detected
```python
positive_indicators = {
    'user_rights': {
        'description': 'Clear user data rights',
        'patterns': [
            r'(?i)right.*?to.*?access.*?your.*?data',
            r'(?i)data.*?portability.*?available'
        ]
    },
    'transparency': {
        'description': 'Clear communication practices',
        'patterns': [
            r'(?i)advance.*?notice.*?of.*?changes',
            r'(?i)plain.*?language.*?explanation'
        ]
    },
    'data_protection': {
        'description': 'Strong security measures',
        'patterns': [
            r'(?i)encrypt.*?your.*?data',
            r'(?i)gdpr.*?compliant.*?processing'
        ]
    }
}
```

## 📊 Risk Scoring Methodology

### Overall Risk Score Calculation

```python
def calculate_risk_score(risk_breakdown):
    """
    Risk Score = Σ(min(category_count × category_weight, max_category_weight))
    Capped at 100 maximum
    """
    total_score = 0
    for category, data in risk_breakdown.items():
        # Prevent single category from dominating score
        category_score = min(data['count'] * data['weight'], data['weight'])
        total_score += category_score
    
    return min(total_score, 100)  # Maximum score is 100

# Example calculation:
# Data sharing: 2 instances × 25 weight = 50 (capped at 25) = 25 points
# Arbitration: 1 instance × 20 weight = 20 points  
# Unilateral changes: 3 instances × 15 weight = 45 (capped at 15) = 15 points
# Total Risk Score: 25 + 20 + 15 = 60
```

### Transparency Score Algorithm

```python
def calculate_transparency_score(risk_score, dark_patterns, positive_indicators):
    """
    Transparency = 100 - (dark_patterns × 8) - (risk_score × 0.25) + positive_boost
    """
    base_transparency = 100 - (len(dark_patterns) * 8) - (risk_score * 0.25)
    positive_boost = min(20, len(positive_indicators) * 5)  # Max 20 point boost
    
    return max(0, min(100, base_transparency + positive_boost))
```

### Readability Assessment

```python
def calculate_readability_score(text):
    """
    Readability = 100 - (avg_sentence_length × 2) - complex_word_percentage
    """
    sentences = split_sentences(text)
    words = extract_words(text)
    
    avg_sentence_length = len(words) / len(sentences)
    
    # Complex words: >10 characters OR legal jargon
    legal_jargon = ['notwithstanding', 'heretofore', 'pursuant', 'wheresoever']
    complex_words = [w for w in words if len(w) > 10 or w.lower() in legal_jargon]
    complex_ratio = (len(complex_words) / len(words)) * 100
    
    readability = max(0, 100 - (avg_sentence_length * 2) - complex_ratio)
    return readability
```

## 📡 API Documentation

### REST Endpoints

#### File Upload and Analysis
```http
POST /upload
Content-Type: multipart/form-data

# Form data:
file: <PDF or TXT file>
max_size: 16MB

# Response:
{
    "status": "success",
    "analysis_id": 123,
    "redirect": "/results/123"
}
```

#### Analysis Results
```http
GET /api/analysis/<analysis_id>

# Response:
{
    "risk_score": 75,
    "transparency_score": 45,
    "risk_breakdown": {
        "data_sharing": {
            "count": 3,
            "weight": 25,
            "description": "Personal data shared with third parties",
            "matches": [...]
        }
    },
    "dark_patterns": {...},
    "positive_indicators": {...},
    "executive_summary": {...},
    "ml_analysis_info": {
        "ml_enabled": true,
        "classification_method": "legalbert",
        "confidence_scores": {...}
    }
}
```

#### Export Analysis
```http
GET /export/<analysis_id>
Accept: application/json

# Response: Complete analysis data in JSON format
```

#### Analysis History
```http
GET /history

# Response: Paginated list of all analyses with metadata
```

#### Document Comparison
```http
GET /compare?ids=123,124,125

# Response: Side-by-side comparison dashboard
```

## 🔧 Development Guide

### Project Structure
```
tos-analyzer/
├── app.py                 # Flask application factory
├── main.py               # Application entry point
├── routes.py             # URL routing and request handlers
├── models.py             # SQLAlchemy database models
├── nlp_analyzer.py       # Main analysis engine
├── ml_analyzer.py        # Machine learning classifier
├── enhanced_patterns.py  # Advanced pattern matching
├── templates/            # Jinja2 HTML templates
│   ├── base.html
│   ├── index.html
│   ├── results.html
│   ├── compare.html
│   └── history.html
├── static/              # CSS, JavaScript, and assets
│   ├── css/style.css
│   └── js/analyzer.js
├── uploads/             # Temporary file storage
└── instance/           # SQLite database location
```

### Database Schema

#### AnalysisResult Model
```python
class AnalysisResult(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    file_hash = db.Column(db.String(64), nullable=False, index=True)
    risk_score = db.Column(db.Integer, nullable=False)
    analysis_data = db.Column(db.Text, nullable=False)  # JSON serialized
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Indexes for performance
    __table_args__ = (
        db.Index('idx_file_hash', 'file_hash'),
        db.Index('idx_created_at', 'created_at'),
        db.Index('idx_risk_score', 'risk_score'),
    )
```

### Adding New Risk Categories

1. **Update Pattern Definitions**
```python
# In nlp_analyzer.py
self.risk_patterns['new_category'] = {
    'patterns': [
        r'(?i)pattern1',
        r'(?i)pattern2'
    ],
    'weight': 15,
    'description': 'Description of this risk'
}
```

2. **Add ML Templates** (if using ML)
```python
# In ml_analyzer.py
self.clause_categories['new_category'] = {
    'templates': [
        "Template sentence showing this risk",
        "Another example of this clause type"
    ],
    'weight': 15,
    'severity': 'moderate'
}
```

3. **Update Frontend Display**
```html
<!-- In templates/results.html -->
<!-- Risk category will automatically appear in results -->
```

### Testing Framework

#### Unit Tests
```python
# tests/test_analyzer.py
import unittest
from nlp_analyzer import TOSAnalyzer

class TestAnalyzer(unittest.TestCase):
    def setUp(self):
        self.analyzer = TOSAnalyzer()
    
    def test_data_sharing_detection(self):
        text = "We may share your personal information with third parties"
        result = self.analyzer.analyze_text(text)
        self.assertIn('data_sharing', result['risk_breakdown'])
        self.assertGreater(result['risk_score'], 0)
```

#### Integration Tests
```python
# tests/test_routes.py
import unittest
from app import app, db

class TestRoutes(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        self.client = app.test_client()
    
    def test_file_upload(self):
        with open('test_tos.txt', 'rb') as f:
            response = self.client.post('/upload', 
                data={'file': f}, 
                follow_redirects=True)
        self.assertEqual(response.status_code, 200)
```

## 🚀 Deployment

### Environment Configuration

#### Required Environment Variables
```bash
# Production settings
export SESSION_SECRET="your-secret-key-here"
export DATABASE_URL="sqlite:///instance/tos_analyzer.db"

# Optional: ML model configuration
export ML_MODEL_PATH="/path/to/custom/model"
export ML_CONFIDENCE_THRESHOLD="0.7"
```

#### Production Deployment (Replit)
```bash
# .replit configuration
[deployment]
run = "gunicorn --bind 0.0.0.0:5000 --workers 4 main:app"
deploymentTarget = "autoscale"

[nix]
channel = "stable-23.05"
```

#### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "main:app"]
```

### Performance Optimization

#### Database Optimization
```python
# Connection pooling configuration
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
    "pool_size": 10,
    "max_overflow": 20
}
```

#### File Processing Optimization
```python
# Chunk large documents for memory efficiency
def chunk_large_text(text, chunk_size=5000):
    """Process large documents in chunks to prevent memory issues"""
    for i in range(0, len(text), chunk_size):
        yield text[i:i + chunk_size]
```

#### Caching Strategy
```python
# Redis caching for analysis results (optional)
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'redis'})

@cache.memoize(timeout=3600)
def analyze_document_cached(file_hash):
    return analysis_result
```

## ⚙ Configuration

### Application Settings

#### config.py
```python
import os

class Config:
    SECRET_KEY = os.environ.get('SESSION_SECRET') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///tos_analyzer.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB file limit
    
    # ML Configuration
    ML_CONFIDENCE_THRESHOLD = float(os.environ.get('ML_CONFIDENCE_THRESHOLD', '0.7'))
    ML_MODEL_CACHE_SIZE = int(os.environ.get('ML_MODEL_CACHE_SIZE', '100'))
    
    # Analysis Configuration
    RISK_SCORE_WEIGHTS = {
        'data_sharing': 25,
        'arbitration_waiver': 20,
        'unilateral_changes': 15,
        'account_termination': 15,
        'liability_limitation': 12,
        'auto_renewal': 10
    }
```

### Customization Options

#### Risk Category Weights
Modify risk importance by adjusting category weights:
```python
# Higher weight = more impact on overall risk score
CUSTOM_WEIGHTS = {
    'data_sharing': 30,      # Increased from 25
    'arbitration_waiver': 25, # Increased from 20
    'liability_limitation': 5  # Decreased from 12
}
```

#### ML Model Configuration
```python
# Use custom legal model
ML_MODEL_NAME = "custom/legal-bert-model"
ML_DEVICE = "cuda"  # or "cpu"
ML_MAX_LENGTH = 512
```

#### UI Customization
```css
/* static/css/style.css */
:root {
    --primary-color: #DC2626;    /* Risk red */
    --secondary-color: #059669;  /* Safe green */
    --accent-color: #D97706;     /* Warning orange */
    --text-color: #1F2937;
    --background-color: #F9FAFB;
}
```

## 🤝 Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch: `git checkout -b feature/new-risk-category`
3. Make changes and add tests
4. Run test suite: `python -m pytest tests/`
5. Submit pull request with detailed description

### Code Style Guidelines
- **Python**: Follow PEP 8 with 100-character line limit
- **JavaScript**: Use ES6+ features with semicolons
- **HTML/CSS**: Consistent indentation, semantic markup
- **Documentation**: Docstrings for all public functions

### Issue Reporting
When reporting issues, include:
- Python version and OS
- Sample document that causes the issue
- Expected vs actual behavior
- Full error traceback

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **LegalBERT**: nlpaueb/legal-bert-base-uncased model
- **Flask**: Web framework and ecosystem
- **Bootstrap**: Frontend component library
- **Chart.js**: Data visualization library
- **PyPDF2**: PDF processing library

---

For detailed CLI documentation and architecture diagrams, see [CLI_DOCS.md](CLI_DOCS.md)