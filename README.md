<p align="center">
    <a href="https://spyboy.in/twitter">
      <img src="https://img.shields.io/badge/-TWITTER-black?logo=twitter&style=for-the-badge">
    </a>
    &nbsp;
    <a href="https://spyboy.in/">
      <img src="https://img.shields.io/badge/-spyboy.in-black?logo=google&style=for-the-badge">
    </a>
    &nbsp;
    <a href="https://spyboy.blog/">
      <img src="https://img.shields.io/badge/-spyboy.blog-black?logo=wordpress&style=for-the-badge">
    </a>
    &nbsp;
    <a href="https://spyboy.in/Discord">
      <img src="https://img.shields.io/badge/-Discord-black?logo=discord&style=for-the-badge">
    </a>
  
</p>

<img width="100%" align="centre" src="https://cdn.discordapp.com/attachments/897390115243065374/978385012401537074/Cream_Brown_Aesthetic_New_Product_Skincare_Canvas_Banner.png" />

<h4 align="center"> Track User's Smartphone/Pc Ip And Gps Location. </h4>

The tool hosts a fake website which uses an iframe to display a legit website and, if the target allows it, it will fetch the Gps location `(latitude and longitude)` of the target along with `IP Address` and `Device Information`.

<h4 align="center"> This tool is a Proof of Concept and is for Educational Purposes Only. </h4> 

Using this tool, you can find out what information a malicious website can gather about you and your devices and why you shouldn't click on random links or grant permissions like Location to them.

---
### On link click

```diff
+ it wil automatically fetch ip address and device information
! if location permission allowed, it will fetch exact location of target.
```

### Limitation

```diff

- It will not work on laptops or phones that have broken GPS, 
# browsers that block javascript,
# or if the user is mocking the GPS location. 

- Safari - auto block location permission
- Brave - auto block location permission
- Firefox - after a recent update this browser became very weird it allows location permission but it's not accurate at all.

+ Best work with Chrome browser and location accuracy will be more accurate if you use this on a smartphone.

```

### IP location vs GPS location

```diff
- Geographic location based on IP address is NOT accurate,
# Does not provide the location of the target. 
# Instead, it provides the approximate location of the ISP (Internet service provider)
```
```diff
+ GPS fetch almost exact location because it uses longitude and latitude coordinates.
@@ Once location permission is granted @@
# accurate location information is recieved to within 20 to 30 meters of the user's location.
# (it's almost exact location)
```
---

<h4 align="center">
  OS compatibility :
  <br><br>
  <img src="https://img.shields.io/badge/Windows-05122A?style=for-the-badge&logo=windows">
  <img src="https://img.shields.io/badge/Linux-05122A?style=for-the-badge&logo=linux">
  <img src="https://img.shields.io/badge/Android-05122A?style=for-the-badge&logo=android">
  <img src="https://img.shields.io/badge/macOS-05122A?style=for-the-badge&logo=macos">
</h4>

<h4 align="center"> 
Requirements:
<br><br>
<img src="https://img.shields.io/badge/Python-05122A?style=for-the-badge&logo=python">
<img src="https://img.shields.io/badge/Git-05122A?style=for-the-badge&logo=git">
<img src="https://img.shields.io/badge/Discord webhook-05122A?style=for-the-badge&logo=discord">
</h4>

### ⭔ Installation
---

```
git clone https://github.com/spyboy-productions/r4ven.git
```
```
cd r4ven
```
```
pip3 install -r requirements.txt
```
```
python3 r4ven.py
```

```enter your discord webhook url (set up a channel in your discord server with webhook integration)```

https://support.discord.com/hc/en-us/articles/228383668-Intro-to-Webhooks

`if not have discord account and sever make one, it's free.`

https://discord.com/

---

📍 _Track info data will be sent to your discord webhook channel._

- why discord webhook? Conveniently, you will receive a notification when someone clicks on the link.

---

#### ⭓ To chnage website template

- open file `index.html` on line 12 and replace the `src` in the iframe. (Note: not every website support iframe)

---

#### ⭓ To port forward install ngrok or use ssh

- For ngrok port forward type: ngrok http 8000
- For ssh port forwarding type: ssh -R 80:localhost:8000 ssh.localhost.run

---

#### 💬 If having issue [Chat here](https://discord.gg/ZChEmMwE8d)
[![Discord Server](https://discord.com/api/guilds/726495265330298973/embed.png)](https://discord.gg/ZChEmMwE8d)

### ⭔ Snapshots
---

<img width="100%" align="centre" src="https://cdn.discordapp.com/attachments/748888788490780721/979512791180390460/Screen_Shot_2022-05-27_at_3.39.33_AM.png" />
<img width="100%" align="centre" src="https://cdn.discordapp.com/attachments/748888788490780721/979508653205913650/Screen_Shot_2022-05-27_at_3.40.19_AM.png" />
<img width="100%" align="centre" src="https://cdn.discordapp.com/attachments/748888788490780721/980448995958722650/Screen_Shot_2022-05-29_at_5.55.48_PM.png" />
<img width="100%" align="centre" src="https://cdn.discordapp.com/attachments/748888788490780721/980449483684982834/Screen_Shot_2022-05-29_at_6.05.44_PM.png" />
