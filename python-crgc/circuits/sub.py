"""
Example Python circuit: Subtraction
This function will be compiled to a boolean circuit
"""

def circuit(a: int, b: int) -> int:
    """
    Subtract two integers
    
    Args:
        a: First input (generator's input)
        b: Second input (evaluator's input)
    
    Returns:
        Difference a - b
    """
    return a - b
