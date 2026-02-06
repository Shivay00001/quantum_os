#!/usr/bin/env python3
"""
Quantum Circuit Designer GUI for QuantumOS
Visual drag-and-drop quantum circuit builder with state visualization
"""

import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from typing import List, Tuple, Dict, Optional
import math

# Import quantum algorithms module
try:
    from quantum_algorithms import QuantumCircuit, QuantumGates, QuantumState
except ImportError:
    print("Warning: quantum_algorithms module not found, using simplified version")
    QuantumCircuit = None

# ============================================================================
# QUANTUM GATE VISUALIZATION
# ============================================================================

class GateShape:
    """Visual representation of quantum gates"""
    
    COLORS = {
        'H': '#4A90E2',      # Blue
        'X': '#E24A4A',      # Red
        'Y': '#E2A54A',      # Orange
        'Z': '#9B4AE2',      # Purple
        'CNOT': '#4AE290',   # Green
        'SWAP': '#E24A90',   # Pink
        'RX': '#4ACCE2',     # Cyan
        'RY': '#CCE24A',     # Yellow-green
        'RZ': '#E2CC4A',     # Yellow
        'MEASURE': '#888888' # Gray
    }
    
    @staticmethod
    def draw_single_gate(canvas, x, y, gate_type, size=40):
        """Draw a single-qubit gate"""
        color = GateShape.COLORS.get(gate_type, '#CCCCCC')
        
        # Draw rectangle
        rect = canvas.create_rectangle(
            x - size//2, y - size//2,
            x + size//2, y + size//2,
            fill=color, outline='black', width=2
        )
        
        # Draw label
        text = canvas.create_text(
            x, y, text=gate_type,
            font=('Arial', 10, 'bold'), fill='white'
        )
        
        return [rect, text]
    
    @staticmethod
    def draw_cnot(canvas, x, y_control, y_target, size=40):
        """Draw CNOT gate"""
        items = []
        
        # Control dot
        dot = canvas.create_oval(
            x - 8, y_control - 8,
            x + 8, y_control + 8,
            fill='black', outline='black'
        )
        items.append(dot)
        
        # Connecting line
        line = canvas.create_line(
            x, y_control, x, y_target,
            fill='black', width=2
        )
        items.append(line)
        
        # Target (X gate)
        circle = canvas.create_oval(
            x - size//2, y_target - size//2,
            x + size//2, y_target + size//2,
            fill=GateShape.COLORS['CNOT'], outline='black', width=2
        )
        items.append(circle)
        
        # Plus sign
        plus_v = canvas.create_line(
            x, y_target - size//3,
            x, y_target + size//3,
            fill='white', width=2
        )
        plus_h = canvas.create_line(
            x - size//3, y_target,
            x + size//3, y_target,
            fill='white', width=2
        )
        items.extend([plus_v, plus_h])
        
        return items

# ============================================================================
# CIRCUIT EDITOR
# ============================================================================

