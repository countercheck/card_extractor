"""
Unit tests for the PDF Image Extractor main module.
"""

import unittest
from unittest.mock import patch, MagicMock
import io
import sys
import os
from contextlib import redirect_stdout

# Import the main module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
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


if __name__ == '__main__':
    unittest.main()