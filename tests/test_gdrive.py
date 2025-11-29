"""
Unit tests for Google Drive Downloader Module
"""

import unittest
import os
import tempfile
from unittest.mock import Mock, patch, MagicMock
import sys

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from modules.gdrive_downloader import GoogleDriveDownloader, GOOGLE_API_AVAILABLE


class TestGoogleDriveDownloader(unittest.TestCase):
    """Tests for GoogleDriveDownloader class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.downloader = GoogleDriveDownloader(
            credentials_path='fake_credentials.json',
            token_path='fake_token.json'
        )
    
    def tearDown(self):
        """Clean up temp files"""
        import shutil
        if os.path.exists(self.temp_dir):
            shutil.rmtree(self.temp_dir)
    
    def test_init(self):
        """Test GoogleDriveDownloader initialization"""
        downloader = GoogleDriveDownloader()
        self.assertEqual(downloader.credentials_path, 'credentials.json')
        self.assertEqual(downloader.token_path, 'token.json')
        self.assertIsNone(downloader.service)
    
    def test_init_custom_paths(self):
        """Test initialization with custom credential paths"""
        downloader = GoogleDriveDownloader(
            credentials_path='my_creds.json',
            token_path='my_token.json'
        )
        self.assertEqual(downloader.credentials_path, 'my_creds.json')
        self.assertEqual(downloader.token_path, 'my_token.json')
    
    def test_authenticate_without_service(self):
        """Test authenticate returns False when service is None and no credentials"""
        result = self.downloader.authenticate()
        # Should fail because credentials.json doesn't exist
        self.assertFalse(result)
    
    def test_list_files_without_auth(self):
        """Test list_files_in_folder returns empty when not authenticated"""
        result = self.downloader.list_files_in_folder('fake_folder_id')
        self.assertEqual(result, [])
    
    def test_download_file_without_auth(self):
        """Test download_file returns False when not authenticated"""
        result = self.downloader.download_file('fake_id', 'test.jpg', self.temp_dir)
        self.assertFalse(result)
    
    def test_download_folder_without_auth(self):
        """Test download_folder fails gracefully when not authenticated"""
        result = self.downloader.download_folder('fake_folder_id', self.temp_dir)
        self.assertFalse(result['success'])
        self.assertIn('Authentication failed', result['errors'][0])
    
    @unittest.skipIf(not GOOGLE_API_AVAILABLE, "Google API not installed")
    @patch('modules.gdrive_downloader.build')
    @patch('modules.gdrive_downloader.Credentials')
    def test_list_files_with_mock_service(self, mock_credentials, mock_build):
        """Test list_files_in_folder with mocked service"""
        # Setup mock
        mock_service = MagicMock()
        mock_files = MagicMock()
        mock_list = MagicMock()
        mock_execute = MagicMock(return_value={
            'files': [
                {'id': '1', 'name': 'doc1.jpg', 'mimeType': 'image/jpeg'},
                {'id': '2', 'name': 'doc2.png', 'mimeType': 'image/png'}
            ],
            'nextPageToken': None
        })
        
        mock_build.return_value = mock_service
        mock_service.files.return_value = mock_files
        mock_files.list.return_value = mock_list
        mock_list.execute = mock_execute
        
        self.downloader.service = mock_service
        
        result = self.downloader.list_files_in_folder('test_folder_id')
        
        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]['name'], 'doc1.jpg')
        self.assertEqual(result[1]['name'], 'doc2.png')
    
    def test_download_folder_creates_directory(self):
        """Test that download_folder creates output directory"""
        output_path = os.path.join(self.temp_dir, 'new_folder')
        
        # Mock the authenticate to return False
        with patch.object(self.downloader, 'authenticate', return_value=False):
            self.downloader.download_folder('fake_id', output_path)
        
        # Directory should not be created if auth fails
        self.assertFalse(os.path.exists(output_path))
    
    @unittest.skipIf(not GOOGLE_API_AVAILABLE, "Google API not installed")
    def test_download_folder_with_extension_filter(self):
        """Test download_folder with file extension filter"""
        # Setup mock service
        mock_service = MagicMock()
        mock_files = [
            {'id': '1', 'name': 'doc1.jpg', 'mimeType': 'image/jpeg'},
            {'id': '2', 'name': 'doc2.pdf', 'mimeType': 'application/pdf'},
            {'id': '3', 'name': 'doc3.png', 'mimeType': 'image/png'}
        ]
        
        mock_list_response = MagicMock()
        mock_list_response.execute.return_value = {
            'files': mock_files,
            'nextPageToken': None
        }
        mock_service.files.return_value.list.return_value = mock_list_response
        
        # Mock download to succeed
        with patch.object(self.downloader, 'download_file', return_value=True):
            self.downloader.service = mock_service
            
            result = self.downloader.download_folder(
                'test_folder',
                self.temp_dir,
                file_extensions=['.jpg', '.png']
            )
        
        # Should have downloaded 2 (jpg, png) and skipped 1 (pdf)
        self.assertEqual(result['downloaded'], 2)
        self.assertEqual(result['skipped'], 1)


class TestGoogleDriveDownloaderIntegration(unittest.TestCase):
    """Integration tests (require actual credentials)"""
    
    @unittest.skip("Requires actual Google credentials")
    def test_real_authentication(self):
        """Test real authentication flow"""
        downloader = GoogleDriveDownloader()
        result = downloader.authenticate()
        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
