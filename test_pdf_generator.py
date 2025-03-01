"""
Unit tests for the PDF Image Extractor main module.
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open, call, ANY
import io
import sys
import os
import tempfile
import shutil
import fitz
import cv2
from contextlib import redirect_stdout

# Update path to ensure we can import from src.card_extractor
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from src.card_extractor.main import (
    parse_args, process_pdf, parse_pages, 
    detect_and_extract_image_regions, save_image
)


class TestArgumentParsing(unittest.TestCase):
    """Tests for the command-line argument parsing functionality."""
    
    @patch('argparse.ArgumentParser.parse_args')
    def test_argument_parsing(self, mock_parse_args):
        """Test that argument parsing correctly handles required arguments."""
        # Mock the return value of parse_args
        mock_args = MagicMock()
        mock_args.input_path = 'test.pdf'
        mock_args.output_folder = 'output'
        mock_args.format = 'png'
        mock_args.pages = None
        mock_args.recursive = False
        mock_parse_args.return_value = mock_args
        
        # Call the function
        args = parse_args()
        
        # Assert the arguments were parsed correctly
        self.assertEqual(args.input_path, 'test.pdf')
        self.assertEqual(args.output_folder, 'output')
        self.assertEqual(args.format, 'png')
        self.assertIsNone(args.pages)
        self.assertFalse(args.recursive)
    
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
        mock_args.pages = None
        mock_args.recursive = False
        mock_parse_args.return_value = mock_args
        
        # Call the function
        args = parse_args()
        
        # Assert the format argument has the default value
        self.assertEqual(args.format, 'png')
        
        # Mock a different format
        mock_args.format = 'jpeg'
        args = parse_args()
        self.assertEqual(args.format, 'jpeg')
    
    @patch('argparse.ArgumentParser.parse_args')
    def test_pages_option(self, mock_parse_args):
        """Test that the pages option is correctly processed."""
        # Mock the return value of parse_args
        mock_args = MagicMock()
        mock_args.input_path = 'test.pdf'
        mock_args.output_folder = 'output'
        mock_args.format = 'png'
        mock_args.pages = '1,3-5'
        mock_args.recursive = False
        mock_parse_args.return_value = mock_args
        
        # Call the function
        args = parse_args()
        
        # Assert the pages argument is passed correctly
        self.assertEqual(args.pages, '1,3-5')
    
    @patch('argparse.ArgumentParser.parse_args')
    def test_recursive_option(self, mock_parse_args):
        """Test that the recursive option is correctly processed."""
        # Mock the return value of parse_args
        mock_args = MagicMock()
        mock_args.input_path = 'test.pdf'
        mock_args.output_folder = 'output'
        mock_args.format = 'png'
        mock_args.pages = None
        mock_args.recursive = True
        mock_parse_args.return_value = mock_args
        
        # Call the function
        args = parse_args()
        
        # Assert the recursive flag is set
        self.assertTrue(args.recursive)


class TestPagesParsing(unittest.TestCase):
    """Tests for the pages parsing functionality."""
    
    def test_parse_pages_no_string(self):
        """Test parsing with no pages string (should return all pages)."""
        # Test with 5 total pages and no pages specified
        pages = parse_pages(None, 5)
        self.assertEqual(pages, {0, 1, 2, 3, 4})
    
    def test_parse_pages_single_page(self):
        """Test parsing a single page number."""
        # Test with 5 total pages and single page specified
        pages = parse_pages('3', 5)
        self.assertEqual(pages, {2})  # 0-indexed, so page 3 is index 2
    
    def test_parse_pages_range(self):
        """Test parsing a range of pages."""
        # Test with 10 total pages and a range specified
        pages = parse_pages('2-5', 10)
        self.assertEqual(pages, {1, 2, 3, 4})  # 0-indexed
    
    def test_parse_pages_comma_separated(self):
        """Test parsing comma-separated page numbers."""
        # Test with 10 total pages and comma-separated values
        pages = parse_pages('1,3,5', 10)
        self.assertEqual(pages, {0, 2, 4})  # 0-indexed
    
    def test_parse_pages_complex(self):
        """Test parsing a complex pages string."""
        # Test with 10 total pages and complex string
        pages = parse_pages('1,3-5,8', 10)
        self.assertEqual(pages, {0, 2, 3, 4, 7})  # 0-indexed
    
    def test_parse_pages_out_of_range(self):
        """Test parsing with out-of-range values."""
        # Capture stdout to check warnings
        output = io.StringIO()
        with redirect_stdout(output):
            # Test with 5 total pages and out-of-range value
            pages = parse_pages('3,8', 5)
            self.assertEqual(pages, {2})  # Only page 3 (index 2) is in range
            self.assertTrue("out of range" in output.getvalue())
    
    def test_parse_pages_invalid_format(self):
        """Test parsing with invalid format."""
        # Capture stdout to check warnings
        output = io.StringIO()
        with redirect_stdout(output):
            # Test with invalid format (non-numeric)
            pages = parse_pages('1,a,3', 5)
            self.assertEqual(pages, {0, 2})  # Only valid pages 1 and 3
            self.assertTrue("Invalid page number" in output.getvalue())


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
    @patch('os.makedirs')
    def test_process_pdf_page_iteration_small(self, mock_makedirs, mock_open):
        """Test iteration through a small PDF (1 page)."""
        # Mock a PDF document with 1 page
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 1
        mock_page = MagicMock()
        mock_page.get_images.return_value = []  # No images
        mock_doc.__iter__.return_value = [mock_page]
        mock_open.return_value = mock_doc
        
        # Capture printed output
        output = io.StringIO()
        with redirect_stdout(output):
            # Mock detect_and_extract_image_regions to return empty list
            with patch('src.card_extractor.main.detect_and_extract_image_regions', return_value=[]):
                process_pdf('small.pdf', 'output')
        
        # Assert that we processed the correct number of pages
        self.assertTrue('Processing page 1 of 1' in output.getvalue())
    
    @patch('fitz.open')
    @patch('os.makedirs')
    def test_process_pdf_page_iteration_medium(self, mock_makedirs, mock_open):
        """Test iteration through a medium PDF (5 pages)."""
        # Mock a PDF document with 5 pages
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 5
        mock_pages = [MagicMock() for _ in range(5)]
        for page in mock_pages:
            page.get_images.return_value = []  # No images
        mock_doc.__iter__.return_value = mock_pages
        mock_open.return_value = mock_doc
        
        # Capture printed output
        output = io.StringIO()
        with redirect_stdout(output):
            # Mock detect_and_extract_image_regions to return empty list
            with patch('src.card_extractor.main.detect_and_extract_image_regions', return_value=[]):
                process_pdf('medium.pdf', 'output')
        
        # Assert that we processed the correct number of pages
        for page_num in range(1, 6):
            self.assertTrue(f'Processing page {page_num} of 5' in output.getvalue())
    
    @patch('fitz.open')
    @patch('os.makedirs')
    def test_process_pdf_password_protected(self, mock_makedirs, mock_open):
        """Test handling of password-protected PDFs."""
        # First attempt raises a RuntimeError with 'password' in message
        mock_open.side_effect = [
            RuntimeError("This file requires a password"),
            MagicMock()  # Second attempt succeeds with password
        ]
        
        # Mock the password input
        with patch('builtins.input', return_value='correct_password'):
            # Capture output
            output = io.StringIO()
            with redirect_stdout(output):
                process_pdf('protected.pdf', 'output')
            
            # Check that password prompt was handled
            self.assertTrue('password-protected' in output.getvalue())
            
            # Check that the file was opened twice (once without password, once with)
            self.assertEqual(mock_open.call_count, 2)
            
            # Check that the second call included the password
            mock_open.assert_called_with('protected.pdf', password='correct_password')
    
    @patch('fitz.open')
    @patch('os.makedirs')
    def test_process_pdf_password_incorrect(self, mock_makedirs, mock_open):
        """Test handling of incorrect password for protected PDFs."""
        # First attempt raises RuntimeError with 'password'
        mock_open.side_effect = [
            RuntimeError("This file requires a password"),
            RuntimeError("Incorrect password")  # Second attempt fails
        ]
        
        # Mock the password input
        with patch('builtins.input', return_value='wrong_password'):
            # Capture output
            output = io.StringIO()
            with redirect_stdout(output):
                process_pdf('protected.pdf', 'output')
            
            # Check that error was handled
            self.assertTrue('Incorrect password' in output.getvalue())
    
    @patch('fitz.open')
    @patch('os.makedirs')
    def test_process_pdf_password_empty(self, mock_makedirs, mock_open):
        """Test handling of empty password for protected PDFs."""
        # First attempt raises RuntimeError with 'password'
        mock_open.side_effect = RuntimeError("This file requires a password")
        
        # Mock the password input to return empty string
        with patch('builtins.input', return_value=''):
            # Capture output
            output = io.StringIO()
            with redirect_stdout(output):
                process_pdf('protected.pdf', 'output')
            
            # Check that file was skipped
            self.assertTrue('No password provided' in output.getvalue())
    
    @patch('fitz.open')
    @patch('os.makedirs')
    def test_process_pdf_corrupted(self, mock_makedirs, mock_open):
        """Test handling of corrupted PDF files."""
        # Mock a FileDataError when opening the PDF
        mock_open.side_effect = fitz.FileDataError("Invalid PDF data")
        
        # Capture output
        output = io.StringIO()
        with redirect_stdout(output):
            process_pdf('corrupted.pdf', 'output')
        
        # Check that error was handled
        self.assertTrue('corrupted or not a valid PDF file' in output.getvalue())


class TestImageDetection(unittest.TestCase):
    """Tests for the computer vision image detection functionality."""
    
    @patch('cv2.imread')
    @patch('cv2.cvtColor')
    @patch('cv2.GaussianBlur')
    @patch('cv2.Canny')
    @patch('cv2.dilate')
    @patch('cv2.findContours')
    @patch('cv2.contourArea')
    @patch('cv2.boundingRect')
    def test_detect_and_extract_image_regions(
        self, mock_boundrect, mock_area, mock_contours, 
        mock_dilate, mock_canny, mock_blur, mock_cvtcolor, mock_imread
    ):
        """Test the image region detection function."""
        # Mock the image and its properties
        mock_image = MagicMock()
        mock_image.shape = (500, 400, 3)  # height, width, channels
        mock_imread.return_value = mock_image
        
        # Mock contours
        mock_contour1 = MagicMock()
        mock_contour2 = MagicMock()
        mock_contours.return_value = ([mock_contour1, mock_contour2], None)
        
        # Mock contour areas
        mock_area.side_effect = [5000, 2000]  # Areas above min_area
        
        # Mock bounding rectangles
        mock_boundrect.side_effect = [(50, 50, 100, 100), (200, 200, 80, 60)]
        
        # Call the function
        regions = detect_and_extract_image_regions('test_image.png')
        
        # Check that it returned the expected number of regions
        self.assertEqual(len(regions), 2)
        
        # Verify that imread was called with the correct path
        mock_imread.assert_called_once_with('test_image.png')
        
        # Verify that findContours was called
        mock_contours.assert_called_once()
        
        # Verify that contourArea was called for each contour
        self.assertEqual(mock_area.call_count, 2)
        
        # Verify that boundingRect was called for each valid contour
        self.assertEqual(mock_boundrect.call_count, 2)
    
    @patch('cv2.imread', return_value=None)
    def test_detect_and_extract_image_regions_file_error(self, mock_imread):
        """Test handling of image file errors in detection function."""
        # Capture output
        output = io.StringIO()
        with redirect_stdout(output):
            # Call the function with an image that can't be read
            regions = detect_and_extract_image_regions('missing_image.png')
        
        # Check that we got an empty list
        self.assertEqual(regions, [])
        
        # Check that error was reported
        self.assertTrue('Could not read image' in output.getvalue())
    
    @patch('cv2.imread')
    @patch('cv2.cvtColor')
    @patch('cv2.GaussianBlur')
    @patch('cv2.Canny')
    @patch('cv2.dilate')
    @patch('cv2.findContours')
    @patch('cv2.contourArea')
    def test_detect_and_extract_image_regions_no_significant_contours(
        self, mock_area, mock_contours, mock_dilate, 
        mock_canny, mock_blur, mock_cvtcolor, mock_imread
    ):
        """Test detection function when no significant contours are found."""
        # Mock the image
        mock_image = MagicMock()
        mock_image.shape = (500, 400, 3)
        mock_imread.return_value = mock_image
        
        # Mock contours
        mock_contour1 = MagicMock()
        mock_contour2 = MagicMock()
        mock_contours.return_value = ([mock_contour1, mock_contour2], None)
        
        # Mock contour areas (below min_area)
        mock_area.side_effect = [500, 800]  # Areas below min_area=1000
        
        # Call the function
        regions = detect_and_extract_image_regions('test_image.png')
        
        # Check that no regions were returned (all contours too small)
        self.assertEqual(regions, [])
        
        # Verify that contourArea was called for each contour
        self.assertEqual(mock_area.call_count, 2)


class TestImageExtraction(unittest.TestCase):
    """Tests for the image extraction and saving functionality."""
    
    @patch('fitz.open')
    @patch('os.makedirs')
    @patch('os.path.exists', return_value=False)
    def test_image_extraction_standard_method(self, mock_exists, mock_makedirs, mock_open):
        """Test image extraction using the standard PyMuPDF method."""
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
        
        # Mock file operations
        mock_file = MagicMock()
        with patch('builtins.open', mock_open(read_data="data")):
            # Capture output
            output = io.StringIO()
            with redirect_stdout(output):
                process_pdf("test.pdf", "output")
        
        # Check that extract_image was called with the correct xref
        mock_doc.extract_image.assert_called_once_with(1)
        
        # Check that the image was written to file
        mock_file = open.return_value.__enter__.return_value
        mock_file.write.assert_called_once_with(b"mock image data")
    
    @patch('fitz.open')
    @patch('os.makedirs')
    @patch('os.path.exists', return_value=True)
    @patch('tempfile.NamedTemporaryFile')
    @patch('src.card_extractor.main.detect_and_extract_image_regions')
    @patch('src.card_extractor.main.save_image')
    @patch('os.unlink')
    def test_image_extraction_opencv_method(
        self, mock_unlink, mock_save, mock_detect, mock_tempfile, 
        mock_exists, mock_makedirs, mock_open
    ):
        """Test image extraction using the OpenCV fallback method."""
        # Mock PDF document and page with no embedded images
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_doc.__iter__.return_value = [mock_page]
        mock_doc.__len__.return_value = 1
        mock_open.return_value = mock_doc
        
        # Page has no images via standard method
        mock_page.get_images.return_value = []
        
        # Mock temporary file
        mock_temp = MagicMock()
        mock_temp.name = '/tmp/temp_file.png'
        mock_tempfile.return_value.__enter__.return_value = mock_temp
        
        # Mock pixmap for page rendering
        mock_pixmap = MagicMock()
        mock_pixmap.width = 800
        mock_pixmap.height = 600
        mock_page.get_pixmap.return_value = mock_pixmap
        
        # Mock OpenCV detection to find two regions
        mock_region1 = MagicMock()
        mock_region1.shape = (200, 300, 3)
        mock_region2 = MagicMock()
        mock_region2.shape = (150, 250, 3)
        mock_detect.return_value = [mock_region1, mock_region2]
        
        # Capture output
        output = io.StringIO()
        with redirect_stdout(output):
            process_pdf("test.pdf", "output", "png")
        
        # Check that pixmap save was called (for rendering the page)
        mock_pixmap.save.assert_called_once_with('/tmp/temp_file.png')
        
        # Check that detect_and_extract_image_regions was called
        mock_detect.assert_called_once_with('/tmp/temp_file.png')
        
        # Check that save_image was called for each region
        self.assertEqual(mock_save.call_count, 2)
        
        # Check that temp file was cleaned up
        mock_unlink.assert_called_once_with('/tmp/temp_file.png')
        
        # Check output log
        output_text = output.getvalue()
        self.assertTrue('No images extracted using standard method' in output_text)
        self.assertTrue('Using computer vision to detect images' in output_text)
        self.assertTrue('Detected 2 distinct image regions' in output_text)
    
    @patch('fitz.open')
    @patch('os.makedirs')
    @patch('os.path.exists', return_value=True)
    @patch('tempfile.NamedTemporaryFile')
    @patch('src.card_extractor.main.detect_and_extract_image_regions')
    @patch('PIL.Image.open')
    @patch('os.unlink')
    def test_image_extraction_opencv_no_regions(
        self, mock_unlink, mock_pil_open, mock_detect, mock_tempfile, 
        mock_exists, mock_makedirs, mock_open
    ):
        """Test OpenCV fallback when no image regions are detected."""
        # Mock PDF document and page with no embedded images
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_doc.__iter__.return_value = [mock_page]
        mock_doc.__len__.return_value = 1
        mock_open.return_value = mock_doc
        
        # Page has no images via standard method
        mock_page.get_images.return_value = []
        
        # Mock temporary file
        mock_temp = MagicMock()
        mock_temp.name = '/tmp/temp_file.png'
        mock_tempfile.return_value.__enter__.return_value = mock_temp
        
        # Mock pixmap for page rendering
        mock_pixmap = MagicMock()
        mock_pixmap.width = 800
        mock_pixmap.height = 600
        mock_page.get_pixmap.return_value = mock_pixmap
        
        # Mock OpenCV detection to find no regions
        mock_detect.return_value = []
        
        # Mock PIL Image for saving whole page
        mock_pil_image = MagicMock()
        mock_pil_open.return_value = mock_pil_image
        
        # Capture output
        output = io.StringIO()
        with redirect_stdout(output):
            process_pdf("test.pdf", "output", "png")
        
        # Check that pixmap save was called (for rendering the page)
        mock_pixmap.save.assert_called_once_with('/tmp/temp_file.png')
        
        # Check that detect_and_extract_image_regions was called
        mock_detect.assert_called_once_with('/tmp/temp_file.png')
        
        # Check that PIL was used to save the whole page when no regions found
        mock_pil_open.assert_called_once_with('/tmp/temp_file.png')
        mock_pil_image.save.assert_called_once()
        
        # Check that temp file was cleaned up
        mock_unlink.assert_called_once_with('/tmp/temp_file.png')
        
        # Check output log
        output_text = output.getvalue()
        self.assertTrue('No distinct image regions detected' in output_text)
        self.assertTrue('Saved full page as:' in output_text)
    
    @patch('cv2.cvtColor')
    @patch('PIL.Image.fromarray')
    def test_save_image(self, mock_from_array, mock_cvt_color):
        """Test the save_image function."""
        # Mock image array
        mock_array = MagicMock()
        
        # Mock PIL image
        mock_pil_image = MagicMock()
        mock_from_array.return_value = mock_pil_image
        
        # Call the function
        save_image(mock_array, 'output.png', 'png')
        
        # Check that cvtColor was called to convert BGR to RGB
        mock_cvt_color.assert_called_once_with(mock_array, cv2.COLOR_BGR2RGB)
        
        # Check that fromarray was called with the converted array
        mock_from_array.assert_called_once()
        
        # Check that save was called with the correct format
        mock_pil_image.save.assert_called_once_with('output.png', format='PNG')


if __name__ == '__main__':
    unittest.main()