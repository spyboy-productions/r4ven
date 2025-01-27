import random
import sys

twitter_url = 'https://spyboy.in/twitter'
discord = 'https://spyboy.in/Discord'
blog = 'https://spyboy.blog/'
github = 'https://github.com/spyboy-productions/r4ven'

VERSION = '1.1.5'

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

    print(f'{B}[~] {R}Note :{G} Track info will be sent to your discord webhook {W}\n')
    