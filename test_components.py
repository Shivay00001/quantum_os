#!/usr/bin/env python3
"""
QuantumOS GUI Test - Verify all components work
"""

import sys
import os

print("=" * 60)
print("QuantumOS Component Test")
print("=" * 60)

# Test 1: Tkinter
print("\n[TEST 1] Tkinter GUI Library")
try:
    import tkinter as tk
    print("✓ Tkinter available")
    
    # Test window creation
    root = tk.Tk()
    root.title("Test")
    root.withdraw()  # Hide window
    root.destroy()
    print("✓ Window creation works")
except Exception as e:
    print(f"✗ Tkinter error: {e}")

# Test 2: NumPy
print("\n[TEST 2] NumPy for Quantum Math")
try:
    import numpy as np
    print(f"✓ NumPy {np.__version__} available")
    
    # Test quantum state vector
    state = np.array([1, 0], dtype=complex)
    prob = np.abs(state) ** 2
    print(f"✓ Quantum math works: {prob}")
except Exception as e:
    print(f"✗ NumPy error: {e}")

# Test 3: Quantum Algorithms Module
print("\n[TEST 3] Quantum Algorithms Module")
try:
    from quantum_algorithms import ShorsAlgorithm, QuantumCircuit
    result = ShorsAlgorithm.factor(15)
    if result:
        print(f"✓ Shor's algorithm: 15 = {result[0]} × {result[1]}")
    else:
        print("✗ Shor's algorithm failed")
except Exception as e:
    print(f"✗ Quantum module error: {e}")

# Test 4: Network Stack
print("\n[TEST 4] Network Stack Module")
try:
    from network_stack import NetworkStack, DNS
    network = NetworkStack()
    ip = network.dns.query("localhost")
    print(f"✓ DNS lookup: localhost → {ip}")
except Exception as e:
    print(f"✗ Network module error: {e}")

# Test 5: QuantumOS Kernel
print("\n[TEST 5] QuantumOS Kernel")
try:
    from quantum_os_advanced import QuantumOSAdvanced, Architecture
    kernel = QuantumOSAdvanced(Architecture.X86_64)
    print(f"✓ Kernel v{kernel.VERSION} initialized")
    
    # Test command execution
    result = kernel.execute_command("uname")
    print(f"✓ Command execution: {result.strip()}")
except Exception as e:
    print(f"✗ Kernel error: {e}")

print("\n" + "=" * 60)
print("Test Complete!")
print("=" * 60)
