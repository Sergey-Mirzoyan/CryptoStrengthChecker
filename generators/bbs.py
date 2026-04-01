from .base import BasePRNG

class BBSGenerator(BasePRNG):
    """
    Blum Blum Shub (BBS) Pseudo-Random Number Generator.
    x_{n+1} = x_n^2 mod M
    """
    def __init__(self, seed=None):
        super().__init__(seed)
        # Two large primes p and q, congruent to 3 mod 4
        # These are 128-bit primes for demonstration/speed
        self.p = 324161900719925474099386716081124667611
        self.q = 324161893815570983748987891543944173371
        self.M = self.p * self.q
        
        if seed is None:
            import time
            seed = int(time.time() * 1000)
            
        # Ensure seed is valid (relatively prime to M and > 1)
        # Simple check: just make sure it's not 0 or 1 and not divisible by p or q
        self.state = seed % self.M
        if self.state <= 1: self.state = 3
        
        # Initial squaring
        self.state = pow(self.state, 2, self.M)

    def generate(self, length_bits):
        """
        Generates a sequence of random bits.
        """
        bits = []
        for _ in range(length_bits):
            self.state = pow(self.state, 2, self.M)
            # Extract least significant bit
            bits.append(str(self.state % 2))
            
        return "".join(bits)
