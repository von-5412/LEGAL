# TOS Analyzer

## Overview

TOS Analyzer is a Flask-based web application that analyzes Terms of Service documents for legal risks and dark patterns using local Natural Language Processing (NLP). The application allows users to upload PDF or text files and receive detailed risk assessments with scoring, highlighting potentially problematic clauses without sending data to external services.

## System Architecture

The application follows a traditional Flask web application architecture with the following layers:

- **Frontend**: Bootstrap-based responsive web interface with JavaScript for interactive features
- **Backend**: Flask web framework with SQLAlchemy ORM for data persistence
- **Database**: SQLite for development with PostgreSQL support configured for production
- **Processing**: Custom NLP analyzer for document text analysis and risk detection

## Key Components

### Web Application (`app.py`, `main.py`)
- Flask application factory pattern with SQLAlchemy integration
- ProxyFix middleware for deployment behind reverse proxies
- File upload handling with 16MB size limit
- Session management with configurable secret keys

### Database Layer (`models.py`)
- **AnalysisResult Model**: Stores analysis results with file metadata, risk scores, and JSON-serialized analysis data
- File deduplication using SHA-256 hashing
- Timestamp tracking for analysis history

### NLP Analysis Engine (`nlp_analyzer.py`)
- **TOSAnalyzer Class**: Core analysis engine with pattern-based risk detection
- Risk categories with weighted scoring:
  - Data sharing with third parties (25 points)
  - Arbitration clauses limiting legal rights (20 points) 
  - Unilateral change rights (15 points)
  - Account suspension terms (configurable weight)
- PDF text extraction using PyPDF2
- File hashing for duplicate detection

### Route Handlers (`routes.py`)
- File upload and validation (PDF, TXT formats)
- Analysis processing pipeline
- Results display and history views
- Error handling and user feedback

### Frontend Interface
- **Templates**: Jinja2 templates with Bootstrap 5 styling
- **Static Assets**: Custom CSS with CSS variables for theming, JavaScript for file upload interactions
- **Features**: Drag-and-drop file upload, risk visualization, analysis history

## Data Flow

1. **File Upload**: User uploads document via web interface
2. **Validation**: File type and size validation
3. **Deduplication**: SHA-256 hash check against existing analyses
4. **Text Extraction**: PDF parsing or direct text processing
5. **NLP Analysis**: Pattern matching against risk categories
6. **Scoring**: Weighted risk score calculation
7. **Storage**: Results saved to database with metadata
8. **Display**: Interactive results page with risk breakdown

## External Dependencies

### Core Framework
- **Flask 3.1.1**: Web framework
- **SQLAlchemy 2.0.41**: Database ORM
- **Flask-SQLAlchemy 3.1.1**: Flask-SQLAlchemy integration

### Document Processing
- **PyPDF2 3.0.1**: PDF text extraction
- **Werkzeug 3.1.3**: File upload utilities

### Database & Deployment
- **SQLite**: Local database for development and production
- **Gunicorn 23.0.0**: WSGI server for production

### Utilities
- **email-validator 2.2.0**: Email validation utilities

## Deployment Strategy

### Development
- SQLite database for local development
- Flask development server with debug mode
- File-based session storage

### Production (Replit)
- **Database**: SQLite for reliable local storage
- **Web Server**: Gunicorn with autoscale deployment target
- **Process Management**: Connection pooling with health checks
- **File Storage**: Local uploads directory with .gitkeep
- **Environment**: Python 3.11 with Nix package management

### Configuration
- SQLite database configuration for portable deployment
- Proxy-aware setup for deployment behind load balancers
- Configurable upload limits and file type restrictions

## Recent Changes

**June 24, 2025 - Project Migration Completed:**
- Successfully migrated TOS Analyzer from Replit Agent to standard Replit environment
- Removed problematic PyTorch/Transformers dependencies that caused installation conflicts
- Maintained ML fallback functionality with enhanced pattern-based analysis
- Application now runs cleanly with core Flask dependencies
- Gunicorn server successfully serving on port 5000

**June 23, 2025 - Enhanced Analysis Features:**
- Added executive summary with intelligent risk assessment
- Implemented positive indicator detection for good practices
- Created readability scoring with legal jargon analysis
- Built comparison dashboard with industry benchmarks
- Added data export functionality (JSON format)
- Enhanced dark pattern detection with 6 categories
- Improved transparency scoring with positive practice bonuses

**Advanced Analysis Features:**
- **Executive Summary**: AI-generated assessment with key concerns and recommendations
- **Positive Indicators**: Detection of user-friendly practices (data rights, transparency, security)
- **Readability Metrics**: Word count, sentence complexity, legal jargon analysis
- **Industry Benchmarks**: Compare documents against analyzed dataset averages
- **Enhanced Dark Patterns**: Auto-renewal, data harvesting, opt-out difficulty detection
- **Export Capabilities**: Structured JSON export with metadata and analysis results

## Changelog
- June 23, 2025. Initial setup and enhanced analysis features
- June 23, 2025. Converted from PostgreSQL to SQLite for simplified deployment
- June 23, 2025. Implemented ML-based clause classification with LegalBERT integration and enhanced pattern fallback

## Documentation

**Comprehensive Documentation Created:**
- **README.md**: Complete project overview with installation, architecture, and development guide
- **CLI_DOCS.md**: Detailed CLI commands, system architecture diagrams, and troubleshooting guide

The documentation includes:
- In-depth analysis engine explanations with code examples
- Complete API documentation with request/response formats
- Performance monitoring and optimization guidelines
- Detailed troubleshooting guide for common issues
- System architecture diagrams and data flow charts
- Database schema design and performance considerations
- ML pipeline architecture with embedding generation details

## User Preferences

Preferred communication style: Simple, everyday language.