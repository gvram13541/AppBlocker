import socket

def discover_computers(subnet):
    found_computers = []
    for ip_addr in [f"{subnet}.{i}" for i in range(1, 255)]:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.1)
            s.connect((ip_addr, 135)) 
            s.close()
            found_computers.append(ip_addr)
        except (socket.timeout, ConnectionRefusedError):
            pass
    return found_computers