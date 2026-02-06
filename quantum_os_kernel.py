#!/usr/bin/env python3
"""
QuantumOS - A Functional Quantum-Classical Hybrid Operating System Kernel
Supports: x86/x64, ARM, and Quantum Computing devices
"""

import os
import time
import threading
import queue
import hashlib
import json
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum
import math
import cmath

# ============================================================================
# QUANTUM COMPUTING ENGINE
# ============================================================================

class QubitState:
    """Represents a quantum bit with superposition"""
    def __init__(self, alpha=1.0, beta=0.0):
        self.alpha = complex(alpha)  # Amplitude for |0⟩
        self.beta = complex(beta)    # Amplitude for |1⟩
        self._normalize()
    
    def _normalize(self):
        norm = math.sqrt(abs(self.alpha)**2 + abs(self.beta)**2)
        if norm > 0:
            self.alpha /= norm
            self.beta /= norm
    
    def measure(self):
        """Collapse to classical bit"""
        import random
        prob_0 = abs(self.alpha)**2
        return 0 if random.random() < prob_0 else 1
    
    def __repr__(self):
        return f"|ψ⟩ = {self.alpha:.3f}|0⟩ + {self.beta:.3f}|1⟩"


class QuantumGate:
    """Quantum gate operations"""
    
    @staticmethod
    def hadamard(qubit: QubitState):
        """Hadamard gate - creates superposition"""
        inv_sqrt2 = 1/math.sqrt(2)
        new_alpha = inv_sqrt2 * (qubit.alpha + qubit.beta)
        new_beta = inv_sqrt2 * (qubit.alpha - qubit.beta)
        qubit.alpha, qubit.beta = new_alpha, new_beta
    
    @staticmethod
    def pauli_x(qubit: QubitState):
        """NOT gate"""
        qubit.alpha, qubit.beta = qubit.beta, qubit.alpha
    
    @staticmethod
    def pauli_z(qubit: QubitState):
        """Phase flip"""
        qubit.beta = -qubit.beta
    
    @staticmethod
    def phase(qubit: QubitState, theta: float):
        """Phase shift gate"""
        qubit.beta *= cmath.exp(1j * theta)


class QuantumProcessor:
    """Simulated quantum processor"""
    
    def __init__(self, num_qubits: int):
        self.qubits = [QubitState() for _ in range(num_qubits)]
        self.num_qubits = num_qubits
    
    def apply_gate(self, gate_name: str, qubit_idx: int, **kwargs):
        """Apply quantum gate to qubit"""
        if qubit_idx >= self.num_qubits:
            raise ValueError(f"Qubit index {qubit_idx} out of range")
        
        qubit = self.qubits[qubit_idx]
        if gate_name == "H":
            QuantumGate.hadamard(qubit)
        elif gate_name == "X":
            QuantumGate.pauli_x(qubit)
        elif gate_name == "Z":
            QuantumGate.pauli_z(qubit)
        elif gate_name == "P":
            QuantumGate.phase(qubit, kwargs.get('theta', 0))
    
    def measure_all(self):
        """Measure all qubits"""
        return [q.measure() for q in self.qubits]
    
    def reset(self):
        """Reset all qubits to |0⟩"""
        self.qubits = [QubitState() for _ in range(self.num_qubits)]


# ============================================================================
# PROCESS MANAGEMENT
# ============================================================================

class ProcessState(Enum):
    NEW = "new"
    READY = "ready"
    RUNNING = "running"
    WAITING = "waiting"
    TERMINATED = "terminated"


@dataclass
class Process:
    pid: int
    name: str
    code: callable
    state: ProcessState = ProcessState.NEW
    priority: int = 5
    memory: Dict[str, Any] = field(default_factory=dict)
    cpu_time: float = 0.0
    thread: Optional[threading.Thread] = None
    result: Any = None
    quantum_mode: bool = False
    
    def execute(self):
        """Execute process code"""
        try:
            self.state = ProcessState.RUNNING
            self.result = self.code(self.memory)
            self.state = ProcessState.TERMINATED
        except Exception as e:
            self.result = f"Error: {str(e)}"
            self.state = ProcessState.TERMINATED


