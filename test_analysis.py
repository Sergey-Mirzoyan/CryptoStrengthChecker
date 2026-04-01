import unittest
import analysis

class TestAnalysis(unittest.TestCase):
    def test_read_binary_string(self):
        self.assertEqual(analysis.read_binary_string("11001"), [1, 1, 0, 0, 1])
        self.assertIsNone(analysis.read_binary_string("110a01"))

    def test_run_full_analysis_structure(self):
        # Create a dummy sequence
        sequence = [1, 0] * 50 # 100 bits
        results = analysis.run_full_analysis(sequence, window_sizes=[4])
        
        self.assertIsNotNone(results)
        self.assertIn('neural_network', results)
        self.assertIn('statistical', results)
        self.assertIn('overall_accuracy', results['neural_network'])
        self.assertIn('overall_p_value', results['statistical'])
        
        # Check details structure
        self.assertTrue(len(results['neural_network']['details']) > 0)
        self.assertTrue(len(results['statistical']['details']) > 0)

if __name__ == '__main__':
    unittest.main()
