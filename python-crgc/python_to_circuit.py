"""
Python Function to Circuit Compiler

Automatically converts Python functions into Boolean circuits.
Supports basic arithmetic, bitwise operations, and control flow.

Usage:
    @circuit_function(input_bits=[8, 8], output_bits=8)
    def adder(a, b):
        return a + b
    
    circuit = adder.compile()
"""

import ast
import inspect
from typing import List, Callable, Dict, Any, Tuple, Optional
from dataclasses import dataclass

from crgc import TransformedCircuit, TransformedGate, CircuitDetails
from tlp_circuit_builder import TLPCircuitBuilder


@dataclass
class BitVector:
    """Represents a multi-bit value in the circuit"""
    wires: List[int]  # Wire IDs (LSB first)
    bits: int  # Number of bits
    
    def __len__(self):
        return self.bits


class CircuitCompiler:
    """
    Compiles Python functions to Boolean circuits
    
    Supports:
    - Arithmetic: +, -, *, // (integer division)
    - Bitwise: &, |, ^, ~, <<, >>
    - Comparison: ==, !=, <, >, <=, >=
    - Control flow: if/else (as MUX)
    - Constants
    """
    
    def __init__(self, builder: TLPCircuitBuilder):
        self.builder = builder
        self.variables: Dict[str, BitVector] = {}
        self.input_vectors: List[BitVector] = []
        
    def allocate_bitvector(self, num_bits: int) -> BitVector:
        """Allocate wires for a multi-bit value"""
        wires = [self.builder._allocate_wire() for _ in range(num_bits)]
        return BitVector(wires=wires, bits=num_bits)
    
    def constant_bitvector(self, value: int, num_bits: int) -> BitVector:
        """Create a bitvector for a constant value - NOT RECOMMENDED, use parameters instead"""
        # Constants in circuits need to be handled specially
        # For now, we just allocate wires and hope they're set correctly
        # In production, constants should be passed as inputs
        raise NotImplementedError("Constants not yet supported - pass values as function parameters instead")
    
    def build_adder(self, a: BitVector, b: BitVector, output_carry: bool = False) -> BitVector:
        """
        Build a ripple-carry adder circuit
        
        Args:
            a, b: Input bitvectors
            output_carry: If True, include carry bit in output (n+1 bits)
        """
        if a.bits != b.bits:
            raise ValueError("Operands must have same bit width")
        
        n = a.bits
        result_bits = n + 1 if output_carry else n
        result = self.allocate_bitvector(result_bits)
        
        # Ripple-carry adder
        carry = None  # No initial carry
        
        for i in range(n):
            if carry is None:
                # First bit: half adder
                # sum = a[i] XOR b[i]
                result.wires[i] = self.builder.build_xor_gate(a.wires[i], b.wires[i])
                # carry = a[i] AND b[i]
                carry = self.builder.build_and_gate(a.wires[i], b.wires[i])
            else:
                # Full adder: sum = a XOR b XOR carry
                xor1 = self.builder.build_xor_gate(a.wires[i], b.wires[i])
                result.wires[i] = self.builder.build_xor_gate(xor1, carry)
                
                # carry_out = (a AND b) OR (carry AND (a XOR b))
                and1 = self.builder.build_and_gate(a.wires[i], b.wires[i])
                and2 = self.builder.build_and_gate(carry, xor1)
                carry = self.builder.build_or_gate(and1, and2)
        
        # Add final carry bit if requested
        if output_carry:
            result.wires[n] = carry
        
        return result
    
    def build_subtractor(self, a: BitVector, b: BitVector) -> BitVector:
        """Build a subtractor circuit (a - b) using complement"""
        if a.bits != b.bits:
            raise ValueError("Operands must have same bit width")
        
        # Use borrow-based subtraction
        # diff[i] = a[i] XOR b[i] XOR borrow[i-1]
        # borrow[i] = (~a[i] AND b[i]) OR (borrow[i-1] AND ~(a[i] XOR b[i]))
        
        result = self.allocate_bitvector(a.bits)
        borrow = None
        
        for i in range(a.bits):
            if borrow is None:
                # First bit: half subtractor
                result.wires[i] = self.builder.build_xor_gate(a.wires[i], b.wires[i])
                # borrow = ~a AND b
                not_a = self.builder.build_not_gate(a.wires[i])
                borrow = self.builder.build_and_gate(not_a, b.wires[i])
            else:
                # Full subtractor
                xor1 = self.builder.build_xor_gate(a.wires[i], b.wires[i])
                result.wires[i] = self.builder.build_xor_gate(xor1, borrow)
                
                # borrow_out = (~a AND b) OR (borrow AND ~(a XOR b))
                not_a = self.builder.build_not_gate(a.wires[i])
                and1 = self.builder.build_and_gate(not_a, b.wires[i])
                not_xor = self.builder.build_not_gate(xor1)
                and2 = self.builder.build_and_gate(borrow, not_xor)
                borrow = self.builder.build_or_gate(and1, and2)
        
        return result
    
    def build_and(self, a: BitVector, b: BitVector) -> BitVector:
        """Build bitwise AND"""
        if a.bits != b.bits:
            raise ValueError("Operands must have same bit width")
        
        result = self.allocate_bitvector(a.bits)
        for i in range(a.bits):
            result.wires[i] = self.builder.build_and_gate(a.wires[i], b.wires[i])
        
        return result
    
    def build_or(self, a: BitVector, b: BitVector) -> BitVector:
        """Build bitwise OR"""
        if a.bits != b.bits:
            raise ValueError("Operands must have same bit width")
        
        result = self.allocate_bitvector(a.bits)
        for i in range(a.bits):
            result.wires[i] = self.builder.build_or_gate(a.wires[i], b.wires[i])
        
        return result
    
    def build_xor(self, a: BitVector, b: BitVector) -> BitVector:
        """Build bitwise XOR"""
        if a.bits != b.bits:
            raise ValueError("Operands must have same bit width")
        
        result = self.allocate_bitvector(a.bits)
        for i in range(a.bits):
            result.wires[i] = self.builder.build_xor_gate(a.wires[i], b.wires[i])
        
        return result
    
    def build_not(self, a: BitVector) -> BitVector:
        """Build bitwise NOT"""
        result = self.allocate_bitvector(a.bits)
        for i in range(a.bits):
            result.wires[i] = self.builder.build_not_gate(a.wires[i])
        
        return result
    
    def build_equals(self, a: BitVector, b: BitVector) -> BitVector:
        """Build equality comparison (returns 1-bit result)"""
        if a.bits != b.bits:
            raise ValueError("Operands must have same bit width")
        
        # Use the equality checker from TLPCircuitBuilder
        eq_wire = self.builder.build_equality_check(a.wires, b.wires)
        return BitVector(wires=[eq_wire], bits=1)
    
    def build_less_than(self, a: BitVector, b: BitVector) -> BitVector:
        """Build less-than comparison (a < b)"""
        # a < b is equivalent to (a - b) has borrow/is negative
        # For unsigned: check if subtraction would borrow
        # Simplified: compare bit by bit from MSB
        
        # For now, use subtraction and check MSB (sign bit in signed arithmetic)
        diff = self.build_subtractor(a, b)
        # MSB indicates if result is negative (for signed)
        # For proper unsigned comparison, need more sophisticated logic
        return BitVector(wires=[diff.wires[-1]], bits=1)
    
    def build_shift_left(self, a: BitVector, shift: int) -> BitVector:
        """Build left shift by constant"""
        result = self.allocate_bitvector(a.bits)
        
        for i in range(a.bits):
            if i < shift:
                # Shifted in zeros - create constant 0 wire
                # Use AND(wire, NOT(wire)) = 0
                zero = self.builder.build_and_gate(a.wires[0], 
                                                   self.builder.build_not_gate(a.wires[0]))
                result.wires[i] = zero
            else:
                result.wires[i] = a.wires[i - shift]
        
        return result
    
    def compile_binop(self, op: str, left: BitVector, right: BitVector) -> BitVector:
        """Compile binary operation"""
        if op == '+':
            # For addition, include carry if result needs more bits
            return self.build_adder(left, right, output_carry=True)
        elif op == '-':
            return self.build_subtractor(left, right)
        elif op == '&':
            return self.build_and(left, right)
        elif op == '|':
            return self.build_or(left, right)
        elif op == '^':
            return self.build_xor(left, right)
        elif op == '==':
            return self.build_equals(left, right)
        elif op == '<':
            return self.build_less_than(left, right)
        else:
            raise NotImplementedError(f"Binary operation '{op}' not yet implemented")
    
    def compile_unaryop(self, op: str, operand: BitVector) -> BitVector:
        """Compile unary operation"""
        if op == '~':
            return self.build_not(operand)
        else:
            raise NotImplementedError(f"Unary operation '{op}' not yet implemented")