class Scheduler:
    """Process scheduler with priority queue"""
    
    def __init__(self):
        self.processes: Dict[int, Process] = {}
        self.ready_queue = queue.PriorityQueue()
        self.next_pid = 1
        self.running_process: Optional[Process] = None
    
    def create_process(self, name: str, code: callable, priority: int = 5, quantum: bool = False):
        """Create new process"""
        pid = self.next_pid
        self.next_pid += 1
        proc = Process(pid, name, code, priority=priority, quantum_mode=quantum)
        self.processes[pid] = proc
        self.ready_queue.put((priority, pid))
        return pid
    
    def schedule(self):
        """Round-robin scheduler"""
        if not self.ready_queue.empty():
            priority, pid = self.ready_queue.get()
            proc = self.processes[pid]
            proc.state = ProcessState.RUNNING
            self.running_process = proc
            
            # Execute in thread
            proc.thread = threading.Thread(target=proc.execute)
            proc.thread.start()
            return proc
        return None
    
    def get_process(self, pid: int) -> Optional[Process]:
        return self.processes.get(pid)
    
    def list_processes(self):
        return [(p.pid, p.name, p.state.value, p.priority) for p in self.processes.values()]


# ============================================================================
# MEMORY MANAGEMENT
# ============================================================================

class MemoryBlock:
    def __init__(self, start: int, size: int, allocated: bool = False):
        self.start = start
        self.size = size
        self.allocated = allocated
        self.process_id: Optional[int] = None


class MemoryManager:
    """Virtual memory manager with paging"""
    
    def __init__(self, total_size: int = 1024 * 1024):  # 1MB default
        self.total_size = total_size
        self.page_size = 4096  # 4KB pages
        self.blocks: List[MemoryBlock] = [MemoryBlock(0, total_size)]
        self.allocations: Dict[int, List[MemoryBlock]] = {}
    
    def allocate(self, process_id: int, size: int) -> Optional[int]:
        """Allocate memory for process (first-fit)"""
        for block in self.blocks:
            if not block.allocated and block.size >= size:
                # Split block if necessary
                if block.size > size:
                    new_block = MemoryBlock(block.start + size, block.size - size)
                    self.blocks.append(new_block)
                
                block.size = size
                block.allocated = True
                block.process_id = process_id
                
                if process_id not in self.allocations:
                    self.allocations[process_id] = []
                self.allocations[process_id].append(block)
                
                return block.start
        return None
    
    def deallocate(self, process_id: int):
        """Free all memory for process"""
        if process_id in self.allocations:
            for block in self.allocations[process_id]:
                block.allocated = False
                block.process_id = None
            del self.allocations[process_id]
            self._coalesce()
    
    def _coalesce(self):
        """Merge adjacent free blocks"""
        self.blocks.sort(key=lambda b: b.start)
        i = 0
        while i < len(self.blocks) - 1:
            if not self.blocks[i].allocated and not self.blocks[i+1].allocated:
                self.blocks[i].size += self.blocks[i+1].size
                self.blocks.pop(i+1)
            else:
                i += 1
    
    def get_stats(self):
        used = sum(b.size for b in self.blocks if b.allocated)
        free = self.total_size - used
        return {"total": self.total_size, "used": used, "free": free, 
                "usage_percent": (used/self.total_size)*100}


# ============================================================================
# FILE SYSTEM
# ============================================================================

@dataclass
class INode:
    name: str
    is_dir: bool
    content: Any = None
    children: Dict[str, 'INode'] = field(default_factory=dict)
    created: float = field(default_factory=time.time)
    modified: float = field(default_factory=time.time)
    size: int = 0


class FileSystem:
    """Simple hierarchical file system"""
    
    def __init__(self):
        self.root = INode("/", is_dir=True)
        self.current_dir = self.root
        self.current_path = "/"
    
    def _resolve_path(self, path: str) -> Optional[INode]:
        """Resolve path to inode"""
        if path == "/":
            return self.root
        
        parts = path.strip("/").split("/")
        node = self.root if path.startswith("/") else self.current_dir
        
        for part in parts:
            if part == "..":
                # Simplified - doesn't track parent
                continue
            if part and part in node.children:
                node = node.children[part]
            else:
                return None
        return node
    
    def mkdir(self, path: str) -> bool:
        """Create directory"""
        parent_path = "/".join(path.split("/")[:-1]) or "/"
        dir_name = path.split("/")[-1]
        
        parent = self._resolve_path(parent_path)
        if parent and parent.is_dir and dir_name not in parent.children:
            parent.children[dir_name] = INode(dir_name, is_dir=True)
            return True
        return False
    
    def create_file(self, path: str, content: str = "") -> bool:
        """Create file"""
        parent_path = "/".join(path.split("/")[:-1]) or "/"
        file_name = path.split("/")[-1]
        
        parent = self._resolve_path(parent_path)
        if parent and parent.is_dir:
            inode = INode(file_name, is_dir=False, content=content)
            inode.size = len(content)
            parent.children[file_name] = inode
            return True
        return False
    
    def read_file(self, path: str) -> Optional[str]:
        """Read file content"""
        node = self._resolve_path(path)
        if node and not node.is_dir:
            return node.content
        return None
    
    def write_file(self, path: str, content: str) -> bool:
        """Write to file"""
        node = self._resolve_path(path)
        if node and not node.is_dir:
            node.content = content
            node.size = len(content)
            node.modified = time.time()
            return True
        return False
    
    def ls(self, path: str = None) -> List[tuple]:
        """List directory"""
        node = self._resolve_path(path or self.current_path)
        if node and node.is_dir:
            return [(name, "DIR" if child.is_dir else "FILE", child.size) 
                    for name, child in node.children.items()]
        return []
    
    def cd(self, path: str) -> bool:
        """Change directory"""
        node = self._resolve_path(path)
        if node and node.is_dir:
            self.current_dir = node
            self.current_path = path
            return True
        return False


