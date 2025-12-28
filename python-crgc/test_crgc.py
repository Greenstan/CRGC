#!/usr/bin/env python3
"""
Comprehensive test suite for Python CRGC implementation
Tests parsing, evaluation, and round-trip transformation
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from crgc import *


class TestBristolParser(unittest.TestCase):
    """Test Bristol Fashion circuit parsing"""
    
    def test_adder64_details(self):
        """Test parsing adder64 circuit metadata"""
        circuit_path = Path(__file__).parent.parent / 'src' / 'circuits' / 'adder64.txt'
        details = import_bristol_circuit_details(str(circuit_path))
        
        self.assertEqual(details.numGates, 376)
        self.assertEqual(details.numWires, 504)
        self.assertEqual(details.bitlengthInputA, 64)
        self.assertEqual(details.bitlengthInputB, 64)
        self.assertEqual(details.bitlengthOutputs, 64)
    
    def test_adder64_circuit_loads(self):
        """Test loading adder64 circuit"""
        circuit_path = Path(__file__).parent.parent / 'src' / 'circuits' / 'adder64.txt'
        details = import_bristol_circuit_details(str(circuit_path))
        circuit = import_bristol_circuit_ex_not(str(circuit_path), details)
        
        self.assertIsNotNone(circuit)
        self.assertEqual(len(circuit.gates), circuit.details.numGates)


class TestHelperFunctions(unittest.TestCase):
    """Test helper utility functions"""
    
    def test_int_to_bool_array(self):
        """Test integer to boolean array conversion"""
        arr = int_to_bool_array(5, 8)
        expected = [False, False, False, False, False, True, False, True]  # 00000101
        self.assertEqual(arr, expected)
    
    def test_bool_array_to_int(self):
        """Test boolean array to integer conversion"""
        arr = [False, False, False, False, False, True, False, True]  # 00000101
        num = bool_array_to_int(arr)
        self.assertEqual(num, 5)
    
    def test_round_trip_conversion(self):
        """Test round-trip integer ↔ bool array conversion"""
        for num in [0, 1, 42, 100, 255, 1000, 2**16 - 1]:
            arr = int_to_bool_array(num, 32)
            result = bool_array_to_int(arr)
            self.assertEqual(num, result)


class TestCircuitEvaluator(unittest.TestCase):
    """Test circuit evaluation"""
    
    def test_adder64_basic(self):
        """Test adder64: 10 + 20 = 30"""
        circuit_path = Path(__file__).parent.parent / 'src' / 'circuits' / 'adder64.txt'
        details = import_bristol_circuit_details(str(circuit_path))
        circuit = import_bristol_circuit_ex_not(str(circuit_path), details)
        
        inputA = int_to_bool_array(10, 64)
        inputB = int_to_bool_array(20, 64)
        output = evaluate_transformed_circuit(circuit, inputA, inputB)
        result = bool_array_to_int(output)
        
        self.assertEqual(result, 30)
    
    def test_adder64_edge_cases(self):
        """Test adder64 edge cases"""
        circuit_path = Path(__file__).parent.parent / 'src' / 'circuits' / 'adder64.txt'
        details = import_bristol_circuit_details(str(circuit_path))
        circuit = import_bristol_circuit_ex_not(str(circuit_path), details)
        
        # Test: 0 + 0 = 0
        inputA = int_to_bool_array(0, 64)
        inputB = int_to_bool_array(0, 64)
        output = evaluate_transformed_circuit(circuit, inputA, inputB)
        self.assertEqual(bool_array_to_int(output), 0)
        
        # Test: 100 + 200 = 300
        inputA = int_to_bool_array(100, 64)
        inputB = int_to_bool_array(200, 64)
        output = evaluate_transformed_circuit(circuit, inputA, inputB)
        self.assertEqual(bool_array_to_int(output), 300)
    
    def test_sub64_basic(self):
        """Test sub64: 100 - 50 = 50"""
        circuit_path = Path(__file__).parent.parent / 'src' / 'circuits' / 'sub64.txt'
        if not circuit_path.exists():
            self.skipTest("sub64.txt not found")
        
        details = import_bristol_circuit_details(str(circuit_path))
        circuit = import_bristol_circuit_ex_not(str(circuit_path), details)
        
        inputA = int_to_bool_array(100, 64)
        inputB = int_to_bool_array(50, 64)
        output = evaluate_transformed_circuit(circuit, inputA, inputB)
        result = bool_array_to_int(output)
        
        self.assertEqual(result, 50)


class TestRGCRoundTrip(unittest.TestCase):
    """Test CRGC transformation round-trip"""
    
    def test_adder64_round_trip(self):
        """Test adder64 full CRGC round-trip: 42 + 17 = 59"""
        circuit_path = Path(__file__).parent.parent / 'src' / 'circuits' / 'adder64.txt'
        details = import_bristol_circuit_details(str(circuit_path))
        circuit = import_bristol_circuit_ex_not(str(circuit_path), details)
        
        # Test inputs
        inputA = int_to_bool_array(42, 64)
        inputB = int_to_bool_array(17, 64)
        
        # Evaluate original circuit
        original_output = evaluate_transformed_circuit(circuit, inputA, inputB)
        self.assertEqual(bool_array_to_int(original_output), 59)
        
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
        self.assertEqual(bool_array_to_int(rgc_output), 59)
    
    def test_adder64_export_import(self):
        """Test exporting and importing RGC files"""
        import tempfile
        import shutil
        
        circuit_path = Path(__file__).parent.parent / 'src' / 'circuits' / 'adder64.txt'
        details = import_bristol_circuit_details(str(circuit_path))
        circuit = import_bristol_circuit_ex_not(str(circuit_path), details)
        
        inputA = int_to_bool_array(42, 64)
        inputB = int_to_bool_array(17, 64)
        
        # Transform to RGC
        obfuscated_val_arr, flipped = obfuscate_input(inputA, circuit.details.numWires)
        get_flipped_circuit(circuit, flipped)
        is_obfuscated = identify_fixed_gates_arr(circuit, obfuscated_val_arr)
        parents = get_parents_of_each_wire(circuit)
        get_intermediary_gates_from_output(circuit.details, is_obfuscated, parents)
        regenerate_gates(circuit, is_obfuscated)
        
        original_output = evaluate_transformed_circuit(circuit, obfuscated_val_arr, inputB)
        
        # Export to temporary directory
        with tempfile.TemporaryDirectory() as tmpdir:
            export_path = Path(tmpdir) / 'test_adder64'
            export_circuit_separate_files(circuit, export_path)
            export_obfuscated_input(obfuscated_val_arr, circuit.details, export_path)
            
            # Import back
            imported_details = import_bristol_circuit_details(
                str(export_path.parent / f"{export_path.name}_rgc_details.txt"), 
                format='rgc'
            )
            imported_circuit = import_transformed_circuit(
                str(export_path.parent / f"{export_path.name}_rgc.txt"), 
                imported_details
            )
            imported_obf = import_obfuscated_input(
                str(export_path.parent / f"{export_path.name}_rgc_inputA.txt"), 
                imported_details.bitlengthInputA
            )
            
            # Evaluate imported RGC
            final_output = evaluate_transformed_circuit(imported_circuit, imported_obf, inputB)
            
            # Verify output matches
            self.assertEqual(final_output, original_output)
            self.assertEqual(bool_array_to_int(final_output), 59)


class TestLeakagePrediction(unittest.TestCase):
    """Test leakage prediction diagnostics"""
    
    def test_parent_tracking(self):
        """Test parent tracking array construction"""
        circuit_path = Path(__file__).parent.parent / 'src' / 'circuits' / 'adder64.txt'
        details = import_bristol_circuit_details(str(circuit_path))
        circuit = import_bristol_circuit_ex_not(str(circuit_path), details)
        
        parents = get_parents_of_each_wire(circuit)
        
        self.assertEqual(len(parents), circuit.details.numWires)
        
        # Verify parent relationships
        for gate in circuit.gates:
            self.assertEqual(parents[gate.outputID][0], gate.leftParentID)
            self.assertEqual(parents[gate.outputID][1], gate.rightParentID)
    
    def test_potentially_obfuscated_gates(self):
        """Test identification of potentially obfuscated gates"""
        circuit_path = Path(__file__).parent.parent / 'src' / 'circuits' / 'adder64.txt'
        details = import_bristol_circuit_details(str(circuit_path))
        circuit = import_bristol_circuit_ex_not(str(circuit_path), details)
        
        po = [False] * circuit.details.numWires
        get_potentially_obfuscated_fixed_gates(circuit, po)
        
        # InputA wires should be marked as potentially obfuscated
        for i in range(circuit.details.bitlengthInputA):
            self.assertTrue(po[i])
        
        # Some gates should be potentially obfuscated
        obf_count = sum(po)
        self.assertGreater(obf_count, circuit.details.bitlengthInputA)


def run_tests():
    """Run all tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestBristolParser))
    suite.addTests(loader.loadTestsFromTestCase(TestHelperFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestCircuitEvaluator))
    suite.addTests(loader.loadTestsFromTestCase(TestRGCRoundTrip))
    suite.addTests(loader.loadTestsFromTestCase(TestLeakagePrediction))
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
