# Python CRGC - Quick Reference

## Quick Start

```bash
# Run tests
./run_tests.sh

# Generate CRGC
python3 generator.py --circuit adder64 --inputa 42 --inputb 17 --store txt

# Evaluate CRGC  
python3 evaluator.py --circuit adder64 --inputb 17 --store txt
```

## Common Commands

### Generator
```bash
# Random inputs
python3 generator.py --circuit adder64 --inputa r --inputb r --store txt

# Specific values
python3 generator.py --circuit adder64 --inputa 100 --inputb 200 --store txt

# No storage (verify only)
python3 generator.py --circuit adder64 --inputa 42 --inputb 17 --store off
```

### Evaluator
```bash
# Random evaluator input
python3 evaluator.py --circuit adder64 --inputb r --store txt

# Specific value
python3 evaluator.py --circuit adder64 --inputb 17 --store txt
```

## Project Files

**Core Library:**
- `crgc/circuit_structures.py` - Data structures
- `crgc/circuit_reader.py` - Bristol parser
- `crgc/circuit_evaluator.py` - Evaluation engine
- `crgc/circuit_obfuscator.py` - Obfuscation logic
- `crgc/circuit_writer.py` - RGC export

**Executables:**
- `generator.py` - Transform circuits to CRGC
- `evaluator.py` - Evaluate CRGC

**Tests:**
- `test_crgc.py` - Unit tests
- `run_tests.sh` - Integration tests

**Documentation:**
- `README.md` - Full documentation
- `IMPLEMENTATION_PLAN.md` - Detailed plan
- `SUMMARY.md` - Implementation summary
- `QUICK_REFERENCE.md` - This file

## Output Files

After running generator with `--store txt`:
- `<circuit>_rgc_details.txt` - Metadata
- `<circuit>_rgc.txt` - Gates
- `<circuit>_rgc_inputA.txt` - Obfuscated input

## Supported Circuits

- `adder64.txt` - 64-bit addition
- `sub64.txt` - 64-bit subtraction
- `sha256.txt` - SHA-256 hash (if available)
- Any Bristol Fashion circuit in `../src/circuits/`

## Example Outputs

### adder64: 42 + 17 = 59
```
---Evaluation--- inA42
---Evaluation--- inB17
---Evaluation--- out59
```

### sub64: 100 - 50 = 50
```
---Evaluation--- inA100
---Evaluation--- inB50
---Evaluation--- out50
```

## Troubleshooting

**Circuit file not found:**
```
Error: Circuit file not found: ../src/circuits/mycircuit.txt
```
→ Check circuit name and ensure file exists

**Invalid input:**
```
Error parsing inputs: Could not parse input: xyz
```
→ Use "r", integer, or valid filename

**Import error:**
```
Error: RGC details file not found
```
→ Run generator first with `--store txt`

## Testing

```bash
# Unit tests only
python3 test_crgc.py

# Full test suite
./run_tests.sh

# Specific test
python3 -m unittest test_crgc.TestCircuitEvaluator.test_adder64_basic
```

## Python API Usage

```python
from crgc import *

# Load circuit
details = import_bristol_circuit_details('adder64.txt')
circuit = import_bristol_circuit_ex_not('adder64.txt', details)

# Prepare inputs
inputA = int_to_bool_array(42, 64)
inputB = int_to_bool_array(17, 64)

# Evaluate
output = evaluate_transformed_circuit(circuit, inputA, inputB)
result = bool_array_to_int(output)  # 59

# Transform to CRGC
obf_arr, flipped = obfuscate_input(inputA, circuit.details.numWires)
get_flipped_circuit(circuit, flipped)
is_obf = identify_fixed_gates_arr(circuit, obf_arr)
parents = get_parents_of_each_wire(circuit)
get_intermediary_gates_from_output(circuit.details, is_obf, parents)
regenerate_gates(circuit, is_obf)

# Export
export_circuit_separate_files(circuit, Path('output'))
export_obfuscated_input(obf_arr, circuit.details, Path('output'))
```

## Command Line Options

### Generator
- `--circuit <name>` - Circuit name (default: adder64)
- `--type txt` - Circuit type
- `--format bristol` - Circuit format (bristol/emp)
- `--inputa <val>` - Input A (r/int/file)
- `--inputb <val>` - Input B (r/int/file)
- `--store txt|off` - Storage (default: txt)
- `--use-numpy` - Enable numpy (optional)

### Evaluator
- `--circuit <name>` - Circuit name (required)
- `--inputb <val>` - Input B (r/int/file)
- `--store txt` - Import format
- `--format bristol` - Circuit format
- `--use-numpy` - Enable numpy (optional)

## Performance Tips

1. Pure Python is fast enough for most circuits (<5ms)
2. Use `--use-numpy` for very large circuits (if needed)
3. File I/O is typically the slowest part
4. Leakage prediction adds minimal overhead

## Implementation Status

✅ Bristol circuit parsing
✅ Circuit evaluation  
✅ CRGC transformation
✅ Leakage prediction
✅ RGC import/export
✅ Comprehensive tests
✅ C++ compatibility

❌ Compression (txt only)
❌ Network transfer (files only)
❌ Multi-threading (future)
