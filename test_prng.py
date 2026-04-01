import unittest
import prng
import numpy as np

class TestPRNG(unittest.TestCase):
    def test_generation(self):
        width = 50
        height = 50
        seed = 12345
        steps = 5
        
        # Test generation
        seq, history = prng.generate_prng_sequence(width, height, seed, steps, visualize=True)
        
        self.assertTrue(len(seq) > 0)
        self.assertEqual(len(history), steps + 1) # Initial + steps
        self.assertEqual(history[0].shape, (height, width))
        
    def test_determinism(self):
        width = 20
        height = 20
        seed = 999
        steps = 5
        
        seq1, _ = prng.generate_prng_sequence(width, height, seed, steps)
        seq2, _ = prng.generate_prng_sequence(width, height, seed, steps)
        
        self.assertEqual(seq1, seq2)
        
    def test_avalanche_sensitivity(self):
        width = 20
        height = 20
        seed = 12345
        steps = 10
        
        seq1, _ = prng.generate_prng_sequence(width, height, seed, steps)
        seq2, _ = prng.generate_prng_sequence(width, height, seed ^ 1, steps)
        
        self.assertNotEqual(seq1, seq2)

if __name__ == '__main__':
    unittest.main()
