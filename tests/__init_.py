"""
Unit tests for the package initialization.
"""

import unittest
import sys
import os

# Add the parent directory to the path so we can import the package
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestPackageInit(unittest.TestCase):
    """Tests for the package initialization."""
    
    def test_version(self):
        """Test that the package has a version number."""
        import src.card_extractor
        self.assertTrue(hasattr(src.card_extractor, '__version__'))
        self.assertEqual(src.card_extractor.__version__, "0.1.0")
    
    def test_direct_imports(self):
        """Test that the key functions are directly importable from the package."""
        from src.card_extractor import process_pdf, main
        self.assertTrue(callable(process_pdf))
        self.assertTrue(callable(main))
    
    def test_all_exports(self):
        """Test that __all__ contains the expected functions."""
        import src.card_extractor
        self.assertTrue(hasattr(src.card_extractor, '__all__'))
        self.assertIn('process_pdf', src.card_extractor.__all__)
        self.assertIn('main', src.card_extractor.__all__) 
    
    def test_wildcard_import(self):
        """Test that wildcard import works correctly."""
        # We need to use exec here because * imports aren't allowed in functions
        namespace = {}
        exec('from src.card_extractor import *', namespace)
        
        self.assertIn('process_pdf', namespace)
        self.assertIn('main', namespace)
        self.assertTrue(callable(namespace['process_pdf']))
        self.assertTrue(callable(namespace['main']))


if __name__ == '__main__':
    unittest.main()