# ============================================================================
# DEVICE DRIVERS
# ============================================================================

class DeviceType(Enum):
    X86_64 = "x86_64"
    ARM64 = "arm64"
    QUANTUM = "quantum"


class DeviceDriver:
    """Abstract device driver"""
    
    def __init__(self, device_type: DeviceType):
        self.device_type = device_type
        self.initialized = False
    
    def initialize(self):
        self.initialized = True
        return True
    
    def get_info(self):
        return {"type": self.device_type.value, "status": "active" if self.initialized else "inactive"}


class DeviceManager:
    """Manages hardware devices"""
    
    def __init__(self):
        self.devices: Dict[str, DeviceDriver] = {}
        self._detect_devices()
    
    def _detect_devices(self):
        """Auto-detect system architecture"""
        import platform
        machine = platform.machine().lower()
        
        if "x86" in machine or "amd64" in machine:
            self.register_device("cpu", DeviceDriver(DeviceType.X86_64))
        elif "arm" in machine or "aarch64" in machine:
            self.register_device("cpu", DeviceDriver(DeviceType.ARM64))
        else:
            self.register_device("cpu", DeviceDriver(DeviceType.X86_64))
        
        # Quantum processor (simulated)
        self.register_device("qpu", DeviceDriver(DeviceType.QUANTUM))
    
    def register_device(self, name: str, driver: DeviceDriver):
        self.devices[name] = driver
        driver.initialize()
    
    def list_devices(self):
        return [(name, dev.get_info()) for name, dev in self.devices.items()]


# ============================================================================
# QUANTUM OS KERNEL
# ============================================================================

