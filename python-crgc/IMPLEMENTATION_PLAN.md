# Python CRGC Implementation Plan

## Overview
Create a Python implementation of CRGC (Completely Reusable Garbled Circuits) focusing on txt-based Bristol Fashion circuits with full C++ compatibility, diagnostic leakage prediction, pure Python core with optional numpy optimization, and comprehensive testing.

## Project Structure
```
python-crgc/
├── crgc/
│   ├── __init__.py
│   ├── circuit_structures.py      # Data structures (CircuitDetails, Gates, Circuits)
│   ├── helper_functions.py        # Utility functions (conversions, random gen)
│   ├── circuit_reader.py          # Bristol circuit parser and RGC importer
│   ├── circuit_evaluator.py       # Circuit evaluation engine
│   ├── circuit_flipper.py         # Input obfuscation and circuit flipping
│   ├── circuit_obfuscator.py      # Fixed gate identification
│   ├── circuit_integrity_breaker.py  # Intermediary gates and regeneration
│   ├── circuit_writer.py          # RGC file export
│   └── leakage_predictor.py       # Leakage diagnostics
├── generator.py                    # Main generator executable
├── evaluator.py                    # Main evaluator executable
├── test_crgc.py                    # Comprehensive test suite
├── run_tests.sh                    # Test runner script
└── IMPLEMENTATION_PLAN.md          # This file
```

## Implementation Steps

### Step 1: Core Data Structures and Helpers
**Files**: `circuit_structures.py`, `helper_functions.py`

**circuit_structures.py**:
- `CircuitDetails` dataclass: numWires, numGates, numOutputs, bitlengthInputA, bitlengthInputB, bitlengthOutputs
- `TransformedGate` dataclass: leftParentID, rightParentID, outputID, truthTable (2x2 bool array)
- `TransformedCircuit` class: details, gates array

**helper_functions.py**:
- `int_to_bool_array(num, bitlength)`: Convert integer to reversed bool array (C++ compatibility)
- `bool_array_to_int(arr)`: Convert bool array to integer
- `swap_left_parent(truth_table)`: Swap rows 0 and 1
- `swap_right_parent(truth_table)`: Swap columns 0 and 1
- `flip_table(truth_table)`: Invert all truth table values
- `generate_random_input(bitlength)`: Use secrets module for cryptographic randomness
- `generate_random_bool()`: Single random bool

**Wire Indexing Convention**:
- Wires 0 to bitlengthInputA-1: Generator's input (InputA)
- Wires bitlengthInputA to bitlengthInputA+bitlengthInputB-1: Evaluator's input (InputB)
- Wires bitlengthInputA+bitlengthInputB onwards: Gate outputs
- Last numOutputs * bitlengthOutputs wires: Circuit outputs

### Step 2: Bristol Circuit Parser
**File**: `circuit_reader.py`

**import_bristol_circuit_details(filepath)**:
- Parse line 1: numGates, numWires
- Parse line 2: number of inputs, bitlengthInputA, bitlengthInputB
- Parse line 3: numOutputs, bitlengthOutputs
- Return CircuitDetails object

**import_bristol_circuit_ex_not(filepath, details)**:
- Initialize exchange_gate[i] = i and flipped[i] = False arrays
- For each gate line:
  - If NOT gate and output not in circuit outputs:
    - exchange_gate[output] = exchange_gate[parent]
    - flipped[output] = NOT flipped[parent]
  - Else if NOT gate and output is circuit output:
    - Create XOR gate (same input twice) with flipped truth table
  - Else (XOR/AND/OR):
    - Convert gate type to truth table:
      - XOR: [[0,1], [1,0]]
      - AND: [[0,0], [0,1]]
      - OR: [[0,1], [1,1]]
    - Apply flipped[left] → swap_left_parent
    - Apply flipped[right] → swap_right_parent
    - Map wire IDs through exchange_gate
    - Add gate to circuit
- Adjust wire indices to account for eliminated NOT gates
- Return TransformedCircuit

