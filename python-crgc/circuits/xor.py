"""
Example Python circuit: XOR
This function will be compiled to a boolean circuit
"""

def circuit(a: int, b: int) -> int:
    """
    Bitwise XOR of two integers
    
    Args:
        a: First input (generator's input)
        b: Second input (evaluator's input)
    
    Returns:
        a XOR b
    """
    return a ^ b
