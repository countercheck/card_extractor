#!/usr/bin/env python3
"""
PDF Image Extractor - A command-line tool for extracting images from PDF files.

This tool allows you to extract all images from PDF files with various options
for output folder, image format, page selection, and recursive directory scanning.
"""

import argparse
import os
import sys
import fitz  # PyMuPDF package
import numpy as np
import cv2
import tempfile
from PIL import Image


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
    
    # Optional format argument with choices
    parser.add_argument(
        "--format", "-f",
        choices=["png", "jpeg", "bmp"],
        default="png",
        help="Output image format (default: png)"
    )
    
    # Optional pages argument
    parser.add_argument(
        "--pages", "-p",
        help="Pages to extract images from (e.g., '1', '1-3', '1,5,8')"
    )
    
    # Optional recursive flag
    parser.add_argument(
        "--recursive", "-r",
        action="store_true",
        help="Recursively scan subfolders for PDF files"
    )
    
    # Parse and return the arguments
    return parser.parse_args()


def parse_pages(pages_string, total_pages):
    """
    Parse a pages string into a set of page numbers.
    
    Args:
        pages_string (str): String specifying pages (e.g., '1', '1-3', '1,5,8')
        total_pages (int): Total number of pages in the PDF
        
    Returns:
        set: Set of page numbers to process (0-based indices)
    """
    if not pages_string:
        # If no pages specified, return all pages
        return set(range(total_pages))
    
    pages_to_process = set()
    
    # Split by comma to handle comma-separated values
    for part in pages_string.split(','):
        # Handle page ranges (e.g., 1-3)
        if '-' in part:
            try:
                start, end = map(int, part.split('-'))
                # Convert to 0-based indexing and ensure within bounds
                start = max(1, start) - 1
                end = min(total_pages, end) - 1
                # Add all pages in the range
                pages_to_process.update(range(start, end + 1))
            except ValueError:
                print(f"Warning: Invalid page range '{part}', skipping")
        else:
            # Handle single page numbers
            try:
                page = int(part) - 1  # Convert to 0-based indexing
                if 0 <= page < total_pages:
                    pages_to_process.add(page)
                else:
                    print(f"Warning: Page {part} out of range, skipping")
            except ValueError:
                print(f"Warning: Invalid page number '{part}', skipping")
    
    return pages_to_process


def detect_and_extract_image_regions(image_path, min_area=1000):
    """
    Detect and extract distinct image regions from a rendered page using OpenCV.
    
    Args:
        image_path (str): Path to the rendered page image
        min_area (int): Minimum contour area to consider (filters out noise)
        
    Returns:
        list: List of extracted images as numpy arrays
    """
    # Read the image
    image = cv2.imread(image_path)
    if image is None:
        print(f"Error: Could not read image at {image_path}")
        return []
    
    # Get image dimensions
    height, width = image.shape[:2]
    
    # Convert to grayscale for processing
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Use Canny edge detection
    edges = cv2.Canny(blurred, 50, 150)
    
    # Dilate to close gaps in edges
    kernel = np.ones((5, 5), np.uint8)
    dilated = cv2.dilate(edges, kernel, iterations=2)
    
    # Find contours
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter contours by area to exclude small noise
    significant_contours = [cnt for cnt in contours if cv2.contourArea(cnt) > min_area]
    
    # Sort contours by area, largest first
    significant_contours.sort(key=cv2.contourArea, reverse=True)
    
    # Extract the image regions
    extracted_images = []
    
    for i, contour in enumerate(significant_contours):
        # Get bounding rectangle for the contour
        x, y, w, h = cv2.boundingRect(contour)
        
        # Add a small margin around the region (5% of width/height)
        margin_x = int(w * 0.05)
        margin_y = int(h * 0.05)
        
        # Ensure margins don't extend beyond image boundaries
        x1 = max(0, x - margin_x)
        y1 = max(0, y - margin_y)
        x2 = min(width, x + w + margin_x)
        y2 = min(height, y + h + margin_y)
        
        # Crop the region from the original image
        region = image[y1:y2, x1:x2]
        
        # Skip very small regions or those that are nearly the full page
        region_area = (x2 - x1) * (y2 - y1)
        page_area = width * height
        if region_area < min_area or region_area > page_area * 0.9:
            continue
        
        extracted_images.append(region)
    
    return extracted_images


