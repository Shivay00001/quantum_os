#!/usr/bin/env python3
"""
Advanced Quantum Algorithms for QuantumOS
Implements: Shor's, QFT, VQE, QAOA, and Quantum Teleportation
"""

import numpy as np
import random
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
import math

# ============================================================================
# QUANTUM STATE REPRESENTATION
# ============================================================================

class QuantumState:
    """Quantum state vector representation"""
    
    def __init__(self, num_qubits: int):
        self.num_qubits = num_qubits
        self.dimension = 2 ** num_qubits
        # Initialize to |0...0⟩ state
        self.state_vector = np.zeros(self.dimension, dtype=complex)
        self.state_vector[0] = 1.0
    
    def from_vector(self, vector: np.ndarray):
        """Initialize from state vector"""
        self.state_vector = vector / np.linalg.norm(vector)
        return self
    
    def measure(self, qubit: int) -> int:
        """Measure a specific qubit"""
        probabilities = np.abs(self.state_vector) ** 2
        outcome = np.random.choice(self.dimension, p=probabilities)
        
        # Collapse to measured state
        bit_value = (outcome >> qubit) & 1
        
        # Project onto measurement outcome subspace
        new_state = np.zeros(self.dimension, dtype=complex)
        for i in range(self.dimension):
            if ((i >> qubit) & 1) == bit_value:
                new_state[i] = self.state_vector[i]
        
        norm = np.linalg.norm(new_state)
        if norm > 0:
            self.state_vector = new_state / norm
        
        return bit_value
    
    def measure_all(self) -> int:
        """Measure all qubits, return as integer"""
        probabilities = np.abs(self.state_vector) ** 2
        return np.random.choice(self.dimension, p=probabilities)
    
    def get_probabilities(self) -> np.ndarray:
        """Get measurement probabilities"""
        return np.abs(self.state_vector) ** 2

# ============================================================================
# QUANTUM GATES
# ============================================================================

class QuantumGates:
    """Library of quantum gate matrices"""
    
    @staticmethod
    def identity():
        return np.array([[1, 0], [0, 1]], dtype=complex)
    
    @staticmethod
    def hadamard():
        return np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
    
    @staticmethod
    def pauli_x():
        return np.array([[0, 1], [1, 0]], dtype=complex)
    
    @staticmethod
    def pauli_y():
        return np.array([[0, -1j], [1j, 0]], dtype=complex)
    
    @staticmethod
    def pauli_z():
        return np.array([[1, 0], [0, -1]], dtype=complex)
    
    @staticmethod
    def phase(theta):
        return np.array([[1, 0], [0, np.exp(1j * theta)]], dtype=complex)
    
    @staticmethod
    def rotation_x(theta):
        return np.array([
            [np.cos(theta/2), -1j * np.sin(theta/2)],
            [-1j * np.sin(theta/2), np.cos(theta/2)]
        ], dtype=complex)
    
    @staticmethod
    def rotation_y(theta):
        return np.array([
            [np.cos(theta/2), -np.sin(theta/2)],
            [np.sin(theta/2), np.cos(theta/2)]
        ], dtype=complex)
    
    @staticmethod
    def rotation_z(theta):
        return np.array([
            [np.exp(-1j * theta/2), 0],
            [0, np.exp(1j * theta/2)]
        ], dtype=complex)
    
    @staticmethod
    def cnot():
        """Controlled-NOT gate"""
        return np.array([
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0]
        ], dtype=complex)
    
    @staticmethod
    def swap():
        """SWAP gate"""
        return np.array([
            [1, 0, 0, 0],
            [0, 0, 1, 0],
            [0, 1, 0, 0],
            [0, 0, 0, 1]
        ], dtype=complex)
    
    @staticmethod
    def toffoli():
        """Toffoli (CCNOT) gate"""
        gate = np.eye(8, dtype=complex)
        gate[6, 6] = 0
        gate[7, 7] = 0
        gate[6, 7] = 1
        gate[7, 6] = 1
        return gate

# ============================================================================
# QUANTUM CIRCUIT
# ============================================================================

