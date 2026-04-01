def calculate_avalanche_effect(seq1, seq2):
    """
    Calculates the avalanche effect between two binary sequences.
    
    Args:
        seq1 (list[int]): First binary sequence.
        seq2 (list[int]): Second binary sequence.
        
    Returns:
        dict: Dictionary containing avalanche effect statistics.
    """
    n1 = len(seq1)
    n2 = len(seq2)
    
    if n1 == 0 or n2 == 0:
        return {
            "error": "Sequences are empty",
            "valid": False
        }
    
    min_len = min(n1, n2)
    truncated = n1 != n2
    
    # Truncate to minimum length
    s1 = seq1[:min_len]
    s2 = seq2[:min_len]
        
    changed_bits = sum(b1 != b2 for b1, b2 in zip(s1, s2))
    avalanche_ratio = changed_bits / min_len
    
    return {
        "valid": True,
        "length": min_len,
        "truncated": truncated,
        "original_lengths": (n1, n2),
        "changed_bits": changed_bits,
        "avalanche_ratio": avalanche_ratio,
        "is_good": 0.45 <= avalanche_ratio <= 0.55
    }
