# PDF Image Extractor Project Implementation Plan

## Phase 1: Project Setup and Basic PDF Processing

### Chunk 1.1: Project Initialization and Single File Processing

#### Step 1.1.1: Project Setup & Dependency Management
- Create a new project directory
- Initialize a pyproject.toml file using poetry (Or a requirements.txt if you aren't using poetry)
- Add PyMuPDF (fitz) as a project dependency
- Create a proper Python package structure with `__init__.py`
- Create a main.py file - the entry point of the application
- Create a tests directory for test files

**Task:**
Create a new Python project named "pdf_image_extractor" using Poetry. Set up a proper Python package structure with a directory called "pdf_image_extractor" containing an `__init__.py` file. The project should have a 'main.py' file which will serve as the command-line entry point. It should also have a 'tests' directory. Add PyMuPDF (also known as 'fitz') as a project dependency. Output only the `pyproject.toml` file's contents. Do not generate any code yet.

#### Step 1.1.1b: Set Up Package Structure with `__init__.py`
- Create a minimal `__init__.py` file in the pdf_image_extractor package directory
- Define version information
- Set up imports for any functions that should be accessible at the package level

**Task:**
Create an `__init__.py` file in the pdf_image_extractor package directory. Include version information (`__version__ = "0.1.0"`) and set up the file structure to properly identify the directory as a Python package. For now, keep it minimal, but structure it so that later you can expose key functions from main.py at the package level.

#### Step 1.1.2: Basic Argument Parsing
- Implement argument parsing in main.py to accept the input PDF path and output folder
- For now, only require the --output-folder (-o) argument. Make it required
- Use the argparse module

**Task:**
Extend 'main.py' to use the 'argparse' module to accept a required command-line argument: '--output-folder' (or '-o'), which specifies the output directory for the extracted images. If the argument is not provided, print a helpful error message and exit. Do not process any PDFs yet. Print the parsed arguments to standard output. Do not create or use a test.

#### Step 1.1.3: PDF Loading and Page Iteration
- In main.py, add a function process_pdf(pdf_path, output_folder) that takes the PDF path and output folder as arguments
- Inside process_pdf, open the PDF using fitz.open()
- Iterate through each page of the PDF using a for loop and doc.pages()
- For now, simply print the page number inside the loop
- Call process_pdf from the main execution block, passing in the provided output folder and a hardcoded path to a test PDF (create a simple one with at least two pages and a couple of images for this)

**Task:**
Extend 'main.py' to include a function called `process_pdf(pdf_path, output_folder)`. This function should open the specified PDF file using `fitz.open()`, iterate through each page, and print the page number to the console. Call this function from the main execution block of your script, passing a *hardcoded path to a sample PDF* (which you should create separately for testing) and the output folder obtained from argparse. Include error handling for file not found, and print a useful error message.

#### Step 1.1.4: Basic Unit Tests
- Create a test file tests/test_main.py
- Write a test case test_argument_parsing to verify that the argument parsing works correctly, including checking for the required -o argument. Use unittest.mock.patch to simulate command-line arguments
- Write a test case test_process_pdf_file_not_found that uses unittest.mock.patch('builtins.print') to assert that the correct error message is printed if a non-existent PDF file is provided
- Write a test case test_process_pdf_page_iteration to confirm the page iteration logic, again use unittest.mock

**Task:**
Create a test file 'tests/test_main.py'. Write unit tests using the 'unittest' framework and mocking. The tests should include:
1. `test_argument_parsing`: Verify that the argparse configuration correctly handles the required '--output-folder' argument, both when it's present and when it's missing. Use `unittest.mock.patch` to simulate command-line arguments.
2. `test_process_pdf_file_not_found`: Assert that the correct error message is printed if a non-existent PDF is provided to `process_pdf`. Use `unittest.mock.patch('builtins.print')` and assert the error message.
3. `test_process_pdf_page_iteration`: Verify that process_pdf iterates of the correct number of pages for a *mocked* PDF. Use unittest.mock to mock the `fitz.open()` method and have it return a mock Document object with a specified number of pages.

## Phase 2: Image Extraction and File Handling

### Chunk 2.1: Basic Image Extraction

#### Step 2.1.1: Image Extraction Logic
- Inside the process_pdf function, within the page iteration loop, use page.get_images(full=True) to get a list of images on the current page
- Iterate through the list of images
- For each image, extract the raw image data using doc.extract_image(image[0]). The image variable is a list, and the xref is at index 0
- For now, simply print the image extension (e.g., "png", "jpeg")

**Task:**
Modify the `process_pdf` function in 'main.py'. Within the page iteration loop, use `page.get_images(full=True)` to retrieve a list of images on the current page. Iterate through this list. For each image, use `doc.extract_image(image[0])` to extract the image data (where `image[0]` is the xref). Print the image extension (e.g., 'png', 'jpeg') to the console. Do not save the image to disk yet.

#### Step 2.1.2: Image Saving
- Construct the output file path using the PDF filename, page number, image number, and image extension
- Use the format: <source-document-name>-page-<page-number>-image-<image-number>.<format>
- Use os.path.join to create paths in a platform-independent way
- Get the filename with os.path.splitext(os.path.basename(pdf_path))[0]
- Write the image data to the constructed file path using open(..., "wb") and file.write(image_data["image"])

**Task:**
Modify the `process_pdf` function in 'main.py'. Inside the image iteration loop, construct the output file path for each extracted image. Use the format: `<source-document-name>-page-<page-number>-image-<image-number>.<format>`. Obtain the source document name using `os.path.splitext(os.path.basename(pdf_path))[0]`. Use `os.path.join` to assemble the file path. Write the image data to this file path using `open(..., 'wb')` and `file.write(image_data['image'])`, where `image_data` is the dictionary returned by `doc.extract_image`. Create the output directory if it does not exist.

#### Step 2.1.3: File Overwrite Handling
- Before saving the image, check if a file with the same name already exists using os.path.exists()
- If the file exists, append a numerical suffix _1, _2, etc., to the filename before the extension until a unique filename is found

**Task:**
Modify the `process_pdf` function in `main.py` to handle potential file overwrites. Before saving an image, check if a file with the intended name already exists using `os.path.exists()`. If it does, append a numerical suffix (e.g., '_1', '_2', etc.) to the filename *before the extension* until a unique filename is found.

#### Step 2.1.4: Unit Tests for Image Extraction and Saving
- Add tests to tests/test_main.py:
  - test_image_extraction: Mock fitz.open and page.get_images to return a mock PDF and images. Verify that doc.extract_image is called with the correct arguments. Assert image is written
  - test_image_saving: Test the image saving functionality. Use a temporary directory (using the tempfile module) as the output folder. Assert that the image files are created with the correct names and in the correct format
  - test_file_overwrite: Test the file overwrite handling. Create a dummy file in the temporary output directory, and then run the extraction. Assert that the extracted image is saved with a numerical suffix

**Task:**
Extend 'tests/test_main.py' with the following unit tests:
1. `test_image_extraction`: Mock `fitz.open` and related methods to simulate a PDF with images. Verify that `doc.extract_image` is called with the expected xref values. Assert the extracted file is written.
2. `test_image_saving`: Use a temporary directory (created using the `tempfile` module) as the output. Mock the necessary fitz methods. Assert that the image files are created with the correct names (using the defined naming convention) in the temporary directory.
3. `test_file_overwrite`: Similar to `test_image_saving`, but create a dummy file in the temporary directory with the same name as an expected extracted image. Assert that the extracted image is saved with a numerical suffix appended to its name to avoid overwriting.

## Phase 3: Command-Line Options and Bulk Processing

### Chunk 3.1: Adding Command-Line Options

#### Step 3.1.1: Format Option
- Add a --format (-f) option to argparse in main.py
- Set the default value to "png"
- Allow only "png", "jpeg", and "bmp" as valid choices. Use choices=['png', 'jpeg', 'bmp']
- In process_pdf, use this format when saving the image

**Task:**
Modify 'main.py' to add a '--format' ('-f') command-line option using 'argparse'. This option should specify the desired output image format. Set the default value to 'png'. Restrict the allowed values to 'png', 'jpeg', and 'bmp' using the `choices` argument in `add_argument`. Use this format when saving the extracted images in the `process_pdf` function.

#### Step 3.1.2: Pages Option
- Add a --pages (-p) option to argparse
- This option should accept:
  - A single page number (e.g., 2)
  - A range of pages (e.g., 1-3)
  - Comma-separated page numbers (e.g., 1,5,8)
- If not provided, process all pages
- Create a helper function parse_pages to handle the parsing of the pages string. This should return a set of integers representing the page numbers to process
- In process_pdf, use this set to determine which pages to process

**Task:**
Modify 'main.py' to add a '--pages' ('-p') command-line option. This option allows the user to specify which pages to process. It should accept a single page number, a range of pages (e.g., '1-3'), or a comma-separated list of page numbers (e.g., '1,5,8'). If the option is not provided, process all pages. Create a helper function `parse_pages(pages_string, total_pages)` that takes the pages string and the total number of pages in the document as input. This function should parse the string and return a set of integers representing the page numbers to process. Handle invalid input gracefully (e.g., non-numeric values, ranges exceeding the total pages). In `process_pdf`, use the result of `parse_pages` to process only the specified pages.

#### Step 3.1.3 Recursive Option
- Add --recursive (-r) flag using action='store_true'

**Task:**
Modify 'main.py' to add a '--recursive' ('-r') command-line option. Use `action='store_true'` so that the option acts as a flag (present or absent). Do not implement the recursive functionality yet, just add the argument parsing.

#### Step 3.1.4: Unit Tests for Command-line Options
- Add tests to tests/test_main.py to verify the new command-line options:
  - test_format_option: Test the --format option, including the default value and valid/invalid choices
  - test_pages_option: Test the --pages option with various inputs (single page, range, comma-separated, and no input)
  - test_parse_pages: Thoroughly test the parse_pages helper function with various valid and invalid inputs
  - test_recursive_flag: Test that the --recursive flag is correctly parsed

**Task:**
Extend 'tests/test_main.py' with the following unit tests:
1. `test_format_option`: Verify that the '--format' option correctly handles the default value ('png'), valid choices ('png', 'jpeg', 'bmp'), and invalid choices.
2. `test_pages_option`: Test the '--pages' option with various inputs: a single page, a range, a comma-separated list, and no input (to test the default behavior of processing all pages).
3. `test_parse_pages`: Create comprehensive tests for the `parse_pages` function. Test cases should include valid single pages, ranges, comma-separated lists, empty input, and invalid input (e.g., non-numeric values, out-of-range values).
4. `test_recursive_flag`: Verify that the `--recursive` flag is parsed correctly (both when present and when absent).

### Chunk 3.2: Bulk Processing and Directory Traversal

#### Step 3.2.1: Directory Handling
- Modify the main function to accept either a file path or a directory path as input
- If the input is a directory, use os.listdir (or os.walk for recursive) to get a list of files
- Filter the list to include only PDF files (using os.path.splitext and checking for .pdf)
- Call process_pdf for each PDF file found

**Task:**
Modify 'main.py' so that it can accept either a single PDF file path *or* a directory path as input (still controlled by the '-o' argument for output). If a directory is provided, use `os.listdir` to get a list of files within that directory. Filter this list to include only files with a '.pdf' extension (case-insensitively). Call the `process_pdf` function for each identified PDF file. Do not implement recursive processing yet.

#### Step 3.2.2: Recursive Directory Traversal
- If the --recursive flag is set, use os.walk to traverse the directory and its subdirectories
- Process PDF files found in all subdirectories

**Task:**
Modify 'main.py' to implement recursive directory traversal when the '--recursive' ('-r') flag is set. Use `os.walk` to traverse the input directory and all its subdirectories. Process all PDF files found during the traversal.

#### Step 3.2.3: Unit Tests for Bulk Processing
- Create tests for tests/test_main.py:
  - test_process_directory: Create a temporary directory structure with a few PDF files (some with images, some empty) and subdirectories. Verify the correct number of pdfs are processed
  - test_process_directory_recursive: Similar to test_process_directory, but with nested subdirectories and PDFs, and with the recursive flag enabled. Verify the correct number of pdfs are processed
  - test_process_directory_no_pdfs: Test with a directory containing no PDF files. Assert the behavior

**Task:**
Extend 'tests/test_main.py' with the following unit tests:
1. `test_process_directory`: Create a temporary directory structure containing a few PDF files (some with images and some possibly empty). Test the processing of this directory (without recursion) and verify that `process_pdf` is called the correct number of times.
2. `test_process_directory_recursive`: Similar to `test_process_directory`, but create a directory structure with nested subdirectories, each containing some PDF files. Test with the '--recursive' flag enabled and verify that `process_pdf` is called for all PDF files in all subdirectories.
3. `test_process_directory_no_pdfs`: Create a temporary directory containing no PDF files. Test the behavior when processing this directory and assert appropriate behavior.

## Phase 4: Password Protection and Logging

### Chunk 4.1: Password-Protected PDFs and Logging

#### Step 4.1.1: Password Prompt
- Modify the process_pdf function
- Wrap the doc = fitz.open(pdf_path) call in a try...except block
- Catch RuntimeError exceptions
- Check if the exception message indicates a password-protected PDF (the message will contain "password")
- If it's password-protected, prompt the user for a password using input()
- Attempt to open the PDF again using fitz.open(pdf_path, password=user_provided_password)
- If the password is correct, proceed with processing. If incorrect or no password provided, log an error and skip the file

**Task:**
Modify the `process_pdf` function in 'main.py' to handle password-protected PDFs. Wrap the `fitz.open(pdf_path)` call in a `try...except` block. Catch `RuntimeError` exceptions. If the exception message indicates that the PDF is password-protected (check if the message contains "password"), prompt the user for a password using `input()`. Attempt to reopen the PDF using `fitz.open(pdf_path, password=user_provided_password)`. If the password is correct (no exception is raised), proceed with processing. If it's incorrect or no password is provided, print an error message to standard output indicating that the file was skipped due to incorrect or missing password, and return from the function without processing the file.

#### Step 4.1.2: Logging of Processed Files and Image Dimensions
- Inside process_pdf, after successfully opening the PDF (and handling any passwords), log the filename being processed using print(f"Processing: {pdf_path}")
- Inside the image extraction loop, after extracting an image, log the dimensions: print(f" Extracted image: {image_filename}, Dimensions: {image_data['width']}x{image_data['height']}")

**Task:**
Modify the `process_pdf` function in 'main.py' to include logging. After successfully opening the PDF (and handling any password attempts), print a message to standard output indicating which file is being processed: `print(f"Processing: {pdf_path}")`. Inside the image extraction loop, after successfully extracting and saving an image, print a message indicating the filename of the extracted image and its dimensions: `print(f"  Extracted image: {image_filename}, Dimensions: {image_data['width']}x{image_data['height']}")`.

#### Step 4.1.3: Error Handling and Logging for Unreadable PDFs
- In the process_pdf function, add more specific error handling within the try...except block:
  - Catch fitz.FileDataError: This indicates a problem with the file data itself (corrupted, etc.). Log an error and skip the file
  - Catch other Exception types as a general catch-all. Log the error and skip the file

**Task:**
Modify the `process_pdf` function in 'main.py' to improve error handling. Within the `try...except` block around `fitz.open`, add more specific exception handling:
1. Catch `fitz.FileDataError`: This indicates a problem with the PDF file data (e.g., corrupted file). Print an error message to standard output indicating that the file is corrupted or unreadable and that it will be skipped.
2. Catch any other `Exception` as a general catch-all. Print a generic error message to standard output, including the exception details, indicating that an unexpected error occurred and the file will be skipped.
In both error cases, ensure that the function returns without further processing of the problematic file.

#### Step 4.1.4: Unit Tests for Password Protection and Logging
- Add to tests/test_main.py:
  - test_password_protected_pdf_correct_password: Mock fitz.open and input to simulate a password-protected PDF and provide the correct password. Assert that processing continues
  - test_password_protected_pdf_incorrect_password: Mock fitz.open and input to simulate an incorrect password. Assert that the file is skipped
  - test_password_protected_pdf_no_password: Mock fitz.open and input to simulate no password being entered. Assert that the file is skipped
  - test_unreadable_pdf: Mock fitz.open to raise a fitz.FileDataError. Assert that the appropriate error message is logged and the file is skipped
  - test_generic_exception: Mock a generic exception during PDF processing. Assert that it's handled and logged
  - test_logging_output: Capture standard output (using io.StringIO and contextlib.redirect_stdout) to verify the logging messages for file processing and image extraction

**Task:**
Extend 'tests/test_main.py' with the following unit tests:
1. `test_password_protected_pdf_correct_password`: Mock `fitz.open` to raise a `RuntimeError` indicating password protection. Mock `input` to return a valid password. Assert that `fitz.open` is called again with the password and that processing continues (you can mock subsequent calls to simulate successful extraction).
2. `test_password_protected_pdf_incorrect_password`: Similar to the above, but mock `input` to return an incorrect password. Assert that processing is skipped after the password attempt (and the appropriate error message is printed).
3. `test_password_protected_pdf_no_password`: Simulate a password-protected PDF, but mock `input` to return an empty string (or simulate the user pressing Enter without entering a password). Assert that processing is skipped.
4. `test_unreadable_pdf`: Mock `fitz.open` to raise a `fitz.FileDataError`. Assert that the appropriate error message is printed and that the file is skipped.
5. `test_generic_exception`: Mock `fitz.open` (or another part of the processing) to raise a generic `Exception`. Assert that a general error message is printed and that the file is skipped.
6. `test_logging_output`: Use `io.StringIO` and `contextlib.redirect_stdout` to capture the standard output during a successful PDF processing run (with mocked PDF and images). Assert that the expected logging messages ("Processing: ...", "Extracted image: ...") are present in the captured output.

## Phase 5: Package Finalization

### Chunk 5.1: Package Structure and Distribution

#### Step 5.1.1: Update `__init__.py` with Proper Exports
- Review the codebase and identify key functions and classes to expose at the package level
- Update the `__init__.py` file to import and expose these components
- Consider using `__all__` to explicitly define public exports

**Task:**
Update the `__init__.py` file to properly expose the main functionality of the package. Import and re-export key functions from main.py that users might want to access programmatically. Use `__all__` to explicitly define what gets imported with `from pdf_image_extractor import *`. Include a docstring that explains the package's purpose.

#### Step 5.1.2: Command-Line Entry Point
- Update pyproject.toml to define a console script entry point
- Configure the entry point to call the main function in main.py

**Task:**
Modify the pyproject.toml file to define a console script entry point for the package. The entry point should be named 'pdf-image-extractor' and should call the main function in main.py. This will allow users to run the tool directly from the command line after installation without having to invoke Python explicitly.

#### Step 5.1.3: Project Documentation
- Create a README.md file with installation and usage instructions
- Document all command-line options
- Include examples for common use cases

**Task:**
Create a README.md file for the project. Include sections for: introduction/overview, installation instructions (both via pip/poetry and from source), usage instructions with examples of all command-line options, and a section on contributing to the project. Make sure to document all the command-line options thoroughly.

## Final Review and Considerations

- **Test Coverage**: The test suite should now have good coverage, testing various scenarios, including edge cases and error conditions.
- **Code Style**: Ensure the code follows PEP 8 guidelines. Use a linter like flake8 or pylint.
- **Documentation**: Add docstrings to all functions and classes.
- **Modularity**: The code is reasonably modular, with process_pdf handling individual files and the main section handling argument parsing and directory traversal. This is good for maintainability and future extensions.
- **Efficiency**: For very large PDFs or directories, consider adding progress indicators.
- **Package Structure**: Ensure the package structure follows Python best practices, with proper use of `__init__.py` and clear separation of concerns.
- **Installation Testing**: Test installation from both source and package repositories to ensure all dependencies are correctly specified.