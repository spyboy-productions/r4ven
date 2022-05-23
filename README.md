__________    _________   _______________ _______   
\______   \  /  |  \   \ /   /\_   _____/ \      \  
 |       _/ /   |  |\   Y   /  |    __)_  /   |   \ 
 |    |   \/    ^   /\     /   |        \/    |    \
 |____|_  /\____   |  \___/   /_______  /\____|__  /
        \/      |__|                  \/         \/ 

Track user ip and gps location.

This tool is a Proof of Concept and is for Educational Purposes Only.

### Installation
---

git clone https://github.com/thisisshubhamkumar/r4ven
cd r4ven
python3 r4ven.py
enter your discord webhook url (setup a channel in your discord server with webhook integration)
https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks

Track info data will be sent to your discord webhook channel.

To port forward install ngrok or use ssh

For ngrok port forward type: ngrok http 8000
For ssh port forwarding type: ssh -R 80:localhost:8080 ssh.localhost.run


