from .base import BasePRNG
import struct
import time
import hashlib

# Standard S-box (id-tc26-gost-28147-param-Z)
S_BOX = [
    [12, 4, 6, 2, 10, 5, 11, 9, 14, 8, 13, 7, 0, 3, 15, 1],
    [6, 8, 2, 3, 9, 10, 5, 12, 1, 14, 4, 7, 11, 13, 0, 15],
    [11, 3, 5, 8, 2, 15, 10, 13, 14, 1, 7, 4, 12, 9, 6, 0],
    [12, 8, 2, 1, 13, 4, 15, 6, 7, 0, 10, 5, 3, 14, 9, 11],
    [7, 15, 5, 10, 8, 1, 6, 13, 0, 9, 3, 14, 11, 4, 2, 12],
    [5, 13, 15, 6, 9, 2, 12, 10, 11, 7, 8, 1, 4, 3, 14, 0],
    [8, 14, 2, 5, 6, 9, 1, 12, 15, 4, 11, 0, 13, 10, 3, 7],
    [1, 7, 14, 13, 0, 5, 8, 3, 4, 15, 10, 6, 9, 12, 11, 2]
]

class Magma:
    def __init__(self, key):
        if len(key) != 32:
            raise ValueError("Key must be 32 bytes")
        self.subkeys = struct.unpack("<8I", key)

    def _g(self, a, k):
        t = (a + k) & 0xFFFFFFFF
        output = 0
        for i in range(8):
            s_idx = (t >> (4 * i)) & 0xF
            output |= (S_BOX[i][s_idx] << (4 * i))
        return ((output << 11) | (output >> 21)) & 0xFFFFFFFF

    def encrypt_block(self, block):
        if len(block) != 8:
            raise ValueError("Block must be 8 bytes")
        
        n1, n2 = struct.unpack("<2I", block)
        
        # Rounds 1-24: Keys 0 to 7 repeated 3 times
        for _ in range(3):
            for i in range(8):
                n1, n2 = n2, n1 ^ self._g(n2, self.subkeys[i])
                
        # Rounds 25-32: Keys 7 to 0
        for i in range(7, -1, -1):
            n1, n2 = n2, n1 ^ self._g(n2, self.subkeys[i])
            
        # Final swap is NOT performed in GOST 28147-89 encryption, 
        # but usually N2, N1 is output. 
        # Actually, standard says output is (N1, N2) but after last round N2 becomes left.
        # Let's stick to standard structure: N2 is left, N1 is right after swap.
        # But last round doesn't swap? 
        # Standard: "After 32 rounds... the result is (N1, N2)".
        # My loop does swap. So I should swap back.
        return struct.pack("<2I", n2, n1)

class MagmaGenerator(BasePRNG):
    def __init__(self, seed=None):
        super().__init__(seed)
        if seed is None:
            seed = int(time.time())
            
        # Derive 256-bit key and 64-bit IV
        key_hash = hashlib.sha256(str(seed).encode()).digest()
        self.key = key_hash # 32 bytes
        
        # IV from second hash to ensure independence
        iv_hash = hashlib.sha256((str(seed) + "IV").encode()).digest()
        self.iv = int.from_bytes(iv_hash[:8], 'little')
        
        self.cipher = Magma(self.key)
        self.counter = self.iv

    def generate(self, length_bits):
        out_bytes = bytearray()
        bytes_needed = (length_bits + 7) // 8
        
        while len(out_bytes) < bytes_needed:
            counter_bytes = self.counter.to_bytes(8, 'little')
            block = self.cipher.encrypt_block(counter_bytes)
            out_bytes.extend(block)
            self.counter = (self.counter + 1) % (2**64)
            
        bits = "".join(f"{b:08b}" for b in out_bytes)
        return bits[:length_bits]
