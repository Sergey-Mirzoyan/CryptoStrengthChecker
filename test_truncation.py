import unittest
import avalanche

class TestTruncation(unittest.TestCase):
    def test_truncation(self):
        seq1 = [0, 0, 0, 0, 0] # length 5
        seq2 = [1, 1, 1]       # length 3
        
        # Should truncate to length 3
        # s1 = [0, 0, 0]
        # s2 = [1, 1, 1]
        # changed = 3
        # ratio = 1.0
        
        result = avalanche.calculate_avalanche_effect(seq1, seq2)
        
        self.assertTrue(result['valid'])
        self.assertTrue(result['truncated'])
        self.assertEqual(result['length'], 3)
        self.assertEqual(result['original_lengths'], (5, 3))
        self.assertEqual(result['avalanche_ratio'], 1.0)

if __name__ == '__main__':
    unittest.main()