**import_transformed_circuit(filepath, details)**:
- Read RGC format gates (leftID rightID outID tt00tt01tt10tt11)
- Parse truth table from 4-character string
- Return TransformedCircuit

**import_obfuscated_input(filepath, bitlength)**:
- Read binary string from file
- Convert to bool array
- Return obfuscated input

### Step 3: Circuit Evaluator
**File**: `circuit_evaluator.py`

**evaluate_transformed_circuit(circuit, inputA, inputB)**:
```python
evaluation = [False] * circuit.details.numWires

# Load InputA (REVERSED for C++ compatibility)
for i in range(circuit.details.bitlengthInputA):
    evaluation[i] = inputA[circuit.details.bitlengthInputA - 1 - i]

# Load InputB (REVERSED)
for i in range(circuit.details.bitlengthInputB):
    evaluation[i + circuit.details.bitlengthInputA] = \
        inputB[circuit.details.bitlengthInputB - 1 - i]

# Evaluate gates
for gate in circuit.gates:
    left_val = evaluation[gate.leftParentID]
    right_val = evaluation[gate.rightParentID]
    evaluation[gate.outputID] = gate.truthTable[left_val][right_val]

# Extract outputs (REVERSED)
output = []
for i in range(circuit.details.numOutputs):
    for j in range(circuit.details.bitlengthOutputs):
        wire_idx = circuit.details.numWires - 1 - j - \
                   circuit.details.bitlengthOutputs * i
        output.append(evaluation[wire_idx])

return output
```

**evaluate_sorted_transformed_circuit(circuit, inputA, inputB)**:
- Same as above but use direct indexing: `evaluation[i + bitlengthInputA + bitlengthInputB]`

**Optional numpy version** (if --use-numpy):
- Use np.array(dtype=bool) for evaluation
- Keep same logic but potentially faster

### Step 4: Leakage Prediction Diagnostics
**File**: `leakage_predictor.py`

**get_parents_of_each_wire(circuit)**:
```python
parents = [[0, 0] for _ in range(circuit.details.numWires)]
for gate in circuit.gates:
    parents[gate.outputID] = [gate.leftParentID, gate.rightParentID]
return parents
```

**get_potentially_obfuscated_fixed_gates(circuit, po)**:
- Initialize po (potentially obfuscated) array
- Mark InputA wires as potentially obfuscated
- For each gate:
  - If both parents potentially obfuscated: mark output
  - If one parent potentially obfuscated and gate output is fixed: mark output
- Count and return statistics

**get_potentially_intermediary_gates_from_output(details, po, parents)**:
- Initialize not_obfuscated array
- BFS from output wires backward through parents
- Mark all gates on path from non-obfuscated to outputs
- Invert for gate wires: po[wire] = NOT not_obfuscated[wire]

**get_leaked_inputs(circuit, po)**:
- Analyze which InputA bits may be inferable
- Return list of potentially leaked input indices

**Output format** (matching C++ exactly):
```
---INFO--- numGates: 376
---TIMING--- 5ms getting Parents of each Wire
---TIMING--- 3ms identifying potentially obfuscated fixed gates
---TIMING--- 8ms identifying potentially intermediary gates
---INFO--- potentially obfuscated fixed and intermediary gates: 200
---TIMING--- 1ms predict leaked inputs
---INFO--- 0 leaked inputs: 
```

### Step 5: CRGC Transformation - Input Obfuscation & Flipping
**File**: `circuit_flipper.py`

**obfuscate_input(inputA)**:
```python
obfuscated_val_arr = [generate_random_bool() for _ in range(len(inputA))]
flipped = [False] * numWires
for i in range(len(inputA)):
    flipped[len(inputA) - 1 - i] = (obfuscated_val_arr[i] != inputA[i])
return obfuscated_val_arr, flipped
```

