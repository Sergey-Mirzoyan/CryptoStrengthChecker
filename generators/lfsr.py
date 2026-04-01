from .base import BasePRNG
import time

class LFSRGenerator(BasePRNG):
    def __init__(self, seed=None):
        super().__init__(seed)
        if seed is None:
            seed = int(time.time() * 1000)
        
        # Ensure seed is non-zero and fits in 32 bits
        self.state = seed & 0xFFFFFFFF
        if self.state == 0:
            self.state = 0xDEADBEEF
            
        # Taps for 32-bit maximal length LFSR: 32, 22, 2, 1
        # Polynomial: x^32 + x^22 + x^2 + x + 1
        # In 0-indexed bit positions (0 to 31), we tap bits corresponding to the powers.
        # Feedback = bit 31 ^ bit 21 ^ bit 1 ^ bit 0
        self.mask = (1 << 31) | (1 << 21) | (1 << 1) | 1

    def generate(self, length_bits):
        bits = []
        for _ in range(length_bits):
            # Fibonacci LFSR
            # Get the output bit (usually the LSB or MSB, let's take LSB)
            out_bit = self.state & 1
            bits.append(str(out_bit))
            
            # Calculate feedback
            # We need to XOR the bits at the tap positions
            # Since we are shifting right, the taps are fixed positions in the register
            # Wait, for x^32 + ... the taps are usually indices.
            # Let's use a simpler approach:
            # bit = (self.state >> 31) ^ (self.state >> 21) ^ (self.state >> 1) ^ (self.state >> 0)
            # bit &= 1
            # self.state = (self.state << 1) | bit
            # self.state &= 0xFFFFFFFF
            
            # Actually, let's use the Galois implementation which is faster and equivalent
            # But user wants to show "weakness", so standard Fibonacci is fine.
            
            # Let's stick to a verified 32-bit tap set: [32, 22, 2, 1]
            # Feedback comes from these taps.
            
            bit = ((self.state >> 31) ^ (self.state >> 21) ^ (self.state >> 1) ^ (self.state >> 0)) & 1
            self.state = ((self.state << 1) | bit) & 0xFFFFFFFF
            
        return "".join(bits)
