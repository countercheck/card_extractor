#!/usr/bin/env python3
"""
PDF Image Extractor - A command-line tool for extracting images from PDF files.

This tool allows you to extract all images from PDF files with various options
for output folder, image format, page selection, and recursive directory scanning.
"""

import argparse
import os
import sys
import fitz  # PyMuPDF package provides the fitz module


def parse_args():
    """
    Parse command-line arguments for the PDF Image Extractor tool.
    
    Returns:
        argparse.Namespace: The parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Extract images from PDF files",
        epilog="Example: python main.py input.pdf -o output_folder"
    )
    
    # Input file or directory argument (positional)
    parser.add_argument(
        "input_path",
        help="Path to a PDF file or directory containing PDF files"
    )
    
    # Required output folder argument
    parser.add_argument(
        "--output-folder", "-o",
        required=True,
        help="Directory where extracted images will be saved"
    )
    
    # Parse and return the arguments
    return parser.parse_args()


def process_pdf(pdf_path, output_folder):
    """
    Process a PDF file to extract images.
    
    Args:
        pdf_path (str): Path to the PDF file
        output_folder (str): Path to the output folder where images will be saved
    """
    try:
        # Create output directory if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            
        # Open the PDF document
        doc = fitz.open(pdf_path)
        
        # Get the source document name (without extension)
        source_doc_name = os.path.splitext(os.path.basename(pdf_path))[0]
        
        # Iterate through each page
        for page_num, page in enumerate(doc):
            print(f"Processing page {page_num + 1} of {len(doc)}")
            
            # Get all images on the current page
            images = page.get_images(full=True)
            
            # Iterate through each image on the page
            for img_idx, img in enumerate(images):
                # Extract the image (img[0] is the xref)
                xref = img[0]
                image_data = doc.extract_image(xref)
                
                # Construct output filename
                base_filename = f"{source_doc_name}-{page_num + 1}-{img_idx + 1}.{image_data['ext']}"
                output_path = os.path.join(output_folder, base_filename)
                
                # Check if file exists and add suffix if needed
                counter = 1
                while os.path.exists(output_path):
                    # Add a numerical suffix before the extension
                    filename_parts = os.path.splitext(base_filename)
                    new_filename = f"{filename_parts[0]}_{counter}{filename_parts[1]}"
                    output_path = os.path.join(output_folder, new_filename)
                    counter += 1
                
                # Write image data to file
                with open(output_path, "wb") as img_file:
                    img_file.write(image_data["image"])
                
                # Print the image information
                print(f"  Extracted image: {os.path.basename(output_path)}, "
                      f"Dimensions: {image_data['width']}x{image_data['height']}")
                
    except FileNotFoundError:
        print(f"Error: PDF file not found: {pdf_path}")
    except Exception as e:
        print(f"Error processing PDF {pdf_path}: {str(e)}")


def main():
    """
    Main function that serves as the entry point for the application.
    """
    # Parse command-line arguments
    args = parse_args()
    
    # Print parsed arguments (for debugging/verification)
    print(f"Input path: {args.input_path}")
    print(f"Output folder: {args.output_folder}")
    
    # Process the PDF file
    process_pdf(args.input_path, args.output_folder)


if __name__ == "__main__":
    main()