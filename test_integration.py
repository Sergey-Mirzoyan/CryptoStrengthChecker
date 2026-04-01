import unittest
import sys
import os

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)
print(f"Added {current_dir} to sys.path")

class TestIntegration(unittest.TestCase):
    def test_imports(self):
        print("Testing imports...")
        try:
            import stats.sp800_22_tests.sp800_22_tests
            print("Imported module successfully")
            from stats.sp800_22_tests.sp800_22_tests import runrun
            print("Imported runrun successfully")
            
            from stats.DIEHARD.dieharder import run_dieharder
            print("Imported dieharder successfully")
            
            import analysis
            import avalanche
            print("Imported local modules successfully")
            
        except ImportError as e:
            print(f"Import Error Details: {e}")
            self.fail(f"Import failed: {e}")
        except Exception as e:
            print(f"Other Error: {e}")
            self.fail(f"Other error: {e}")

if __name__ == '__main__':
    unittest.main()
