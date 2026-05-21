import sys
import os
import tempfile
from io import StringIO
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from generators.game_of_life import GameOfLifePRNG
from stats.sp800_22_tests.sp800_22_tests import runrun

mass_length = 20000
gen = GameOfLifePRNG(width=50, height=max(20, mass_length//50 + 1), seed=42, boundary_mode='toroid')
bit_string, _ = gen.generate(10, extract_mode='ternary')
bit_string = bit_string[:mass_length]
print("Ternary Generated length:", len(bit_string))
print("Zeros:", bit_string.count('0'), "Ones:", bit_string.count('1'))

with tempfile.NamedTemporaryFile(mode='w+', delete=False) as tmp:
    tmp.write(bit_string)
    tmp_path = tmp.name

try:
    old_stdout = sys.stdout
    sys.stdout = mystdout = StringIO()
    runrun(tmp_path)
    sys.stdout = old_stdout
    nist_output = mystdout.getvalue()
    print("NIST passes:", nist_output.count("PASS"))
    print("NIST fails:", nist_output.count("FAIL"))
except Exception as e:
    sys.stdout = old_stdout
    print("NIST Error:", e)
finally:
    os.unlink(tmp_path)
