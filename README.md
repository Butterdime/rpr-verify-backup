# RPR CIS Dashboard v6.0

A comprehensive Customer Identity Verification (CIS) system with advanced document quality assessment, OCR extraction, mismatch detection, and dispute management.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Usage](#usage)
  - [Web Interface](#web-interface)
  - [Batch Processing](#batch-processing)
  - [Report Generation](#report-generation)
- [API Reference](#api-reference)
- [Configuration](#configuration)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## Overview

The RPR CIS Dashboard provides an end-to-end solution for customer identity verification, featuring:

- **Document Quality Assessment**: Automated analysis of document image quality using multi-metric approach
- **OCR Extraction**: Tesseract-based text extraction with confidence scoring
- **Mismatch Detection**: Intelligent comparison of document fields with severity classification
- **Risk Assessment**: Three-tier risk classification (Low/Moderate/High)
- **Dispute Management**: Complete workflow for handling verification disputes
- **Audit Trail**: 7-year immutable audit log with SHA-256 integrity verification
- **Compliance Reporting**: External certificates and internal audit reports

## Features

| Feature | Description |
|---------|-------------|
| Quality Assessment | DPI, contrast, rotation, blur, and brightness analysis |
| Document Enhancement | CLAHE contrast enhancement, denoising, perspective correction |
| OCR Extraction | Structured data extraction (Name, DOB, Address, ABN, ACN, Postcode) |
| Mismatch Detection | Fuzzy string matching with field-specific thresholds |
| Risk Tiering | Tier 1 (Low), Tier 2 (Moderate), Tier 3 (High) classification |
| Dispute Workflow | Create, triage, re-verify, and resolve disputes |
| Audit Trail | SHA-256 hashed immutable records with 7-year retention |
| Web Interface | Flask-based UI for document upload and verification |

## Prerequisites

Before installation, ensure you have:

- **Python 3.9+** (tested with Python 3.13)
- **Tesseract OCR Engine** (required for text extraction)
  - macOS: `brew install tesseract`
  - Ubuntu/Debian: `sudo apt-get install tesseract-ocr`
  - Windows: Download from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki)

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Butterdime/rpr-cis-dashboard.git
   cd rpr-cis-dashboard
   ```

2. **Create and activate a virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # Linux/macOS
   # or
   venv\Scripts\activate     # Windows
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Verify Tesseract installation**
   ```bash
   tesseract --version
   ```

5. **Configure Tesseract path** (if not in system PATH)
   
   Edit `src/config.py` and update the `tesseract_cmd` path:
   ```python
   self.ocr_config = {
       'tesseract_cmd': '/usr/local/bin/tesseract',  # Update this path
       'confidence_threshold': 60
   }
   ```

## Quick Start

1. **Start the web application**
   ```bash
   python ui/app.py
   ```

2. **Open your browser** and navigate to `http://localhost:5000`

3. **Upload documents** for verification via the web interface

## Project Structure

```
rpr-cis-dashboard/
├── src/                           # Source code
│   ├── main.py                    # Entry point
│   ├── config.py                  # Configuration settings
│   ├── database.py                # SQLite database handler
│   └── modules/
│       ├── document_processor.py  # Quality assessment, enhancement, OCR
│       ├── mismatch_detector.py   # Mismatch detection and risk assessment
│       ├── dispute_manager.py     # Dispute workflow management
│       ├── report_generator.py    # Report generation
│       └── audit_trail.py         # 7-year immutable audit trail
├── ui/                            # Web interface
│   ├── app.py                     # Flask application
│   ├── templates/                 # HTML templates
│   └── static/                    # CSS and JavaScript
├── templates/                     # Report templates
│   └── report_template.html       # HTML report template
├── tests/                         # Unit tests
│   ├── test_quality.py
│   ├── test_ocr.py
│   ├── test_mismatch.py
│   └── test_dispute.py
├── data/                          # Runtime data (auto-created)
│   ├── documents/                 # Uploaded documents
│   └── audit_trail/               # Audit log files
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Usage

### Web Interface

The web interface provides an intuitive workflow for document verification:

1. **Home Page** (`/`): Overview and navigation
2. **Upload** (`/upload`): Upload 2+ documents for verification
3. **Verification Result** (`/verify`): View quality scores, mismatches, and risk tier
4. **Dispute** (`/dispute`): Submit disputes with additional documentation
5. **Reports** (`/report/<id>`): Generate verification reports

### Batch Processing

Process multiple documents from the command line:

```bash
# Create input and output directories
mkdir -p input_folder output_folder

# Place documents in input_folder, then run:
python src/modules/document_processor.py \
  --batch input_folder/ \
  --output output_folder/
```

**Supported file formats**: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.tiff`

**Output**:
- Enhanced images: `output_folder/enhanced_*.jpg`
- JSON results: `output_folder/*_result.json`

### Report Generation

Generate HTML reports from processed documents:

```bash
python src/modules/report_generator.py \
  --input output_folder/ \
  --template templates/report_template.html \
  --output html_reports/
```

## API Reference

### DocumentQualityAssessor

Assesses document image quality using multiple metrics.

```python
from modules.document_processor import DocumentQualityAssessor

assessor = DocumentQualityAssessor()
result = assessor.assess_document_quality('path/to/image.jpg')

# Returns:
# {
#     'success': True,
#     'score': 85,           # 0-100 quality score
#     'level': 'GOOD',       # EXCELLENT/GOOD/ACCEPTABLE/POOR
#     'metrics': {
#         'dpi': {'dpi': 200, 'severity': 'GREEN', ...},
#         'contrast': {'contrast': 75.5, 'severity': 'GREEN', ...},
#         'rotation': {'rotation': 0.5, 'severity': 'GREEN', ...},
#         'blur': {'blur': 72.3, 'severity': 'GREEN', ...},
#         'brightness': {'brightness': 150, 'severity': 'GREEN', ...}
#     }
# }
```

### MismatchDetector

Detects mismatches between document fields.

```python
from modules.mismatch_detector import MismatchDetector, RiskAssessor

detector = MismatchDetector()
mismatches = detector.detect_mismatches(doc1_fields, doc2_fields)

risk_assessor = RiskAssessor()
risk = risk_assessor.assess_risk_tier(mismatches, ocr_quality=85)

# risk['tier']: 1 (Low), 2 (Moderate), or 3 (High)
# risk['decision']: 'APPROVE', 'ESCALATE', or 'REJECT'
```

### DisputeManager

Manages the dispute workflow.

```python
from modules.dispute_manager import DisputeManager

manager = DisputeManager(database)
dispute = manager.create_dispute(verification_id, reason, additional_docs)
triage = manager.perform_dispute_triage(dispute_id, original_assessment)
resolution = manager.resolve_dispute(dispute_id, 'APPROVED', 'Documents verified')
```

## Configuration

Configuration is managed in `src/config.py`:

| Setting | Description | Default |
|---------|-------------|---------|
| `database_path` | SQLite database location | `data/database.db` |
| `upload_folder` | Document upload directory | `data/documents` |
| `audit_folder` | Audit trail directory | `data/audit_trail` |
| `quality_thresholds.dpi` | DPI thresholds | min: 100, target: 200 |
| `quality_thresholds.contrast` | Contrast thresholds | min: 60%, target: 75% |
| `quality_thresholds.rotation` | Rotation thresholds | max: 5°, target: 1° |
| `ocr_config.tesseract_cmd` | Tesseract executable path | `/usr/local/bin/tesseract` |
| `ocr_config.confidence_threshold` | Minimum OCR confidence | 60 |

**Example configuration structure** (in `src/config.py`):

```python
class Config:
    def __init__(self):
        self.database_path = 'data/database.db'
        self.upload_folder = 'data/documents'
        self.audit_folder = 'data/audit_trail'
        
        self.quality_thresholds = {
            'dpi': {'min': 100, 'target': 200},
            'contrast': {'min': 60, 'target': 75},
            'rotation': {'max': 5, 'target': 1}
        }
        
        self.ocr_config = {
            'tesseract_cmd': '/usr/local/bin/tesseract',
            'confidence_threshold': 60
        }
```

## Testing

Run the test suite:

```bash
# Run all tests
python -m unittest discover tests/

# Run specific test file
python -m unittest tests/test_quality.py

# Run with verbose output
python -m unittest discover tests/ -v
```

## Troubleshooting

### Tesseract not found

**Error**: `pytesseract.pytesseract.TesseractNotFoundError`

**Solution**: Install Tesseract OCR and update the path in `src/config.py`:
```python
self.ocr_config = {
    'tesseract_cmd': '/path/to/tesseract',
    ...
}
```

### Low OCR confidence

**Issue**: OCR extraction returns low confidence scores

**Solutions**:
1. Ensure documents meet minimum quality requirements (DPI ≥ 100)
2. Use the DocumentEnhancer to preprocess images before OCR
3. Adjust the confidence threshold in config.py

### Import errors when running tests

**Error**: `ModuleNotFoundError: No module named 'modules'`

**Solution**: Run tests from the project root with PYTHONPATH set:
```bash
# Option 1: Set PYTHONPATH and run from project root
PYTHONPATH=src python -m unittest discover tests/

# Option 2: Run specific test file
PYTHONPATH=src python -m unittest tests.test_quality

# Option 3: Navigate to tests directory first
cd tests
python -m unittest test_quality
```

### Database errors

**Error**: Database-related errors on first run

**Solution**: The database and required directories are created automatically. Ensure write permissions in the project directory.

---

## License

This project is proprietary software. All rights reserved.

## Support

For issues and questions, please open a GitHub issue or contact the development team.