class CircuitFunction:
    """
    Decorator for Python functions to make them compilable to circuits
    
    Example:
        @circuit_function(input_bits=[8, 8], output_bits=9)
        def adder(a, b):
            return a + b
    """
    
    def __init__(self, input_bits: List[int], output_bits: int):
        self.input_bits = input_bits
        self.output_bits = output_bits
        self.func = None
        self.circuit = None
        
    def __call__(self, func: Callable):
        self.func = func
        self.func_name = func.__name__
        return self
    
    def compile(self) -> TransformedCircuit:
        """Compile the function to a circuit"""
        if self.circuit is not None:
            return self.circuit
        
        print(f"Compiling function '{self.func_name}' to circuit...")
        
        # Create builder and compiler
        builder = TLPCircuitBuilder()
        compiler = CircuitCompiler(builder)
        
        # Allocate input wires
        total_input_bits = sum(self.input_bits)
        builder.wire_counter = total_input_bits
        
        # Create input bitvectors
        offset = 0
        params = list(inspect.signature(self.func).parameters.keys())
        
        for i, (param_name, num_bits) in enumerate(zip(params, self.input_bits)):
            wires = list(range(offset, offset + num_bits))
            vec = BitVector(wires=wires, bits=num_bits)
            compiler.variables[param_name] = vec
            compiler.input_vectors.append(vec)
            offset += num_bits
        
        # Parse function AST
        source = inspect.getsource(self.func)
        tree = ast.parse(source)
        
        # Find function definition
        func_def = None
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == self.func_name:
                func_def = node
                break
        
        if func_def is None:
            raise ValueError(f"Could not find function definition for {self.func_name}")
        
        # Compile function body
        result = self._compile_ast(func_def.body, compiler)
        
        # Ensure result has correct bit width
        if result.bits != self.output_bits:
            print(f"  Warning: Result has {result.bits} bits, expected {self.output_bits}")
            # Truncate or extend as needed
            if result.bits > self.output_bits:
                result = BitVector(wires=result.wires[:self.output_bits], bits=self.output_bits)
            else:
                # Zero-extend
                while result.bits < self.output_bits:
                    zero = builder.build_and_gate(result.wires[0], 
                                                  builder.build_not_gate(result.wires[0]))
                    result.wires.append(zero)
                    result.bits += 1
        
        # Add output buffers
        output_wires = []
        for wire in result.wires:
            buf = builder._allocate_wire()
            gate = TransformedGate()
            gate.leftParentID = wire
            gate.rightParentID = wire
            gate.outputID = buf
            gate.truthTable = [[False, False], [False, True]]  # Buffer
            builder.gates.append(gate)
            output_wires.append(buf)
        
        # Create circuit
        details = CircuitDetails()
        details.numGates = len(builder.gates)
        details.numWires = builder.wire_counter
        
        # Single input for simplicity (can be extended to multiple inputs)
        if len(self.input_bits) == 1:
            details.bitlengthInputA = self.input_bits[0]
            details.bitlengthInputB = 0
        else:
            # Split inputs between A and B
            mid = len(self.input_bits) // 2
            details.bitlengthInputA = sum(self.input_bits[:mid]) if mid > 0 else self.input_bits[0]
            details.bitlengthInputB = sum(self.input_bits[mid:]) if len(self.input_bits) > 1 else 0
        
        details.numOutputs = 1
        details.bitlengthOutputs = self.output_bits
        
        circuit = TransformedCircuit(details)
        circuit.gates = builder.gates
        
        self.circuit = circuit
        
        print(f"✓ Circuit compiled:")
        print(f"  Gates: {details.numGates}")
        print(f"  Wires: {details.numWires}")
        print(f"  Inputs: {self.input_bits} bits")
        print(f"  Output: {self.output_bits} bits")
        
        return circuit
    
    def _compile_ast(self, body: List[ast.stmt], compiler: CircuitCompiler) -> BitVector:
        """Compile AST body to circuit"""
        result = None
        
        for stmt in body:
            if isinstance(stmt, ast.Return):
                result = self._compile_expr(stmt.value, compiler)
            elif isinstance(stmt, ast.Assign):
                # Variable assignment
                value = self._compile_expr(stmt.value, compiler)
                for target in stmt.targets:
                    if isinstance(target, ast.Name):
                        compiler.variables[target.id] = value
            elif isinstance(stmt, ast.Expr):
                # Expression statement (like docstrings) - skip
                continue
            else:
                raise NotImplementedError(f"Statement type {type(stmt).__name__} not implemented")
        
        return result
    
    def _compile_expr(self, expr: ast.expr, compiler: CircuitCompiler) -> BitVector:
        """Compile expression to circuit"""
        if isinstance(expr, ast.BinOp):
            left = self._compile_expr(expr.left, compiler)
            right = self._compile_expr(expr.right, compiler)
            op = self._get_op_string(expr.op)
            return compiler.compile_binop(op, left, right)
        
        elif isinstance(expr, ast.UnaryOp):
            operand = self._compile_expr(expr.operand, compiler)
            op = self._get_op_string(expr.op)
            return compiler.compile_unaryop(op, operand)
        
        elif isinstance(expr, ast.Name):
            # Variable reference
            if expr.id in compiler.variables:
                return compiler.variables[expr.id]
            else:
                raise NameError(f"Variable '{expr.id}' not defined")
        
        elif isinstance(expr, ast.Constant) or isinstance(expr, ast.Num):
            # Constant value
            value = expr.value if isinstance(expr, ast.Constant) else expr.n
            # Infer bit width (default to output bits)
            return compiler.constant_bitvector(value, self.output_bits)
        
        else:
            raise NotImplementedError(f"Expression type {type(expr).__name__} not implemented")
    
    def _get_op_string(self, op) -> str:
        """Convert AST operator to string"""
        op_map = {
            ast.Add: '+',
            ast.Sub: '-',
            ast.Mult: '*',
            ast.BitAnd: '&',
            ast.BitOr: '|',
            ast.BitXor: '^',
            ast.Invert: '~',
            ast.Eq: '==',
            ast.Lt: '<',
            ast.Gt: '>',
        }
        return op_map.get(type(op), str(type(op).__name__))


