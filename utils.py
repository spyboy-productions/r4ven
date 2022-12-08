"""
Purpose: will hold the util functions of the program
"""
import json
import requests


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
