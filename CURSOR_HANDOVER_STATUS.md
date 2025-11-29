# CIS Dashboard - Processing Workflow Guide

**Last Updated:** 2025-11-29  
**Status:** ✅ Ready for Document Processing

---

## Overview

This document describes the workflow for processing client documents through the RPR CIS Dashboard system. The system provides batch document processing, quality assessment, OCR extraction, and report generation capabilities.

---

## Quick Start

### Prerequisites

1. **Python 3.9+** installed
2. **Tesseract OCR** installed (see README.md for installation instructions)
3. **Virtual environment** activated with dependencies installed

### Setup Commands

```bash
# Navigate to project directory
cd rpr-cis-dashboard

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
```

---

## Processing Workflow

### Step 1: Prepare Input Directory

Create an input directory and add your documents:

```bash
mkdir -p input_folder
# Copy documents to input_folder/
cp /path/to/your/documents/* input_folder/
```

**Supported Formats:** `.jpg`, `.jpeg`, `.png`, `.bmp`, `.tiff`

### Step 2: Run Batch Document Processing

```bash
python src/modules/document_processor.py \
  --batch input_folder/ \
  --output output_folder/
```

**Output:**
- Enhanced images: `output_folder/enhanced_*.jpg`
- JSON results: `output_folder/*_result.json`

### Step 3: Generate HTML Reports

```bash
python src/modules/report_generator.py \
  --input output_folder/ \
  --template templates/report_template.html \
  --output html_reports/
```

**Output:**
- HTML reports: `html_reports/*_report.html`

### Step 4: Review Results

1. Open the generated HTML reports in a browser
2. Review quality scores and metrics
3. Check OCR extraction results
4. Verify document enhancement quality

---

## System Capabilities

### Document Quality Assessment

| Metric | Target | Acceptable |
|--------|--------|------------|
| DPI | 200+ | 100+ |
| Contrast | 75%+ | 60%+ |
| Rotation | <1° | <5° |
| Brightness | 50-200/255 | 30-225/255 |

**Severity Levels:**
- 🟢 **GREEN**: Meets target threshold
- 🟡 **YELLOW**: Acceptable but below target
- 🔴 **RED**: Below acceptable threshold

### Document Enhancement Pipeline

1. **Rotation Correction** - Automatically detects and corrects skew
2. **Perspective Correction** - Fixes trapezoid distortion
3. **CLAHE Enhancement** - Adaptive contrast improvement
4. **Noise Reduction** - Bilateral filtering for cleaner images
5. **Brightness Normalization** - Equalizes exposure

### OCR Extraction

Automatically extracts structured data:
- **Names**
- **Dates of Birth**
- **Addresses**
- **Postcodes** (4-digit Australian format)
- **ABN** (11-digit Australian Business Number)
- **ACN** (9-digit Australian Company Number)

---

## Output Files

| Directory | Contents |
|-----------|----------|
| `output_folder/` | Enhanced images and JSON results |
| `html_reports/` | Generated HTML reports |
| `data/documents/` | Uploaded documents (web UI) |
| `data/audit_trail/` | Immutable audit logs |

---

## Web Interface

For interactive document processing:

```bash
python ui/app.py
```

Then open `http://localhost:5000` in your browser.

**Features:**
- Document upload with drag-and-drop
- Real-time quality assessment
- Side-by-side document comparison
- Dispute management workflow

---

## Troubleshooting

### Common Issues

**"Tesseract not found"**
- Install Tesseract OCR for your platform
- Update path in `src/config.py`

**"No module named 'modules'"**
- Ensure you're running from the project root
- Or set `PYTHONPATH=src` before running

**Low quality scores**
- Use higher resolution scans (200+ DPI)
- Ensure good lighting and contrast
- Avoid blurry or rotated images

---

## Quality Control Checklist

Before delivering results:

- [ ] All documents processed without errors
- [ ] Quality scores meet minimum thresholds
- [ ] OCR extraction verified for accuracy
- [ ] Reports generated successfully
- [ ] Enhanced images visually reviewed

---

**System Status:** ✅ **READY FOR PROCESSING**

Refer to the main [README.md](README.md) for detailed installation and API documentation.