**get_flipped_circuit(circuit, flipped)**:
```python
for gate in circuit.gates:
    # Recover integrity from parent flips
    if flipped[gate.leftParentID]:
        swap_left_parent(gate.truthTable)
    if flipped[gate.rightParentID]:
        swap_right_parent(gate.truthTable)
    
    # Randomly flip output (except circuit outputs)
    if generate_random_bool() and not is_output_wire(gate.outputID):
        flip_table(gate.truthTable)
        flipped[gate.outputID] = True
```

### Step 6: CRGC Transformation - Fixed Gate Identification
**File**: `circuit_obfuscator.py`

**identify_fixed_gates_arr(circuit, obfuscated_val_arr)**:
```python
is_obfuscated = [False] * circuit.details.numWires
unobfuscated_values = [False] * circuit.details.numWires

# Mark InputA as obfuscated
for i in range(circuit.details.bitlengthInputA):
    unobfuscated_values[i] = obfuscated_val_arr[circuit.details.bitlengthInputA - 1 - i]
    is_obfuscated[i] = True

for gate in circuit.gates:
    if is_obfuscated[gate.leftParentID] and is_obfuscated[gate.rightParentID]:
        # Both parents known
        if not is_circuit_output(gate.outputID):
            unobfuscated_values[gate.outputID] = \
                gate.truthTable[unobfuscated_values[gate.leftParentID]][
                                unobfuscated_values[gate.rightParentID]]
            is_obfuscated[gate.outputID] = True
    
    elif is_obfuscated[gate.leftParentID]:
        # Left parent known, check if output is fixed
        left_val = unobfuscated_values[gate.leftParentID]
        if gate.truthTable[left_val][0] == gate.truthTable[left_val][1]:
            if not is_circuit_output(gate.outputID):
                unobfuscated_values[gate.outputID] = gate.truthTable[left_val][0]
                is_obfuscated[gate.outputID] = True
        else:
            # Recover integrity: copy known column to unknown
            gate.truthTable[not left_val][0] = gate.truthTable[left_val][0]
            gate.truthTable[not left_val][1] = gate.truthTable[left_val][1]
    
    elif is_obfuscated[gate.rightParentID]:
        # Right parent known, check if output is fixed
        right_val = unobfuscated_values[gate.rightParentID]
        if gate.truthTable[0][right_val] == gate.truthTable[1][right_val]:
            if not is_circuit_output(gate.outputID):
                unobfuscated_values[gate.outputID] = gate.truthTable[0][right_val]
                is_obfuscated[gate.outputID] = True
        else:
            # Recover integrity: copy known row to unknown
            gate.truthTable[0][not right_val] = gate.truthTable[0][right_val]
            gate.truthTable[1][not right_val] = gate.truthTable[1][right_val]

return is_obfuscated
```

### Step 7: CRGC Transformation - Intermediary Gates & Regeneration
**File**: `circuit_integrity_breaker.py`

**get_intermediary_gates_from_output(details, is_obfuscated, parents)**:
```python
not_obfuscated = [False] * details.numWires
queue = []

# Start from output wires
for i in range(details.numOutputs):
    for j in range(details.bitlengthOutputs):
        wire_idx = details.numWires - 1 - j - details.bitlengthOutputs * i
        queue.append(wire_idx)

# BFS backward through parents
added = [False] * details.numWires
while queue:
    wire = queue.pop(0)
    not_obfuscated[wire] = True
    
    for parent in parents[wire]:
        if parent >= details.bitlengthInputA + details.bitlengthInputB:
            if not is_obfuscated[parent] and not added[parent]:
                queue.append(parent)
                added[parent] = True

# Invert for gate wires
for wire in range(details.bitlengthInputA + details.bitlengthInputB, details.numWires):
    if wire not in output_wires:
        is_obfuscated[wire] = not not_obfuscated[wire]
```

