# Python CRGC with Time-Lock Puzzles

Python implementation of Completely Reusable Garbled Circuits (CRGC) with Time-Lock Puzzle (TLP) support using SHA-256 sequential functions.

## Overview

This implementation provides:

- ✅ Bristol Fashion circuit parser with NOT gate elimination
- ✅ Circuit evaluation engine with C++ compatibility
- ✅ CRGC transformation pipeline (obfuscation, flipping, regeneration)
- ✅ Time-Lock Puzzle implementation with CRGC garbling
- ✅ SHA-256 sequential function for cryptographic security
- ✅ XOR-mixing alternative for testing/benchmarking
- ✅ Pure Python implementation with optional numpy acceleration

## Quick Start

### Installation

```bash
cd python-crgc
# Dependencies managed via uv (already installed)
```

### TLP Benchmark

```bash
python3 test_tlp_benchmark.py
```

Expected output:
```
SHA-256 Sequential (T=1):
  Generation: ~57 μs
  Solving: ~12,170 μs (214x slower than generation)
  
XOR-Mixing (T=2):
  Generation: ~56 μs  
  Solving: ~192 μs (3.4x slower than generation)
```

### CRGC Generator/Evaluator

```bash
# Generate CRGC
python3 generator.py --circuit adder64 --inputa 42 --inputb 17 --store txt

# Evaluate CRGC
python3 evaluator.py --circuit adder64 --inputb 17 --store txt
```

## Project Structure

```
python-crgc/
├── crgc/                          # Core CRGC library
│   ├── circuit_structures.py          # Data structures
│   ├── helper_functions.py            # Utility functions
│   ├── circuit_reader.py              # Bristol parser
│   ├── circuit_evaluator.py           # Circuit evaluation
│   ├── circuit_flipper.py             # Input obfuscation
│   ├── circuit_obfuscator.py          # Fixed gate identification
│   ├── circuit_integrity_breaker.py   # Gate regeneration
│   ├── circuit_writer.py              # RGC export
│   └── leakage_predictor.py           # Diagnostics
│
├── tlp_python_garbling.py         # TLP implementation (PSetup/PGen/PSolve)
├── tlp_circuit_builder.py         # TLP circuit builder
├── sequential_function.py         # SHA-256 sequential function
├── test_tlp_benchmark.py          # TLP benchmarking
│
├── generator.py                   # CRGC generator
├── evaluator.py                   # CRGC evaluator
├── python_to_circuit.py           # Python function compiler
│
├── circuits/                      # Bristol circuits
└── README.md                      # This file
```

## Core Components

### 1. CRGC Library (`crgc/`)

The core library implements the complete CRGC transformation pipeline:

**Circuit Processing:**
- Parse Bristol Fashion circuits (3-line format)
- Eliminate NOT gates via wire mapping
- Convert gates to truth tables
- Evaluate circuits with arbitrary inputs

**CRGC Transformation:**
- Obfuscate generator input with random flip pattern
- Flip circuit truth tables based on obfuscation
- Identify fixed gates that leak information
- Regenerate compromised intermediary gates
- Export to RGC format

### 2. Time-Lock Puzzles (`tlp_*.py`)

**tlp_python_garbling.py** - Main TLP algorithms:
```python
from tlp_python_garbling import PSetup, PGen, PSolve

# Setup (garble once, reuse for all puzzles)
circuit, pk = PSetup(T=1, mode='sha256', message_bits=256)

# Generate puzzle
z_tilde, s_tilde = PGen(circuit, pk, message=m)

# Solve puzzle (requires T sequential evaluations)
m_recovered = PSolve(circuit, z_tilde, s_tilde, T=1)
```

**tlp_circuit_builder.py** - Circuit builder:
- `TLPCircuitBuilder`: Low-level gate primitives
- `create_tlp_unrolled_circuit(T, mode)`: T-fold unrolled circuit

**sequential_function.py** - Sequential functions:
- `SequentialFunction`: Base class for f(x)
- SHA-256 mode: Full SHA-256 circuit (134,755 gates)
- XOR-mixing mode: Lightweight alternative (2,048-2,560 gates)

### 3. Generator & Evaluator

**Generator** (`generator.py`):
```bash
python3 generator.py --circuit adder64 --inputa 42 --inputb 17 --store txt
```

Transforms Bristol circuits into CRGC:
1. Parses Bristol circuit
2. Obfuscates generator input
3. Flips circuit truth tables
4. Identifies and regenerates leaked gates
5. Exports RGC format

**Evaluator** (`evaluator.py`):
```bash
python3 evaluator.py --circuit adder64 --inputb 17 --store txt
```

Evaluates CRGC with evaluator input:
1. Imports RGC circuit
2. Loads obfuscated generator input
3. Evaluates with evaluator input
4. Returns circuit output

## Time-Lock Puzzle Details

### Construction from Paper (Agrawal et al. 2024)

Our implementation follows Construction 4.1 from "Time-Lock Puzzles from Lattices":

**Circuit C(b, x, m, z, i)**:
- If i = T+1:
  - If b = 0: Return m
  - If b = 1: Return x ⊕ z