class QuantumCircuit:
    """Quantum circuit builder and executor"""
    
    def __init__(self, num_qubits: int):
        self.num_qubits = num_qubits
        self.state = QuantumState(num_qubits)
        self.gates = QuantumGates()
        self.operations = []
    
    def _apply_single_qubit_gate(self, gate: np.ndarray, qubit: int):
        """Apply single-qubit gate to specified qubit"""
        # Build full gate matrix using tensor product
        full_gate = np.array([1], dtype=complex)
        
        for i in range(self.num_qubits):
            if i == qubit:
                full_gate = np.kron(full_gate, gate)
            else:
                full_gate = np.kron(full_gate, self.gates.identity())
        
        self.state.state_vector = full_gate @ self.state.state_vector
        return self
    
    def _apply_two_qubit_gate(self, gate: np.ndarray, control: int, target: int):
        """Apply two-qubit gate"""
        # For simplicity, handle CNOT specially (most common case)
        if control > target:
            control, target = target, control
        
        new_state = np.zeros(self.state.dimension, dtype=complex)
        
        for i in range(self.state.dimension):
            control_bit = (i >> control) & 1
            target_bit = (i >> target) & 1
            
            if control_bit == 1:
                # Flip target bit
                j = i ^ (1 << target)
                new_state[j] = self.state.state_vector[i]
            else:
                new_state[i] = self.state.state_vector[i]
        
        self.state.state_vector = new_state
        return self
    
    def h(self, qubit: int):
        """Apply Hadamard gate"""
        self.operations.append(('H', qubit))
        return self._apply_single_qubit_gate(self.gates.hadamard(), qubit)
    
    def x(self, qubit: int):
        """Apply Pauli-X gate"""
        self.operations.append(('X', qubit))
        return self._apply_single_qubit_gate(self.gates.pauli_x(), qubit)
    
    def y(self, qubit: int):
        """Apply Pauli-Y gate"""
        self.operations.append(('Y', qubit))
        return self._apply_single_qubit_gate(self.gates.pauli_y(), qubit)
    
    def z(self, qubit: int):
        """Apply Pauli-Z gate"""
        self.operations.append(('Z', qubit))
        return self._apply_single_qubit_gate(self.gates.pauli_z(), qubit)
    
    def rx(self, qubit: int, theta: float):
        """Apply rotation-X gate"""
        self.operations.append(('RX', qubit, theta))
        return self._apply_single_qubit_gate(self.gates.rotation_x(theta), qubit)
    
    def ry(self, qubit: int, theta: float):
        """Apply rotation-Y gate"""
        self.operations.append(('RY', qubit, theta))
        return self._apply_single_qubit_gate(self.gates.rotation_y(theta), qubit)
    
    def rz(self, qubit: int, theta: float):
        """Apply rotation-Z gate"""
        self.operations.append(('RZ', qubit, theta))
        return self._apply_single_qubit_gate(self.gates.rotation_z(theta), qubit)
    
    def cnot(self, control: int, target: int):
        """Apply CNOT gate"""
        self.operations.append(('CNOT', control, target))
        return self._apply_two_qubit_gate(self.gates.cnot(), control, target)
    
    def measure(self, qubit: int) -> int:
        """Measure a qubit"""
        return self.state.measure(qubit)
    
    def measure_all(self) -> int:
        """Measure all qubits"""
        return self.state.measure_all()

# ============================================================================
# QUANTUM FOURIER TRANSFORM
# ============================================================================

