# RPR CIS Dashboard v6.0
## Complete Implementation with Gemini Integration

### Overview
This project implements a comprehensive Customer Identity Verification (CIS) system with advanced document quality assessment, OCR extraction, mismatch detection, and dispute management.

### Features
- Document quality assessment using multi-metric approach (DPI, contrast, rotation, blur)
- OCR extraction with confidence scoring and calibration
- Mismatch detection and risk tiering (Tier 1/2/3)
- Dispute management workflow with re-verification
- Reporting and 7-year immutable audit trail
- Web-based UI for verification and dispute workflows

### Project Structure
```
rpr-cis-dashboard/
├── src/
│   ├── main.py                    [Entry point]
│   ├── config.py                  [Configuration]
│   ├── database.py                [SQLite setup]
│   └── modules/
│       ├── __init__.py
│       ├── document_processor.py  [Quality + Enhancement + OCR]
│       ├── gdrive_downloader.py   [Google Drive folder download]
│       ├── mismatch_detector.py   [Mismatch detection + Risk]
│       ├── dispute_manager.py     [Dispute workflows]
│       ├── report_generator.py    [Report generation]
│       └── audit_trail.py         [7-year audit]
├── ui/
│   ├── app.py                     [Flask UI]
│   ├── templates/                 [HTML templates]
│   └── static/
│       ├── css/                   [Styling]
│       └── js/                    [UI interactions]
├── tests/
│   ├── test_quality.py
│   ├── test_ocr.py
│   ├── test_mismatch.py
│   ├── test_dispute.py
│   └── test_gdrive.py
├── data/
│   ├── documents/                 [Uploaded docs]
│   ├── database.db                [SQLite]
│   └── audit_trail/               [7-year logs]
├── requirements.txt               [Dependencies]
└── README.md                      [Documentation]
```

### Installation
1. Navigate to the project directory
2. Create virtual environment: `python3 -m venv venv`
3. Activate: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Run the application: `python ui/app.py`

### Dependencies
- opencv-python
- pytesseract
- pillow
- numpy
- flask
- werkzeug
- google-api-python-client
- google-auth-httplib2
- google-auth-oauthlib

### Implementation Status
✅ **COMPLETE** - All modules implemented and integrated

**Completed Tasks:**
- ✅ Project Setup (30 minutes)
- ✅ Document Quality Assessment (4 hours)
- ✅ Document Enhancement & OCR (4 hours)
- ✅ Mismatch Detection & Risk Assessment (3 hours)
- ✅ Dispute Management Module (4-5 hours)
- ✅ Reporting & Audit Trail (3-4 hours)
- ✅ User Interface (3-4 hours)
- ✅ Testing & Documentation (2-3 hours)

**Total Implementation Time:** 22-26 hours (as planned)

### Key Components
1. **DocumentQualityAssessor**: Multi-metric quality assessment (DPI, contrast, rotation, blur, brightness)
2. **DocumentEnhancer**: Preprocessing pipeline with CLAHE, denoising, perspective correction
3. **OCRExtractor**: Tesseract integration with confidence scoring and structured data extraction
4. **MismatchDetector**: Fuzzy string matching with field-specific severity classification
5. **RiskAssessor**: Tier-based risk assessment (1=Low, 2=Moderate, 3=High)
6. **DisputeManager**: Complete dispute workflow with re-verification and resolution
7. **ReportGenerator**: External/internal reports and compliance summaries
8. **AuditTrail**: 7-year immutable audit trail with integrity verification
9. **Flask UI**: Web interface for document upload, verification, and dispute management
10. **GoogleDriveDownloader**: Download folders and files from Google Drive for document processing

### Google Drive Integration

The system includes a Google Drive downloader module to download documents from Google Drive folders for processing.

#### Setup Google Drive API

1. **Create Google Cloud Project:**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select an existing one

2. **Enable Google Drive API:**
   - In the Cloud Console, go to "APIs & Services" > "Library"
   - Search for "Google Drive API" and enable it

3. **Create OAuth 2.0 Credentials:**
   - Go to "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "OAuth client ID"
   - Select "Desktop app" as the application type
   - Download the credentials JSON file
   - Save it as `credentials.json` in the project root

4. **First Run Authentication:**
   - On first run, a browser window will open for Google authentication
   - Sign in and grant access to Google Drive
   - A `token.json` file will be created for subsequent runs

#### Download Files from Google Drive

**Using Command Line:**
```bash
# Download all files from a folder
python src/modules/gdrive_downloader.py --folder-id <FOLDER_ID> --output input_folder/

# Download only specific file types
python src/modules/gdrive_downloader.py --folder-id <FOLDER_ID> --output input_folder/ --extensions jpg png pdf

# Download recursively (including subfolders)
python src/modules/gdrive_downloader.py --folder-id <FOLDER_ID> --output input_folder/ --recursive

# Use custom credentials file
python src/modules/gdrive_downloader.py --folder-id <FOLDER_ID> --output input_folder/ --credentials my_creds.json
```

**Getting the Folder ID:**
- Navigate to your Google Drive folder in a browser
- The URL will look like: `https://drive.google.com/drive/folders/1ABC123xyz`
- The folder ID is the last part: `1ABC123xyz`

**Using in Python:**
```python
from modules.gdrive_downloader import GoogleDriveDownloader

# Initialize downloader
downloader = GoogleDriveDownloader()

# Authenticate (opens browser on first run)
downloader.authenticate()

# Download folder
results = downloader.download_folder(
    folder_id='your_folder_id',
    output_path='input_folder/',
    file_extensions=['.jpg', '.png', '.pdf']  # Optional filter
)

print(f"Downloaded: {results['downloaded']} files")
```

### Validation
- All core modules implemented with comprehensive error handling
- Unit tests created for all major components
- Web UI with responsive design and user-friendly workflows
- SQLite database with proper schema and relationships
- Audit trail with SHA-256 hashing for immutability

### Next Steps
1. Install Tesseract OCR engine: `brew install tesseract`
2. Configure Tesseract path in config.py if needed
3. Run tests: `python -m unittest discover tests/`
4. Start application: `python ui/app.py`
5. Access UI at http://localhost:5000

**Status:** ✅ Implementation Complete - Ready for Testing and Deployment