def save_image(image_array, output_path, format="png"):
    """
    Save a numpy image array to disk.
    
    Args:
        image_array (numpy.ndarray): Image as a numpy array (BGR format from OpenCV)
        output_path (str): Path where to save the image
        format (str): Image format (png, jpeg, bmp)
    """
    # Convert BGR to RGB (OpenCV uses BGR, PIL uses RGB)
    image_rgb = cv2.cvtColor(image_array, cv2.COLOR_BGR2RGB)
    
    # Convert numpy array to PIL Image
    pil_image = Image.fromarray(image_rgb)
    
    # Save the image
    pil_image.save(output_path, format=format.upper())


def process_pdf(pdf_path, output_folder, output_format="png", pages_string=None):
    """
    Process a PDF file to extract images.
    
    Args:
        pdf_path (str): Path to the PDF file
        output_folder (str): Path to the output folder where images will be saved
        output_format (str): Format to save images in (png, jpeg, bmp)
        pages_string (str): String specifying which pages to process
    """
    try:
        # Create output directory if it doesn't exist
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            
        # Try to open the PDF document
        try:
            doc = fitz.open(pdf_path)
        except RuntimeError as e:
            # Check if this is a password-protected PDF
            if "password" in str(e).lower():
                password = input(f"PDF '{pdf_path}' is password-protected. Enter password: ")
                if not password:
                    print(f"No password provided, skipping '{pdf_path}'")
                    return
                try:
                    doc = fitz.open(pdf_path, password=password)
                except Exception:
                    print(f"Incorrect password, skipping '{pdf_path}'")
                    return
            else:
                raise
        
        print(f"Processing: {pdf_path}")
        
        # Get the source document name (without extension)
        source_doc_name = os.path.splitext(os.path.basename(pdf_path))[0]
        
        # Determine which pages to process
        pages_to_process = parse_pages(pages_string, len(doc))
        
        # Iterate through each page to process
        for page_idx in pages_to_process:
            page = doc[page_idx]
            page_num = page_idx + 1
            print(f"Processing page {page_num} of {len(doc)}")
            
            # First attempt - try using the standard extract_image approach
            image_list = page.get_images(full=True)
            
            # Track image count for this page
            img_count = 0
            extracted_any_images = False
            
            # Process all images if there are any detected
            if image_list:
                # Keep track of unique positions for images
                position_signatures = set()
                
                for img in image_list:
                    xref = img[0]
                    
                    # Create a position signature for this image instance
                    # Include all available transformation data
                    position_sig = '-'.join(str(x) for x in img)
                    
                    # Skip if we've seen this exact image with this transform before
                    if position_sig in position_signatures:
                        continue
                    
                    position_signatures.add(position_sig)
                    img_count += 1
                    
                    try:
                        # Extract the image
                        image_data = doc.extract_image(xref)
                        ext = image_data["ext"]
                        
                        # Construct output filename using required naming convention
                        base_filename = f"{source_doc_name}-page-{page_num}-image-{img_count}.{ext}"
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
                        
                        extracted_any_images = True
                        
                        # Print the image information
                        print(f"  Extracted image: {os.path.basename(output_path)}, "
                              f"Dimensions: {image_data['width']}x{image_data['height']}")
                            
                    except Exception as e:
                        print(f"  Error extracting image {img_count} (xref={xref}): {str(e)}")
            
            # If no images were successfully extracted using traditional methods,
            # fall back to rendering the page and using computer vision
            if not extracted_any_images:
                print(f"  No images extracted using standard method from page {page_num}")
                print(f"  Using computer vision to detect images on page {page_num}")
                
                # Create a temporary file to store the rendered page
                with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
                    temp_path = temp_file.name
                
                try:
                    # Render the page to a high-quality pixmap
                    zoom_factor = 2.0  # Higher zoom = better quality
                    mat = fitz.Matrix(zoom_factor, zoom_factor)
                    pix = page.get_pixmap(matrix=mat, alpha=False)
                    pix.save(temp_path)
                    
                    # Use computer vision to detect and extract image regions
                    extracted_regions = detect_and_extract_image_regions(temp_path)
                    
                    if not extracted_regions:
                        print(f"  No distinct image regions detected on page {page_num}")
                        # Save the whole page as a single image
                        region_count = 1
                        
                        # Construct output filename for the full page
                        page_image_name = f"{source_doc_name}-page-{page_num}-image-{region_count}.{output_format}"
                        page_image_path = os.path.join(output_folder, page_image_name)
                        
                        # Handle potential file overwrite
                        counter = 1
                        while os.path.exists(page_image_path):
                            filename_parts = os.path.splitext(page_image_name)
                            new_filename = f"{filename_parts[0]}_{counter}{filename_parts[1]}"
                            page_image_path = os.path.join(output_folder, new_filename)
                            counter += 1
                        
                        # Convert from PyMuPDF format to the requested format
                        # This is simple since we're just copying the file in this case
                        img = Image.open(temp_path)
                        img.save(page_image_path, format=output_format.upper())
                        
                        print(f"  Saved full page as: {os.path.basename(page_image_path)}, "
                              f"Dimensions: {pix.width}x{pix.height}")
                    else:
                        print(f"  Detected {len(extracted_regions)} distinct image regions on page {page_num}")
                        
                        # Save each detected region as a separate image
                        for i, region in enumerate(extracted_regions):
                            region_count = i + 1
                            
                            # Construct output filename
                            region_image_name = f"{source_doc_name}-page-{page_num}-image-{region_count}.{output_format}"
                            region_image_path = os.path.join(output_folder, region_image_name)
                            
                            # Handle potential file overwrite
                            counter = 1
                            while os.path.exists(region_image_path):
                                filename_parts = os.path.splitext(region_image_name)
                                new_filename = f"{filename_parts[0]}_{counter}{filename_parts[1]}"
                                region_image_path = os.path.join(output_folder, new_filename)
                                counter += 1
                            
                            # Save the cropped region
                            save_image(region, region_image_path, format=output_format)
                            
                            height, width = region.shape[:2]
                            print(f"  Extracted region: {os.path.basename(region_image_path)}, "
                                  f"Dimensions: {width}x{height}")
                finally:
                    # Clean up temporary file
                    if os.path.exists(temp_path):
                        os.unlink(temp_path)
        
        # Close the document
        doc.close()
        
    except FileNotFoundError:
        print(f"Error: PDF file not found: {pdf_path}")
    except fitz.FileDataError:
        print(f"Error: '{pdf_path}' is corrupted or not a valid PDF file")
    except Exception as e:
        print(f"Error processing PDF {pdf_path}: {str(e)}")


