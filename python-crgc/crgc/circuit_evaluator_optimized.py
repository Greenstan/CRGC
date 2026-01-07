"""
Optimized circuit evaluator for CRGC - applies transformations on-the-fly
No circuit copying required - matches C++ implementation performance
"""

from typing import List
from .circuit_structures import TransformedCircuit


def evaluate_with_obfuscation(circuit: TransformedCircuit, 
                               obfuscated_inputA: List[bool], 
                               inputB: List[bool],
                               flipped: List[bool]) -> List[bool]:
    """
    Evaluate circuit with obfuscation pattern applied on-the-fly
    
    This matches the C++ evaluateTransformedCircuit behavior:
    - Takes obfuscated inputs directly
    - Applies flip transformations during evaluation (no circuit copy)
    - Significantly faster than copying circuit first
    
    Args:
        circuit: Base circuit structure (not modified)
        obfuscated_inputA: Already obfuscated inputA
        inputB: Normal inputB
        flipped: Flip pattern for wires
    
    Returns:
        Circuit output (bool array)
    """
    evaluation = [False] * circuit.details.numWires
    
    # Load obfuscated InputA (REVERSED for C++ compatibility)
    for i in range(circuit.details.bitlengthInputA):
        evaluation[i] = obfuscated_inputA[circuit.details.bitlengthInputA - 1 - i]
    
    # Load InputB (REVERSED for C++ compatibility)
    for i in range(circuit.details.bitlengthInputB):
        evaluation[i + circuit.details.bitlengthInputA] = inputB[circuit.details.bitlengthInputB - 1 - i]
    
    # Evaluate gates with on-the-fly transformation
    for gate in circuit.gates:
        # Get parent values
        left_val = evaluation[gate.leftParentID]
        right_val = evaluation[gate.rightParentID]
        
        # Apply flipping transformations on-the-fly
        # If parent is flipped, swap the index we use
        left_idx = int(not left_val if flipped[gate.leftParentID] else left_val)
        right_idx = int(not right_val if flipped[gate.rightParentID] else right_val)
        
        # Lookup in truth table
        output_val = gate.truthTable[left_idx][right_idx]
        
        # Apply output flip if needed
        if flipped[gate.outputID]:
            output_val = not output_val
        
        evaluation[gate.outputID] = output_val
    
    # Extract outputs (REVERSED for C++ compatibility)
    output = []
    for i in range(circuit.details.numOutputs):
        for j in range(circuit.details.bitlengthOutputs):
            wire_idx = circuit.details.numWires - 1 - j - circuit.details.bitlengthOutputs * i
            output.append(evaluation[wire_idx])
    
    return output
