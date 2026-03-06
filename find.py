import streamlit as st
from ping3 import ping

def ping_and_identify(ip: str) -> str:
    try:
        # ping with TTL info
        response = ping(ip, unit='ms', ttl=True)
        if response is None:
            return f"{ip}: No response"

        # ping3 returns (time, ttl) if ttl=True
        if isinstance(response, tuple):
            _, ttl = response
        else:
            # fallback if ttl not available
            ttl = None

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

    except Exception as e:
        return f"{ip}: Error ({e})"

# --- Streamlit Webapp ---
st.set_page_config(page_title="OS Detector via Ping", page_icon="🌐", layout="centered")
st.title("🌐 OS Detection via Ping")

st.write("Enter a list of IP addresses (comma or newline separated). "
         "The app will ping each and guess the OS based on TTL values.")

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
