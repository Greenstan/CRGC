#!/bin/bash
# Test runner for Python CRGC implementation
# Runs unit tests and integration tests with fixed test vectors

set -e  # Exit on error

echo "========================================="
echo "Python CRGC Test Suite"
echo "========================================="
echo ""

# Run unit tests
echo "Running unit tests..."
echo "-------------------------------------"
python3 test_crgc.py
echo ""

# Integration tests with fixed inputs
echo "========================================="
echo "Integration Tests (Fixed Inputs)"
echo "========================================="
echo ""

# Test 1: adder64 (42 + 17 = 59)
echo "Test 1: adder64 circuit (42 + 17 = 59)"
echo "-------------------------------------"
python3 generator.py --circuit adder64 --inputa 42 --inputb 17 --store txt
echo ""
python3 evaluator.py --circuit adder64 --inputb 17 --store txt
echo ""

# Test 2: adder64 different inputs (100 + 200 = 300)
echo "Test 2: adder64 circuit (100 + 200 = 300)"
echo "-------------------------------------"
python3 generator.py --circuit adder64 --inputa 100 --inputb 200 --store txt
echo ""
python3 evaluator.py --circuit adder64 --inputb 200 --store txt
echo ""

# Test 3: sub64 if it exists (100 - 50 = 50)
if [ -f "../src/circuits/sub64.txt" ]; then
    echo "Test 3: sub64 circuit (100 - 50 = 50)"
    echo "-------------------------------------"
    python3 generator.py --circuit sub64 --inputa 100 --inputb 50 --store txt
    echo ""
    python3 evaluator.py --circuit sub64 --inputb 50 --store txt
    echo ""
fi

# Test 4: Edge case - zeros
echo "Test 4: adder64 edge case (0 + 0 = 0)"
echo "-------------------------------------"
python3 generator.py --circuit adder64 --inputa 0 --inputb 0 --store txt
echo ""
python3 evaluator.py --circuit adder64 --inputb 0 --store txt
echo ""

echo "========================================="
echo "All tests completed successfully!"
echo "========================================="
