#!/bin/bash
# Script to run all tests in the tests directory regardless of naming convention

echo "Running all tests in the tests directory..."

# Run the tests with unittest discover
python -m unittest discover -s tests -p "*.py"

# Capture the exit code
EXIT_CODE=$?

# Output based on exit code
if [ $EXIT_CODE -eq 0 ]; then
    echo -e "\n✅ All tests passed!"
else
    echo -e "\n❌ Some tests failed. Exit code: $EXIT_CODE"
fi

# Return the exit code
exit $EXIT_CODE