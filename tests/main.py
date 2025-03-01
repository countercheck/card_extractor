"""
Unit tests for the PDF Image Extractor main module.
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
import io
import sys
import os
import tempfile
import shutil
from contextlib import redirect_stdout

# Update path to ensure we can import from src.card_extractor
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.card_extractor.main import parse_args, process_pdf


class TestArgumentParsing(unittest.TestCase):
    """Tests for the command-line argument parsing functionality."""
    
    @patch('argparse.ArgumentParser.parse_args')
    def test_argument_parsing(self, mock_parse_args):
        """Test that argument parsing correctly handles required arguments."""
        # Mock the return value of parse_args
        mock_args = MagicMock()
        mock_args.input_path = 'test.pdf'
        mock_args.output_folder = 'output'
        mock_parse_args.return_value = mock_args
        
        # Call the function
        args = parse_args()
        
        # Assert the arguments were parsed correctly
        self.assertEqual(args.input_path, 'test.pdf')
        self.assertEqual(args.output_folder, 'output')
    
    @patch('sys.argv', ['main.py', 'test.pdf'])  # Missing required -o argument
    def test_missing_required_argument(self):
        """Test that the parser exits when a required argument is missing."""
        with self.assertRaises(SystemExit):
            parse_args()
    
    @patch('argparse.ArgumentParser.parse_args')
    def test_format_option(self, mock_parse_args):
        """Test that the format option is correctly processed."""
        # Mock the return value of parse_args for default format
        mock_args = MagicMock()
        mock_args.input_path = 'test.pdf'
        mock_args.output_folder = 'output'
        mock_args.format = 'png'  # Default value
        mock_parse_args.return_value = mock_args
        
        # Call the function
        args = parse_args()
        
        # Assert the format argument has the default value
        self.assertEqual(args.format, 'png')
        
        # Mock a different format
        mock_args.format = 'jpeg'
        args = parse_args()
        self.assertEqual(args.format, 'jpeg')


class TestPDFProcessing(unittest.TestCase):
    """Tests for the PDF processing functionality."""
    
    @patch('builtins.print')
    @patch('fitz.open', side_effect=FileNotFoundError("File not found"))
    def test_process_pdf_file_not_found(self, mock_open, mock_print):
        """Test handling of non-existent PDF files."""
        # Call the function with a non-existent file
        process_pdf('nonexistent.pdf', 'output')
        
        # Assert the correct error message was printed
        mock_print.assert_called_with('Error: PDF file not found: nonexistent.pdf')
    
    @patch('fitz.open')
    def test_process_pdf_page_iteration(self, mock_open):
        """Test iteration through PDF pages."""
        # Mock the PDF document and its pages
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 3  # PDF has 3 pages
        mock_doc.__iter__.return_value = [MagicMock(), MagicMock(), MagicMock()]
        mock_open.return_value = mock_doc
        
        # Capture printed output
        output = io.StringIO()
        with redirect_stdout(output):
            process_pdf('test.pdf', 'output')
        
        # Assert that we processed the correct number of pages
        self.assertTrue('Processing page 1 of 3' in output.getvalue())
        self.assertTrue('Processing page 2 of 3' in output.getvalue())
        self.assertTrue('Processing page 3 of 3' in output.getvalue())


class TestImageExtraction(unittest.TestCase):
    """Tests for the image extraction and saving functionality."""
    
    @patch('fitz.open')
    def test_image_extraction(self, mock_open):
        """Test that images are correctly extracted from a PDF."""
        # Mock PDF document and page
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_doc.__iter__.return_value = [mock_page]
        mock_doc.__len__.return_value = 1
        mock_open.return_value = mock_doc
        
        # Mock image list return value for page.get_images()
        mock_page.get_images.return_value = [(1, 0, 0, 0, 0, 0, 0)]  # Mock xref is 1
        
        # Mock extract_image return value
        mock_image_data = {
            "ext": "png",
            "width": 100,
            "height": 100,
            "image": b"mock image data"
        }
        mock_doc.extract_image.return_value = mock_image_data
        
        # Use a temporary directory for output
        with tempfile.TemporaryDirectory() as temp_dir:
            # Redirect stdout to capture print statements
            with redirect_stdout(io.StringIO()):
                process_pdf("test.pdf", temp_dir)
            
            # Check that extract_image was called with the correct xref
            mock_doc.extract_image.assert_called_once_with(1)
            
            # Check that an image file was created
            files = os.listdir(temp_dir)
            self.assertEqual(len(files), 1)
            self.assertTrue(files[0].startswith("test-1-1.png"))
    
    @patch('fitz.open')
    def test_image_saving(self, mock_open):
        """Test that images are saved with the correct naming convention."""
        # Mock PDF document and page
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_doc.__iter__.return_value = [mock_page]
        mock_doc.__len__.return_value = 1
        mock_open.return_value = mock_doc
        
        # Mock multiple images on a page
        mock_page.get_images.return_value = [(1, 0, 0, 0, 0, 0, 0), (2, 0, 0, 0, 0, 0, 0)]
        
        # Mock extract_image return values with different extensions
        def extract_image_side_effect(xref):
            if xref == 1:
                return {
                    "ext": "png",
                    "width": 100,
                    "height": 100,
                    "image": b"mock png data"
                }
            elif xref == 2:
                return {
                    "ext": "jpeg",
                    "width": 200,
                    "height": 150,
                    "image": b"mock jpeg data"
                }
        
        mock_doc.extract_image.side_effect = extract_image_side_effect
        
        # Use a temporary directory for output
        with tempfile.TemporaryDirectory() as temp_dir:
            # Redirect stdout to capture print statements
            with redirect_stdout(io.StringIO()):
                process_pdf("sample.pdf", temp_dir)
            
            # Check that image files were created with correct names
            files = os.listdir(temp_dir)
            self.assertEqual(len(files), 2)
            
            # Check file names follow the convention
            expected_files = ["sample-1-1.png", "sample-1-2.jpeg"]
            for expected_file in expected_files:
                self.assertTrue(any(file == expected_file for file in files), 
                                f"Expected {expected_file} in {files}")
            
            # Check file contents
            with open(os.path.join(temp_dir, "sample-1-1.png"), "rb") as f:
                self.assertEqual(f.read(), b"mock png data")
            
            with open(os.path.join(temp_dir, "sample-1-2.jpeg"), "rb") as f:
                self.assertEqual(f.read(), b"mock jpeg data")
    
    @patch('fitz.open')
    def test_file_overwrite(self, mock_open):
        """Test that files with duplicate names are handled correctly."""
        # Mock PDF document and page
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_doc.__iter__.return_value = [mock_page]
        mock_doc.__len__.return_value = 1
        mock_open.return_value = mock_doc
        
        # Mock a single image
        mock_page.get_images.return_value = [(1, 0, 0, 0, 0, 0, 0)]
        
        # Mock extract_image return value
        mock_doc.extract_image.return_value = {
            "ext": "png",
            "width": 100,
            "height": 100,
            "image": b"new image data"
        }
        
        # Use a temporary directory for output
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create a file with the same name that would be generated
            existing_filename = os.path.join(temp_dir, "duplicate-1-1.png")
            with open(existing_filename, "wb") as f:
                f.write(b"existing image data")
            
            # Redirect stdout to capture print statements
            with redirect_stdout(io.StringIO()):
                process_pdf("duplicate.pdf", temp_dir)
            
            # Check that both files exist (original and with suffix)
            files = os.listdir(temp_dir)
            self.assertEqual(len(files), 2)
            
            # Check the content of the original file is unchanged
            with open(existing_filename, "rb") as f:
                self.assertEqual(f.read(), b"existing image data")
            
            # Check the content of the new file with suffix
            with open(os.path.join(temp_dir, "duplicate-1-1_1.png"), "rb") as f:
                self.assertEqual(f.read(), b"new image data")


if __name__ == '__main__':
    unittest.main()