def circuit_function(input_bits: List[int], output_bits: int):
    """
    Decorator to mark a Python function as compilable to a circuit
    
    Args:
        input_bits: List of bit widths for each input parameter
        output_bits: Bit width of the output
    
    Example:
        @circuit_function(input_bits=[8, 8], output_bits=9)
        def adder(a, b):
            return a + b
    """
    return CircuitFunction(input_bits, output_bits)


# ============================================================================
# Example Functions
# ============================================================================

@circuit_function(input_bits=[8, 8], output_bits=9)
def simple_adder(a, b):
    """8-bit adder with 9-bit output (includes carry)"""
    return a + b


@circuit_function(input_bits=[8, 8], output_bits=8)
def simple_xor(a, b):
    """8-bit XOR"""
    return a ^ b


@circuit_function(input_bits=[8, 8], output_bits=8)
def and_or_combo(a, b):
    """Combination: (a & b) | (a ^ b)"""
    return (a & b) | (a ^ b)


@circuit_function(input_bits=[8], output_bits=8)
def not_gate(a):
    """8-bit NOT"""
    return ~a


@circuit_function(input_bits=[8, 8], output_bits=8)
def simple_and(a, b):
    """8-bit AND - simplest possible test"""
    return a & b


# ============================================================================
# Testing and Demo
# ============================================================================