**regenerate_gates(circuit, is_obfuscated)**:
```python
for gate in circuit.gates:
    if is_obfuscated[gate.outputID]:
        if is_level_1_gate(gate):  # Has input wire as parent
            # Obfuscate to look like XOR (balanced)
            rand_bit = generate_random_bool()
            gate.truthTable = [[rand_bit, not rand_bit], 
                              [not rand_bit, rand_bit]]
        else:
            # Randomize to non-constant gate
            # Avoid 0000 and 1111
            while True:
                tt = [[generate_random_bool(), generate_random_bool()],
                      [generate_random_bool(), generate_random_bool()]]
                # Check has at least one 0 and one 1
                flat = [tt[0][0], tt[0][1], tt[1][0], tt[1][1]]
                if True in flat and False in flat:
                    gate.truthTable = tt
                    break
```

### Step 8: Circuit Writer
**File**: `circuit_writer.py`

**export_circuit_separate_files(circuit, destination_path)**:
```python
# Write _rgc_details.txt
with open(f"{destination_path}_rgc_details.txt", 'w') as f:
    f.write(f"{circuit.details.numGates} {circuit.details.numWires}\n")
    f.write(f"{circuit.details.bitlengthInputA} {circuit.details.bitlengthInputB}\n")
    f.write(f"{circuit.details.numOutputs} {circuit.details.bitlengthOutputs}\n")

# Write _rgc.txt
with open(f"{destination_path}_rgc.txt", 'w') as f:
    for gate in circuit.gates:
        tt = gate.truthTable
        tt_str = f"{int(tt[0][0])}{int(tt[0][1])}{int(tt[1][0])}{int(tt[1][1])}"
        f.write(f"{gate.leftParentID} {gate.rightParentID} {gate.outputID} {tt_str}\n")
```

**export_obfuscated_input(obfuscated_val_arr, details, destination_path)**:
```python
# Write _rgc_inputA.txt
with open(f"{destination_path}_rgc_inputA.txt", 'w') as f:
    binary_str = ''.join(['1' if b else '0' for b in obfuscated_val_arr])
    f.write(binary_str + '\n')
```

### Step 9: Generator Executable
**File**: `generator.py`

