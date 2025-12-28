# Python CRGC Implementation

Python implementation of Completely Reusable Garbled Circuits (CRGC) for Bristol Fashion circuit processing.

## Features

- ✅ Bristol Fashion circuit parser with NOT gate elimination
- ✅ Circuit evaluation engine with C++ compatibility
- ✅ CRGC transformation pipeline (obfuscation, flipping, regeneration)
- ✅ Leakage prediction diagnostics
- ✅ RGC format import/export
- ✅ Comprehensive test suite with fixed test vectors
- ✅ Pure Python implementation (optional numpy acceleration)

## Installation

The project uses `uv` for package management:

```bash
cd python-crgc
# Dependencies are already installed via uv
```

## Project Structure

```
python-crgc/
├── crgc/                      # Core library
│   ├── circuit_structures.py      # Data structures
│   ├── helper_functions.py        # Utility functions
│   ├── circuit_reader.py          # Bristol circuit parser
│   ├── circuit_evaluator.py       # Circuit evaluation
│   ├── circuit_flipper.py         # Input obfuscation
│   ├── circuit_obfuscator.py      # Fixed gate identification
│   ├── circuit_integrity_breaker.py  # Gate regeneration
│   ├── circuit_writer.py          # RGC export
│   └── leakage_predictor.py       # Leakage diagnostics
├── generator.py                # Generator executable
├── evaluator.py                # Evaluator executable
├── test_crgc.py                # Unit tests
├── run_tests.sh                # Test runner
├── IMPLEMENTATION_PLAN.md      # Detailed implementation plan
└── README.md                   # This file
```

## Usage

### Generator

Transform a Bristol Fashion circuit into a CRGC:

```bash
python3 generator.py --circuit adder64 --inputa 42 --inputb 17 --store txt
```

**Options:**
- `--circuit <name>`: Circuit name (default: adder64)
- `--type txt`: Circuit type (only txt supported)
- `--format bristol`: Circuit format (bristol or emp)
- `--inputa <value>`: Input A ("r" for random, integer, or filename)
- `--inputb <value>`: Input B ("r" for random, integer, or filename)
- `--store txt`: Storage format (txt or off)
- `--use-numpy`: Use numpy acceleration (optional)

### Evaluator

Evaluate a CRGC with evaluator's input:

```bash
python3 evaluator.py --circuit adder64 --inputb 17 --store txt
```

**Options:**
- `--circuit <name>`: Circuit name (required)
- `--inputb <value>`: Input B ("r" for random, integer, or filename)
- `--store txt`: Import format (only txt supported)
- `--format bristol`: Circuit format (bristol or emp)
- `--use-numpy`: Use numpy acceleration (optional)

## Examples

### Example 1: 64-bit Addition (42 + 17 = 59)

```bash
# Generate CRGC
python3 generator.py --circuit adder64 --inputa 42 --inputb 17 --store txt

# Evaluate CRGC
python3 evaluator.py --circuit adder64 --inputb 17 --store txt
```

**Output:**
```
---Evaluation--- inA42
---Evaluation--- inB17
---Evaluation--- out59
```

### Example 2: 64-bit Subtraction (100 - 50 = 50)

```bash
# Generate CRGC
python3 generator.py --circuit sub64 --inputa 100 --inputb 50 --store txt

# Evaluate CRGC
python3 evaluator.py --circuit sub64 --inputb 50 --store txt
```

**Output:**
```
---Evaluation--- inA100
---Evaluation--- inB50
---Evaluation--- out50
```

## Testing

### Run Unit Tests

```bash
python3 test_crgc.py
```

### Run Full Test Suite

```bash
./run_tests.sh
```

The test suite includes:
- Bristol circuit parser tests
- Helper function tests
- Circuit evaluator tests (adder64, sub64)
- CRGC round-trip tests
- Leakage prediction tests
- Integration tests with fixed inputs

## Output Format Compatibility

The Python implementation matches C++ output format exactly:

**Diagnostic Messages:**
```
---INFO--- numGates: 376
---TIMING--- 0ms converting program to circuit
---TIMING--- 0ms getting Parents of each Wire
---INFO--- potentially obfuscated fixed and intermediary gates: 249
---INFO--- 64 leaked inputs: 0 1 2 3 ...
---Success--- Evaluation of original circuit and constructed RGC are equal
```

**RGC File Format:**

- `<circuit>_rgc_details.txt`: Circuit metadata (3 lines)
- `<circuit>_rgc.txt`: Gates with truth tables
- `<circuit>_rgc_inputA.txt`: Obfuscated generator input (binary string)

## Implementation Notes

### C++ Compatibility

1. **Bit Reversal**: Inputs and outputs are reversed during circuit evaluation to match C++ behavior
2. **Wire Indexing**: Maintains exact wire numbering (InputA, InputB, gates, outputs)
3. **Truth Table Format**: `truthTable[leftInput][rightInput] = output`
4. **NOT Gate Elimination**: Inline elimination via wire mapping and truth table swapping

### Key Algorithms

1. **Bristol Parser**: Eliminates NOT gates during parsing
2. **Circuit Evaluator**: Gate-by-gate truth table evaluation
3. **Input Obfuscation**: Random obfuscated input generation
4. **Circuit Flipping**: Truth table transformation based on wire flips
5. **Fixed Gate Identification**: Propagates known values through gates
6. **Intermediary Gate Detection**: Backward BFS from outputs
7. **Gate Regeneration**: Randomizes obfuscated truth tables

### Leakage Prediction

The implementation includes diagnostic leakage prediction:
- Identifies potentially obfuscated fixed gates
- Identifies intermediary gates on path to outputs
- Reports leaked input bits

## Performance

Pure Python implementation is fast for typical circuits:
- adder64 (376 gates): <5ms total processing
- sub64 (376 gates): <5ms total processing
- sha256 (larger): varies by circuit size

Optional numpy acceleration available via `--use-numpy` flag.

## Limitations

- Only txt-based Bristol Fashion format (no compression)
- No network transfer (local file I/O only)
- No multi-threading (reserved for future)
- No C++ program compilation (txt circuits only)

## Testing Results

All tests pass with fixed test vectors:

```
✅ 12 unit tests passed
✅ adder64: 42 + 17 = 59
✅ adder64: 100 + 200 = 300
✅ sub64: 100 - 50 = 50
✅ adder64: 0 + 0 = 0
✅ RGC round-trip verified
```

## Contributing

The implementation follows the detailed plan in `IMPLEMENTATION_PLAN.md`.

## License

Same as parent CRGC project.
