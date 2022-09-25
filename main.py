#!/usr/bin/env python3
"""
Author: R3tr0
Date: 25/09/2022
Purpose: will handle the fast api requests.
"""
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from utils import get_file_data

FILE_NAME = "index_new.html"
web_app = FastAPI()


@web_app.get("/", response_class=HTMLResponse)
def get_website():
    """
    gets the regular website for the victim device
    """
    html_data = ""
    try:
        html_data = get_file_data(FILE_NAME)
    except FileNotFoundError:
        pass
    return html_data


@web_app.post("/location_update")
def update_location():
    """
    handles the location update of the program from the client side
    """
    pass