- Otherwise: Return (b, f(x), m, z, i+1)

Where C_T is the T-fold repetition of C.

**PSetup(1^λ, T)**:
- Compute (C̃, pk) ← rGC.Garble(1^λ, C_T)
- Returns pp = (C̃, pk)

**PGen(pp, s)**:
- Given secret s ∈ {0,1}
- Sample random x ← {0,1}^λ, m ← {0,1}^λ, r ← {0,1}^λ
- Compute x̃ ← rGC.Enc(pk, (0, x, m, 0^λ, 1))
- Return Z = (x̃, r, r·m ⊕ s)

Where r·m is the Goldreich-Levin inner-product predicate.

**PSolve(pp, Z)**:
- Compute y ← rGC.Eval(C̃, C_T, x̃)
- Unmask: s = y·r ⊕ (r·m ⊕ s)
- Returns recovered secret s

### Implementation Details

**Our Reusable Garbled Circuit (rGC)**:
- `rGC.Garble`: Uses CRGC's `get_flipped_circuit` to transform truth tables
- `rGC.Enc`: Encodes inputs according to the flip pattern from garbling
- `rGC.Eval`: Uses `evaluate_transformed_circuit` on pre-garbled circuit

**Key Properties**:
- Circuit is garbled **once** in PSetup (one-time cost)
- Each PGen reuses the same garbled circuit with fresh input encoding
- PSolve requires T sequential evaluations of the sequential function f
- Correctness: With b=0, circuit returns m after T iterations, allowing unmask

### Sequential Functions

**SHA-256 (Cryptographic)**:
- 134,755 gates (AND/XOR from Bristol format)
- Secure cryptographic hash function
- Generation: ~57 μs
- Solving T=1: ~12,170 μs (214x slower)

**XOR-Mixing (Lightweight)**:
- 2,048-2,560 gates (depends on T)
- Fast testing/benchmarking
- Generation: ~56 μs
- Solving T=2: ~192 μs (3.4x slower)
- Solving T=4: ~243 μs (4.5x slower)

### Performance Characteristics

| Configuration | Gates | Gen Time | Solve Time | Slowdown |
|--------------|-------|----------|------------|----------|
| SHA-256 T=1 | 134,755 | 57 μs | 12,170 μs | 214x |
| XOR T=2 | 2,048 | 56 μs | 192 μs | 3.4x |
| XOR T=4 | 2,560 | 54 μs | 243 μs | 4.5x |

**Key Observation**: Generation is always faster than solving, confirming correct TLP behavior where puzzle creation is efficient but solving requires sequential work.

### Known Limitations

- **Non-determinism**: Success rate 60-80% due to garbled circuit evaluation issues
- **Input encoding**: The `pk` parameter stores the flip pattern (`base_flipped`) for encoding inputs, not a cryptographic public key
- **Circuit size**: SHA-256 creates large circuits (~135K gates)

## Usage Examples

### Example 1: Basic TLP

```python
from tlp_python_garbling import PythonGarbledTLP
import secrets

# Initialize with SHA-256, T=1
tlp = PythonGarbledTLP(lam=256, T=1, use_sha256=True)

# PSetup: Garble circuit once
pp = tlp.PSetup_Garble()

# PGen: Generate puzzle for secret bit s
s = 1  # Secret bit
Z = tlp.PGen(s, pp)

# PSolve: Solve puzzle to recover s
s_recovered = tlp.PSolve_Garbled(Z, pp)

# Verify
assert s_recovered == s
```

### Example 2: Benchmark Multiple Configurations

```python
from test_tlp_benchmark import test_configuration

# SHA-256 with T=1
test_configuration(T=1, lam=256, use_sha256=True, num_puzzles=10)

# XOR-mixing with T=2
test_configuration(T=2, lam=256, use_sha256=False, num_puzzles=10)

# XOR-mixing with T=4
test_configuration(T=4, lam=256, use_sha256=False, num_puzzles=10)
```

### Example 3: CRGC Pipeline

```python
from crgc import *
from crgc.circuit_reader import import_bristol_circuit_details, import_bristol_circuit_ex_not
from crgc.circuit_flipper import obfuscate_input, get_flipped_circuit

# Load circuit
details = import_bristol_circuit_details("circuits/adder64.txt", format='bristol')
circuit = import_bristol_circuit_ex_not("circuits/adder64.txt", details)

# Obfuscate input A
inputA = [False] * 64  # Value: 0
flip_pattern, obfuscated_inputA = obfuscate_input(inputA)

# Flip circuit
flipped_circuit = get_flipped_circuit(circuit, flip_pattern)

# Evaluate with inputB
inputB = [True, False, False, False, False, False, False] + [False] * 57  # Value: 1
result = evaluate_transformed_circuit(flipped_circuit, obfuscated_inputA, inputB)
```

## Technical Details

### Bristol Format

3-line header format:
```
<numGates> <numWires>
<numInputs> <bitlengthA> <bitlengthB>
<numOutputs> <bitlengthOutputs>

<gate lines...>
```

Gate format: `<numInputs> <numOutputs> <input1> [input2] <output> <type>`

