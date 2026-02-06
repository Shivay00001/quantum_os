                                                #`````````  `!/usr/bin/env python3
"""
Network Protocol Stack for QuantumOS
Implements: TCP/IP, UDP, DNS, HTTP protocols
"""

import random
import time
import hashlib
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import struct

# ============================================================================
# ETHERNET (LINK LAYER)
# ============================================================================

@dataclass
class EthernetFrame:
    """Ethernet frame structure"""
    dest_mac: str
    src_mac: str
    ethertype: int  # 0x0800 for IPv4, 0x0806 for ARP
    payload: bytes
    
    def to_bytes(self) -> bytes:
        """Serialize frame to bytes"""
        header = f"{self.dest_mac}{self.src_mac}{self.ethertype:04x}".encode()
        return header + self.payload
    
    @staticmethod
    def from_bytes(data: bytes) -> 'EthernetFrame':
        """Deserialize frame from bytes"""
        dest_mac = data[:12].decode()
        src_mac = data[12:24].decode()
        ethertype = int(data[24:28].decode(), 16)
        payload = data[28:]
        return EthernetFrame(dest_mac, src_mac, ethertype, payload)

# ============================================================================
# ARP (ADDRESS RESOLUTION PROTOCOL)
# ============================================================================

class ARPTable:
    """ARP table for IP to MAC address mapping"""
    
    def __init__(self):
        self.table: Dict[str, str] = {}
        self.cache_timeout = 300  # 5 minutes
        self.timestamps: Dict[str, float] = {}
    
    def add_entry(self, ip: str, mac: str):
        """Add or update ARP table entry"""
        self.table[ip] = mac
        self.timestamps[ip] = time.time()
    
    def lookup(self, ip: str) -> Optional[str]:
        """Lookup MAC address for IP"""
        if ip in self.table:
            # Check if entry is still valid
            if time.time() - self.timestamps[ip] < self.cache_timeout:
                return self.table[ip]
            else:
                del self.table[ip]
                del self.timestamps[ip]
        return None
    
    def get_all(self) -> Dict[str, str]:
        """Get all ARP entries"""
        return self.table.copy()

# ============================================================================
# IP (NETWORK LAYER)
# ============================================================================

class IPProtocol(Enum):
    ICMP = 1
    TCP = 6
    UDP = 17

@dataclass
class IPPacket:
    """IPv4 packet structure"""
    version: int = 4
    header_length: int = 5
    ttl: int = 64
    protocol: IPProtocol = IPProtocol.TCP
    src_ip: str = "0.0.0.0"
    dest_ip: str = "0.0.0.0"
    payload: bytes = b""
    
    def calculate_checksum(self) -> int:
        """Calculate IP header checksum"""
        # Simplified checksum calculation
        data = f"{self.version}{self.header_length}{self.ttl}{self.protocol.value}{self.src_ip}{self.dest_ip}".encode()
        return sum(data) & 0xFFFF
    
    def to_bytes(self) -> bytes:
        """Serialize packet to bytes"""
        header = struct.pack('!BBHHHBBH4s4s',
            (self.version << 4) | self.header_length,  # Version + IHL
            0,  # TOS
            20 + len(self.payload),  # Total length
            random.randint(0, 65535),  # Identification
            0,  # Flags + Fragment offset
            self.ttl,
            self.protocol.value,
            self.calculate_checksum(),
            self._ip_to_bytes(self.src_ip),
            self._ip_to_bytes(self.dest_ip)
        )
        return header + self.payload
    
    @staticmethod
    def _ip_to_bytes(ip: str) -> bytes:
        """Convert IP string to bytes"""
        return bytes([int(x) for x in ip.split('.')])
    
    @staticmethod
    def _bytes_to_ip(data: bytes) -> str:
        """Convert bytes to IP string"""
        return '.'.join(str(b) for b in data)

# ============================================================================
# TCP (TRANSPORT LAYER)
# ============================================================================

class TCPFlags:
    """TCP flag constants"""
    FIN = 0x01
    SYN = 0x02
    RST = 0x04
    PSH = 0x08
    ACK = 0x10
    URG = 0x20

