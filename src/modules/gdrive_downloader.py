"""
Google Drive Folder Downloader Module
Downloads folders and files from Google Drive for CIS document processing.

Prerequisites:
1. Create a Google Cloud Console project: https://console.cloud.google.com/
2. Enable Google Drive API
3. Create OAuth 2.0 credentials (Desktop app)
4. Download credentials.json and place it in the project root
5. First run will open browser for authorization

Usage:
    python src/modules/gdrive_downloader.py --folder-id <FOLDER_ID> --output <OUTPUT_PATH>
    
To get the folder ID:
    - Navigate to the Google Drive folder in browser
    - The ID is the last part of the URL: https://drive.google.com/drive/folders/<FOLDER_ID>
"""

import os
import io
import logging
from typing import List, Dict, Optional

# Google API imports - installed via pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib
try:
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseDownload
    GOOGLE_API_AVAILABLE = True
except ImportError:
    GOOGLE_API_AVAILABLE = False


# If modifying these SCOPES, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/drive.readonly']


class GoogleDriveDownloader:
    """
    Downloads folders and files from Google Drive.
    
    Attributes:
        credentials_path: Path to the OAuth2 credentials JSON file.
        token_path: Path to store the user's access token.
        service: Google Drive API service instance.
    """
    
    def __init__(self, credentials_path: str = 'credentials.json', token_path: str = 'token.json'):
        """
        Initialize the Google Drive downloader.
        
        Args:
            credentials_path: Path to credentials.json from Google Cloud Console.
            token_path: Path where the token will be saved after authentication.
        """
        self.logger = logging.getLogger(__name__)
        self.credentials_path = credentials_path
        self.token_path = token_path
        self.service = None
        
        if not GOOGLE_API_AVAILABLE:
            self.logger.error(
                "Google API libraries not installed. Run: "
                "pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib"
            )
    
    def authenticate(self) -> bool:
        """
        Authenticate with Google Drive API using OAuth2.
        
        Returns:
            True if authentication successful, False otherwise.
        """
        if not GOOGLE_API_AVAILABLE:
            self.logger.error("Google API libraries not available.")
            return False
        
        creds = None
        
        # Check for existing token
        if os.path.exists(self.token_path):
            creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)
        
        # If no valid credentials, authenticate
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    self.logger.warning(f"Token refresh failed: {e}. Re-authenticating...")
                    creds = None
            
            if not creds:
                if not os.path.exists(self.credentials_path):
                    self.logger.error(
                        f"Credentials file not found: {self.credentials_path}\n"
                        "Please download it from Google Cloud Console:\n"
                        "1. Go to https://console.cloud.google.com/\n"
                        "2. Create or select a project\n"
                        "3. Enable Google Drive API\n"
                        "4. Create OAuth 2.0 credentials (Desktop app)\n"
                        "5. Download and save as credentials.json"
                    )
                    return False
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)
            
            # Save the credentials for next run
            with open(self.token_path, 'w') as token:
                token.write(creds.to_json())
        
        try:
            self.service = build('drive', 'v3', credentials=creds)
            self.logger.info("Successfully authenticated with Google Drive API")
            return True
        except Exception as e:
            self.logger.error(f"Failed to build Drive service: {e}")
            return False
    
    def list_files_in_folder(self, folder_id: str) -> List[Dict]:
        """
        List all files in a Google Drive folder.
        
        Args:
            folder_id: The ID of the Google Drive folder.
            
        Returns:
            List of file metadata dictionaries.
        """
        if not self.service:
            self.logger.error("Not authenticated. Call authenticate() first.")
            return []
        
        files = []
        page_token = None
        
        try:
            while True:
                query = f"'{folder_id}' in parents and trashed = false"
                response = self.service.files().list(
                    q=query,
                    spaces='drive',
                    fields='nextPageToken, files(id, name, mimeType, size)',
                    pageToken=page_token
                ).execute()
                
                files.extend(response.get('files', []))
                page_token = response.get('nextPageToken')
                
                if not page_token:
                    break
                    
            self.logger.info(f"Found {len(files)} files in folder")
            return files
            
        except Exception as e:
            self.logger.error(f"Error listing files: {e}")
            return []
    
    def download_file(self, file_id: str, file_name: str, output_path: str) -> bool:
        """
        Download a single file from Google Drive.
        
        Args:
            file_id: The ID of the file to download.
            file_name: Name to save the file as.
            output_path: Directory to save the file to.
            
        Returns:
            True if download successful, False otherwise.
        """
        if not self.service:
            self.logger.error("Not authenticated. Call authenticate() first.")
            return False
        
        try:
            request = self.service.files().get_media(fileId=file_id)
            
            file_path = os.path.join(output_path, file_name)
            fh = io.FileIO(file_path, 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    self.logger.info(f"Download progress: {int(status.progress() * 100)}%")
            
            fh.close()
            self.logger.info(f"Downloaded: {file_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error downloading {file_name}: {e}")
            return False
    
    def download_folder(
        self, 
        folder_id: str, 
        output_path: str, 
        file_extensions: Optional[List[str]] = None
    ) -> Dict:
        """
        Download all files from a Google Drive folder.
        
        Args:
            folder_id: The ID of the Google Drive folder.
            output_path: Directory to save files to.
            file_extensions: Optional list of file extensions to filter (e.g., ['.jpg', '.png']).
                           If None, downloads all files.
            
        Returns:
            Dictionary with download results including counts and any errors.
        """
        results = {
            'success': False,
            'downloaded': 0,
            'skipped': 0,
            'failed': 0,
            'files': [],
            'errors': []
        }
        
        if not self.service:
            if not self.authenticate():
                results['errors'].append("Authentication failed")
                return results
        
        # Create output directory if it doesn't exist
        if not os.path.exists(output_path):
            os.makedirs(output_path)
            self.logger.info(f"Created output directory: {output_path}")
        
        # List files in folder
        files = self.list_files_in_folder(folder_id)
        
        if not files:
            results['errors'].append("No files found in folder or access denied")
            return results
        
        # Normalize file extensions for comparison
        if file_extensions:
            file_extensions = [ext.lower() if ext.startswith('.') else f'.{ext.lower()}' 
                            for ext in file_extensions]
        
        # Download each file
        for file in files:
            file_name = file['name']
            file_id = file['id']
            mime_type = file.get('mimeType', '')
            
            # Skip Google Docs/Sheets/etc (these have special mime types)
            if mime_type.startswith('application/vnd.google-apps'):
                self.logger.info(f"Skipping Google Doc: {file_name}")
                results['skipped'] += 1
                continue
            
            # Skip subfolders (handled separately if recursive download needed)
            if mime_type == 'application/vnd.google-apps.folder':
                self.logger.info(f"Skipping subfolder: {file_name}")
                results['skipped'] += 1
                continue
            
            # Filter by extension if specified
            if file_extensions:
                file_ext = os.path.splitext(file_name)[1].lower()
                if file_ext not in file_extensions:
                    self.logger.info(f"Skipping {file_name} (extension {file_ext} not in filter)")
                    results['skipped'] += 1
                    continue
            
            # Download the file
            if self.download_file(file_id, file_name, output_path):
                results['downloaded'] += 1
                results['files'].append(file_name)
            else:
                results['failed'] += 1
                results['errors'].append(f"Failed to download: {file_name}")
        
        results['success'] = results['failed'] == 0
        
        self.logger.info(
            f"Download complete: {results['downloaded']} downloaded, "
            f"{results['skipped']} skipped, {results['failed']} failed"
        )
        
        return results
    
    def download_folder_recursive(
        self, 
        folder_id: str, 
        output_path: str, 
        file_extensions: Optional[List[str]] = None
    ) -> Dict:
        """
        Recursively download all files from a Google Drive folder and subfolders.
        
        Args:
            folder_id: The ID of the Google Drive folder.
            output_path: Directory to save files to.
            file_extensions: Optional list of file extensions to filter.
            
        Returns:
            Dictionary with download results.
        """
        results = {
            'success': False,
            'downloaded': 0,
            'skipped': 0,
            'failed': 0,
            'files': [],
            'errors': []
        }
        
        if not self.service:
            if not self.authenticate():
                results['errors'].append("Authentication failed")
                return results
        
        def _download_recursive(fid: str, path: str):
            """Inner recursive function"""
            if not os.path.exists(path):
                os.makedirs(path)
            
            files = self.list_files_in_folder(fid)
            
            for file in files:
                file_name = file['name']
                file_id = file['id']
                mime_type = file.get('mimeType', '')
                
                # Handle subfolders recursively
                if mime_type == 'application/vnd.google-apps.folder':
                    subfolder_path = os.path.join(path, file_name)
                    _download_recursive(file_id, subfolder_path)
                    continue
                
                # Skip Google Docs
                if mime_type.startswith('application/vnd.google-apps'):
                    results['skipped'] += 1
                    continue
                
                # Filter by extension
                if file_extensions:
                    file_extensions_lower = [ext.lower() if ext.startswith('.') else f'.{ext.lower()}' 
                                            for ext in file_extensions]
                    file_ext = os.path.splitext(file_name)[1].lower()
                    if file_ext not in file_extensions_lower:
                        results['skipped'] += 1
                        continue
                
                # Download
                if self.download_file(file_id, file_name, path):
                    results['downloaded'] += 1
                    results['files'].append(os.path.join(path, file_name))
                else:
                    results['failed'] += 1
                    results['errors'].append(f"Failed: {file_name}")
        
        _download_recursive(folder_id, output_path)
        results['success'] = results['failed'] == 0
        
        return results


def main():
    """CLI entry point for Google Drive folder download."""
    import argparse
    
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    parser = argparse.ArgumentParser(
        description='Download a folder from Google Drive',
        epilog='''
Example:
    python gdrive_downloader.py --folder-id 1ABC123xyz --output ./input_folder

To get the folder ID:
    Navigate to your Google Drive folder in a browser.
    The URL will look like: https://drive.google.com/drive/folders/1ABC123xyz
    The folder ID is: 1ABC123xyz
        '''
    )
    parser.add_argument(
        '--folder-id', '-f',
        required=True, 
        help='Google Drive folder ID (from URL)'
    )
    parser.add_argument(
        '--output', '-o',
        required=True, 
        help='Output directory path'
    )
    parser.add_argument(
        '--credentials', '-c',
        default='credentials.json',
        help='Path to credentials.json (default: credentials.json)'
    )
    parser.add_argument(
        '--extensions', '-e',
        nargs='+',
        help='File extensions to download (e.g., jpg png pdf). Downloads all if not specified.'
    )
    parser.add_argument(
        '--recursive', '-r',
        action='store_true',
        help='Download subfolders recursively'
    )
    
    args = parser.parse_args()
    
    # Check for Google API libraries
    if not GOOGLE_API_AVAILABLE:
        print("Error: Google API libraries not installed.")
        print("Install with: pip install google-api-python-client google-auth-httplib2 google-auth-oauthlib")
        return 1
    
    # Initialize downloader
    downloader = GoogleDriveDownloader(credentials_path=args.credentials)
    
    # Authenticate
    print("Authenticating with Google Drive...")
    if not downloader.authenticate():
        print("Authentication failed. Please check your credentials.")
        return 1
    
    print(f"Downloading files from folder ID: {args.folder_id}")
    print(f"Output directory: {args.output}")
    
    # Download
    if args.recursive:
        results = downloader.download_folder_recursive(
            args.folder_id, 
            args.output,
            args.extensions
        )
    else:
        results = downloader.download_folder(
            args.folder_id, 
            args.output,
            args.extensions
        )
    
    # Print results
    print(f"\nDownload Results:")
    print(f"  Downloaded: {results['downloaded']}")
    print(f"  Skipped: {results['skipped']}")
    print(f"  Failed: {results['failed']}")
    
    if results['errors']:
        print("\nErrors:")
        for error in results['errors']:
            print(f"  - {error}")
    
    return 0 if results['success'] else 1


if __name__ == "__main__":
    exit(main())
