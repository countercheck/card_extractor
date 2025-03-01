"""
Card Extractor - A command-line tool for extracting images from PDF files.

This package provides functionality to extract images from PDF files with
various options for output folder, image format, page selection, and 
recursive directory scanning.

Example usage as a library:
    from card_extractor import process_pdf
    process_pdf('document.pdf', 'output_folder')
"""

__version__ = "0.1.0"

# Import and expose key functions from the package
from .main import process_pdf, main

# Define which symbols are exported when using "from card_extractor import *"
__all__ = ['process_pdf', 'main']