from .base import BasePRNG
import time

# S-box
s_box = (
    0x63, 0x7C, 0x77, 0x7B, 0xF2, 0x6B, 0x6F, 0xC5, 0x30, 0x01, 0x67, 0x2B, 0xFE, 0xD7, 0xAB, 0x76,
    0xCA, 0x82, 0xC9, 0x7D, 0xFA, 0x59, 0x47, 0xF0, 0xAD, 0xD4, 0xA2, 0xAF, 0x9C, 0xA4, 0x72, 0xC0,
    0xB7, 0xFD, 0x93, 0x26, 0x36, 0x3F, 0xF7, 0xCC, 0x34, 0xA5, 0xE5, 0xF1, 0x71, 0xD8, 0x31, 0x15,
    0x04, 0xC7, 0x23, 0xC3, 0x18, 0x96, 0x05, 0x9A, 0x07, 0x12, 0x80, 0xE2, 0xEB, 0x27, 0xB2, 0x75,
    0x09, 0x83, 0x2C, 0x1A, 0x1B, 0x6E, 0x5A, 0xA0, 0x52, 0x3B, 0xD6, 0xB3, 0x29, 0xE3, 0x2F, 0x84,
    0x53, 0xD1, 0x00, 0xED, 0x20, 0xFC, 0xB1, 0x5B, 0x6A, 0xCB, 0xBE, 0x39, 0x4A, 0x4C, 0x58, 0xCF,
    0xD0, 0xEF, 0xAA, 0xFB, 0x43, 0x4D, 0x33, 0x85, 0x45, 0xF9, 0x02, 0x7F, 0x50, 0x3C, 0x9F, 0xA8,
    0x51, 0xA3, 0x40, 0x8F, 0x92, 0x9D, 0x38, 0xF5, 0xBC, 0xB6, 0xDA, 0x21, 0x10, 0xFF, 0xF3, 0xD2,
    0xCD, 0x0C, 0x13, 0xEC, 0x5F, 0x97, 0x44, 0x17, 0xC4, 0xA7, 0x7E, 0x3D, 0x64, 0x5D, 0x19, 0x73,
    0x60, 0x81, 0x4F, 0xDC, 0x22, 0x2A, 0x90, 0x88, 0x46, 0xEE, 0xB8, 0x14, 0xDE, 0x5E, 0x0B, 0xDB,
    0xE0, 0x32, 0x3A, 0x0A, 0x49, 0x06, 0x24, 0x5C, 0xC2, 0xD3, 0xAC, 0x62, 0x91, 0x95, 0xE4, 0x79,
    0xE7, 0xC8, 0x37, 0x6D, 0x8D, 0xD5, 0x4E, 0xA9, 0x6C, 0x56, 0xF4, 0xEA, 0x65, 0x7A, 0xAE, 0x08,
    0xBA, 0x78, 0x25, 0x2E, 0x1C, 0xA6, 0xB4, 0xC6, 0xE8, 0xDD, 0x74, 0x1F, 0x4B, 0xBD, 0x8B, 0x8A,
    0x70, 0x3E, 0xB5, 0x66, 0x48, 0x03, 0xF6, 0x0E, 0x61, 0x35, 0x57, 0xB9, 0x86, 0xC1, 0x1D, 0x9E,
    0xE1, 0xF8, 0x98, 0x11, 0x69, 0xD9, 0x8E, 0x94, 0x9B, 0x1E, 0x87, 0xE9, 0xCE, 0x55, 0x28, 0xDF,
    0x8C, 0xA1, 0x89, 0x0D, 0xBF, 0xE6, 0x42, 0x68, 0x41, 0x99, 0x2D, 0x0F, 0xB0, 0x54, 0xBB, 0x16,
)

r_con = (
    0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20, 0x40,
    0x80, 0x1B, 0x36, 0x6C, 0xD8, 0xAB, 0x4D, 0x9A,
    0x2F, 0x5E, 0xBC, 0x63, 0xC6, 0x97, 0x35, 0x6A,
    0xD4, 0xB3, 0x7D, 0xFA, 0xEF, 0xC5, 0x91, 0x39,
)

def sub_bytes(s):
    for i in range(4):
        for j in range(4):
            s[i][j] = s_box[s[i][j]]

def shift_rows(s):
    s[0][1], s[1][1], s[2][1], s[3][1] = s[1][1], s[2][1], s[3][1], s[0][1]
    s[0][2], s[1][2], s[2][2], s[3][2] = s[2][2], s[3][2], s[0][2], s[1][2]
    s[0][3], s[1][3], s[2][3], s[3][3] = s[3][3], s[0][3], s[1][3], s[2][3]