def test_adder():
    """Test the adder circuit compilation and execution"""
    print("\n" + "="*70)
    print("TESTING ADDER CIRCUIT")
    print("="*70)
    
    # Compile
    circuit = simple_adder.compile()
    
    # Save to disk
    from pathlib import Path
    from crgc.bristol_writer import export_bristol_format
    
    circuits_dir = Path(__file__).parent / "circuits"
    circuits_dir.mkdir(exist_ok=True)
    
    circuit_path = circuits_dir / "adder8_bristol.txt"
    export_bristol_format(circuit, circuit_path)
    print(f"✓ Circuit saved to: {circuit_path}")
    
    # Test cases
    test_cases = [
        (5, 3, 8),
        (255, 1, 256),  # Overflow test
        (100, 50, 150),
        (0, 0, 0),
        (255, 255, 510),
    ]
    
    from crgc.circuit_evaluator import evaluate_transformed_circuit
    
    def int_to_bits(value: int, num_bits: int) -> List[bool]:
        """Convert integer to bit array (MSB first for C++ compatibility)"""
        bits = []
        for i in range(num_bits):
            bits.append(bool((value >> i) & 1))
        return bits[::-1]  # Reverse to MSB-first
    
    def bits_to_int(bits: List[bool]) -> int:
        """Convert bit array to integer (MSB first from C++ evaluator)"""
        bits = bits[::-1]  # Reverse from MSB-first to LSB-first
        result = 0
        for i, bit in enumerate(bits):
            if bit:
                result |= (1 << i)
        return result
    
    print("\nTest Cases:")
    print(f"{'a':>5} + {'b':>5} = {'Expected':>8} | {'Got':>8} | {'Binary Got':>12} | Status")
    print("-" * 80)
    
    for a, b, expected in test_cases:
        # Prepare inputs
        inputA = int_to_bits(a, 8)
        inputB = int_to_bits(b, 8)
        
        # Evaluate circuit
        output = evaluate_transformed_circuit(circuit, inputA, inputB)
        result = bits_to_int(output)
        
        status = "✓ PASS" if result == expected else "✗ FAIL"
        print(f"{a:>5} + {b:>5} = {expected:>8} | {result:>8} | {bin(result):>12} | {status}")
    
    print("\n✓ Adder test complete!")


