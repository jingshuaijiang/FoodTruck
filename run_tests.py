#!/usr/bin/env python3
"""
Test runner script for SF Food Truck Finder API
"""

import subprocess
import sys
import os

def run_tests():
    """Run all tests with pytest"""
    print("🚀 Running SF Food Truck Finder API Tests...")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists('tests'):
        print("❌ Error: 'tests' directory not found!")
        print("Make sure you're running this from the project root directory.")
        sys.exit(1)
    
    # Run tests
    try:
        result = subprocess.run([
            'python', '-m', 'pytest', 
            'tests/', 
            '-v', 
            '--tb=short',
            '--cov=app',
            '--cov-report=term-missing'
        ], capture_output=False, text=True)
        
        if result.returncode == 0:
            print("\n✅ All tests passed!")
        else:
            print(f"\n❌ Some tests failed (exit code: {result.returncode})")
            sys.exit(result.returncode)
            
    except FileNotFoundError:
        print("❌ Error: pytest not found!")
        print("Please install pytest: pip install pytest pytest-cov")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        sys.exit(1)

def run_specific_test(test_path):
    """Run a specific test file or test function"""
    print(f"🧪 Running specific test: {test_path}")
    print("=" * 50)
    
    try:
        result = subprocess.run([
            'python', '-m', 'pytest', 
            test_path,
            '-v', 
            '--tb=short'
        ], capture_output=False, text=True)
        
        if result.returncode == 0:
            print("\n✅ Test passed!")
        else:
            print(f"\n❌ Test failed (exit code: {result.returncode})")
            sys.exit(result.returncode)
            
    except Exception as e:
        print(f"❌ Error running test: {e}")
        sys.exit(1)

def show_help():
    """Show help information"""
    print("SF Food Truck Finder API Test Runner")
    print("=" * 40)
    print("Usage:")
    print("  python run_tests.py              # Run all tests")
    print("  python run_tests.py <test_path>  # Run specific test")
    print("")
    print("Examples:")
    print("  python run_tests.py")
    print("  python run_tests.py tests/test_models.py")
    print("  python run_tests.py tests/test_models.py::TestSearchRequest::test_valid_name_search")
    print("")
    print("Available test files:")
    print("  - tests/test_models.py      # Pydantic models")
    print("  - tests/test_utils.py       # Utility functions")
    print("  - tests/test_dataloader.py  # Data loader")
    print("  - tests/test_api.py         # API endpoints")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] in ['-h', '--help']:
            show_help()
        else:
            run_specific_test(sys.argv[1])
    else:
        run_tests()