def add_round_key(s, k):
    for i in range(4):
        for j in range(4):
            s[i][j] ^= k[i][j]

def mix_columns(s):
    for i in range(4):
        a = [s[i][0], s[i][1], s[i][2], s[i][3]]
        s[i][0] = galois_mult(a[0], 2) ^ galois_mult(a[1], 3) ^ a[2] ^ a[3]
        s[i][1] = a[0] ^ galois_mult(a[1], 2) ^ galois_mult(a[2], 3) ^ a[3]
        s[i][2] = a[0] ^ a[1] ^ galois_mult(a[2], 2) ^ galois_mult(a[3], 3)
        s[i][3] = galois_mult(a[0], 3) ^ a[1] ^ a[2] ^ galois_mult(a[3], 2)

def galois_mult(a, b):
    p = 0
    for i in range(8):
        if b & 1:
            p ^= a
        hi_bit_set = a & 0x80
        a <<= 1
        if hi_bit_set:
            a ^= 0x1B
        b >>= 1
    return p & 0xFF

def key_expansion(key):
    key_symbols = [x for x in key]
    # ... simplified for 128 bit key
    # Actually, let's use a simpler implementation structure
    # Or just implement the round function
    pass

# Simplified AES class
class AES:
    def __init__(self, key):
        self.round_keys = self._expand_key(key)

    def _expand_key(self, key):
        # 128-bit key expansion
        w = list(key)
        for i in range(16, 176):
            temp = w[i-4]
            if i % 16 == 0:
                temp = self._sub_word(self._rot_word(temp)) ^ r_con[i//16]
            w.append(w[i-16] ^ temp)
        
        # Convert to state matrices
        keys = []
        for i in range(0, 176, 16):
            keys.append(self._bytes_to_matrix(w[i:i+16]))
        return keys

    def _rot_word(self, word):
        return ((word << 8) | (word >> 24)) & 0xFFFFFFFF # Wait, word is byte? No, word is 4 bytes.
        # My implementation above was byte-based.
        # Let's restart with a cleaner implementation or just use bytes.
        pass
    
    # Let's use a simpler byte-array based approach for expansion
    def _expand_key(self, key):
        w = list(key)
        bytes_key = list(key)
        expanded_key = bytes_key[:]
        
        for i in range(16, 176):
            temp = expanded_key[i-4:i] # 4 bytes
            if i % 16 == 0:
                # RotWord
                temp = temp[1:] + temp[:1]
                # SubWord
                temp = [s_box[b] for b in temp]
                # Rcon
                temp[0] ^= r_con[i//16]
                
            for j in range(4):
                expanded_key.append(expanded_key[i-16+j] ^ temp[j])
                
        return expanded_key

    def encrypt(self, plaintext):
        state = [list(plaintext[i:i+4]) for i in range(0, 16, 4)]
        
        add_round_key(state, self._bytes_to_matrix(self.round_keys[:16]))
        
        for i in range(1, 10):
            sub_bytes(state)
            shift_rows(state)
            mix_columns(state)
            add_round_key(state, self._bytes_to_matrix(self.round_keys[i*16:(i+1)*16]))
            
        sub_bytes(state)
        shift_rows(state)
        add_round_key(state, self._bytes_to_matrix(self.round_keys[160:]))
        
        output = []
        for i in range(4):
            for j in range(4):
                output.append(state[i][j])
        return bytes(output)

    def _bytes_to_matrix(self, text):
        return [list(text[i:i+4]) for i in range(0, 16, 4)]

class AESGenerator(BasePRNG):
    def __init__(self, seed=None):
        super().__init__(seed)
        if seed is None:
            seed = int(time.time())
            
        # Derive key and IV from seed
        # Simple derivation: hash seed or just pad
        import hashlib
        key_hash = hashlib.sha256(str(seed).encode()).digest()
        self.key = key_hash[:16]
        self.iv = int.from_bytes(key_hash[16:], 'big')
        
        self.cipher = AES(self.key)
        self.counter = self.iv

    def generate(self, length_bits):
        out_bytes = bytearray()
        bytes_needed = (length_bits + 7) // 8
        
        while len(out_bytes) < bytes_needed:
            # CTR mode: encrypt counter
            counter_bytes = self.counter.to_bytes(16, 'big')
            block = self.cipher.encrypt(counter_bytes)
            out_bytes.extend(block)
            self.counter = (self.counter + 1) % (2**128)
            
        # Convert to bits
        bits = "".join(f"{b:08b}" for b in out_bytes)
        return bits[:length_bits]