class TCPState(Enum):
    """TCP connection states"""
    CLOSED = "CLOSED"
    LISTEN = "LISTEN"
    SYN_SENT = "SYN_SENT"
    SYN_RECEIVED = "SYN_RECEIVED"
    ESTABLISHED = "ESTABLISHED"
    FIN_WAIT_1 = "FIN_WAIT_1"
    FIN_WAIT_2 = "FIN_WAIT_2"
    CLOSE_WAIT = "CLOSE_WAIT"
    CLOSING = "CLOSING"
    LAST_ACK = "LAST_ACK"
    TIME_WAIT = "TIME_WAIT"

@dataclass
class TCPSegment:
    """TCP segment structure"""
    src_port: int
    dest_port: int
    seq_num: int
    ack_num: int
    flags: int
    window_size: int = 65535
    payload: bytes = b""
    
    def to_bytes(self) -> bytes:
        """Serialize TCP segment"""
        header = struct.pack('!HHIIBBHHH',
            self.src_port,
            self.dest_port,
            self.seq_num,
            self.ack_num,
            (5 << 4),  # Data offset (5 * 4 = 20 bytes)
            self.flags,
            self.window_size,
            0,  # Checksum (simplified)
            0   # Urgent pointer
        )
        return header + self.payload

@dataclass
class TCPConnection:
    """TCP connection state"""
    local_ip: str
    local_port: int
    remote_ip: str
    remote_port: int
    state: TCPState = TCPState.CLOSED
    seq_num: int = 0
    ack_num: int = 0
    send_buffer: bytes = b""
    recv_buffer: bytes = b""
    
    def __hash__(self):
        return hash((self.local_ip, self.local_port, self.remote_ip, self.remote_port))

class TCP:
    """TCP protocol implementation"""
    
    def __init__(self):
        self.connections: Dict[tuple, TCPConnection] = {}
        self.listeners: Dict[int, TCPConnection] = {}
    
    def listen(self, local_ip: str, port: int) -> bool:
        """Listen on a port"""
        if port in self.listeners:
            return False
        
        conn = TCPConnection(
            local_ip=local_ip,
            local_port=port,
            remote_ip="0.0.0.0",
            remote_port=0,
            state=TCPState.LISTEN
        )
        self.listeners[port] = conn
        return True
    
    def connect(self, local_ip: str, local_port: int, remote_ip: str, remote_port: int) -> TCPConnection:
        """Initiate TCP connection (3-way handshake)"""
        
        # Create connection
        conn = TCPConnection(
            local_ip=local_ip,
            local_port=local_port,
            remote_ip=remote_ip,
            remote_port=remote_port,
            state=TCPState.SYN_SENT,
            seq_num=random.randint(0, 2**32 - 1)
        )
        
        key = (local_ip, local_port, remote_ip, remote_port)
        self.connections[key] = conn
        
        # Send SYN
        syn_segment = TCPSegment(
            src_port=local_port,
            dest_port=remote_port,
            seq_num=conn.seq_num,
            ack_num=0,
            flags=TCPFlags.SYN
        )
        
        # Simulate receiving SYN-ACK
        conn.state = TCPState.ESTABLISHED
        conn.ack_num = random.randint(0, 2**32 - 1)
        
        return conn
    
    def send(self, conn: TCPConnection, data: bytes) -> int:
        """Send data over TCP connection"""
        if conn.state != TCPState.ESTABLISHED:
            return 0
        
        # Add to send buffer
        conn.send_buffer += data
        
        # Create TCP segment
        segment = TCPSegment(
            src_port=conn.local_port,
            dest_port=conn.remote_port,
            seq_num=conn.seq_num,
            ack_num=conn.ack_num,
            flags=TCPFlags.PSH | TCPFlags.ACK,
            payload=data
        )
        
        conn.seq_num += len(data)
        return len(data)
    
    def receive(self, conn: TCPConnection, max_bytes: int = 4096) -> bytes:
        """Receive data from TCP connection"""
        data = conn.recv_buffer[:max_bytes]
        conn.recv_buffer = conn.recv_buffer[max_bytes:]
        return data
    
    def close(self, conn: TCPConnection):
        """Close TCP connection (4-way handshake)"""
        if conn.state == TCPState.ESTABLISHED:
            conn.state = TCPState.FIN_WAIT_1
            
            # Send FIN
            fin_segment = TCPSegment(
                src_port=conn.local_port,
                dest_port=conn.remote_port,
                seq_num=conn.seq_num,
                ack_num=conn.ack_num,
                flags=TCPFlags.FIN | TCPFlags.ACK
            )
            
            # Simulate complete close
            conn.state = TCPState.CLOSED
            
            # Remove from connections
            key = (conn.local_ip, conn.local_port, conn.remote_ip, conn.remote_port)
            if key in self.connections:
                del self.connections[key]

