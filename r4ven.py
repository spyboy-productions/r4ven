#!/usr/bin/env python3
VERSION = '1.1.0'

R = '\033[31m'  # red
G = '\033[32m'  # green
C = '\033[36m'  # cyan
W = '\033[0m'   # white
Y = '\033[33m'  # yellow

import sys
import os
import subprocess

twitter_url = 'https://spyboy.in/twitter'
discord = 'https://spyboy.in/Discord'
website = 'https://spyboy.in/'
blog = 'https://spyboy.blog/'


art = r'''                                                    
__________    _________   _______________ _______   
\______   \  /  |  \   \ /   /\_   _____/ \      \  
 |       _/ /   |  |\   Y   /  |    __)_  /   |   \ 
 |    |   \/    ^   /\     /   |        \/    |    \
 |____|_  /\____   |  \___/   /_______  /\____|__  /
        \/      |__|                  \/         \/ '''

print(f'{R}{art}{W}\n')
print(f'{G}[+] {C}Version      : {W}{VERSION}')
print(f'{G}[+] {C}Created By   : {W}Spyboy')
print(f'{G} ╰➤ {C}Twitter   : {W}{twitter_url}')
print(f'{G} ╰➤ {C}Discord : {W}{discord}')
print(f'{G} ╰➤ {C}Website : {W}{website}')
print(f'{G} ╰➤ {C}Blog : {W}{blog}\n')

print(f'{Y}Localhost Link: {W}http://localhost:8000/r4ven.html')
os.system("python3 -m http.server")

