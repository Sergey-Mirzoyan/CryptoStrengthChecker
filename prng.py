import random
import numpy as np
import time
import timeit

class GameOfLifePRNG:
    def __init__(self, width=100, height=100, seed=None):
        self.width = width
        self.height = height
        
        if seed is not None:
            self.seed = seed
            # Deterministic entropy for manual seed
            self.entropy = seed % 10000
            if self.entropy == 0: self.entropy = 1
        else:
            # Enhanced entropy using multiple time sources with XOR mixing
            # This provides better randomness and more uniform initial distribution
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
        # Use the calculated entropy/seed
        # We use a robust hash mixing of coordinates and seed to ensure
        # a uniform and well-distributed initial state ("well filled").
        
        for i in range(self.height):
            for j in range(self.width):
                # Mix coordinates and seed
                # Constants are arbitrary large primes for mixing to avoid patterns
                h = self.seed + i * 374761393 + j * 668265263
                
                # Apply xorshift-like mixing steps
                h = (h ^ (h >> 13)) * 1274124909
                h = h ^ (h >> 16)
                
                # Map to 0, 1, 2 with equal probability (~33% each)
                # This ensures high entropy and coverage (~66% non-zero)
                self.current_field[i][j] = h % 3

    def _check_cell(self, x, y):
        """Calculates the next state of a cell."""
        count = 0
        H, W = self.height, self.width
        
        # Count neighbors
        for j in range(y - 1, y + 2):
            for i in range(x - 1, x + 2):
                if self.current_field[j % H][i % W] != 0:
                    count += 1
        
        cell_value = self.current_field[y][x]
        
        # Zombie (2) logic - Original algorithm
        if cell_value == 2:
            count -= 1
            if count == 2 or count == 4:
                return 2
            return 0
        
        # Alive (1) logic (and Dead (0) logic combined in original?)
        # Original code structure was a bit ambiguous, let's follow it closely:
        # if current_field[y][x] == 0: ... else: ...
        
        # Special rule: Dead cells with 6 neighbors become Zombie
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
        """
        Selects the row with the highest entropy (most transitions).
        Returns the bits from that row.
        """
        best_row_idx = 0
        max_transitions = -1
        
        for i, row in enumerate(self.current_field):
            # Count transitions (0->1, 1->2, etc.)
            transitions = np.sum(row[:-1] != row[1:])
            if transitions > max_transitions:
                max_transitions = transitions
                best_row_idx = i
                
        # Extract bits from the best row (mapping 2->1 for binary)
        best_row = self.current_field[best_row_idx]
        binary_row = np.where(best_row > 0, 1, 0)
        return "".join(map(str, binary_row))

    def extract_sequence_ternary(self):
        """
        Extracts a large sequence by treating each row as a ternary number
        and converting it to binary.
        """
        full_binary = []
        for row in self.current_field:
            # Row to ternary string
            ternary_str = "".join(map(str, row))
            # Ternary to integer
            try:
                val = int(ternary_str, 3)
                # Integer to binary (remove '0b')
                if val > 0:
                    binary_str = bin(val)[2:]
                    full_binary.append(binary_str)
            except ValueError:
                continue
                
        return "".join(full_binary)

    def generate(self, steps=10, return_history=False, extract_mode="flatten"):
        """
        Generates a sequence of states.
        
        Args:
            steps (int): Number of steps to evolve.
            return_history (bool): If True, returns list of fields for visualization.
            extract_mode (str): 'flatten', 'best_line', or 'ternary'.
            
        Returns:
            str: Generated binary string.
            list: History of fields (if return_history=True).
        """
        history = []
        if return_history:
            history.append(np.copy(self.current_field))
            
        for _ in range(steps):
            self.step()
            if return_history:
                history.append(np.copy(self.current_field))
        
        # Extract bits based on mode
        if extract_mode == "ternary":
            bit_string = self.extract_sequence_ternary()
        elif extract_mode == "best_line":
            bit_string = self._extract_best_line()
        else:
            # Default: flatten all
            binary_grid = np.where(self.current_field > 0, 1, 0)
            flat_bits = binary_grid.flatten()
            bit_string = "".join(map(str, flat_bits))
        
        return bit_string, history

def generate_prng_sequence(width, height, seed, steps, visualize=False, extract_mode="flatten"):
    """Wrapper to generate sequence and optionally return history."""
    prng = GameOfLifePRNG(width, height, seed)
    return prng.generate(steps, return_history=visualize, extract_mode=extract_mode)