def process_directory(dir_path, output_folder, output_format="png", pages_string=None, recursive=False):
    """
    Process all PDF files in a directory.
    
    Args:
        dir_path (str): Path to the directory containing PDF files
        output_folder (str): Path to the output folder for extracted images
        output_format (str): Format to save images in (png, jpeg, bmp)
        pages_string (str): String specifying which pages to process
        recursive (bool): Whether to recursively scan subdirectories
    """
    # Use os.walk for recursive scanning or just os.listdir for non-recursive
    if recursive:
        for root, _, files in os.walk(dir_path):
            for file in files:
                if file.lower().endswith('.pdf'):
                    pdf_path = os.path.join(root, file)
                    process_pdf(pdf_path, output_folder, output_format, pages_string)
    else:
        for file in os.listdir(dir_path):
            if file.lower().endswith('.pdf'):
                pdf_path = os.path.join(dir_path, file)
                process_pdf(pdf_path, output_folder, output_format, pages_string)


def main():
    """
    Main function that serves as the entry point for the application.
    """
    # Parse command-line arguments
    args = parse_args()
    
    # Print parsed arguments (for debugging/verification)
    print(f"Input path: {args.input_path}")
    print(f"Output folder: {args.output_folder}")
    print(f"Format: {args.format}")
    if args.pages:
        print(f"Pages: {args.pages}")
    if args.recursive:
        print("Recursive scanning enabled")
    
    # Check if input path is a file or directory
    if os.path.isfile(args.input_path):
        # Process a single PDF file
        process_pdf(args.input_path, args.output_folder, args.format, args.pages)
    elif os.path.isdir(args.input_path):
        # Process a directory of PDF files
        process_directory(args.input_path, args.output_folder, args.format, args.pages, args.recursive)
    else:
        print(f"Error: '{args.input_path}' is not a valid file or directory")
        sys.exit(1)


if __name__ == "__main__":
    main()