# ============================================================================
# UDP (TRANSPORT LAYER)
# ============================================================================

@dataclass
class UDPDatagram:
    """UDP datagram structure"""
    src_port: int
    dest_port: int
    payload: bytes
    
    def to_bytes(self) -> bytes:
        """Serialize UDP datagram"""
        length = 8 + len(self.payload)
        header = struct.pack('!HHHH',
            self.src_port,
            self.dest_port,
            length,
            0  # Checksum (simplified)
        )
        return header + self.payload

class UDP:
    """UDP protocol implementation"""
    
    def __init__(self):
        self.sockets: Dict[int, list] = {}
    
    def bind(self, port: int):
        """Bind to a port"""
        if port not in self.sockets:
            self.sockets[port] = []
    
    def send(self, src_port: int, dest_ip: str, dest_port: int, data: bytes) -> UDPDatagram:
        """Send UDP datagram"""
        datagram = UDPDatagram(
            src_port=src_port,
            dest_port=dest_port,
            payload=data
        )
        return datagram
    
    def receive(self, port: int) -> Optional[Tuple[str, int, bytes]]:
        """Receive UDP datagram"""
        if port in self.sockets and self.sockets[port]:
            src_ip, src_port, data = self.sockets[port].pop(0)
            return (src_ip, src_port, data)
        return None

# ============================================================================
# DNS (APPLICATION LAYER)
# ============================================================================

@dataclass
class DNSRecord:
    """DNS record"""
    name: str
    record_type: str  # A, AAAA, CNAME, MX, etc.
    value: str
    ttl: int = 3600

class DNS:
    """DNS resolver and server"""
    
    def __init__(self):
        self.records: Dict[str, List[DNSRecord]] = {}
        self.cache: Dict[str, Tuple[str, float]] = {}
        
        # Add some default records
        self._initialize_default_records()
    
    def _initialize_default_records(self):
        """Add default DNS records"""
        default_records = [
            DNSRecord("localhost", "A", "127.0.0.1"),
            DNSRecord("quantumos.local", "A", "192.168.1.100"),
            DNSRecord("gateway", "A", "192.168.1.1"),
            DNSRecord("dns", "A", "8.8.8.8"),
        ]
        
        for record in default_records:
            if record.name not in self.records:
                self.records[record.name] = []
            self.records[record.name].append(record)
    
    def add_record(self, record: DNSRecord):
        """Add DNS record"""
        if record.name not in self.records:
            self.records[record.name] = []
        self.records[record.name].append(record)
    
    def query(self, hostname: str, record_type: str = "A") -> Optional[str]:
        """Query DNS for hostname"""
        
        # Check cache first
        cache_key = f"{hostname}:{record_type}"
        if cache_key in self.cache:
            value, timestamp = self.cache[cache_key]
            if time.time() - timestamp < 300:  # 5 minute cache
                return value
        
        # Lookup in records
        if hostname in self.records:
            for record in self.records[hostname]:
                if record.record_type == record_type:
                    # Cache the result
                    self.cache[cache_key] = (record.value, time.time())
                    return record.value
        
        return None
    
    def reverse_lookup(self, ip: str) -> Optional[str]:
        """Reverse DNS lookup (IP to hostname)"""
        for hostname, records in self.records.items():
            for record in records:
                if record.record_type == "A" and record.value == ip:
                    return hostname
        return None

# ============================================================================
# HTTP (APPLICATION LAYER)
# ============================================================================

