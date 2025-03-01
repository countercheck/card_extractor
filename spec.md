# Developer-Ready Specification: PDF Image Extractor Command-Line Tool

## 1. Overview
The goal is to develop a command-line tool that extracts all distinct images (referred to as cards and tokens) from PDFs. The tool will support bulk extraction from multiple PDFs in a folder, with user-configurable options for output, format, and page selection. It should support macOS and Linux platforms.

## 2. Core Requirements

### Image Extraction:
- Extract all distinct images (of varying sizes and positions) from PDFs.
- Handle multiple images scattered across any part of a PDF page.
- No post-processing (such as resizing or cropping) is needed.

### File Naming Convention:
- Images should be named as `<source-document-name>-page-<page-number>-image-<image-number>.<format>`.
- Append a numerical suffix to avoid overwriting files if a file with the same name already exists.

### Output Structure:
- All extracted images should be saved in a single output folder specified by the user.

### Bulk Processing:
- The tool must support extracting images from multiple PDFs in a folder.
- It should provide a flag to scan subfolders recursively.

### Password-Protected PDFs:
- When encountering password-protected PDFs, prompt the user to enter a password for each file.

## 3. Command-Line Flags and Options
The following command-line flags and options will be supported:

### `--output-folder` / `-o` (Required):
- Specifies the folder where extracted images will be saved.
- Default: Current working directory if not provided.

### `--format` / `-f` (Optional, Default: png):
- Allows the user to specify the output image format (e.g., png, jpeg, bmp).

### `--pages` / `-p` (Optional):
- Specify the page(s) to extract images from. Accepts single page numbers (e.g., `--pages 2`), ranges (e.g., `--pages 1-3`), or comma-separated values (e.g., `--pages 1,5,8`).

### `--recursive` / `-r` (Optional):
- Enables recursive scanning of subfolders for PDFs.

## 4. Architecture and Technical Approach

### Programming Language:
The developer has the freedom to choose the programming language that best suits the requirements, such as Python (using libraries like PyPDF2, pdf2image, or fitz from PyMuPDF) or Go.

### Folder Traversal:
- For bulk processing, the tool will iterate through all files in the specified folder, and if the recursive flag is enabled, it will search through all subdirectories.

### PDF Processing:
- Open and scan each page of the PDF using an appropriate library to detect and extract images.
- Convert the images into the format specified by the user (default: PNG).

### Error Handling:
- If a PDF is unreadable (e.g., corrupted or malformed), log the error and skip to the next PDF.
- If an image extraction fails, log the error but continue with the next page or file.
- Password-protected PDFs will prompt the user for a password.

### Image Extraction:
- Use a library capable of detecting and extracting embedded images from PDFs (such as PyMuPDF).
- Save images to the output folder in the specified format.

## 5. Logging and Output

### CLI Logging:
- Output information to the command-line interface (no log file required).
- Log the name of each processed PDF and the dimensions of extracted images (in pixels).
- Log any encountered errors (e.g., unreadable files, failed image extraction).

## 6. Error Handling Strategies

### Unreadable PDFs:
- Skip any unreadable files (corrupted or unsupported formats) and log the failure.

### Password-Protected PDFs:
- When encountering a password-protected PDF, the tool will prompt the user for the password. If the password is incorrect or skipped, the file will be skipped, and the failure will be logged.

### File Overwrite Handling:
- Append a numerical suffix (e.g., image-1.png, image-2.png) to avoid overwriting files with the same name.

### Incomplete Extractions:
- If image extraction fails on any page or part of a page, log the failure but continue processing the rest of the document.

## 7. Testing Plan
To ensure the tool works reliably across different scenarios, the following test cases should be covered:

### Basic Functionality:
- Test extracting images from a single PDF with multiple pages.
- Verify that images are saved in the correct format and with the expected naming convention.

### Bulk Extraction:
- Test bulk extraction from multiple PDFs in a folder.
- Test recursive folder scanning to ensure images are correctly extracted from subfolders.

### Page Range Handling:
- Test extraction for specific pages, including single pages, ranges, and non-sequential pages.

### Password-Protected PDFs:
- Test with password-protected PDFs to ensure correct handling when the password is provided and when it's incorrect.

### Error Handling:
- Test with corrupted or unreadable PDFs to ensure they are skipped, and errors are logged.
- Test failed extractions (e.g., unsupported image formats or embedded content that cannot be extracted).

### File Overwriting:
- Test scenarios where files with the same name already exist in the output folder to ensure suffixes are correctly appended.

### Platform Compatibility:
- Test on both macOS and Linux to verify correct operation on supported platforms.