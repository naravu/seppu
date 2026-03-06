import subprocess
import platform
import streamlit as st

def ping_and_identify(ip: str) -> str:
    # Choose ping command based on OS
    ping_cmd = ["ping", "-c", "1", ip] if platform.system() != "Windows" else ["ping", "-n", "1", ip]
    
    try:
        output = subprocess.check_output(ping_cmd, stderr=subprocess.STDOUT, universal_newlines=True)
        
        ttl = None
        for line in output.splitlines():
            if "ttl=" in line.lower():
                ttl = int(line.lower().split("ttl=")[1].split()[0])
                break
        
        if ttl is None:
            return f"{ip}: Unknown (no TTL found)"
        
        # Heuristic classification
        if 120 <= ttl <= 128:
            os_type = "Windows"
        elif 60 <= ttl <= 64:
            os_type = "Linux/Unix"
        elif 240 <= ttl <= 255:
            os_type = "Network Device"
        else:
            os_type = "Unknown"
        
        return f"{ip}: {os_type} (TTL={ttl})"
    
    except subprocess.CalledProcessError:
        return f"{ip}: No response"

# --- Streamlit Webapp ---
st.set_page_config(page_title="OS Detector via Ping", page_icon="🌐", layout="centered")
st.title("🌐 OS Detection via Ping")

st.write("Enter a list of IP addresses (comma or newline separated). The app will ping each and guess the OS based on TTL values.")

# Input box
ip_input = st.text_area("IP Addresses:", placeholder="192.168.1.1\n192.168.1.10\n192.168.1.20")

if st.button("🔍 Detect OS"):
    ips = [ip.strip() for ip in ip_input.replace(",", "\n").splitlines() if ip.strip()]
    if not ips:
        st.warning("Please enter at least one IP address.")
    else:
        results = [ping_and_identify(ip) for ip in ips]
        st.subheader("Results")
        for res in results:
            st.write(res)