@dataclass
class HTTPRequest:
    """HTTP request"""
    method: str  # GET, POST, PUT, DELETE, etc.
    path: str
    version: str = "HTTP/1.1"
    headers: Dict[str, str] = field(default_factory=dict)
    body: bytes = b""
    
    def to_bytes(self) -> bytes:
        """Serialize HTTP request"""
        request_line = f"{self.method} {self.path} {self.version}\r\n"
        headers = "".join(f"{k}: {v}\r\n" for k, v in self.headers.items())
        return (request_line + headers + "\r\n").encode() + self.body
    
    @staticmethod
    def from_bytes(data: bytes) -> 'HTTPRequest':
        """Parse HTTP request from bytes"""
        lines = data.split(b'\r\n')
        request_line = lines[0].decode().split()
        
        method = request_line[0]
        path = request_line[1]
        version = request_line[2] if len(request_line) > 2 else "HTTP/1.1"
        
        headers = {}
        i = 1
        while i < len(lines) and lines[i]:
            if b':' in lines[i]:
                key, value = lines[i].decode().split(': ', 1)
                headers[key] = value
            i += 1
        
        body = b'\r\n'.join(lines[i+1:]) if i+1 < len(lines) else b""
        
        return HTTPRequest(method, path, version, headers, body)

@dataclass
class HTTPResponse:
    """HTTP response"""
    version: str = "HTTP/1.1"
    status_code: int = 200
    status_message: str = "OK"
    headers: Dict[str, str] = field(default_factory=dict)
    body: bytes = b""
    
    def to_bytes(self) -> bytes:
        """Serialize HTTP response"""
        status_line = f"{self.version} {self.status_code} {self.status_message}\r\n"
        
        if 'Content-Length' not in self.headers:
            self.headers['Content-Length'] = str(len(self.body))
        
        headers = "".join(f"{k}: {v}\r\n" for k, v in self.headers.items())
        return (status_line + headers + "\r\n").encode() + self.body

class HTTPServer:
    """Simple HTTP server"""
    
    def __init__(self, host: str = "0.0.0.0", port: int = 80):
        self.host = host
        self.port = port
        self.routes: Dict[str, callable] = {}
    
    def route(self, path: str):
        """Decorator to register route handlers"""
        def decorator(func):
            self.routes[path] = func
            return func
        return decorator
    
    def handle_request(self, request: HTTPRequest) -> HTTPResponse:
        """Handle incoming HTTP request"""
        
        if request.path in self.routes:
            handler = self.routes[request.path]
            return handler(request)
        else:
            return HTTPResponse(
                status_code=404,
                status_message="Not Found",
                headers={"Content-Type": "text/html"},
                body=b"<h1>404 Not Found</h1>"
            )

# ============================================================================
# SOCKET INTERFACE
# ============================================================================

class SocketType(Enum):
    STREAM = "STREAM"  # TCP
    DGRAM = "DGRAM"    # UDP

class Socket:
    """BSD-style socket interface"""
    
    def __init__(self, socket_type: SocketType):
        self.type = socket_type
        self.tcp = TCP() if socket_type == SocketType.STREAM else None
        self.udp = UDP() if socket_type == SocketType.DGRAM else None
        self.connection: Optional[TCPConnection] = None
        self.bound_port: Optional[int] = None
    
    def bind(self, ip: str, port: int):
        """Bind socket to address"""
        self.bound_port = port
        if self.type == SocketType.STREAM:
            self.tcp.listen(ip, port)
        else:
            self.udp.bind(port)
    
    def connect(self, remote_ip: str, remote_port: int):
        """Connect to remote address (TCP only)"""
        if self.type == SocketType.STREAM:
            local_port = self.bound_port or random.randint(10000, 65535)
            self.connection = self.tcp.connect("127.0.0.1", local_port, remote_ip, remote_port)
    
    def send(self, data: bytes) -> int:
        """Send data"""
        if self.type == SocketType.STREAM and self.connection:
            return self.tcp.send(self.connection, data)
        return 0
    
    def recv(self, max_bytes: int = 4096) -> bytes:
        """Receive data"""
        if self.type == SocketType.STREAM and self.connection:
            return self.tcp.receive(self.connection, max_bytes)
        elif self.type == SocketType.DGRAM:
            result = self.udp.receive(self.bound_port)
            if result:
                return result[2]  # Return just the data
        return b""
    
    def close(self):
        """Close socket"""
        if self.type == SocketType.STREAM and self.connection:
            self.tcp.close(self.connection)

# ============================================================================
# NETWORK STACK MANAGER
# ============================================================================

