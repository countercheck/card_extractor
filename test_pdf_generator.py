#!/usr/bin/env python3
"""
Create a test PDF with multiple pages and images for testing the PDF Image Extractor.
This script requires the ReportLab library, which can be installed with:
    pip install reportlab pillow
"""

import os
import sys
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import Image
from reportlab.lib.utils import ImageReader
from io import BytesIO
from PIL import Image as PILImage
import math


def create_simple_image(filename, size=(300, 300), color=(255, 0, 0)):
    """Create a simple colored square image and save it to disk."""
    img = PILImage.new('RGB', size, color=color)
    img.save(filename)
    return filename


def create_test_pdf(output_path):
    """
    Create a test PDF with multiple pages and various images.
    
    Args:
        output_path (str): Path where the PDF will be saved
    """
    # Create a canvas with letter size
    c = canvas.Canvas(output_path, pagesize=letter)
    width, height = letter
    
    # Create some temp images if they don't exist
    temp_dir = os.path.dirname(output_path)
    if not os.path.exists(temp_dir) and temp_dir:
        os.makedirs(temp_dir)
    
    red_img = create_simple_image(os.path.join(temp_dir, "red_square.png"), color=(255, 0, 0))
    blue_img = create_simple_image(os.path.join(temp_dir, "blue_square.png"), color=(0, 0, 255))
    green_img = create_simple_image(os.path.join(temp_dir, "green_square.png"), color=(0, 255, 0))
    
    # Page 1: Title page with a single image
    c.setFont("Helvetica-Bold", 24)
    c.drawCentredString(width/2, height - 2*inch, "Test PDF for Image Extraction")
    c.setFont("Helvetica", 16)
    c.drawCentredString(width/2, height - 3*inch, "Page 1: Single Image")
    
    # Add a red square image to page 1
    c.drawImage(red_img, width/2 - 1.5*inch, height/2 - 1.5*inch, 3*inch, 3*inch)
    
    c.showPage()  # End page 1

    # Page 2: Multiple images with different sizes
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width/2, height - 1*inch, "Page 2: Multiple Images with Different Sizes")
    
    # Add multiple images with different sizes
    c.drawImage(red_img, 1*inch, height - 3*inch, 2*inch, 2*inch)
    c.drawImage(blue_img, width - 3*inch, height - 3*inch, 2*inch, 2*inch)
    c.drawImage(green_img, width/2 - 1*inch, height/2 - 1*inch, 2*inch, 2*inch)
    
    c.showPage()  # End page 2

    # Page 3: Images at different positions
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width/2, height - 1*inch, "Page 3: Images at Different Positions")
    
    # Top left
    c.drawImage(red_img, 1*inch, height - 2*inch, 1*inch, 1*inch)
    
    # Top right
    c.drawImage(blue_img, width - 2*inch, height - 2*inch, 1*inch, 1*inch)
    
    # Bottom left
    c.drawImage(green_img, 1*inch, 1*inch, 1*inch, 1*inch)
    
    # Bottom right
    c.drawImage(red_img, width - 2*inch, 1*inch, 1*inch, 1*inch)
    
    # Center
    c.drawImage(blue_img, width/2 - 0.5*inch, height/2 - 0.5*inch, 1*inch, 1*inch)
    
    c.showPage()  # End page 3
    
    # Page 4: Overlapping images
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width/2, height - 1*inch, "Page 4: Overlapping Images")
    
    # Draw several overlapping images
    c.drawImage(red_img, width/2 - 1.5*inch, height/2 - 1.5*inch, 3*inch, 3*inch)
    c.drawImage(blue_img, width/2 - 1*inch, height/2 - 1*inch, 2*inch, 2*inch)
    c.drawImage(green_img, width/2 - 0.5*inch, height/2 - 0.5*inch, 1*inch, 1*inch)
    
    c.showPage()  # End page 4
    
    # Page 5: Random distribution of images
    c.setFont("Helvetica-Bold", 18)
    c.drawCentredString(width/2, height - 1*inch, "Page 5: Random Distribution")
    
    # Create a spiraling pattern of small images
    images = [red_img, blue_img, green_img]
    for i in range(10):
        angle = i * 36 * (math.pi / 180)  # 36 degrees in radians
        radius = i * 0.3 * inch
        x = width/2 + radius * math.cos(angle) - 0.25*inch
        y = height/2 + radius * math.sin(angle) - 0.25*inch
        c.drawImage(images[i % 3], x, y, 0.5*inch, 0.5*inch)
    
    c.showPage()  # End page 5
    
    # Save the PDF
    c.save()
    
    # Clean up temporary image files
    os.remove(red_img)
    os.remove(blue_img)
    os.remove(green_img)
    
    print(f"Test PDF created: {output_path}")
    print("The PDF contains 5 pages with various images in different sizes and positions.")


if __name__ == "__main__":
    # Determine output path
    if len(sys.argv) > 1:
        output_path = sys.argv[1]
    else:
        output_path = "./tests/pdfs/test_pdf_with_images.pdf"
    
    create_test_pdf(output_path)