```python
import argparse
import time
from pathlib import Path
from crgc import *

def main():
    parser = argparse.ArgumentParser(description='CRGC Generator')
    parser.add_argument('--circuit', default='adder64', help='Circuit name')
    parser.add_argument('--type', default='txt', choices=['txt'], help='Circuit type')
    parser.add_argument('--format', default='bristol', choices=['bristol'], help='Circuit format')
    parser.add_argument('--inputa', default='r', help='Input A (r=random, number, or filename)')
    parser.add_argument('--inputb', default='r', help='Input B (r=random, number, or filename)')
    parser.add_argument('--store', default='txt', choices=['txt', 'off'], help='Storage format')
    parser.add_argument('--use-numpy', action='store_true', help='Use numpy acceleration')
    args = parser.parse_args()
    
    circuit_path = Path('../src/circuits') / f"{args.circuit}.txt"
    
    # Step 1: Load circuit
    t1 = time.time()
    details = import_bristol_circuit_details(circuit_path)
    circuit = import_bristol_circuit_ex_not(circuit_path, details)
    print(f"---TIMING--- {int((time.time()-t1)*1000)}ms converting program to circuit")
    print(f"---INFO--- numGates: {circuit.details.numGates}")
    
    # Step 2: Predict leakage (diagnostics)
    t1 = time.time()
    parents = get_parents_of_each_wire(circuit)
    print(f"---TIMING--- {int((time.time()-t1)*1000)}ms getting Parents of each Wire")
    
    po = [False] * circuit.details.numWires
    t1 = time.time()
    get_potentially_obfuscated_fixed_gates(circuit, po)
    print(f"---TIMING--- {int((time.time()-t1)*1000)}ms identifying potentially obfuscated fixed gates")
    
    t1 = time.time()
    get_potentially_intermediary_gates_from_output(circuit.details, po, parents)
    print(f"---TIMING--- {int((time.time()-t1)*1000)}ms identifying potentially intermediary gates")
    
    poc = sum(po) - circuit.details.bitlengthInputA
    print(f"---INFO--- potentially obfuscated fixed and intermediary gates: {poc}")
    
    t1 = time.time()
    leaked = get_leaked_inputs(circuit, po)
    print(f"---TIMING--- {int((time.time()-t1)*1000)}ms predict leaked inputs")
    print(f"---INFO--- {len(leaked)} leaked inputs: {' '.join(map(str, leaked))}")
    
    # Step 3: Parse inputs
    inputA = parse_input(args.inputa, circuit.details.bitlengthInputA, args.circuit, 'A')
    inputB = parse_input(args.inputb, circuit.details.bitlengthInputB, args.circuit, 'B')
    
    # Step 4: Evaluate original circuit
    t1 = time.time()
    original_output = evaluate_transformed_circuit(circuit, inputA, inputB)
    print(f"---TIMING--- {int((time.time()-t1)*1000)}ms evaluate circuit")
    print(f"---Evaluation--- inA{bool_array_to_int(inputA)}")
    print(f"---Evaluation--- inB{bool_array_to_int(inputB)}")
    print(f"---Evaluation--- out{bool_array_to_int(original_output)}")
    
    # Step 5: Obfuscate input and flip circuit
    obfuscated_val_arr, flipped = obfuscate_input(inputA, circuit.details.numWires)
    
    t1 = time.time()
    get_flipped_circuit(circuit, flipped)
    print(f"---TIMING--- {int((time.time()-t1)*1000)}ms flip circuit")
    
    # Step 6: Identify fixed gates
    t1 = time.time()
    is_obfuscated = identify_fixed_gates_arr(circuit, obfuscated_val_arr)
    print(f"---TIMING--- {int((time.time()-t1)*1000)}ms identify fixed Gates")
    obf_count = sum(is_obfuscated)
    print(f"---INFO--- obfuscated gates: {obf_count}")
    
    # Step 7: Identify intermediary gates
    t1 = time.time()
    get_intermediary_gates_from_output(circuit.details, is_obfuscated, parents)
    print(f"---TIMING--- {int((time.time()-t1)*1000)}ms identify intermediary gates")
    final_obf = sum(is_obfuscated) - circuit.details.bitlengthInputA
    print(f"---INFO--- obfuscated fixed and intermediary gates: {final_obf}")
    
    # Step 8: Regenerate obfuscated gates
    t1 = time.time()
    regenerate_gates(circuit, is_obfuscated)
    print(f"---TIMING--- {int((time.time()-t1)*1000)}ms obfuscate gates")
    
    # Step 9: Verify integrity
    rgc_output = evaluate_transformed_circuit(circuit, obfuscated_val_arr, inputB)
    if rgc_output == original_output:
        print("---Success--- Evaluation of original circuit and constructed RGC are equal")
    else:
        print("---Error--- RGC output does not match original!")
    
    print(f"---Evaluation--- inA{bool_array_to_int(obfuscated_val_arr)}")
    print(f"---Evaluation--- inB{bool_array_to_int(inputB)}")
    print(f"---Evaluation--- out{bool_array_to_int(rgc_output)}")
    
    # Step 10: Export RGC
    if args.store == 'txt':
        t1 = time.time()
        output_path = Path('../src/circuits') / args.circuit
        export_circuit_separate_files(circuit, output_path)
        export_obfuscated_input(obfuscated_val_arr, circuit.details, output_path)
        print(f"---TIMING--- {int((time.time()-t1)*1000)}ms exporting")

if __name__ == '__main__':
    main()
```

### Step 10: Evaluator Executable
**File**: `evaluator.py`

