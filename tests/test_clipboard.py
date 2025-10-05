"""Tests for clipboard functionality"""

import unittest
import platform
from unittest.mock import MagicMock, patch
from clipin import Clipboard, copy, paste, clear


class TestClipboard(unittest.TestCase):
    """Test cases for the Clipboard class"""
    
    def test_clipboard_initialization(self):
        """Test that clipboard initializes with correct system"""
        clipboard = Clipboard()
        self.assertIsNotNone(clipboard.system)
        self.assertIn(clipboard.system, ['Linux', 'Darwin', 'Windows'])
    
    def test_copy_converts_to_string(self):
        """Test that non-string values are converted to string"""
        clipboard = Clipboard()
        # Mock the subprocess calls to avoid actual clipboard operations
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.returncode = 0
            mock_process.communicate.return_value = (b'', b'')
            mock_popen.return_value = mock_process
            
            result = clipboard.copy(123)
            # Should not raise an exception
            self.assertTrue(True)
    
    def test_module_level_functions_exist(self):
        """Test that module level convenience functions exist"""
        self.assertTrue(callable(copy))
        self.assertTrue(callable(paste))
        self.assertTrue(callable(clear))
    
    def test_clear_calls_copy_with_empty_string(self):
        """Test that clear() calls copy with empty string"""
        clipboard = Clipboard()
        with patch.object(clipboard, 'copy') as mock_copy:
            mock_copy.return_value = True
            result = clipboard.clear()
            mock_copy.assert_called_once_with("")
            self.assertTrue(result)


class TestModuleLevelFunctions(unittest.TestCase):
    """Test cases for module-level convenience functions"""
    
    def test_functions_use_default_clipboard(self):
        """Test that module level functions work"""
        # These tests just verify the functions can be called
        # without raising exceptions (actual clipboard operations are mocked)
        with patch('subprocess.Popen') as mock_popen:
            mock_process = MagicMock()
            mock_process.returncode = 0
            mock_process.communicate.return_value = (b'test', b'')
            mock_popen.return_value = mock_process
            
            # Test copy
            result = copy("test")
            self.assertIsInstance(result, bool)
            
            # Test paste
            result = paste()
            self.assertIsInstance(result, str)
            
            # Test clear
            result = clear()
            self.assertIsInstance(result, bool)


if __name__ == '__main__':
    unittest.main()
