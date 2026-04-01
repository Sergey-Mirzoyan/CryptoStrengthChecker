import numpy as np
from scipy.stats import chi2
from sklearn.neural_network import MLPClassifier
from collections import Counter

def read_binary_string(content):
    """
    Parses binary string content.
    Args:
        content (str): The string content of the file.
    Returns:
        list[int]: List of bits, or None if invalid.
    """
    try:
        sequence = content.strip()
        if not all(bit in '01' for bit in sequence):
            return None
        return [int(bit) for bit in sequence]
    except Exception as e:
        print(f"Error parsing content: {e}")
        return None

def analyze_sequence_direction(sequence, window_size, start_pos, direction='next'):
    """Analysis of sequence in one direction using Neural Network"""
    X_train = []
    y_train = []
    
    # Define training size as 20% of available data, max 50
    training_size = min(len(sequence) // 5, 50)
    
    # Form training set around start_pos
    if direction == 'next':
        train_range = range(max(0, start_pos - training_size//2), 
                          min(start_pos + training_size//2, len(sequence) - window_size))
        for i in train_range:
            X_train.append(sequence[i:i+window_size])
            y_train.append(sequence[i+window_size])
            
        # Predict sequence after start_pos
        test_range = range(start_pos, len(sequence) - window_size)
    else:
        train_range = range(min(len(sequence)-1, start_pos + training_size//2), 
                          max(window_size-1, start_pos - training_size//2), -1)
        for i in train_range:
            X_train.append(sequence[i-window_size:i])
            y_train.append(sequence[i-window_size-1])
            
        # Predict sequence before start_pos
        test_range = range(start_pos, window_size-1, -1)
            
    if len(X_train) == 0:
        return [], 0, 0
        
    # Create and train model
    clf = MLPClassifier(hidden_layer_sizes=(window_size,), max_iter=5000, random_state=42)
    clf.fit(X_train, y_train)
    
    # Make predictions
    predictions = []
    correct_predictions = 0
    
    for i in test_range:
        if direction == 'next':
            window = sequence[i:i+window_size]
            actual = sequence[i+window_size]
            predicted = clf.predict([window])[0]
            pos = i+window_size
        else:
            window = sequence[i-window_size:i]
            actual = sequence[i-window_size-1]
            predicted = clf.predict([window])[0]
            pos = i-window_size-1
            
        predictions.append({
            'position': pos,
            'window': ''.join(map(str, window)),
            'predicted': int(predicted),
            'actual': int(actual),
            'correct': bool(predicted == actual)
        })
        correct_predictions += (predicted == actual)
    
    accuracy = correct_predictions / len(predictions) if predictions else 0
    return predictions, accuracy, len(predictions)

def statistical_prediction(sequence, window_size, start_pos, direction='next'):
    """Statistical analysis using Chi-Square method"""
    predictions = []
    total_chi_square = 0
    total_p_value = 0
    total_tests = 0
    
    # Define training size as 20% of available data, max 50
    training_size = min(len(sequence) // 5, 50)
    
    # Analyze frequencies in training set
    if direction == 'next':
        train_range = range(max(0, start_pos - training_size//2),
                          min(start_pos + training_size//2, len(sequence) - window_size))
        test_range = range(start_pos, len(sequence) - window_size)
    else:
        train_range = range(min(len(sequence)-1, start_pos + training_size//2),
                          max(window_size-1, start_pos - training_size//2), -1)
        test_range = range(start_pos, window_size-1, -1)
    
    # Collect statistics from training set
    window_stats = {}
    for i in train_range:
        if direction == 'next':
            window = tuple(sequence[i:i+window_size])
            next_bit = sequence[i+window_size]
        else:
            window = tuple(sequence[i-window_size:i])
            next_bit = sequence[i-window_size-1]
            
        if window not in window_stats:
            window_stats[window] = Counter()
        window_stats[window][next_bit] += 1
    
    # Make predictions
    for i in test_range:
        if direction == 'next':
            window = tuple(sequence[i:i+window_size])
            actual = sequence[i+window_size]
            pos = i+window_size
        else:
            window = tuple(sequence[i-window_size:i])
            actual = sequence[i-window_size-1]
            pos = i-window_size-1
            
        freq = window_stats.get(window, Counter())
        
        if sum(freq.values()) > 0:
            expected = sum(freq.values()) / 2
            chi_square = sum((obs - expected) ** 2 / expected for obs in freq.values())
            p_value = 1 - chi2.cdf(chi_square, df=1)
            
            predictions.append({
                'position': pos,
                'window': ''.join(map(str, window)),
                'actual': int(actual),
                'chi_square': float(chi_square),
                'p_value': float(p_value)
            })
            total_chi_square += chi_square
            total_p_value += p_value
            total_tests += 1
    
    avg_chi_square = total_chi_square / total_tests if total_tests > 0 else 0
    avg_p_value = total_p_value / total_tests if total_tests > 0 else 0
    return predictions, avg_chi_square, avg_p_value, total_tests

def run_full_analysis(sequence, window_sizes=[8, 16, 32]):
    """
    Runs full analysis on the sequence.
    Returns a dictionary with structured results.
    """
    if not sequence:
        return None
    
    start_pos = len(sequence) // 2
    
    results = {
        'sequence_length': len(sequence),
        'neural_network': {
            'details': [],
            'overall_accuracy': 0,
            'total_analyzed': 0,
            'is_strong': False
        },
        'statistical': {
            'details': [],
            'overall_chi_square': 0,
            'overall_p_value': 0,
            'total_tests': 0,
            'is_strong': False
        }
    }
    
    # Neural Network Analysis
    total_accuracy = 0
    total_analyzed = 0
    
    for window_size in window_sizes:
        for direction in ['next', 'prev']:
            predictions, accuracy, bits_analyzed = analyze_sequence_direction(
                sequence, window_size, start_pos, direction)
            
            if bits_analyzed > 0:
                results['neural_network']['details'].append({
                    'window_size': window_size,
                    'direction': direction,
                    'bits_analyzed': bits_analyzed,
                    'accuracy': accuracy,
                    'predictions': predictions
                })
                total_accuracy += accuracy * bits_analyzed
                total_analyzed += bits_analyzed
    
    if total_analyzed > 0:
        results['neural_network']['overall_accuracy'] = total_accuracy / total_analyzed
        results['neural_network']['total_analyzed'] = total_analyzed
        results['neural_network']['is_strong'] = results['neural_network']['overall_accuracy'] <= 0.55

    # Statistical Analysis
    total_chi_square = 0
    total_p_value = 0
    total_stat_tests = 0
    
    for window_size in window_sizes:
        for direction in ['next', 'prev']:
            predictions, avg_chi_square, avg_p_value, tests = statistical_prediction(
                sequence, window_size, start_pos, direction)
            if tests > 0:
                results['statistical']['details'].append({
                    'window_size': window_size,
                    'direction': direction,
                    'tests': tests,
                    'avg_chi_square': avg_chi_square,
                    'avg_p_value': avg_p_value,
                    'predictions': predictions
                })
                total_chi_square += avg_chi_square * tests
                total_p_value += avg_p_value * tests
                total_stat_tests += tests

    if total_stat_tests > 0:
        results['statistical']['overall_chi_square'] = total_chi_square / total_stat_tests
        results['statistical']['overall_p_value'] = total_p_value / total_stat_tests
        results['statistical']['total_tests'] = total_stat_tests
        results['statistical']['is_strong'] = results['statistical']['overall_p_value'] > 0.05
        
    return results