class NetworkStack:
    """Complete network stack manager"""
    
    def __init__(self, local_ip: str = "192.168.1.100", mac: str = "00:1A:2B:3C:4D:5E"):
        self.local_ip = local_ip
        self.mac_address = mac
        self.arp = ARPTable()
        self.dns = DNS()
        self.tcp = TCP()
        self.udp = UDP()
        
        # Add self to ARP table
        self.arp.add_entry(local_ip, mac)
    
    def create_socket(self, socket_type: SocketType) -> Socket:
        """Create a new socket"""
        return Socket(socket_type)
    
    def ping(self, target_ip: str) -> bool:
        """Ping a target IP (ICMP echo)"""
        # Simplified ping - just check if we can resolve it
        mac = self.arp.lookup(target_ip)
        return mac is not None or target_ip == self.local_ip
    
    def traceroute(self, target_ip: str) -> List[str]:
        """Trace route to target (simplified)"""
        # Simplified traceroute
        hops = [
            self.local_ip,
            "192.168.1.1",  # Gateway
        ]
        
        if target_ip not in ["192.168.1.1", self.local_ip]:
            hops.append(target_ip)
        
        return hops
    
    def get_stats(self) -> Dict:
        """Get network statistics"""
        return {
            "local_ip": self.local_ip,
            "mac_address": self.mac_address,
            "arp_entries": len(self.arp.table),
            "dns_records": len(self.dns.records),
            "tcp_connections": len(self.tcp.connections),
            "tcp_listeners": len(self.tcp.listeners),
        }

# ============================================================================
# TESTING
# ============================================================================

def run_network_tests():
    """Test network stack functionality"""
    print("=" * 70)
    print("NETWORK PROTOCOL STACK TESTS")
    print("=" * 70)
    
    # Initialize network stack
    network = NetworkStack()
    
    # Test 1: DNS Resolution
    print("\n[TEST] DNS Resolution")
    ip = network.dns.query("localhost")
    print(f"localhost -> {ip}")
    ip = network.dns.query("quantumos.local")
    print(f"quantumos.local -> {ip}")
    
    # Test 2: ARP Table
    print("\n[TEST] ARP Table")
    network.arp.add_entry("192.168.1.1", "AA:BB:CC:DD:EE:FF")
    mac = network.arp.lookup("192.168.1.1")
    print(f"ARP: 192.168.1.1 -> {mac}")
    
    # Test 3: TCP Connection
    print("\n[TEST] TCP Socket")
    sock = network.create_socket(SocketType.STREAM)
    sock.bind("192.168.1.100", 8080)
    sock.connect("192.168.1.1", 80)
    sent = sock.send(b"GET / HTTP/1.1\r\n\r\n")
    print(f"TCP: Sent {sent} bytes")
    sock.close()
    print("TCP: Connection closed")
    
    # Test 4: UDP Datagram
    print("\n[TEST] UDP Socket")
    udp_sock = network.create_socket(SocketType.DGRAM)
    udp_sock.bind("192.168.1.100", 5353)
    print("UDP: Socket bound to port 5353")
    
    # Test 5: HTTP Request/Response
    print("\n[TEST] HTTP Protocol")
    request = HTTPRequest(
        method="GET",
        path="/index.html",
        headers={"Host": "quantumos.local"}
    )
    print(f"HTTP Request: {request.method} {request.path}")
    
    response = HTTPResponse(
        status_code=200,
        headers={"Content-Type": "text/html"},
        body=b"<html><body>Hello QuantumOS!</body></html>"
    )
    print(f"HTTP Response: {response.status_code} {response.status_message}")
    
    # Test 6: Network Stats
    print("\n[TEST] Network Statistics")
    stats = network.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Test 7: Ping and Traceroute
    print("\n[TEST] Network Utilities")
    result = network.ping("192.168.1.1")
    print(f"Ping 192.168.1.1: {'Success' if result else 'Failed'}")
    
    hops = network.traceroute("8.8.8.8")
    print(f"Traceroute to 8.8.8.8:")
    for i, hop in enumerate(hops, 1):
        print(f"  {i}. {hop}")
    
    print("\n" + "=" * 70)

if __name__ == "__main__":
    run_network_tests()
