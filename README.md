# Quantum Os

An enterprise-grade solution engineered for high performance.

![Language](https://img.shields.io/badge/Language-Python-blue)
![Status](https://img.shields.io/badge/Status-Active-success)
![License](https://img.shields.io/badge/License-MIT-green)

## 🚀 Overview

Welcome to the **Quantum Os** repository. This project is built to deliver a robust and scalable solution tailored to modern development standards.

QuantumOS is a Python-based **simulated operating system environment** that combines fundamental OS concepts (process management, memory, filesystem, system calls, IPC) with **quantum computing simulations** (Shor's factorization, QFT, VQE, QAOA, quantum teleportation) and a **simulated TCP/IP network stack** — all accessible through both a desktop GUI and an interactive shell.

## ✨ Features

- **High Performance:** Optimized for speed and efficiency.
- **Scalable Architecture:** Designed to grow with your needs.
- **Clean Codebase:** Follows best practices and industry standards.
- **Secure by Default:** Engineered with security in mind (sensitive files excluded via `.gitignore`).
- **Quantum Algorithms:** Shor's factorization, Quantum Fourier Transform, VQE, QAOA, and quantum teleportation via `quantum_algorithms`.
- **Network Stack:** Simulated DNS lookup, ping, HTTP server, and sockets via `network_stack`.
- **Inter-Process Communication:** Message queues and shared memory segments with PID-based access control.
- **System Call Interface:** `open`, `read`, `write`, `send_msg`, `rcv_msg`, `malloc`, `free`, and more via `SyscallHandler`.
- **GUI Dashboard:** Tkinter-based tabbed interface with live system stats, memory visualization, file browser, and network tools.
- **Logging & Profiling:** Built-in OS logger and performance profiler tracking CPU/memory metrics.

## 🏗️ Architecture / How It Works

The system is organized into layered components:

### 1. Kernel Layer (`quantum_os_mvp.py`, `quantum_os_advanced.py`)
- **`QuantumOSKernel`** (base): process table, memory manager, virtual filesystem, and basic shell.
- **`QuantumOSAdvanced`** (extends the base kernel): wires in the IPC manager, syscall handler, logger, profiler, network stack, and advanced quantum algorithms. It boots the system, records initial memory metrics, and launches the interactive `AdvancedShell`.

### 2. Inter-Process Communication (IPC)
- **`MessageQueue`**: bounded queue for passing `Message` dataclasses between PIDs.
- **`SharedMemory`**: byte-array segments with attach/detach semantics and PID-based read/write authorization enforced through a lock.

### 3. System Calls
- **`SystemCall` enum + `SyscallHandler`**: dispatches calls like `OPEN`, `READ`, `WRITE`, `SEND_MSG`, `RCV_MSG`, `MALLOC`, `FREE` to the appropriate kernel subsystem, returning a `SyscallResult` (success/return value/error).

### 4. Quantum Subsystem (`quantum_algorithms.py`, optional)
- `ShorsAlgorithm.factor(n)`, `QuantumFourierTransform.qft()`, `VQE`, `QAOA`, `QuantumTeleportation`, and a circuit/state-vector model. If the module is missing, the kernel degrades gracefully (`QUANTUM_ADVANCED = False`).

### 5. Network Subsystem (`network_stack.py`, optional)
- `NetworkStack` with `DNS` resolution, `ping`, sockets, and an `HTTPServer`. Gracefully disabled if the module is absent.

### 6. GUI (`quantumos_gui_simple.py`)
- A self-contained Tkinter application (`QuantumOSSimpleGUI`) backed by `SimpleQuantumOS`, exposing five tabs:
  - **📊 Dashboard** — system info + live uptime/process/memory stats (1s refresh loop).
  - **⚛ Quantum** — run factorization with visual output.
  - **🌐 Network** — DNS lookup and ping tools.
  - **📁 Files** — virtual filesystem browser.
  - **📈 Monitor** — memory usage bar and process table.

### 7. Testing (`test_components.py`)
- Verifies Tkinter, NumPy, the quantum module, network stack, and kernel initialization/command execution.

### Shell Commands (Advanced Mode)
`uname`, `netstat`, `ping <ip>`, `nslookup <host>`, `factor <n>`, `qft <qubits>`, `logs [n]`, `profile`, `ipc`, plus base kernel commands.

## 🛠️ Prerequisites

Ensure you have the following installed in your environment before proceeding:
- **Python 3.10+**
- Standard development tools
- (For GUI) A display server — Tkinter requires a desktop environment; it will not render in a headless container without X11 forwarding.
- (Optional) `numpy` for quantum state math

## 📦 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Shivay00001/quantum_os.git
   ```
2. Navigate to the project directory:
   ```bash
   cd quantum_os
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## 💻 Usage

**Run the GUI (requires a desktop environment):**
```bash
python quantumos_gui_simple.py
```

**Run the advanced kernel with interactive shell:**
```bash
python quantum_os_advanced.py
```

**Run the component test suite:**
```bash
python test_components.py
```

## 🐳 Running with Docker

The repository ships with a `Dockerfile` (Python 3.10-slim) and `docker-compose.yml`, so it can run identically on any laptop or server.

### Option 1: Docker Compose (recommended)
```bash
docker-compose up --build
```
This builds the image and starts the container, mapping host port **8090** → container port **8000**, with automatic restart (`unless-stopped`).

### Option 2: Plain Docker
```bash
# Build the image
docker build -t quantum_os .

# Run the container
docker run -p 8090:8000 quantum_os
```

**Note:** The container's default command is `python main.py`. Ensure a `main.py` entry point exists (or override the command, e.g. `docker run quantum_os python quantum_os_advanced.py`). The Tkinter GUI will **not** display inside a container unless you configure X11 forwarding (e.g., `-e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix` on Linux).

## 🔍 Workability Assessment

In the interest of full transparency, here is an honest evaluation of the current state of this repository:

**What works well:**
- `quantumos_gui_simple.py` is genuinely self-contained and functional — its backend (`SimpleQuantumOS`) has no external dependencies beyond Tkinter, so the GUI should run out of the box on any desktop Python install.
- `quantum_os_advanced.py` is defensively coded: optional modules (`quantum_algorithms`, `network_stack`) are wrapped in try/except, so the kernel degrades gracefully rather than crashing.
- The IPC, syscall, logging, and profiling subsystems are coherent and consistently designed.
- Docker support is present and correctly structured for a Python app.

**Significant gaps and issues:**
- **Missing core files:** `quantum_os_mvp.py` (the base kernel), `quantum_algorithms.py`, `network_stack.py`, `requirements.txt`, and `main.py` are referenced but **not present** in the provided repository snapshot. Without them, `quantum_os_advanced.py` and `test_components.py` will fail, and the Docker image **will not start** (`CMD ["python", "main.py"]` targets a nonexistent file).
- **Simulated, not real:** the "quantum" factorization is classical trial division; ping/DNS/filesystem/processes are in-memory simulations. This is an educational simulation, not an actual OS or quantum computing framework.
- **No real service on port 8000:** the Docker setup exposes port 8000, but no HTTP server is started by any entry point shown — the port mapping is currently aspirational.
- **No CI, packaging, or formal test framework** (tests are a single ad-hoc script).

**Verdict:** This is a promising **educational prototype / proof-of-concept**, roughly at an MVP stage. It is **not production-ready**. To make the repository fully functional, you must add the missing modules (`quantum_os_mvp.py`, `quantum_algorithms.py`, `network_stack.py`), create `main.py` and `requirements.txt`, and align the Docker entry point with an actual runnable target. Once those gaps are closed, the architecture is sound enough to serve as a solid learning platform for OS and quantum computing concepts.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the issues page. High-impact contributions would include: implementing the missing kernel/quantum/network modules, adding a `main.py` entry point, and expanding the test suite.

## 📝 License

This project is licensed under standard terms (MIT).