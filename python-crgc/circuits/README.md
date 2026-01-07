# Python Circuit Functions

This directory contains Python functions that can be compiled to boolean circuits and transformed into CRGCs.

## Usage

Create a Python file with a function named `circuit` that takes two integer arguments and returns an integer:

```python
def circuit(a: int, b: int) -> int:
    """Your circuit logic here"""
    return a + b  # Example: addition
```

Then compile and garble it:

```bash
python3 generator.py --circuit add --type python --inputa 42 --inputb 17 --store txt
```

## Supported Operations

- **Addition**: `a + b`
- **Subtraction**: `a - b`
- **Bitwise XOR**: `a ^ b`
- **Bitwise AND**: `a & b`
- **Bitwise OR**: `a | b`

## Bit Widths

Specify bit widths for inputs and outputs:

```bash
python3 generator.py --circuit add --type python \
    --input-bits-a 32 --input-bits-b 32 --output-bits 32 \
    --inputa 100 --inputb 200 --store txt
```

## Export to Bristol Format

To export the compiled circuit to Bristol Fashion format:

```bash
python3 generator.py --circuit add --type python \
    --export-bristol --store off
```

This creates `../src/circuits/add_python.txt` that can be used with `--type txt`.

## Examples

### Addition (32-bit)
```bash
python3 generator.py --circuit add --type python \
    --input-bits-a 32 --input-bits-b 32 --output-bits 32 \
    --inputa 42 --inputb 17
```

### XOR (64-bit)
```bash
python3 generator.py --circuit xor --type python \
    --inputa 255 --inputb 128
```

### Subtraction (16-bit)
```bash
python3 generator.py --circuit sub --type python \
    --input-bits-a 16 --input-bits-b 16 --output-bits 16 \
    --inputa 100 --inputb 50
```

## Limitations

- Only basic arithmetic and bitwise operations supported
- No control flow (if/else, loops)
- No function calls
- Function must be pure (no side effects)
- Inputs must be integers

## Advanced Example

Create your own circuit:

```python
# circuits/multiply_by_3.py
def circuit(a: int, b: int) -> int:
    """Multiply input a by 3"""
    return a + a + a
```

Then:

```bash
python3 generator.py --circuit multiply_by_3 --type python \
    --inputa 10 --inputb 0 --store txt
```
