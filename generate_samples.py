import random

def generate_random_sequence(length):
    return "".join(str(random.randint(0, 1)) for _ in range(length))

def create_samples():
    length = 10000
    
    # 1. Generate "Original" Sequence
    seq_a = generate_random_sequence(length)
    
    # 2. Generate "Perturbed" Sequence (Independent random sequence)
    # In a good RNG, a small change in seed produces a completely different output,
    # statistically indistinguishable from an independent random sequence.
    # So comparing two random sequences should give ~50% difference.
    seq_b = generate_random_sequence(length)
    
    with open("sample_avalanche_1.txt", "w") as f:
        f.write(seq_a)
        
    with open("sample_avalanche_2.txt", "w") as f:
        f.write(seq_b)
        
    print(f"Generated sample_avalanche_1.txt and sample_avalanche_2.txt ({length} bits)")

if __name__ == "__main__":
    create_samples()