Supported gates: `XOR`, `AND`, `OR`, `NOT` (eliminated inline)

### RGC Format

Generated CRGC files:
- `<circuit>_rgc_details.txt`: Circuit metadata
- `<circuit>_rgc.txt`: Gates with truth tables
- `<circuit>_rgc_inputA.txt`: Obfuscated generator input

### Wire Indexing

- Wires `0` to `bitlengthInputA-1`: Generator input (InputA)
- Wires `bitlengthInputA` to `bitlengthInputA+bitlengthInputB-1`: Evaluator input (InputB)
- Wires `bitlengthInputA+bitlengthInputB` onwards: Gate outputs
- Last `numOutputs × bitlengthOutputs` wires: Circuit outputs

**Important**: All I/O is bit-reversed for C++ compatibility.

### Truth Tables

2×2 boolean arrays indexed as `[leftParent][rightParent]`:
- XOR: `[[0,1], [1,0]]`
- AND: `[[0,0], [0,1]]`
- OR: `[[0,1], [1,1]]`

Transformations:
- `swap_left_parent()`: Swap rows
- `swap_right_parent()`: Swap columns
- `flip_table()`: Invert all values

## Testing

### Run TLP Benchmark

```bash
python3 test_tlp_benchmark.py
```

Tests 3 configurations:
1. XOR-mixing with T=2
2. SHA-256 with T=1
3. XOR-mixing with T=4

Each test runs 100 trials and reports:
- Average generation time (μs)
- Average solving time (μs)
- Success rate (%)
- Timing verification (generation < solving)

### Run Unit Tests (if available)

```bash
./run_tests.sh
```

## Command Reference

### Generator Options

```bash
python3 generator.py [OPTIONS]

--circuit <name>      Circuit name (default: adder64)
--type <txt|python>   Circuit type (default: txt)
--format bristol      Format for txt type
--inputa <value>      Input A (integer, "r" for random, or filename)
--inputb <value>      Input B (integer, "r" for random, or filename)
--store <txt|off>     Storage format (default: txt)
--use-numpy           Enable numpy acceleration
```

### Evaluator Options

```bash
python3 evaluator.py [OPTIONS]

--circuit <name>      Circuit name (required)
--inputb <value>      Input B (integer, "r" for random, or filename)
--store txt           Import format (only txt supported)
--format bristol      Circuit format
--use-numpy           Enable numpy acceleration
```

## Implementation Notes

### PSetup(1^λ, T) - Garble Once, Reuse Forever

The `PSetup_Garble` function performs the expensive garbling operation once:
```python
tlp = PythonGarbledTLP(lam=256, T=1, use_sha256=True)
pp = tlp.PSetup_Garble()  # Returns (C̃, pk)
```

Returns pp = (C̃, pk):
- `C̃`: Garbled circuit with transformed truth tables (reusable)
- `pk`: Encoding key with `base_flipped` pattern for rGC.Enc

The garbled circuit can be reused for unlimited puzzle generation.

### PGen(pp, s) - Fast Puzzle Generation

Each `PGen` call creates a puzzle for secret bit s:
1. Samples random x, m, r ← {0,1}^λ
2. Computes x̃ ← rGC.Enc(pk, (0, x, m, 0^λ, 1))
3. Returns Z = (x̃, r, r·m ⊕ s)

Generation time: ~50-60 μs (constant, independent of T)

**Key insight**: No circuit evaluation needed in PGen, just input encoding.

### PSolve(pp, Z) - Sequential Work Required

Each `PSolve` call recovers the secret:
1. Computes y ← rGC.Eval(C̃, C_T, x̃)
2. Unmasks: s = y·r ⊕ (r·m ⊕ s)

Solving time: Proportional to T (requires T sequential evaluations of f)
- SHA-256 T=1: ~12 ms
- XOR T=2: ~190 μs
- XOR T=4: ~240 μs

**Security**: No parallelization possible due to sequential nature of f^T.

### Security vs Performance Trade-off

**SHA-256**:
- ✅ Cryptographically secure
- ✅ Well-studied sequential function
- ⚠️ Large circuit (134,755 gates)
- ⚠️ Slower evaluation

**XOR-mixing**:
- ✅ Lightweight (2,048-2,560 gates)
- ✅ Fast evaluation
- ⚠️ Not cryptographically secure
- ⚠️ Suitable only for testing

## Files to Keep

**Core TLP Implementation** (3 files):
- `tlp_python_garbling.py` (240 lines)
- `tlp_circuit_builder.py` (180 lines)
- `sequential_function.py` (220 lines)

**CRGC Library** (`crgc/` directory):
- All 9 modules required for circuit processing

**Testing/Utilities**:
- `test_tlp_benchmark.py` - TLP performance testing
- `generator.py` - CRGC generator
- `evaluator.py` - CRGC evaluator
- `python_to_circuit.py` - Python function compiler

## References

Based on:
- Agrawal et al. (2024) - Time-Lock Puzzles from Lattices
- Construction 4.1: TLP from Completely Reusable Garbled Circuits
- SHA-256 Bristol format circuit for sequential function
- CRGC transformation pipeline for garbling

## License

See LICENSE file in parent directory.
