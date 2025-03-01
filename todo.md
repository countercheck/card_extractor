# PDF Image Extractor Implementation Todo List

## Phase 1: Project Setup and Basic PDF Processing

### Project Initialization
- [x] Create new project directory "pdf_image_extractor" (created as "card-extractor" instead)
- [x] Initialize pyproject.toml using poetry
- [x] Add PyMuPDF (fitz) as a project dependency
- [x] Set up proper Python package structure
- [x] Create minimal `__init__.py` with version info (`__version__ = "0.1.0"`)
- [x] Create main.py entry point file
- [x] Create tests directory

### Basic Argument Parsing
- [x] Implement argparse in main.py
- [x] Add required --output-folder (-o) argument
- [x] Add helpful error message if output folder not provided
- [x] Add code to print parsed arguments to console

### PDF Loading and Page Iteration
- [x] Create process_pdf(pdf_path, output_folder) function
- [x] Implement PDF opening with fitz.open()
- [x] Add page iteration loop
- [x] Add file not found error handling
- [x] Create test PDF file with multiple pages and images

### Basic Unit Tests
- [x] Create tests/test_main.py (created as tests/main.py)
- [x] Implement test_argument_parsing
- [x] Implement test_process_pdf_file_not_found
- [x] Implement test_process_pdf_page_iteration

## Phase 2: Image Extraction and File Handling

### Basic Image Extraction
- [ ] Add image extraction with page.get_images(full=True)
- [ ] Implement iteration through images on each page
- [ ] Extract image data with doc.extract_image(image[0])
- [ ] Add code to print image extension

### Image Saving
- [ ] Create output file path constructor using PDF filename, page number, image number
- [ ] Use os.path.join for platform-independent paths
- [ ] Add code to create output directory if it doesn't exist
- [ ] Implement image data writing to file

### File Overwrite Handling
- [ ] Add check for existing files with os.path.exists()
- [ ] Implement numerical suffix (_1, _2, etc.) for duplicate filenames
- [ ] Add loop to find unique filename

### Unit Tests for Image Extraction
- [ ] Implement test_image_extraction
- [ ] Implement test_image_saving with tempfile module
- [ ] Implement test_file_overwrite

## Phase 3: Command-Line Options and Bulk Processing

### Additional Command-Line Options
- [ ] Add --format (-f) option with default "png"
- [ ] Restrict format choices to png, jpeg, bmp
- [ ] Add --pages (-p) option with support for single pages, ranges, and comma-separated values
- [ ] Create parse_pages helper function
- [ ] Add --recursive (-r) flag with action='store_true'

### Unit Tests for Command-Line Options
- [ ] Implement test_format_option
- [ ] Implement test_pages_option
- [ ] Implement test_parse_pages
- [ ] Implement test_recursive_flag

### Bulk Processing and Directory Traversal
- [x] Modify main function to accept file or directory path
- [ ] Add os.listdir to get files in directory
- [ ] Add filter for PDF files only
- [ ] Implement process_pdf call for each PDF
- [ ] Add recursive directory traversal with os.walk when --recursive is set

### Unit Tests for Bulk Processing
- [ ] Implement test_process_directory
- [ ] Implement test_process_directory_recursive
- [ ] Implement test_process_directory_no_pdfs

## Phase 4: Password Protection and Logging

### Password Protection Handling
- [x] Add try/except block around fitz.open()
- [ ] Catch RuntimeError and check for "password" in message
- [ ] Add prompt for password with input()
- [ ] Implement retry with fitz.open(pdf_path, password=user_provided_password)
- [ ] Add error handling for incorrect passwords

### Logging Implementation
- [ ] Add logging for file processing: print(f"Processing: {pdf_path}")
- [ ] Add logging for extracted images with dimensions
- [ ] Implement error handling for corrupted files (fitz.FileDataError)
- [x] Add generic exception handling

### Unit Tests for Password Protection and Logging
- [ ] Implement test_password_protected_pdf_correct_password
- [ ] Implement test_password_protected_pdf_incorrect_password
- [ ] Implement test_password_protected_pdf_no_password
- [ ] Implement test_unreadable_pdf
- [ ] Implement test_generic_exception
- [ ] Implement test_logging_output

## Phase 5: Package Finalization

### Package Structure Completion
- [x] Review codebase for key functions to expose
- [x] Update `__init__.py` with proper imports
- [x] Define `__all__` list
- [x] Add package docstring

### Entry Point Configuration
- [x] Update pyproject.toml with console script entry point
- [x] Configure entry point to call main function

### Documentation
- [ ] Create README.md (referenced in pyproject.toml but content not provided)
- [ ] Add installation instructions
- [ ] Document all command-line options
- [ ] Include usage examples

## Final Review

### Quality Assurance
- [ ] Run full test suite and ensure all tests pass
- [ ] Check test coverage
- [ ] Run code through linter (flake8 or pylint)
- [x] Add docstrings to all functions and classes

### Package Testing
- [ ] Test installation from source
- [ ] Verify command-line entry point works
- [ ] Test with various PDF types (large, small, with/without images)
- [ ] Check handling of edge cases