```python
import argparse
import time
from pathlib import Path
from crgc import *

def main():
    parser = argparse.ArgumentParser(description='CRGC Evaluator')
    parser.add_argument('--circuit', required=True, help='Circuit name')
    parser.add_argument('--inputb', default='r', help='Input B (r=random, number, or filename)')
    parser.add_argument('--store', default='txt', choices=['txt'], help='Import format')
    parser.add_argument('--use-numpy', action='store_true', help='Use numpy acceleration')
    args = parser.parse_args()
    
    circuit_path = Path('../src/circuits') / args.circuit
    
    # Step 1: Import RGC
    t1 = time.time()
    details = import_bristol_circuit_details(f"{circuit_path}_rgc_details.txt", format='rgc')
    circuit = import_transformed_circuit(f"{circuit_path}_rgc.txt", details)
    obfuscated_val_arr = import_obfuscated_input(f"{circuit_path}_rgc_inputA.txt", 
                                                   details.bitlengthInputA)
    print(f"---TIMING--- {int((time.time()-t1)*1000)}ms importing")
    
    # Step 2: Parse input B
    inputB = parse_input(args.inputb, details.bitlengthInputB, args.circuit, 'B')
    
    # Step 3: Evaluate CRGC
    t1 = time.time()
    output = evaluate_transformed_circuit(circuit, obfuscated_val_arr, inputB)
    print(f"---TIMING--- {int((time.time()-t1)*1000)}ms evaluate circuit")
    
    print(f"---Evaluation--- inA{bool_array_to_int(obfuscated_val_arr)}")
    print(f"---Evaluation--- inB{bool_array_to_int(inputB)}")
    print(f"---Evaluation--- out{bool_array_to_int(output)}")

if __name__ == '__main__':
    main()
```

### Step 11: Test Suite
**File**: `test_crgc.py`

```python
import unittest
from pathlib import Path
from crgc import *

class TestBristolParser(unittest.TestCase):
    def test_adder64_details(self):
        details = import_bristol_circuit_details('../src/circuits/adder64.txt')
        self.assertEqual(details.numGates, 376)
        self.assertEqual(details.numWires, 504)
        self.assertEqual(details.bitlengthInputA, 64)
        self.assertEqual(details.bitlengthInputB, 64)
        self.assertEqual(details.bitlengthOutputs, 64)
    
    def test_adder64_circuit_loads(self):
        details = import_bristol_circuit_details('../src/circuits/adder64.txt')
        circuit = import_bristol_circuit_ex_not('../src/circuits/adder64.txt', details)
        self.assertIsNotNone(circuit)
        self.assertEqual(len(circuit.gates), details.numGates)

class TestCircuitEvaluator(unittest.TestCase):
    def test_adder64_evaluation(self):
        # Test: 10 + 20 = 30
        details = import_bristol_circuit_details('../src/circuits/adder64.txt')
        circuit = import_bristol_circuit_ex_not('../src/circuits/adder64.txt', details)
        
        inputA = int_to_bool_array(10, 64)
        inputB = int_to_bool_array(20, 64)
        output = evaluate_transformed_circuit(circuit, inputA, inputB)
        result = bool_array_to_int(output)
        
        self.assertEqual(result, 30)
    
    def test_adder64_edge_cases(self):
        details = import_bristol_circuit_details('../src/circuits/adder64.txt')
        circuit = import_bristol_circuit_ex_not('../src/circuits/adder64.txt', details)
        
        # Test: 0 + 0 = 0
        inputA = int_to_bool_array(0, 64)
        inputB = int_to_bool_array(0, 64)
        output = evaluate_transformed_circuit(circuit, inputA, inputB)
        self.assertEqual(bool_array_to_int(output), 0)
        
        # Test: MAX + 1 = 0 (overflow)
        max_64 = (1 << 64) - 1
        inputA = int_to_bool_array(max_64, 64)
        inputB = int_to_bool_array(1, 64)
        output = evaluate_transformed_circuit(circuit, inputA, inputB)
        self.assertEqual(bool_array_to_int(output), 0)

class TestRGCRoundTrip(unittest.TestCase):
    def test_adder64_round_trip(self):
        # Load circuit
        details = import_bristol_circuit_details('../src/circuits/adder64.txt')
        circuit = import_bristol_circuit_ex_not('../src/circuits/adder64.txt', details)
        
        # Test inputs
        inputA = int_to_bool_array(42, 64)
        inputB = int_to_bool_array(17, 64)
        
        # Evaluate original
        original_output = evaluate_transformed_circuit(circuit, inputA, inputB)
        
        # Transform to RGC
        obfuscated_val_arr, flipped = obfuscate_input(inputA, circuit.details.numWires)
        get_flipped_circuit(circuit, flipped)
        is_obfuscated = identify_fixed_gates_arr(circuit, obfuscated_val_arr)
        parents = get_parents_of_each_wire(circuit)
        get_intermediary_gates_from_output(circuit.details, is_obfuscated, parents)
        regenerate_gates(circuit, is_obfuscated)
        
        # Verify RGC produces same output
        rgc_output = evaluate_transformed_circuit(circuit, obfuscated_val_arr, inputB)
        self.assertEqual(rgc_output, original_output)
        
        # Export and re-import
        export_circuit_separate_files(circuit, Path('/tmp/test_adder64'))
        export_obfuscated_input(obfuscated_val_arr, circuit.details, Path('/tmp/test_adder64'))
        
        imported_details = import_bristol_circuit_details('/tmp/test_adder64_rgc_details.txt', 
                                                           format='rgc')
        imported_circuit = import_transformed_circuit('/tmp/test_adder64_rgc.txt', 
                                                      imported_details)
        imported_obf = import_obfuscated_input('/tmp/test_adder64_rgc_inputA.txt', 
                                                imported_details.bitlengthInputA)
        
        # Evaluate imported RGC
        final_output = evaluate_transformed_circuit(imported_circuit, imported_obf, inputB)
        self.assertEqual(final_output, original_output)

if __name__ == '__main__':
    unittest.main()
```

