#!/usr/bin/env python3
"""
QuantumOS Unified GUI - Complete Operating System Interface
Integrates all features: Terminal, Quantum Computing, Networking, File System, Process Management
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import threading
import queue
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import QuantumOS modules
try:
    from quantum_os_advanced import QuantumOSAdvanced, Architecture, AdvancedShell
    from quantum_algorithms import QuantumCircuit, ShorsAlgorithm
    from network_stack import NetworkStack, DNS
    MODULES_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Some modules not available: {e}")
    MODULES_AVAILABLE = False

# ============================================================================
# MAIN QUANTUMOS GUI
# ============================================================================

class QuantumOSGUI(tk.Tk):
    """Unified QuantumOS GUI Application"""
    
    def __init__(self):
        super().__init__()
        
        self.title("QuantumOS - Advanced Operating System")
        self.geometry("1600x900")
        self.configure(bg='#1e1e1e')
        
        # Initialize OS kernel
        if MODULES_AVAILABLE:
            self.kernel = QuantumOSAdvanced(Architecture.X86_64)
            self.kernel.boot()
        else:
            self.kernel = None
            
        self.command_queue = queue.Queue()
        
        self._create_ui()
        self._start_update_loop()
        
    def _create_ui(self):
        """Create main user interface"""
        
        # Top menu bar
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Exit", command=self.quit)
        
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Header
        header = tk.Frame(self, bg='#0d47a1', height=80)
        header.pack(side=tk.TOP, fill=tk.X)
        header.pack_propagate(False)
        
        tk.Label(
            header,
            text="⚛ QuantumOS Advanced v1.0.0",
            font=('Arial', 24, 'bold'),
            bg='#0d47a1',
            fg='white'
        ).pack(side=tk.LEFT, padx=20, pady=20)
        
        tk.Label(
            header,
            text="Quantum Computing • Networking • Process Management",
            font=('Arial', 10),
            bg='#0d47a1',
            fg='#bbdefb'
        ).pack(side=tk.LEFT, padx=20)
        
        # Main content area with tabs
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create tabs
        self._create_dashboard_tab()
        self._create_terminal_tab()
        self._create_quantum_tab()
        self._create_network_tab()
        self._create_filesystem_tab()
        self._create_processes_tab()
        self._create_monitor_tab()
        
        # Status bar
        self.status_bar = tk.Label(
            self,
            text="QuantumOS Ready",
            bg='#263238',
            fg='#eceff1',
            anchor=tk.W,
            font=('Consolas', 9)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    # ========================================================================
    # DASHBOARD TAB
    # ========================================================================
    
    def _create_dashboard_tab(self):
        """Create main dashboard"""
        tab = tk.Frame(self.notebook, bg='#263238')
        self.notebook.add(tab, text="📊 Dashboard")
        
        # System info cards
        cards_frame = tk.Frame(tab, bg='#263238')
        cards_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Card 1: System Info
        self._create_info_card(
            cards_frame,
            "System Information",
            [
                ("OS Version", "QuantumOS v1.0.0-ADVANCED"),
                ("Architecture", "x86_64"),
                ("Kernel", "Microkernel"),
                ("Quantum Support", "✓ Enabled"),
                ("Network Stack", "✓ TCP/IP"),
            ],
            row=0, col=0
        )
        
        # Card 2: Quick Stats
        self.stats_labels = {}
        self.stats_card = self._create_info_card(
            cards_frame,
            "System Statistics",
            [
                ("Uptime", "0s"),
                ("Processes", "0"),
                ("Memory Used", "0 KB"),
                ("Network Connections", "0"),
            ],
            row=0, col=1,
            store_labels=True
        )
        
        # Card 3: Quick Actions
        actions_card = tk.LabelFrame(
            cards_frame,
            text="Quick Actions",
            bg='#37474f',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=20
        )
        actions_card.grid(row=1, column=0, columnspan=2, sticky='nsew', padx=10, pady=10)
        
        buttons = [
            ("🔬 Run Quantum Algorithm", self.quick_quantum),
            ("🌐 Test Network", self.quick_network),
            ("📁 Browse Files", lambda: self.notebook.select(4)),
            ("📟 Open Terminal", lambda: self.notebook.select(1)),
        ]
        
        for i, (text, cmd) in enumerate(buttons):
            tk.Button(
                actions_card,
                text=text,
                command=cmd,
                bg='#0d47a1',
                fg='white',
                font=('Arial', 11, 'bold'),
                width=25,
                height=2
            ).grid(row=i//2, column=i%2, padx=10, pady=10)
        
        cards_frame.grid_rowconfigure(0, weight=1)
        cards_frame.grid_rowconfigure(1, weight=1)
        cards_frame.grid_columnconfigure(0, weight=1)
        cards_frame.grid_columnconfigure(1, weight=1)
    
    def _create_info_card(self, parent, title, items, row, col, store_labels=False):
        """Create an info card"""
        card = tk.LabelFrame(
            parent,
            text=title,
            bg='#37474f',
            fg='white',
            font=('Arial', 12, 'bold'),
            padx=20,
            pady=20
        )
        card.grid(row=row, column=col, sticky='nsew', padx=10, pady=10)
        
        for i, (key, value) in enumerate(items):
            tk.Label(
                card,
                text=f"{key}:",
                bg='#37474f',
                fg='#90caf9',
                font=('Arial', 10, 'bold'),
                anchor=tk.W
            ).grid(row=i, column=0, sticky='w', pady=5)
            
            label = tk.Label(
                card,
                text=value,
                bg='#37474f',
                fg='white',
                font=('Arial', 10),
                anchor=tk.W
            )
            label.grid(row=i, column=1, sticky='w', padx=20, pady=5)
            
            if store_labels:
                self.stats_labels[key] = label
        
        return card
    
    # ========================================================================
    # TERMINAL TAB
    # ========================================================================
    
    def _create_terminal_tab(self):
        """Create terminal emulator"""
        tab = tk.Frame(self.notebook, bg='#1e1e1e')
        self.notebook.add(tab, text="💻 Terminal")
        
        # Terminal output
        terminal_frame = tk.Frame(tab, bg='#1e1e1e')
        terminal_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.terminal_output = scrolledtext.ScrolledText(
            terminal_frame,
            bg='#1e1e1e',
            fg='#00ff00',
            font=('Consolas', 11),
            insertbackground='#00ff00',
            wrap=tk.WORD
        )
        self.terminal_output.pack(fill=tk.BOTH, expand=True)
        
        # Welcome message
        self.terminal_write("QuantumOS Advanced Terminal v1.0.0\n")
        self.terminal_write("Type 'help' for available commands\n\n")
        self.terminal_write("quantumos$ ")
        
        # Command input
        input_frame = tk.Frame(tab, bg='#263238')
        input_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Label(
            input_frame,
            text="quantumos$",
            bg='#263238',
            fg='#00ff00',
            font=('Consolas', 11, 'bold')
        ).pack(side=tk.LEFT, padx=5)
        
        self.terminal_input = tk.Entry(
            input_frame,
            bg='#1e1e1e',
            fg='#00ff00',
            font=('Consolas', 11),
            insertbackground='#00ff00'
        )
        self.terminal_input.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.terminal_input.bind('<Return>', self.execute_command)
        
        tk.Button(
            input_frame,
            text="Execute",
            command=lambda: self.execute_command(None),
            bg='#0d47a1',
            fg='white',
            font=('Arial', 10, 'bold')
        ).pack(side=tk.RIGHT, padx=5)
    
    def terminal_write(self, text):
        """Write to terminal"""
        self.terminal_output.insert(tk.END, text)
        self.terminal_output.see(tk.END)
    
    def execute_command(self, event):
        """Execute terminal command"""
        command = self.terminal_input.get().strip()
        if not command:
            return
        
        self.terminal_write(f"{command}\n")
        self.terminal_input.delete(0, tk.END)
        
        if command == "clear":
            self.terminal_output.delete(1.0, tk.END)
            self.terminal_write("quantumos$ ")
            return
        
        # Execute on kernel
        if self.kernel:
            try:
                output = self.kernel.execute_command(command)
                if output:
                    self.terminal_write(f"{output}\n")
            except Exception as e:
                self.terminal_write(f"Error: {str(e)}\n")
        else:
            self.terminal_write("Kernel not available\n")
        
        self.terminal_write("quantumos$ ")
    
    # ========================================================================
    # QUANTUM TAB
    # ========================================================================
    
    def _create_quantum_tab(self):
        """Create quantum computing tab"""
        tab = tk.Frame(self.notebook, bg='#263238')
        self.notebook.add(tab, text="⚛ Quantum")
        
        # Left: Algorithms
        left_panel = tk.Frame(tab, bg='#37474f', width=400)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10)
        
        tk.Label(
            left_panel,
            text="Quantum Algorithms",
            bg='#37474f',
            fg='white',
            font=('Arial', 14, 'bold')
        ).pack(pady=10)
        
        # Shor's Algorithm
        shor_frame = tk.LabelFrame(left_panel, text="Shor's Factorization", bg='#455a64', fg='white', font=('Arial', 11, 'bold'))
        shor_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(shor_frame, text="Number to factor:", bg='#455a64', fg='white').pack(pady=5)
        self.shor_input = tk.Entry(shor_frame, font=('Arial', 11))
        self.shor_input.pack(pady=5)
        self.shor_input.insert(0, "15")
        
        tk.Button(
            shor_frame,
            text="Factor Number",
            command=self.run_shor,
            bg='#0d47a1',
            fg='white',
            font=('Arial', 10, 'bold')
        ).pack(pady=10)
        
        self.shor_result = tk.Label(shor_frame, text="", bg='#455a64', fg='#4caf50', font=('Arial', 11, 'bold'))
        self.shor_result.pack(pady=5)
        
        # QFT
        qft_frame = tk.LabelFrame(left_panel, text="Quantum Fourier Transform", bg='#455a64', fg='white', font=('Arial', 11, 'bold'))
        qft_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(qft_frame, text="Number of qubits:", bg='#455a64', fg='white').pack(pady=5)
        self.qft_input = tk.Spinbox(qft_frame, from_=1, to=5, font=('Arial', 11))
        self.qft_input.pack(pady=5)
        
        tk.Button(
            qft_frame,
            text="Run QFT",
            command=self.run_qft,
            bg='#0d47a1',
            fg='white',
            font=('Arial', 10, 'bold')
        ).pack(pady=10)
        
        self.qft_result = tk.Label(qft_frame, text="", bg='#455a64', fg='#4caf50', font=('Arial', 9))
        self.qft_result.pack(pady=5)
        
        # Right: Results
        right_panel = tk.Frame(tab, bg='#37474f')
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(
            right_panel,
            text="Quantum Computation Results",
            bg='#37474f',
            fg='white',
            font=('Arial', 14, 'bold')
        ).pack(pady=10)
        
        self.quantum_output = scrolledtext.ScrolledText(
            right_panel,
            bg='#1e1e1e',
            fg='#00ff00',
            font=('Consolas', 10),
            wrap=tk.WORD
        )
        self.quantum_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def run_shor(self):
        """Run Shor's algorithm"""
        try:
            n = int(self.shor_input.get())
            self.quantum_output.insert(tk.END, f"\n▶ Running Shor's Algorithm on {n}...\n")
            
            if MODULES_AVAILABLE:
                factors = ShorsAlgorithm.factor(n)
                if factors:
                    result = f"✓ Factors: {factors[0]} × {factors[1]}"
                    self.shor_result.config(text=result)
                    self.quantum_output.insert(tk.END, f"{result}\n")
                    self.quantum_output.insert(tk.END, f"  Verification: {factors[0]} × {factors[1]} = {factors[0] * factors[1]}\n")
                else:
                    self.shor_result.config(text="Failed to factor")
                    self.quantum_output.insert(tk.END, "✗ Failed to factor\n")
            else:
                self.quantum_output.insert(tk.END, "Quantum algorithms not available\n")
            
            self.quantum_output.see(tk.END)
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    def run_qft(self):
        """Run Quantum Fourier Transform"""
        try:
            num_qubits = int(self.qft_input.get())
            self.quantum_output.insert(tk.END, f"\n▶ Running QFT on {num_qubits} qubits...\n")
            
            if MODULES_AVAILABLE:
                from quantum_algorithms import QuantumFourierTransform
                circuit = QuantumCircuit(num_qubits)
                for i in range(num_qubits):
                    circuit.h(i)
                QuantumFourierTransform.qft(circuit, list(range(num_qubits)))
                probs = circuit.state.get_probabilities()
                
                self.qft_result.config(text=f"✓ QFT Complete")
                self.quantum_output.insert(tk.END, "✓ QFT transformation complete\n")
                self.quantum_output.insert(tk.END, f"  State probabilities: {probs[:min(8, len(probs))]}\n")
            else:
                self.quantum_output.insert(tk.END, "Quantum algorithms not available\n")
            
            self.quantum_output.see(tk.END)
        except Exception as e:
            messagebox.showerror("Error", str(e))
    
    # ========================================================================
    # NETWORK TAB
    # ========================================================================
    
    def _create_network_tab(self):
        """Create network tools tab"""
        tab = tk.Frame(self.notebook, bg='#263238')
        self.notebook.add(tab, text="🌐 Network")
        
        # Tools panel
        tools_frame = tk.Frame(tab, bg='#37474f', width=400)
        tools_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=10, pady=10)
        
        tk.Label(
            tools_frame,
            text="Network Tools",
            bg='#37474f',
            fg='white',
            font=('Arial', 14, 'bold')
        ).pack(pady=10)
        
        # Ping
        ping_frame = tk.LabelFrame(tools_frame, text="Ping", bg='#455a64', fg='white', font=('Arial', 11, 'bold'))
        ping_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(ping_frame, text="Host/IP:", bg='#455a64', fg='white').pack(pady=5)
        self.ping_input = tk.Entry(ping_frame, font=('Arial', 11))
        self.ping_input.pack(pady=5, fill=tk.X, padx=10)
        self.ping_input.insert(0, "192.168.1.1")
        
        tk.Button(
            ping_frame,
            text="Ping",
            command=self.run_ping,
            bg='#0d47a1',
            fg='white'
        ).pack(pady=5)
        
        # DNS Lookup
        dns_frame = tk.LabelFrame(tools_frame, text="DNS Lookup", bg='#455a64', fg='white', font=('Arial', 11, 'bold'))
        dns_frame.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(dns_frame, text="Hostname:", bg='#455a64', fg='white').pack(pady=5)
        self.dns_input = tk.Entry(dns_frame, font=('Arial', 11))
        self.dns_input.pack(pady=5, fill=tk.X, padx=10)
        self.dns_input.insert(0, "localhost")
        
        tk.Button(
            dns_frame,
            text="Lookup",
            command=self.run_dns,
            bg='#0d47a1',
            fg='white'
        ).pack(pady=5)
        
        # Network Stats
        tk.Button(
            tools_frame,
            text="Show Network Statistics",
            command=self.show_network_stats,
            bg='#1b5e20',
            fg='white',
            font=('Arial', 11, 'bold'),
            height=2
        ).pack(fill=tk.X, padx=10, pady=20)
        
        # Output panel
        output_frame = tk.Frame(tab, bg='#37474f')
        output_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(
            output_frame,
            text="Network Output",
            bg='#37474f',
            fg='white',
            font=('Arial', 14, 'bold')
        ).pack(pady=10)
        
        self.network_output = scrolledtext.ScrolledText(
            output_frame,
            bg='#1e1e1e',
            fg='#00ff00',
            font=('Consolas', 10)
        )
        self.network_output.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    
    def run_ping(self):
        """Run ping command"""
        host = self.ping_input.get()
        self.network_output.insert(tk.END, f"\n▶ Pinging {host}...\n")
        
        if self.kernel and hasattr(self.kernel, 'network'):
            result = self.kernel.network.ping(host)
            self.network_output.insert(tk.END, f"{'✓ Success' if result else '✗ Failed'}\n")
        else:
            self.network_output.insert(tk.END, "Network not available\n")
        
        self.network_output.see(tk.END)
    
    def run_dns(self):
        """Run DNS lookup"""
        hostname = self.dns_input.get()
        self.network_output.insert(tk.END, f"\n▶ Looking up {hostname}...\n")
        
        if self.kernel and hasattr(self.kernel, 'network'):
            ip = self.kernel.network.dns.query(hostname)
            if ip:
                self.network_output.insert(tk.END, f"✓ {hostname} → {ip}\n")
            else:
                self.network_output.insert(tk.END, f"✗ Host not found\n")
        else:
            self.network_output.insert(tk.END, "Network not available\n")
        
        self.network_output.see(tk.END)
    
    def show_network_stats(self):
        """Show network statistics"""
        self.network_output.insert(tk.END, "\n▶ Network Statistics:\n")
        self.network_output.insert(tk.END, "=" * 50 + "\n")
        
        if self.kernel and hasattr(self.kernel, 'network'):
            stats = self.kernel.network.get_stats()
            for key, value in stats.items():
                self.network_output.insert(tk.END, f"  {key}: {value}\n")
        else:
            self.network_output.insert(tk.END, "Network not available\n")
        
        self.network_output.see(tk.END)
    
    # ========================================================================
    # FILESYSTEM TAB
    # ========================================================================
    
    def _create_filesystem_tab(self):
        """Create file system browser"""
        tab = tk.Frame(self.notebook, bg='#263238')
        self.notebook.add(tab, text="📁 Files")
        
        # Toolbar
        toolbar = tk.Frame(tab, bg='#37474f')
        toolbar.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            toolbar,
            text="📂 List Directory",
            command=self.list_directory,
            bg='#0d47a1',
            fg='white',
            font=('Arial', 10, 'bold')
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toolbar,
            text="➕ Create File",
            command=self.create_file_dialog,
            bg='#1b5e20',
            fg='white',
            font=('Arial', 10, 'bold')
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            toolbar,
            text="📋 Create Directory",
            command=self.create_dir_dialog,
            bg='#f57c00',
            fg='white',
            font=('Arial', 10, 'bold')
        ).pack(side=tk.LEFT, padx=5)
        
        # Current path
        path_frame = tk.Frame(tab, bg='#37474f')
        path_frame.pack(fill=tk.X, padx=10, pady=(0, 10))
        
        tk.Label(path_frame, text="Path:", bg='#37474f', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=5)
        
        self.fs_path = tk.Entry(path_frame, font=('Consolas', 10))
        self.fs_path.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        self.fs_path.insert(0, "/")
        
        # File list
        list_frame = tk.Frame(tab, bg='#263238')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.file_list = scrolledtext.ScrolledText(
            list_frame,
            bg='#1e1e1e',
            fg='#00ff00',
            font=('Consolas', 10)
        )
        self.file_list.pack(fill=tk.BOTH, expand=True)
        
        # Initial listing
        self.list_directory()
    
    def list_directory(self):
        """List directory contents"""
        path = self.fs_path.get()
        self.file_list.delete(1.0, tk.END)
        
        if self.kernel:
            files = self.kernel.filesystem.ls(path)
            self.file_list.insert(tk.END, f"Directory: {path}\n")
            self.file_list.insert(tk.END, "=" * 60 + "\n\n")
            self.file_list.insert(tk.END, f"{'TYPE':<8} {'SIZE':<10} {'PERMISSIONS':<12} NAME\n")
            self.file_list.insert(tk.END, "-" * 60 + "\n")
            
            for f in files:
                self.file_list.insert(
                    tk.END,
                    f"{f['type']:<8} {f['size']:<10} {f['permissions']:<12} {f['name']}\n"
                )
    
    def create_file_dialog(self):
        """Show create file dialog"""
        dialog = tk.Toplevel(self)
        dialog.title("Create File")
        dialog.geometry("400x150")
        dialog.configure(bg='#37474f')
        
        tk.Label(dialog, text="File path:", bg='#37474f', fg='white').pack(pady=5)
        path_entry = tk.Entry(dialog, font=('Arial', 11))
        path_entry.pack(fill=tk.X, padx=20, pady=5)
        
        tk.Label(dialog, text="Content:", bg='#37474f', fg='white').pack(pady=5)
        content_entry = tk.Entry(dialog, font=('Arial', 11))
        content_entry.pack(fill=tk.X, padx=20, pady=5)
        
        def create():
            path = path_entry.get()
            content = content_entry.get()
            if self.kernel:
                success = self.kernel.filesystem.create_file(path, content.encode())
                if success:
                    messagebox.showinfo("Success", "File created")
                    self.list_directory()
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Failed to create file")
        
        tk.Button(dialog, text="Create", command=create, bg='#0d47a1', fg='white').pack(pady=10)
    
    def create_dir_dialog(self):
        """Show create directory dialog"""
        dialog = tk.Toplevel(self)
        dialog.title("Create Directory")
        dialog.geometry("400x100")
        dialog.configure(bg='#37474f')
        
        tk.Label(dialog, text="Directory path:", bg='#37474f', fg='white').pack(pady=5)
        path_entry = tk.Entry(dialog, font=('Arial', 11))
        path_entry.pack(fill=tk.X, padx=20, pady=5)
        
        def create():
            path = path_entry.get()
            if self.kernel:
                success = self.kernel.filesystem.mkdir(path)
                if success:
                    messagebox.showinfo("Success", "Directory created")
                    self.list_directory()
                    dialog.destroy()
                else:
                    messagebox.showerror("Error", "Failed to create directory")
        
        tk.Button(dialog, text="Create", command=create, bg='#0d47a1', fg='white').pack(pady=10)
    
    # ========================================================================
    # PROCESSES TAB
    # ========================================================================
    
    def _create_processes_tab(self):
        """Create process manager"""
        tab = tk.Frame(self.notebook, bg='#263238')
        self.notebook.add(tab, text="⚙ Processes")
        
        # Toolbar
        toolbar = tk.Frame(tab, bg='#37474f')
        toolbar.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Button(
            toolbar,
            text="🔄 Refresh Processes",
            command=self.refresh_processes,
            bg='#0d47a1',
            fg='white',
            font=('Arial', 10, 'bold')
        ).pack(side=tk.LEFT, padx=5)
        
        # Process list
        list_frame = tk.Frame(tab, bg='#263238')
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0, 10))
        
        self.process_list = scrolledtext.ScrolledText(
            list_frame,
            bg='#1e1e1e',
            fg='#00ff00',
            font=('Consolas', 10)
        )
        self.process_list.pack(fill=tk.BOTH, expand=True)
        
        # Initial listing
        self.refresh_processes()
    
    def refresh_processes(self):
        """Refresh process list"""
        self.process_list.delete(1.0, tk.END)
        
        if self.kernel:
            processes = self.kernel.scheduler.list_processes()
            self.process_list.insert(tk.END, "Process List\n")
            self.process_list.insert(tk.END, "=" * 80 + "\n\n")
            self.process_list.insert(tk.END, f"{'PID':<6} {'NAME':<15} {'STATE':<12} {'PRI':<5} {'MEM':<10} {'CPU':<10} QUANTUM\n")
            self.process_list.insert(tk.END, "-" * 80 + "\n")
            
            for p in processes:
                self.process_list.insert(
                    tk.END,
                    f"{p['pid']:<6} {p['name']:<15} {p['state']:<12} {p['priority']:<5} {p['memory_kb']}KB{'':<5} {p['cpu_time']}s{'':<5} {p['quantum']}\n"
                )
    
    # ========================================================================
    # MONITOR TAB
    # ========================================================================
    
    def _create_monitor_tab(self):
        """Create system monitor"""
        tab = tk.Frame(self.notebook, bg='#263238')
        self.notebook.add(tab, text="📈 Monitor")
        
        # Memory usage
        mem_frame = tk.LabelFrame(tab, text="Memory Usage", bg='#37474f', fg='white', font=('Arial', 12, 'bold'))
        mem_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.mem_canvas = tk.Canvas(mem_frame, height=100, bg='#263238', highlightthickness=0)
        self.mem_canvas.pack(fill=tk.X, padx=10, pady=10)
        
        self.mem_label = tk.Label(mem_frame, text="", bg='#37474f', fg='white', font=('Arial', 10))
        self.mem_label.pack(pady=5)
        
        # Performance stats
        perf_frame = tk.LabelFrame(tab, text="Performance Statistics", bg='#37474f', fg='white', font=('Arial', 12, 'bold'))
        perf_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.perf_text = scrolledtext.ScrolledText(
            perf_frame,
            bg='#1e1e1e',
            fg='#00ff00',
            font=('Consolas', 10)
        )
        self.perf_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Refresh button
        tk.Button(
            tab,
            text="🔄 Refresh Stats",
            command=self.refresh_monitor,
            bg='#0d47a1',
            fg='white',
            font=('Arial', 11, 'bold'),
            height=2
        ).pack(fill=tk.X, padx=10, pady=10)
        
        # Initial refresh
        self.refresh_monitor()
    
    def refresh_monitor(self):
        """Refresh monitor stats"""
        if not self.kernel:
            return
        
        # Memory usage
        mem_usage = self.kernel.memory.get_usage()
        total = mem_usage['total_kb']
        used = mem_usage['used_kb']
        free = total - used
        
        self.mem_canvas.delete('all')
        width = self.mem_canvas.winfo_width() or 600
        used_width = (used / total * width) if total > 0 else 0
        
        self.mem_canvas.create_rectangle(0, 20, used_width, 80, fill='#4caf50', outline='')
        self.mem_canvas.create_rectangle(used_width, 20, width, 80, fill='#424242', outline='')
        self.mem_canvas.create_text(
            width // 2, 50,
            text=f"{used} KB / {total} KB ({(used/total*100 if total > 0 else 0):.1f}%)",
            fill='white',
            font=('Arial', 11, 'bold')
        )
        
        self.mem_label.config(text=f"Free: {free} KB  |  Pages: {mem_usage['allocated_pages']}/{mem_usage['total_pages']}")
        
        # Performance stats
        self.perf_text.delete(1.0, tk.END)
        
        if hasattr(self.kernel, 'profiler'):
            stats = self.kernel.profiler.get_stats()
            self.perf_text.insert(tk.END, "Performance Statistics\n")
            self.perf_text.insert(tk.END, "=" * 60 + "\n\n")
            
            for key, value in stats.items():
                if isinstance(value, float):
                    self.perf_text.insert(tk.END, f"{key}: {value:.2f}\n")
                else:
                    self.perf_text.insert(tk.END, f"{key}: {value}\n")
    
    # ========================================================================
    # QUICK ACTIONS
    # ========================================================================
    
    def quick_quantum(self):
        """Quick quantum test"""
        self.notebook.select(2)
        self.run_shor()
    
    def quick_network(self):
        """Quick network test"""
        self.notebook.select(3)
        self.run_dns()
    
    # ========================================================================
    # UPDATE LOOP
    # ========================================================================
    
    def _start_update_loop(self):
        """Start periodic update loop"""
        self.update_dashboard()
        self.after(1000, self._start_update_loop)
    
    def update_dashboard(self):
        """Update dashboard stats"""
        if not self.kernel:
            return
        
        # Update quick stats
        if hasattr(self.kernel, 'profiler'):
            stats = self.kernel.profiler.get_stats()
            uptime = stats.get('uptime_seconds', 0)
            self.stats_labels['Uptime'].config(text=f"{int(uptime)}s")
        
        processes = len(self.kernel.scheduler.processes)
        self.stats_labels['Processes'].config(text=str(processes))
        
        mem_usage = self.kernel.memory.get_usage()
        self.stats_labels['Memory Used'].config(text=f"{mem_usage['used_kb']} KB")
        
        if hasattr(self.kernel, 'network'):
            net_stats = self.kernel.network.get_stats()
            self.stats_labels['Network Connections'].config(text=str(net_stats.get('tcp_connections', 0)))
    
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            "About QuantumOS",
            "QuantumOS Advanced v1.0.0\n\n"
            "A fully functional operating system with:\n"
            "• Quantum Computing (Shor's, QFT, VQE, QAOA)\n"
            "• Network Stack (TCP/IP, DNS, HTTP)\n"
            "• Process Management\n"
            "• File System\n"
            "• IPC and System Calls\n\n"
            "Built with Python and Tkinter"
        )

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run QuantumOS GUI"""
    app = QuantumOSGUI()
    app.mainloop()

if __name__ == "__main__":
    main()
