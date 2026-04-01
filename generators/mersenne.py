from .base import BasePRNG
import random
import time

class MersenneTwisterGenerator(BasePRNG):
    def __init__(self, seed=None):
        super().__init__(seed)
        if seed is None:
            seed = int(time.time() * 1000)
        self.rng = random.Random(seed)

    def generate(self, length_bits):
        # Generate bits efficiently
        # We can generate 32 bits at a time using getrandbits
        num_chunks = (length_bits + 31) // 32
        bits = ""
        for _ in range(num_chunks):
            chunk = self.rng.getrandbits(32)
            bits += f"{chunk:032b}"
        return bits[:length_bits]