**File**: `run_tests.sh`

```bash
#!/bin/bash

echo "Running Python CRGC tests..."

# Run unit tests
python test_crgc.py

# Generate RGC with known inputs
echo ""
echo "Generating adder64 RGC (42 + 17)..."
python generator.py --circuit adder64 --inputa 42 --inputb 17 --store txt

# Evaluate RGC
echo ""
echo "Evaluating adder64 RGC with inputB=17..."
python evaluator.py --circuit adder64 --inputb 17 --store txt

# Test other circuits
echo ""
echo "Testing sub64 circuit (100 - 50)..."
python generator.py --circuit sub64 --inputa 100 --inputb 50 --store txt
python evaluator.py --circuit sub64 --inputb 50 --store txt

echo ""
echo "All tests complete!"
```

## Implementation Checklist

- [ ] Step 1: Implement circuit_structures.py and helper_functions.py
- [ ] Step 2: Implement circuit_reader.py (Bristol parser)
- [ ] Step 3: Implement circuit_evaluator.py
- [ ] Step 4: Implement leakage_predictor.py (diagnostics)
- [ ] Step 5: Implement circuit_flipper.py (obfuscation)
- [ ] Step 6: Implement circuit_obfuscator.py (fixed gates)
- [ ] Step 7: Implement circuit_integrity_breaker.py (intermediary gates)
- [ ] Step 8: Implement circuit_writer.py (export RGC)
- [ ] Step 9: Implement generator.py
- [ ] Step 10: Implement evaluator.py
- [ ] Step 11: Implement test_crgc.py and run_tests.sh
- [ ] Test with adder64.txt (fixed inputs: 42 + 17 = 59)
- [ ] Test with sub64.txt (fixed inputs: 100 - 50 = 50)
- [ ] Test with sha256.txt
- [ ] Verify output format matches C++ exactly
- [ ] Add numpy optimization (optional flag)

## Key C++ Compatibility Notes

1. **Bit reversal**: Inputs and outputs are reversed during circuit evaluation
2. **Wire indexing**: Exact layout must match C++ (InputA, InputB, gates, outputs)
3. **Truth table format**: `truthTable[leftInput][rightInput] = output`
4. **Output messages**: Match C++ format exactly for testing
5. **File formats**: RGC files must be byte-identical to C++ output
6. **Fixed test vectors**: Use deterministic inputs for reproducibility

## Dependencies

- Python 3.8+ (dataclasses, pathlib, secrets)
- Optional: numpy (for acceleration when --use-numpy flag is used)
- No compression libraries needed (txt format only)