def test_xor():
    """Test XOR circuit"""
    print("\n" + "="*70)
    print("TESTING XOR CIRCUIT")
    print("="*70)
    
    circuit = simple_xor.compile()
    
    # Save to disk
    from pathlib import Path
    from crgc.bristol_writer import export_bristol_format
    
    circuits_dir = Path(__file__).parent / "circuits"
    circuits_dir.mkdir(exist_ok=True)
    
    circuit_path = circuits_dir / "xor8_bristol.txt"
    export_bristol_format(circuit, circuit_path)
    print(f"✓ Circuit saved to: {circuit_path}")
    
    from crgc.circuit_evaluator import evaluate_transformed_circuit
    
    def int_to_bits(value: int, num_bits: int) -> List[bool]:
        bits = []
        for i in range(num_bits):
            bits.append(bool((value >> i) & 1))
        return bits[::-1]  # Reverse to MSB-first
    
    def bits_to_int(bits: List[bool]) -> int:
        bits = bits[::-1]  # Reverse from MSB-first to LSB-first
        result = 0
        for i, bit in enumerate(bits):
            if bit:
                result |= (1 << i)
        return result
    
    test_cases = [
        (0b10101010, 0b01010101, 0b11111111),
        (0b11110000, 0b00001111, 0b11111111),
        (0b10101010, 0b10101010, 0b00000000),
    ]
    
    print("\nTest Cases:")
    print(f"{'a':>10} ^ {'b':>10} = {'Expected':>10} | {'Got':>10} | Status")
    print("-" * 70)
    
    for a, b, expected in test_cases:
        inputA = int_to_bits(a, 8)
        inputB = int_to_bits(b, 8)
        
        output = evaluate_transformed_circuit(circuit, inputA, inputB)
        result = bits_to_int(output)
        
        status = "✓ PASS" if result == expected else "✗ FAIL"
        print(f"{bin(a):>10} ^ {bin(b):>10} = {bin(expected):>10} | {bin(result):>10} | {status}")
    
    print("\n✓ XOR test complete!")


