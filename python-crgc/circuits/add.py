"""
Example Python circuit: Addition
This function will be compiled to a boolean circuit
"""

def circuit(a: int, b: int) -> int:
    """
    Add two integers
    
    Args:
        a: First input (generator's input)
        b: Second input (evaluator's input)
    
    Returns:
        Sum of a and b
    """
    return a + b
