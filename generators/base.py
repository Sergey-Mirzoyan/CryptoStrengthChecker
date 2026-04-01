from abc import ABC, abstractmethod

class BasePRNG(ABC):
    """
    Abstract base class for all PRNG implementations.
    """
    def __init__(self, seed=None):
        self.seed = seed

    @abstractmethod
    def generate(self, length_bits):
        """
        Generates a sequence of random bits.
        
        Args:
            length_bits (int): The number of bits to generate.
            
        Returns:
            str: A string of '0' and '1' characters.
        """
        pass
