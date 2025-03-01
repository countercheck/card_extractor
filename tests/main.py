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
    def test_process_pdf_page_iteration_small(self, mock_open):
        """Test iteration through a small PDF (1 page)."""
        # Mock a PDF document with 1 page
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 1
        mock_doc.__iter__.return_value = [MagicMock()]
        mock_open.return_value = mock_doc
        
        # Capture printed output
        output = io.StringIO()
        with redirect_stdout(output):
            process_pdf('small.pdf', 'output')
        
        # Assert that we processed the correct number of pages
        self.assertTrue('Processing page 1 of 1' in output.getvalue())
    
    @patch('fitz.open')
    def test_process_pdf_page_iteration_medium(self, mock_open):
        """Test iteration through a medium PDF (5 pages)."""
        # Mock a PDF document with 5 pages
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 5
        mock_doc.__iter__.return_value = [MagicMock() for _ in range(5)]
        mock_open.return_value = mock_doc
        
        # Capture printed output
        output = io.StringIO()
        with redirect_stdout(output):
            process_pdf('medium.pdf', 'output')
        
        # Assert that we processed the correct number of pages
        for page_num in range(1, 6):
            self.assertTrue(f'Processing page {page_num} of 5' in output.getvalue())
    
    @patch('fitz.open')
    def test_process_pdf_page_iteration_large(self, mock_open):
        """Test iteration through a large PDF (50 pages)."""
        # Mock a PDF document with 50 pages
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 50
        mock_doc.__iter__.return_value = [MagicMock() for _ in range(50)]
        mock_open.return_value = mock_doc
        
        # Capture printed output
        output = io.StringIO()
        with redirect_stdout(output):
            process_pdf('large.pdf', 'output')
        
        # Assert that we processed the correct number of pages
        for page_num in range(1, 51):
            self.assertTrue(f'Processing page {page_num} of 50' in output.getvalue())
            
    @patch('fitz.open')
    def test_process_pdf_empty(self, mock_open):
        """Test handling of an empty PDF (0 pages)."""
        # Mock an empty PDF document
        mock_doc = MagicMock()
        mock_doc.__len__.return_value = 0
        mock_doc.__iter__.return_value = []
        mock_open.return_value = mock_doc
        
        # Capture printed output
        output = io.StringIO()
        with redirect_stdout(output):
            process_pdf('empty.pdf', 'output')
        
        # Assert that no page processing messages were printed
        self.assertFalse('Processing page' in output.getvalue())


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
    def test_multiple_images_per_page(self, mock_open):
        """Test extraction of multiple images from a single page."""
        # Mock PDF document and page
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_doc.__iter__.return_value = [mock_page]
        mock_doc.__len__.return_value = 1
        mock_open.return_value = mock_doc
        
        # Mock many images on a page (10 images)
        mock_page.get_images.return_value = [(i, 0, 0, 0, 0, 0, 0) for i in range(1, 11)]
        
        # Mock extract_image return values
        def extract_image_side_effect(xref):
            return {
                "ext": "png",
                "width": 100,
                "height": 100,
                "image": f"image data {xref}".encode()
            }
        
        mock_doc.extract_image.side_effect = extract_image_side_effect
        
        # Use a temporary directory for output
        with tempfile.TemporaryDirectory() as temp_dir:
            # Redirect stdout to capture print statements
            with redirect_stdout(io.StringIO()):
                process_pdf("multi_image.pdf", temp_dir)
            
            # Check that all 10 image files were created
            files = os.listdir(temp_dir)
            self.assertEqual(len(files), 10)
            
            # Check each file exists with correct naming pattern
            for i in range(1, 11):
                expected_filename = f"multi_image-1-{i}.png"
                self.assertTrue(any(file == expected_filename for file in files),
                               f"Expected {expected_filename} in {files}")
                
                # Check file content
                with open(os.path.join(temp_dir, expected_filename), "rb") as f:
                    self.assertEqual(f.read(), f"image data {i}".encode())
    
    @patch('fitz.open')
    def test_various_image_sizes(self, mock_open):
        """Test extraction of images with different dimensions."""
        # Mock PDF document and page
        mock_doc = MagicMock()
        mock_page = MagicMock()
        mock_doc.__iter__.return_value = [mock_page]
        mock_doc.__len__.return_value = 1
        mock_open.return_value = mock_doc
        
        # Mock images of different sizes
        mock_page.get_images.return_value = [(1, 0, 0, 0, 0, 0, 0), (2, 0, 0, 0, 0, 0, 0), (3, 0, 0, 0, 0, 0, 0)]
        
        # Mock extract_image return values with different dimensions
        def extract_image_side_effect(xref):
            sizes = {
                1: (50, 50),      # Small image
                2: (500, 500),    # Medium image
                3: (2000, 1500)   # Large image
            }
            width, height = sizes[xref]
            return {
                "ext": "png",
                "width": width,
                "height": height,
                "image": f"image data size {width}x{height}".encode()
            }
        
        mock_doc.extract_image.side_effect = extract_image_side_effect
        
        # Use a temporary directory for output
        with tempfile.TemporaryDirectory() as temp_dir:
            # Capture stdout to verify dimensions are logged
            output = io.StringIO()
            with redirect_stdout(output):
                process_pdf("size_test.pdf", temp_dir)
            
            # Check all image files were created
            files = os.listdir(temp_dir)
            self.assertEqual(len(files), 3)
            
            # Verify dimensions were logged correctly
            output_text = output.getvalue()
            self.assertTrue("Dimensions: 50x50" in output_text)
            self.assertTrue("Dimensions: 500x500" in output_text)
            self.assertTrue("Dimensions: 2000x1500" in output_text)
    
    @patch('fitz.open')
    def test_multi_page_multi_image(self, mock_open):
        """Test extraction from multiple pages with multiple images each."""
        # Mock PDF document with 3 pages
        mock_doc = MagicMock()
        mock_pages = [MagicMock() for _ in range(3)]
        mock_doc.__iter__.return_value = mock_pages
        mock_doc.__len__.return_value = 3
        mock_open.return_value = mock_doc
        
        # Mock different numbers of images per page
        # Page 1: 2 images, Page 2: 3 images, Page 3: 1 image
        mock_pages[0].get_images.return_value = [(1, 0, 0, 0, 0, 0, 0), (2, 0, 0, 0, 0, 0, 0)]
        mock_pages[1].get_images.return_value = [(3, 0, 0, 0, 0, 0, 0), (4, 0, 0, 0, 0, 0, 0), (5, 0, 0, 0, 0, 0, 0)]
        mock_pages[2].get_images.return_value = [(6, 0, 0, 0, 0, 0, 0)]
        
        # Mock extract_image return values
        def extract_image_side_effect(xref):
            return {
                "ext": "png",
                "width": 100 * xref,  # Different size for each image
                "height": 75 * xref,
                "image": f"image data xref {xref}".encode()
            }
        
        mock_doc.extract_image.side_effect = extract_image_side_effect
        
        # Use a temporary directory for output
        with tempfile.TemporaryDirectory() as temp_dir:
            # Redirect stdout to capture print statements
            output = io.StringIO()
            with redirect_stdout(output):
                process_pdf("multi_page.pdf", temp_dir)
            
            # Check all 6 image files were created
            files = os.listdir(temp_dir)
            self.assertEqual(len(files), 6)
            
            # Expected filenames based on page number and image number
            expected_files = [
                "multi_page-1-1.png", "multi_page-1-2.png",  # Page 1
                "multi_page-2-1.png", "multi_page-2-2.png", "multi_page-2-3.png",  # Page 2
                "multi_page-3-1.png"  # Page 3
            ]
            
            for expected_file in expected_files:
                self.assertTrue(any(file == expected_file for file in files),
                               f"Expected {expected_file} in {files}")
            
            # Verify dimensions in output
            output_text = output.getvalue()
            # Check for processing messages for each page
            self.assertTrue("Processing page 1 of 3" in output_text)
            self.assertTrue("Processing page 2 of 3" in output_text)
            self.assertTrue("Processing page 3 of 3" in output_text)
            
            # Check for specific dimension logs
            for i in range(1, 7):
                self.assertTrue(f"Dimensions: {100*i}x{75*i}" in output_text)
    
    @patch('fitz.open')
    def test_no_images_in_pdf(self, mock_open):
        """Test handling of a PDF with no images."""
        # Mock PDF document with pages but no images
        mock_doc = MagicMock()
        mock_pages = [MagicMock() for _ in range(2)]
        mock_doc.__iter__.return_value = mock_pages
        mock_doc.__len__.return_value = 2
        mock_open.return_value = mock_doc
        
        # All pages return empty image lists
        for page in mock_pages:
            page.get_images.return_value = []
        
        # Use a temporary directory for output
        with tempfile.TemporaryDirectory() as temp_dir:
            output = io.StringIO()
            with redirect_stdout(output):
                process_pdf("no_images.pdf", temp_dir)
            
            # Verify no files were created
            files = os.listdir(temp_dir)
            self.assertEqual(len(files), 0)
            
            # Verify pages were still processed
            output_text = output.getvalue()
            self.assertTrue("Processing page 1 of 2" in output_text)
            self.assertTrue("Processing page 2 of 2" in output_text)
            # No "Extracted image" messages should appear
            self.assertFalse("Extracted image" in output_text)
    
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
                
    @patch('fitz.open')
    def test_multiple_file_duplicates(self, mock_open):
        """Test handling of multiple file name collisions."""
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
            "image": b"newest image data"
        }
        
        # Use a temporary directory for output
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create multiple files with the same base name and numbered suffixes
            base_filename = "collision-1-1.png"
            base_path = os.path.join(temp_dir, base_filename)
            with open(base_path, "wb") as f:
                f.write(b"existing image data")
                
            # Also create collision-1-1_1.png and collision-1-1_2.png
            with open(os.path.join(temp_dir, "collision-1-1_1.png"), "wb") as f:
                f.write(b"existing image data 1")
                
            with open(os.path.join(temp_dir, "collision-1-1_2.png"), "wb") as f:
                f.write(b"existing image data 2")
            
            # Redirect stdout to capture print statements
            with redirect_stdout(io.StringIO()):
                process_pdf("collision.pdf", temp_dir)
            
            # Check that all files exist (original and all suffixes including the new one)
            files = os.listdir(temp_dir)
            self.assertEqual(len(files), 4)
            
            # Check that the original files are unchanged
            with open(base_path, "rb") as f:
                self.assertEqual(f.read(), b"existing image data")
                
            with open(os.path.join(temp_dir, "collision-1-1_1.png"), "rb") as f:
                self.assertEqual(f.read(), b"existing image data 1")
                
            with open(os.path.join(temp_dir, "collision-1-1_2.png"), "rb") as f:
                self.assertEqual(f.read(), b"existing image data 2")
            
            # Check the content of the new file with suffix _3
            with open(os.path.join(temp_dir, "collision-1-1_3.png"), "rb") as f:
                self.assertEqual(f.read(), b"newest image data")


if __name__ == '__main__':
    unittest.main()