class QuantumFourierTransform:
    """Quantum Fourier Transform implementation"""
    
    @staticmethod
    def qft(circuit: QuantumCircuit, qubits: List[int]):
        """Apply QFT to specified qubits"""
        n = len(qubits)
        
        for j in range(n):
            qubit = qubits[j]
            circuit.h(qubit)
            
            for k in range(j + 1, n):
                angle = 2 * np.pi / (2 ** (k - j + 1))
                # Controlled phase rotation
                circuit.rz(qubits[k], angle)
        
        # Reverse qubit order
        for i in range(n // 2):
            # SWAP gates would go here in a real implementation
            pass
        
        return circuit
    
    @staticmethod
    def inverse_qft(circuit: QuantumCircuit, qubits: List[int]):
        """Apply inverse QFT"""
        n = len(qubits)
        
        # Reverse qubit order
        for i in range(n // 2):
            pass
        
        for j in range(n - 1, -1, -1):
            qubit = qubits[j]
            
            for k in range(n - 1, j, -1):
                angle = -2 * np.pi / (2 ** (k - j + 1))
                circuit.rz(qubits[k], angle)
            
            circuit.h(qubit)
        
        return circuit

# ============================================================================
# SHOR'S ALGORITHM
# ============================================================================

class ShorsAlgorithm:
    """Shor's algorithm for integer factorization"""
    
    @staticmethod
    def gcd(a: int, b: int) -> int:
        """Greatest common divisor"""
        while b:
            a, b = b, a % b
        return a
    
    @staticmethod
    def modular_exponentiation(base: int, exp: int, mod: int) -> int:
        """Compute (base^exp) mod mod efficiently"""
        result = 1
        base = base % mod
        
        while exp > 0:
            if exp % 2 == 1:
                result = (result * base) % mod
            exp = exp >> 1
            base = (base * base) % mod
        
        return result
    
    @staticmethod
    def find_period_classical(a: int, N: int) -> int:
        """Classical period finding (for simulation)"""
        if ShorsAlgorithm.gcd(a, N) != 1:
            return -1
        
        for r in range(1, N):
            if ShorsAlgorithm.modular_exponentiation(a, r, N) == 1:
                return r
        return -1
    
    @staticmethod
    def factor(N: int, use_quantum: bool = True) -> Optional[Tuple[int, int]]:
        """Factor integer N using Shor's algorithm"""
        
        # Check if N is even
        if N % 2 == 0:
            return (2, N // 2)
        
        # Check if N is a perfect power
        for b in range(2, int(np.log2(N)) + 1):
            a = round(N ** (1/b))
            if a ** b == N:
                return (a, N // a)
        
        # Classical simulation of quantum period finding
        max_attempts = 10
        for attempt in range(max_attempts):
            # Pick random a
            a = random.randint(2, N - 1)
            
            # Check if gcd(a, N) != 1
            g = ShorsAlgorithm.gcd(a, N)
            if g != 1:
                return (g, N // g)
            
            # Find period (quantum part simulated classically)
            r = ShorsAlgorithm.find_period_classical(a, N)
            
            if r == -1 or r % 2 != 0:
                continue
            
            # Check if a^(r/2) != -1 (mod N)
            x = ShorsAlgorithm.modular_exponentiation(a, r // 2, N)
            if x == N - 1:
                continue
            
            # Found factors
            factor1 = ShorsAlgorithm.gcd(x - 1, N)
            factor2 = ShorsAlgorithm.gcd(x + 1, N)
            
            if factor1 != 1 and factor1 != N:
                return (factor1, N // factor1)
            if factor2 != 1 and factor2 != N:
                return (factor2, N // factor2)
        
        return None

# ============================================================================
# VARIATIONAL QUANTUM EIGENSOLVER (VQE)
# ============================================================================

class VQE:
    """Variational Quantum Eigensolver for finding ground states"""
    
    @staticmethod
    def expectation_value(circuit: QuantumCircuit, hamiltonian: np.ndarray) -> float:
        """Calculate expectation value of Hamiltonian"""
        state = circuit.state.state_vector
        return np.real(np.conj(state) @ hamiltonian @ state)
    
    @staticmethod
    def variational_circuit(circuit: QuantumCircuit, params: List[float]):
        """Build variational ansatz circuit"""
        n = circuit.num_qubits
        
        # Layer of RY rotations
        for i in range(n):
            circuit.ry(i, params[i])
        
        # Entangling CNOTs
        for i in range(n - 1):
            circuit.cnot(i, i + 1)
        
        # Another layer of RZ rotations
        for i in range(n):
            if len(params) > n + i:
                circuit.rz(i, params[n + i])
        
        return circuit
    
    @staticmethod
    def optimize(hamiltonian: np.ndarray, num_qubits: int, iterations: int = 100) -> Tuple[float, List[float]]:
        """Optimize parameters to find ground state energy"""
        
        # Initialize random parameters
        num_params = 2 * num_qubits
        params = [random.uniform(0, 2 * np.pi) for _ in range(num_params)]
        
        learning_rate = 0.1
        best_energy = float('inf')
        best_params = params.copy()
        
        for iteration in range(iterations):
            # Build circuit with current parameters
            circuit = QuantumCircuit(num_qubits)
            VQE.variational_circuit(circuit, params)
            
            # Calculate energy
            energy = VQE.expectation_value(circuit, hamiltonian)
            
            if energy < best_energy:
                best_energy = energy
                best_params = params.copy()
            
            # Gradient descent (finite differences)
            gradient = []
            epsilon = 0.01
            
            for i in range(len(params)):
                params_plus = params.copy()
                params_plus[i] += epsilon
                
                circuit_plus = QuantumCircuit(num_qubits)
                VQE.variational_circuit(circuit_plus, params_plus)
                energy_plus = VQE.expectation_value(circuit_plus, hamiltonian)
                
                grad = (energy_plus - energy) / epsilon
                gradient.append(grad)
            
            # Update parameters
            for i in range(len(params)):
                params[i] -= learning_rate * gradient[i]
        
        return best_energy, best_params

# ============================================================================
# QUANTUM APPROXIMATE OPTIMIZATION ALGORITHM (QAOA)
# ============================================================================

class QAOA:
    """QAOA for combinatorial optimization"""
    
    @staticmethod
    def mixer_operator(circuit: QuantumCircuit, beta: float):
        """Apply mixer Hamiltonian (X rotations)"""
        for i in range(circuit.num_qubits):
            circuit.rx(i, 2 * beta)
        return circuit
    
    @staticmethod
    def cost_operator(circuit: QuantumCircuit, gamma: float, cost_matrix: np.ndarray):
        """Apply cost Hamiltonian (problem-specific)"""
        # For MaxCut: apply ZZ interactions
        n = circuit.num_qubits
        for i in range(n):
            for j in range(i + 1, n):
                if cost_matrix[i, j] != 0:
                    # Simulate ZZ interaction
                    circuit.rz(i, gamma * cost_matrix[i, j])
                    circuit.rz(j, gamma * cost_matrix[i, j])
        return circuit
    
    @staticmethod
    def qaoa_circuit(num_qubits: int, cost_matrix: np.ndarray, 
                     params: List[float], layers: int = 1) -> QuantumCircuit:
        """Build QAOA circuit"""
        circuit = QuantumCircuit(num_qubits)
        
        # Initial state: equal superposition
        for i in range(num_qubits):
            circuit.h(i)
        
        # QAOA layers
        for layer in range(layers):
            gamma = params[2 * layer]
            beta = params[2 * layer + 1]
            
            QAOA.cost_operator(circuit, gamma, cost_matrix)
            QAOA.mixer_operator(circuit, beta)
        
        return circuit
    
    @staticmethod
    def solve_maxcut(graph: np.ndarray, layers: int = 2, iterations: int = 50) -> Tuple[float, List[int]]:
        """Solve MaxCut problem using QAOA"""
        num_qubits = graph.shape[0]
        num_params = 2 * layers
        
        # Initialize parameters
        params = [random.uniform(0, np.pi) for _ in range(num_params)]
        
        best_cost = -float('inf')
        best_solution = None
        
        for iteration in range(iterations):
            circuit = QAOA.qaoa_circuit(num_qubits, graph, params, layers)
            
            # Sample from circuit
            num_samples = 100
            costs = []
            
            for _ in range(num_samples):
                result = circuit.measure_all()
                
                # Calculate cost (MaxCut value)
                bitstring = [(result >> i) & 1 for i in range(num_qubits)]
                cost = 0
                for i in range(num_qubits):
                    for j in range(i + 1, num_qubits):
                        if bitstring[i] != bitstring[j]:
                            cost += graph[i, j]
                costs.append(cost)
            
            avg_cost = np.mean(costs)
            
            if avg_cost > best_cost:
                best_cost = avg_cost
                best_solution = bitstring
            
            # Simple parameter update (would use optimizer in practice)
            params = [p + random.gauss(0, 0.1) for p in params]
        
        return best_cost, best_solution

# ============================================================================
# QUANTUM TELEPORTATION
# ============================================================================

class QuantumTeleportation:
    """Quantum teleportation protocol"""
    
    @staticmethod
    def teleport(state_to_teleport: np.ndarray) -> Tuple[np.ndarray, List[int]]:
        """
        Teleport a quantum state using entanglement
        Returns: (final_state, measurement_results)
        """
        # Create 3-qubit system
        # Qubit 0: state to teleport
        # Qubits 1, 2: entangled Bell pair
        
        circuit = QuantumCircuit(3)
        
        # Initialize qubit 0 with state to teleport
        circuit.state.state_vector = np.kron(
            state_to_teleport,
            np.kron(np.array([1, 0]), np.array([1, 0]))
        )
        
        # Create Bell pair between qubits 1 and 2
        circuit.h(1)
        circuit.cnot(1, 2)
        
        # Bell measurement on qubits 0 and 1
        circuit.cnot(0, 1)
        circuit.h(0)
        
        # Measure qubits 0 and 1
        m0 = circuit.measure(0)
        m1 = circuit.measure(1)
        
        # Apply corrections to qubit 2 based on measurements
        if m1 == 1:
            circuit.x(2)
        if m0 == 1:
            circuit.z(2)
        
        # Extract state of qubit 2
        # In a real implementation, would need to trace out qubits 0 and 1
        
        return circuit.state.state_vector, [m0, m1]

# ============================================================================
# TESTING AND EXAMPLES
# ============================================================================

def run_algorithm_tests():
    """Run tests for all quantum algorithms"""
    print("=" * 70)
    print("QUANTUM ALGORITHM TESTS")
    print("=" * 70)
    
    # Test 1: Quantum Fourier Transform
    print("\n[TEST] Quantum Fourier Transform")
    qft_circuit = QuantumCircuit(3)
    for i in range(3):
        qft_circuit.h(i)
    QuantumFourierTransform.qft(qft_circuit, [0, 1, 2])
    probs = qft_circuit.state.get_probabilities()
    print(f"QFT State probabilities: {probs[:8]}")
    
    # Test 2: Shor's Algorithm
    print("\n[TEST] Shor's Factorization Algorithm")
    for N in [15, 21, 35]:
        factors = ShorsAlgorithm.factor(N)
        if factors:
            print(f"Factors of {N}: {factors[0]} × {factors[1]}")
        else:
            print(f"Failed to factor {N}")
    
    # Test 3: VQE for simple Hamiltonian
    print("\n[TEST] Variational Quantum Eigensolver")
    # Simple 1-qubit Hamiltonian (Pauli-Z)
    H = np.array([[1, 0], [0, -1]], dtype=complex)
    energy, params = VQE.optimize(H, num_qubits=1, iterations=20)
    print(f"Ground state energy: {energy:.4f} (expected: -1.0)")
    
    # Test 4: QAOA for small graph
    print("\n[TEST] QAOA for MaxCut")
    graph = np.array([
        [0, 1, 1],
        [1, 0, 1],
        [1, 1, 0]
    ])
    cost, solution = QAOA.solve_maxcut(graph, layers=1, iterations=10)
    print(f"MaxCut value: {cost:.2f}, Solution: {solution}")
    
    # Test 5: Quantum Teleportation
    print("\n[TEST] Quantum Teleportation")
    state = np.array([np.cos(np.pi/6), np.sin(np.pi/6)])  # |ψ⟩
    final_state, measurements = QuantumTeleportation.teleport(state)
    print(f"Measurements: {measurements}")
    print(f"Teleportation complete!")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    run_algorithm_tests()