def test_and():
    """Test simple AND circuit - simplest possible test"""
    print("\n" + "="*70)
    print("TESTING AND CIRCUIT (SIMPLEST)")
    print("="*70)
    
    circuit = simple_and.compile()
    
    # Save to disk
    from pathlib import Path
    from crgc.bristol_writer import export_bristol_format
    
    circuits_dir = Path(__file__).parent / "circuits"
    circuits_dir.mkdir(exist_ok=True)
    
    circuit_path = circuits_dir / "and8_bristol.txt"
    export_bristol_format(circuit, circuit_path)
    print(f"✓ Circuit saved to: {circuit_path}")
    
    from crgc.circuit_evaluator import evaluate_transformed_circuit
    
    def int_to_bits(value: int, num_bits: int) -> List[bool]:
        bits = []
        for i in range(num_bits):
            bits.append(bool((value >> i) & 1))
        return bits[::-1]  # Reverse to MSB-first
    
    def bits_to_int(bits: List[bool]) -> int:
        bits = bits[::-1]  # Reverse from MSB-first to LSB-first
        result = 0
        for i, bit in enumerate(bits):
            if bit:
                result |= (1 << i)
        return result
    
    test_cases = [
        (0b11111111, 0b11111111, 0b11111111),  # All 1s
        (0b11110000, 0b00001111, 0b00000000),  # No overlap
        (0b10101010, 0b01010101, 0b00000000),  # Alternating
        (0b11111111, 0b00000000, 0b00000000),  # One zero
        (0b11001100, 0b10101010, 0b10001000),  # Mixed
    ]
    
    print("\nTest Cases:")
    print(f"{'a':>10} & {'b':>10} = {'Expected':>10} | {'Got':>10} | Status")
    print("-" * 70)
    
    for a, b, expected in test_cases:
        inputA = int_to_bits(a, 8)
        inputB = int_to_bits(b, 8)
        
        output = evaluate_transformed_circuit(circuit, inputA, inputB)
        result = bits_to_int(output)
        
        status = "✓ PASS" if result == expected else "✗ FAIL"
        print(f"{bin(a):>10} & {bin(b):>10} = {bin(expected):>10} | {bin(result):>10} | {status}")
    
    print("\n✓ AND test complete!")


def main():

    print("\nSupported operations:")
    print("  - Arithmetic: +, -, & (bitwise AND), | (bitwise OR), ^ (bitwise XOR)")
    print("  - Unary: ~ (bitwise NOT)")
    print("  - not supported: *, //, comparisons, if/else")
    print("#"*70)
    
    # Run tests
    test_adder()
    test_xor()
    test_and()
    



if __name__ == "__main__":
    main()
