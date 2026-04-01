import unittest
import avalanche

class TestAvalanche(unittest.TestCase):
    def test_calculate_avalanche_effect(self):
        seq1 = [0, 0, 0, 0]
        seq2 = [1, 1, 1, 1]
        result = avalanche.calculate_avalanche_effect(seq1, seq2)
        self.assertTrue(result['valid'])
        self.assertEqual(result['avalanche_ratio'], 1.0)
        
        seq1 = [0, 0, 0, 0]
        seq2 = [0, 0, 1, 1]
        result = avalanche.calculate_avalanche_effect(seq1, seq2)
        self.assertEqual(result['avalanche_ratio'], 0.5)
        self.assertTrue(result['is_good'])

    def test_invalid_input(self):
        seq1 = [0, 0]
        seq2 = [0]
        result = avalanche.calculate_avalanche_effect(seq1, seq2)
        self.assertFalse(result['valid'])

if __name__ == '__main__':
    unittest.main()