class QuantumOSKernel:
    """Main OS kernel"""
    
    def __init__(self):
        self.version = "1.0.0"
        self.name = "QuantumOS"
        self.scheduler = Scheduler()
        self.memory = MemoryManager()
        self.filesystem = FileSystem()
        self.devices = DeviceManager()
        self.quantum_processor = QuantumProcessor(8)
        self.running = False
        
        # Initialize system
        self._boot()
    
    def _boot(self):
        """Boot sequence"""
        print(f"\n{'='*60}")
        print(f"  {self.name} v{self.version} - Quantum-Classical Hybrid OS")
        print(f"{'='*60}")
        print(f"[BOOT] Initializing kernel...")
        print(f"[BOOT] Memory: {self.memory.total_size} bytes")
        print(f"[BOOT] Quantum Processor: {self.quantum_processor.num_qubits} qubits")
        
        for name, info in self.devices.list_devices():
            print(f"[BOOT] Device {name}: {info['type']} [{info['status']}]")
        
        # Create system directories
        self.filesystem.mkdir("/home")
        self.filesystem.mkdir("/bin")
        self.filesystem.mkdir("/tmp")
        self.filesystem.mkdir("/quantum")
        
        print(f"[BOOT] File system initialized")
        print(f"[BOOT] Boot complete!\n")
    
    def execute_quantum_circuit(self, gates: List[tuple]) -> List[int]:
        """Execute quantum circuit"""
        self.quantum_processor.reset()
        for gate_name, qubit_idx, *params in gates:
            kwargs = {}
            if params:
                kwargs = params[0] if isinstance(params[0], dict) else {}
            self.quantum_processor.apply_gate(gate_name, qubit_idx, **kwargs)
        return self.quantum_processor.measure_all()
    
    def run_shell(self):
        """Interactive shell"""
        self.running = True
        print(f"Welcome to {self.name} Shell")
        print(f"Type 'help' for commands\n")
        
        while self.running:
            try:
                cmd = input(f"{self.name}:{self.filesystem.current_path}$ ").strip()
                if not cmd:
                    continue
                
                self._execute_command(cmd)
            
            except KeyboardInterrupt:
                print("\nUse 'exit' to quit")
            except Exception as e:
                print(f"Error: {str(e)}")
    
    def _execute_command(self, cmd: str):
        """Execute shell command"""
        parts = cmd.split()
        command = parts[0]
        args = parts[1:]
        
        if command == "help":
            print("""
Commands:
  help                  - Show this help
  exit                  - Exit shell
  ps                    - List processes
  exec <name> <code>    - Execute Python code as process
  quantum <circuit>     - Run quantum circuit (e.g., "H 0 X 1")
  mem                   - Show memory stats
  ls [path]             - List directory
  mkdir <path>          - Create directory
  touch <file>          - Create file
  cat <file>            - Read file
  echo <text> > <file>  - Write to file
  devices               - List devices
  sysinfo               - System information
            """)
        
        elif command == "exit":
            self.running = False
            print("Shutting down...")
        
        elif command == "ps":
            procs = self.scheduler.list_processes()
            print(f"{'PID':<6} {'NAME':<20} {'STATE':<12} {'PRIORITY'}")
            print("-" * 50)
            for pid, name, state, priority in procs:
                print(f"{pid:<6} {name:<20} {state:<12} {priority}")
        
        elif command == "exec":
            if len(args) < 2:
                print("Usage: exec <name> <python_code>")
            else:
                name = args[0]
                code_str = " ".join(args[1:])
                try:
                    code_func = lambda mem: eval(code_str)
                    pid = self.scheduler.create_process(name, code_func)
                    proc = self.scheduler.schedule()
                    if proc:
                        proc.thread.join()
                        print(f"Process {pid} result: {proc.result}")
                except Exception as e:
                    print(f"Error: {str(e)}")
        
        elif command == "quantum":
            if not args:
                print("Usage: quantum <gate> <qubit> [<gate> <qubit> ...]")
                print("Gates: H (Hadamard), X (NOT), Z (Phase flip)")
            else:
                gates = []
                i = 0
                while i < len(args):
                    gate = args[i]
                    if i+1 < len(args):
                        qubit = int(args[i+1])
                        gates.append((gate, qubit))
                        i += 2
                    else:
                        break
                
                result = self.execute_quantum_circuit(gates)
                print(f"Quantum measurement: {result}")
        
        elif command == "mem":
            stats = self.memory.get_stats()
            print(f"Memory Statistics:")
            print(f"  Total: {stats['total']} bytes")
            print(f"  Used:  {stats['used']} bytes")
            print(f"  Free:  {stats['free']} bytes")
            print(f"  Usage: {stats['usage_percent']:.2f}%")
        
        elif command == "ls":
            path = args[0] if args else None
            entries = self.filesystem.ls(path)
            for name, type_, size in entries:
                print(f"{type_:<6} {size:>10} {name}")
        
        elif command == "mkdir":
            if args:
                if self.filesystem.mkdir(args[0]):
                    print(f"Directory created: {args[0]}")
                else:
                    print("Failed to create directory")
        
        elif command == "touch":
            if args:
                if self.filesystem.create_file(args[0]):
                    print(f"File created: {args[0]}")
                else:
                    print("Failed to create file")
        
        elif command == "cat":
            if args:
                content = self.filesystem.read_file(args[0])
                if content is not None:
                    print(content)
                else:
                    print("File not found")
        
        elif command == "echo":
            if ">" in args:
                idx = args.index(">")
                text = " ".join(args[:idx])
                file = args[idx+1] if idx+1 < len(args) else None
                if file:
                    if self.filesystem.write_file(file, text) or \
                       (self.filesystem.create_file(file, text)):
                        print(f"Written to {file}")
                    else:
                        print("Failed to write file")
            else:
                print(" ".join(args))
        
        elif command == "devices":
            print(f"{'DEVICE':<15} {'TYPE':<15} {'STATUS'}")
            print("-" * 45)
            for name, info in self.devices.list_devices():
                print(f"{name:<15} {info['type']:<15} {info['status']}")
        
        elif command == "sysinfo":
            print(f"{self.name} v{self.version}")
            print(f"Quantum Qubits: {self.quantum_processor.num_qubits}")
            print(f"Processes: {len(self.scheduler.processes)}")
            stats = self.memory.get_stats()
            print(f"Memory: {stats['used']}/{stats['total']} bytes ({stats['usage_percent']:.1f}%)")
        
        else:
            print(f"Unknown command: {command}")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    kernel = QuantumOSKernel()
    kernel.run_shell()
