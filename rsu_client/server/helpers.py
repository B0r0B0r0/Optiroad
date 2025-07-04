import socket

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        # Folosește un IP „extern” doar ca să determine rețeaua locală (nu face conexiune reală)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception as e:
        print("Could not determine local IP:", e)
        return "127.0.0.1"