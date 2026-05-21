import random
import numpy as np
import time
import timeit
import sys
sys.set_int_max_str_digits(0)

from .base import BasePRNG

class GameOfLifePRNG(BasePRNG):
    def __init__(self, width=100, height=100, seed=None, boundary_mode="toroid"):
        super().__init__(seed)
        self.width = width
        self.height = height
        self.boundary_mode = boundary_mode # "toroid" or "fixed"
        
        if seed is not None:
            self.seed = seed
            # Deterministic entropy for manual seed
            self.entropy = seed % 10000
            if self.entropy == 0: self.entropy = 1
        else:
            # Enhanced entropy using multiple time sources with XOR mixing
            try:
                # Collect multiple time sources
                t1 = timeit.timeit(number=1)  # Execution time
                t2 = time.process_time_ns()   # Process time
                t3 = time.perf_counter_ns()   # High-resolution counter
                
                # Mix sources with XOR to prevent correlation
                seed_raw = int((t2 ^ int(t1 * 1e12)) * (t3 % 1000000))
                
                # Apply xorshift-like mixing for better distribution
                seed_raw ^= (seed_raw >> 21)
                seed_raw ^= (seed_raw << 35)
                seed_raw ^= (seed_raw >> 4)
                
                self.seed = seed_raw
                self.entropy = abs(seed_raw) % 10000
            except:
                # Fallback to simpler method
                self.seed = int(time.time() * 1000000)
                self.entropy = self.seed % 10000
                
            if self.entropy == 0: self.entropy = 1
            
        self.current_field = np.zeros((height, width), dtype=int)
        self.next_field = np.zeros((height, width), dtype=int)
        self._initialize_field()

    def _initialize_field(self):
        """Initializes the field based on the seed and coordinates using mixing."""
        for i in range(self.height):
            for j in range(self.width):
                # Mix coordinates and seed
                h = self.seed + i * 374761393 + j * 668265263
                h = (h ^ (h >> 13)) * 1274124909
                h = h ^ (h >> 16)
                self.current_field[i][j] = h % 3

    def _check_cell(self, x, y):
        """Calculates the next state of a cell."""
        count = 0
        H, W = self.height, self.width
        
        # Count neighbors
        for j in range(y - 1, y + 2):
            for i in range(x - 1, x + 2):
                if self.boundary_mode == "fixed":
                    # Fixed boundary: Check if neighbor is within bounds
                    if 0 <= j < H and 0 <= i < W:
                        if self.current_field[j][i] != 0:
                            count += 1
                else:
                    # Toroid boundary: Wrap around
                    if self.current_field[j % H][i % W] != 0:
                        count += 1
        
        cell_value = self.current_field[y][x]
        
        # Zombie (2) logic
        if cell_value == 2:
            count -= 1
            if count == 2 or count == 4:
                return 2
            return 0
        
        # Dead (0) -> Zombie (2) if 6 neighbors
        if count == 6:
            return 2
        
        # Alive (1) logic
        if cell_value == 0:
            count -= 1
            if count == 2 or count == 3:
                return 1
            return 0
        
        else:  # cell_value == 1
            if count == 3:
                return 1
            return 0

    def step(self):
        """Performs one step of evolution."""
        for x in range(self.width):
            for y in range(self.height):
                self.next_field[y][x] = self._check_cell(x, y)
        
        self.current_field = np.copy(self.next_field)
        return self.current_field

    def _extract_best_line(self):
        """Selects the row with the highest entropy."""
        best_row_idx = 0
        max_transitions = -1
        
        for i, row in enumerate(self.current_field):
            transitions = np.sum(row[:-1] != row[1:])
            if transitions > max_transitions:
                max_transitions = transitions
                best_row_idx = i
                
        best_row = self.current_field[best_row_idx]
        ternary_str = "".join(map(str, best_row))
        try:
            val = int(ternary_str, 3)
            if val > 0:
                return bin(val)[2:]
            return "0"
        except ValueError:
            return ""

    def extract_sequence_ternary(self):
        """Extracts a large sequence by treating each row as a ternary number."""
        full_binary = []
        for row in self.current_field:
            ternary_str = "".join(map(str, row))
            try:
                val = int(ternary_str, 3)
                if val > 0:
                    binary_str = bin(val)[2:]
                    full_binary.append(binary_str)
            except ValueError:
                continue
        return "".join(full_binary)

    def generate(self, steps=10, return_history=False, extract_mode="flatten"):
        """Generates a sequence of states."""
        history = []
        if return_history:
            history.append(np.copy(self.current_field))
            
        for _ in range(steps):
            self.step()
            if return_history:
                history.append(np.copy(self.current_field))
        
        if extract_mode == "ternary":
            bit_string = self.extract_sequence_ternary()
        elif extract_mode == "best_line":
            bit_string = self._extract_best_line()
        else:
            flat_bits = self.current_field.flatten()
            ternary_str = "".join(map(str, flat_bits))
            try:
                val = int(ternary_str, 3)
                if val > 0:
                    bit_string = bin(val)[2:]
                else:
                    bit_string = "0"
            except ValueError:
                bit_string = ""
        
        return bit_string, history
