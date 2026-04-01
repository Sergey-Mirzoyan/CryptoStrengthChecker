import sys
import os

# Add current directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("Sys path:", sys.path)

try:
    import stats
    print("Imported stats:", stats)
except ImportError as e:
    print("Failed to import stats:", e)

try:
    import stats.sp800_22_tests
    print("Imported stats.sp800_22_tests:", stats.sp800_22_tests)
except ImportError as e:
    print("Failed to import stats.sp800_22_tests:", e)

try:
    import stats.sp800_22_tests.sp800_22_tests
    print("Imported stats.sp800_22_tests.sp800_22_tests:", stats.sp800_22_tests.sp800_22_tests)
except ImportError as e:
    print("Failed to import stats.sp800_22_tests.sp800_22_tests:", e)