class CircuitEditor(tk.Frame):
    """Visual quantum circuit editor"""
    
    def __init__(self, parent, num_qubits=3):
        super().__init__(parent)
        self.num_qubits = num_qubits
        self.circuit_gates = []  # List of (gate_type, qubit, column, params)
        self.num_columns = 10
        
        self.qubit_spacing = 60
        self.column_spacing = 80
        self.start_x = 100
        self.start_y = 50
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create circuit editor widgets"""
        # Create canvas for circuit
        self.canvas = tk.Canvas(
            self, width=1000, height=self.num_qubits * self.qubit_spacing + 100,
            bg='white', highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        # Draw qubit lines
        for i in range(self.num_qubits):
            y = self.start_y + i * self.qubit_spacing
            
            # Qubit label
            self.canvas.create_text(
                self.start_x - 60, y,
                text=f'|q{i}⟩',
                font=('Arial', 12, 'bold')
            )
            
            # Qubit wire
            self.canvas.create_line(
                self.start_x, y,
                self.start_x + self.num_columns * self.column_spacing, y,
                fill='black', width=2
            )
    
    def add_gate(self, gate_type: str, qubit: int, column: int, params: Optional[List] = None):
        """Add a gate to the circuit"""
        if qubit >= self.num_qubits or column >= self.num_columns:
            return False
        
        x = self.start_x + column * self.column_spacing
        y = self.start_y + qubit * self.qubit_spacing
        
        # Draw gate
        if gate_type in ['H', 'X', 'Y', 'Z', 'RX', 'RY', 'RZ']:
            GateShape.draw_single_gate(self.canvas, x, y, gate_type)
        elif gate_type == 'CNOT' and params and len(params) > 0:
            target_qubit = params[0]
            y_target = self.start_y + target_qubit * self.qubit_spacing
            GateShape.draw_cnot(self.canvas, x, y, y_target)
        
        # Store gate
        self.circuit_gates.append((gate_type, qubit, column, params))
        return True
    
    def clear_circuit(self):
        """Clear all gates from circuit"""
        self.canvas.delete('all')
        self.circuit_gates = []
        self._create_widgets()
    
    def get_circuit(self) -> List[Tuple]:
        """Get the circuit as a list of gates"""
        # Sort by column
        sorted_gates = sorted(self.circuit_gates, key=lambda g: g[2])
        return sorted_gates

# ============================================================================
# STATE VISUALIZER
# ============================================================================

class StateVisualizer(tk.Frame):
    """Visualize quantum state"""
    
    def __init__(self, parent, num_qubits=3):
        super().__init__(parent)
        self.num_qubits = num_qubits
        self.dimension = 2 ** num_qubits
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create visualization widgets"""
        # Canvas for bar chart
        self.canvas = tk.Canvas(
            self, width=600, height=300,
            bg='white', highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
    
    def update_state(self, state_vector: np.ndarray):
        """Update visualization with new state"""
        self.canvas.delete('all')
        
        probabilities = np.abs(state_vector) ** 2
        
        # Draw bar chart
        bar_width = 600 / self.dimension
        max_height = 250
        
        for i, prob in enumerate(probabilities):
            height = prob * max_height
            x = i * bar_width
            
            # Draw bar
            color = '#4A90E2' if prob > 0.01 else '#CCCCCC'
            self.canvas.create_rectangle(
                x + 2, 280 - height,
                x + bar_width - 2, 280,
                fill=color, outline='black'
            )
            
            # Draw basis state label
            if self.dimension <= 16:  # Only show labels for small systems
                basis = format(i, f'0{self.num_qubits}b')
                self.canvas.create_text(
                    x + bar_width/2, 290,
                    text=f'|{basis}⟩',
                    font=('Arial', 8),
                    angle=45
                )
            
            # Show probability value if significant
            if prob > 0.01:
                self.canvas.create_text(
                    x + bar_width/2, 270 - height - 10,
                    text=f'{prob:.3f}',
                    font=('Arial', 8)
                )

# ============================================================================
# BLOCH SPHERE (SINGLE QUBIT)
# ============================================================================

class BlochSphere(tk.Frame):
    """3D-style Bloch sphere visualization"""
    
    def __init__(self, parent):
        super().__init__(parent)
        self._create_widgets()
    
    def _create_widgets(self):
        """Create Bloch sphere canvas"""
        self.canvas = tk.Canvas(
            self, width=300, height=300,
            bg='white', highlightthickness=0
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)
        
        self.center_x = 150
        self.center_y = 150
        self.radius = 100
        
        self._draw_sphere()
    
    def _draw_sphere(self):
        """Draw the Bloch sphere framework"""
        # Draw sphere outline
        self.canvas.create_oval(
            self.center_x - self.radius,
            self.center_y - self.radius,
            self.center_x + self.radius,
            self.center_y + self.radius,
            outline='gray', width=2
        )
        
        # Draw axes
        # Z-axis (vertical)
        self.canvas.create_line(
            self.center_x, self.center_y - self.radius - 20,
            self.center_x, self.center_y + self.radius + 20,
            fill='black', width=2, arrow=tk.LAST
        )
        self.canvas.create_text(
            self.center_x + 15, self.center_y - self.radius - 25,
            text='|0⟩', font=('Arial', 10, 'bold')
        )
        self.canvas.create_text(
            self.center_x + 15, self.center_y + self.radius + 25,
            text='|1⟩', font=('Arial', 10, 'bold')
        )
        
        # X-axis (horizontal)
        self.canvas.create_line(
            self.center_x - self.radius - 20, self.center_y,
            self.center_x + self.radius + 20, self.center_y,
            fill='black', width=2, arrow=tk.LAST
        )
        self.canvas.create_text(
            self.center_x + self.radius + 30, self.center_y,
            text='X', font=('Arial', 10, 'bold')
        )
        
        # Equator
        self.canvas.create_oval(
            self.center_x - self.radius * 0.7,
            self.center_y - 20,
            self.center_x + self.radius * 0.7,
            self.center_y + 20,
            outline='lightgray', width=1, dash=(2, 2)
        )
    
    def update_state(self, alpha: complex, beta: complex):
        """Update Bloch vector for state α|0⟩ + β|1⟩"""
        # Remove old state vector
        self.canvas.delete('state_vector')
        
        # Calculate Bloch sphere coordinates
        theta = 2 * np.arccos(np.abs(alpha))
        phi = np.angle(beta) - np.angle(alpha)
        
        # Convert to Cartesian (simplified 2D projection)
        x = np.sin(theta) * np.cos(phi)
        y = -np.cos(theta)  # Negative because canvas y increases downward
        
        # Scale to canvas
        end_x = self.center_x + x * self.radius
        end_y = self.center_y + y * self.radius
        
        # Draw state vector
        self.canvas.create_line(
            self.center_x, self.center_y,
            end_x, end_y,
            fill='red', width=3, arrow=tk.LAST,
            tags='state_vector'
        )
        
        # Draw point at end
        self.canvas.create_oval(
            end_x - 5, end_y - 5,
            end_x + 5, end_y + 5,
            fill='red', outline='darkred',
            tags='state_vector'
        )

# ============================================================================
# MAIN GUI APPLICATION
# ============================================================================

class QuantumCircuitDesigner(tk.Tk):
    """Main quantum circuit designer application"""
    
    def __init__(self):
        super().__init__()
        
        self.title("QuantumOS - Quantum Circuit Designer")
        self.geometry("1400x800")
        self.configure(bg='#2C3E50')
        
        self.num_qubits = 3
        self.circuit = None
        
        self._create_widgets()
        self._create_menu()
    
    def _create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="New Circuit", command=self.new_circuit)
        file_menu.add_command(label="Clear Circuit", command=self.clear_circuit)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        
        # Circuit menu
        circuit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Circuit", menu=circuit_menu)
        circuit_menu.add_command(label="Execute Circuit", command=self.execute_circuit)
        circuit_menu.add_command(label="Show State", command=self.show_state)
    
    def _create_widgets(self):
        """Create main GUI widgets"""
        # Top toolbar
        toolbar = tk.Frame(self, bg='#34495E', height=60)
        toolbar.pack(side=tk.TOP, fill=tk.X)
        
        tk.Label(
            toolbar, text="Quantum Circuit Designer",
            font=('Arial', 16, 'bold'),
            bg='#34495E', fg='white'
        ).pack(side=tk.LEFT, padx=20, pady=10)
        
        # Main content area
        main_frame = tk.Frame(self, bg='#2C3E50')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Gate palette
        left_panel = tk.Frame(main_frame, bg='white', width=200)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        tk.Label(
            left_panel, text="Gate Library",
            font=('Arial', 12, 'bold'),
            bg='white'
        ).pack(pady=10)
        
        # Gate buttons
        gates = ['H', 'X', 'Y', 'Z', 'CNOT', 'RX', 'RY', 'RZ']
        for gate in gates:
            color = GateShape.COLORS.get(gate, '#CCCCCC')
            btn = tk.Button(
                left_panel, text=gate,
                width=15, height=2,
                bg=color, fg='white',
                font=('Arial', 10, 'bold'),
                command=lambda g=gate: self.select_gate(g)
            )
            btn.pack(pady=5, padx=10)
        
        # Middle panel - Circuit editor
        middle_panel = tk.Frame(main_frame, bg='white')
        middle_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        tk.Label(
            middle_panel, text="Circuit Editor",
            font=('Arial', 12, 'bold'),
            bg='white'
        ).pack(pady=5)
        
        self.circuit_editor = CircuitEditor(middle_panel, self.num_qubits)
        self.circuit_editor.pack(fill=tk.BOTH, expand=True)
        
        # Control panel
        control_panel = tk.Frame(middle_panel, bg='#ECF0F1')
        control_panel.pack(fill=tk.X, pady=5)
        
        tk.Button(
            control_panel, text="Execute Circuit",
            command=self.execute_circuit,
            bg='#27AE60', fg='white',
            font=('Arial', 10, 'bold'),
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            control_panel, text="Clear Circuit",
            command=self.clear_circuit,
            bg='#E74C3C', fg='white',
            font=('Arial', 10, 'bold'),
            width=15
        ).pack(side=tk.LEFT, padx=5)
        
        # Right panel - State visualization
        right_panel = tk.Frame(main_frame, bg='white', width=400)
        right_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(10, 0))
        
        tk.Label(
            right_panel, text="Quantum State",
            font=('Arial', 12, 'bold'),
            bg='white'
        ).pack(pady=5)
        
        self.state_visualizer = StateVisualizer(right_panel, self.num_qubits)
        self.state_visualizer.pack(fill=tk.BOTH, expand=True)
        
        # Bloch sphere (for single qubit)
        if self.num_qubits == 1:
            self.bloch_sphere = BlochSphere(right_panel)
            self.bloch_sphere.pack(fill=tk.BOTH, expand=True, pady=10)
        
        # Status bar
        self.status_bar = tk.Label(
            self, text="Ready",
            bg='#34495E', fg='white',
            anchor=tk.W, font=('Arial', 9)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def select_gate(self, gate_type: str):
        """Handle gate selection"""
        self.status_bar.config(text=f"Selected gate: {gate_type}")
        
        # Simple dialog to get qubit and column
        dialog = tk.Toplevel(self)
        dialog.title(f"Add {gate_type} Gate")
        dialog.geometry("300x200")
        
        tk.Label(dialog, text="Qubit:").pack(pady=5)
        qubit_var = tk.IntVar(value=0)
        tk.Spinbox(
            dialog, from_=0, to=self.num_qubits-1,
            textvariable=qubit_var, width=10
        ).pack()
        
        tk.Label(dialog, text="Column:").pack(pady=5)
        col_var = tk.IntVar(value=0)
        tk.Spinbox(
            dialog, from_=0, to=9,
            textvariable=col_var, width=10
        ).pack()
        
        target_var = None
        if gate_type == 'CNOT':
            tk.Label(dialog, text="Target Qubit:").pack(pady=5)
            target_var = tk.IntVar(value=1)
            tk.Spinbox(
                dialog, from_=0, to=self.num_qubits-1,
                textvariable=target_var, width=10
            ).pack()
        
        def add():
            qubit = qubit_var.get()
            col = col_var.get()
            params = [target_var.get()] if target_var else None
            
            if self.circuit_editor.add_gate(gate_type, qubit, col, params):
                self.status_bar.config(text=f"Added {gate_type} gate at qubit {qubit}, column {col}")
                dialog.destroy()
            else:
                messagebox.showerror("Error", "Failed to add gate")
        
        tk.Button(
            dialog, text="Add Gate", command=add,
            bg='#3498DB', fg='white'
        ).pack(pady=20)
    
    def execute_circuit(self):
        """Execute the quantum circuit"""
        if QuantumCircuit is None:
            messagebox.showwarning("Warning", "Quantum algorithms module not available")
            return
        
        gates = self.circuit_editor.get_circuit()
        if not gates:
            messagebox.showinfo("Info", "Circuit is empty")
            return
        
        try:
            # Create quantum circuit
            circuit = QuantumCircuit(self.num_qubits)
            
            # Apply gates
            for gate_type, qubit, column, params in gates:
                if gate_type == 'H':
                    circuit.h(qubit)
                elif gate_type == 'X':
                    circuit.x(qubit)
                elif gate_type == 'Y':
                    circuit.y(qubit)
                elif gate_type == 'Z':
                    circuit.z(qubit)
                elif gate_type == 'CNOT' and params:
                    circuit.cnot(qubit, params[0])
                elif gate_type == 'RX':
                    circuit.rx(qubit, np.pi/4)
                elif gate_type == 'RY':
                    circuit.ry(qubit, np.pi/4)
                elif gate_type == 'RZ':
                    circuit.rz(qubit, np.pi/4)
            
            # Update visualization
            self.state_visualizer.update_state(circuit.state.state_vector)
            
            # Update Bloch sphere for single qubit
            if self.num_qubits == 1 and hasattr(self, 'bloch_sphere'):
                state = circuit.state.state_vector
                self.bloch_sphere.update_state(state[0], state[1])
            
            self.status_bar.config(text="Circuit executed successfully")
            
        except Exception as e:
            messagebox.showerror("Error", f"Circuit execution failed: {str(e)}")
            self.status_bar.config(text="Execution failed")
    
    def show_state(self):
        """Show detailed quantum state information"""
        if QuantumCircuit is None:
            return
        
        # Create info window
        info_window = tk.Toplevel(self)
        info_window.title("Quantum State Information")
        info_window.geometry("500x400")
        
        text = tk.Text(info_window, wrap=tk.WORD, font=('Courier', 10))
        text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # This would show the current state vector
        text.insert(tk.END, "Quantum State Vector:\n\n")
        text.insert(tk.END, "Execute circuit to see state information")
    
    def clear_circuit(self):
        """Clear the circuit"""
        self.circuit_editor.clear_circuit()
        self.status_bar.config(text="Circuit cleared")
    
    def new_circuit(self):
        """Create new circuit"""
        self.clear_circuit()

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run the quantum circuit designer"""
    app = QuantumCircuitDesigner()
    app.mainloop()

if __name__ == "__main__":
    main()
