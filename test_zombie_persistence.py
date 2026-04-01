#!/usr/bin/env python3
"""Quick test to verify high density coverage."""
import numpy as np
import prng

print("Testing high density coverage (Target: ~90% non-zero)...")
print("=" * 60)

generator = prng.GameOfLifePRNG(width=50, height=50, seed=42)

# Check initial state
unique, counts = np.unique(generator.current_field, return_counts=True)
dist = dict(zip(unique, counts))
total_cells = 2500
non_zero = total_cells - dist.get(0, 0)
print(f"Step 0: Non-zero = {non_zero} ({non_zero/total_cells*100:.1f}%) | Zombies = {dist.get(2, 0)}")

# Evolve and check
for step in range(1, 101):
    generator.step()
    unique, counts = np.unique(generator.current_field, return_counts=True)
    dist = dict(zip(unique, counts))
    non_zero = total_cells - dist.get(0, 0)
    
    if step % 10 == 0 or step < 10:
        print(f"Step {step}: Non-zero = {non_zero} ({non_zero/total_cells*100:.1f}%) | Zombies = {dist.get(2, 0)}")

print("=" * 60)
print("✅ Test complete!")
