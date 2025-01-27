import json
import requests
import socket
import os
import re
import sys

DISCORD_WEBHOOK_FILE_NAME = "dwebhook.js"

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

def get_file_data(file_path):
    """
    gets the file data
    :param file_path: the path to the file you want to read
    :return: the file data as plain text
    """
    with open(file_path, 'r') as open_file:
        return open_file.read()


def update_webhook(webhook: str, webhook_data: dict):
    """
    will send a post request to the given webhook
    :param webhook: the webhook you want to update
    """
    request_payload = json.dumps(webhook_data)
    headers = {'Content-Type': 'application/json'}
    requests.request("POST", webhook, headers=headers, data=request_payload)

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

