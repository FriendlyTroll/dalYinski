# Installation
1. Install Firefox

2. Create new firefox profile

Open firefox and in address bar type "about:profiles" and click "Create a New Profile". Name it "selenium".
Then click "Launch profile in new browser" and navigate to Youtube and login with your
credentials. 

3. [Download and install server part](https://friendlytroll.github.io/dalYinski/)

After starting the app on Windows you may get a popup "Windows protected your PC". Click on more info
and choose "Run anyway".

If you get a Windows Defender firewall window, check the box "Private networks, such as my home or work network" and "Public networks..." to allow the program to communicate with mobile app over your home network and check for updates.

4. Install Android app

<a href='https://play.google.com/store/apps/details?id=org.dalyinski.dalyinski&pcampaignid=pcampaignidMKT-Other-global-all-co-prtnr-py-PartBadge-Mar2515-1'><img alt='Get it on Google Play' src='https://play.google.com/intl/en_us/badges/static/images/badges/en_badge_web_generic.png' width="200"/></a>

5. Click on "Start server and open browser"


You should now be able to browse videos with the Android app.

**Make sure the Firefox window remains open while you are using the app!**

# Screenshots
<img src="screenshots/Screenshot_20210306-113503.png" width=200 height=400>
<img src="screenshots/Screenshot_20210306-113510.png" width=200 height=400>
<img src="screenshots/Screenshot_20210306-114735.png" width=200 height=400>
<img src="screenshots/Screenshot_(Mar_6,_2021_12_40_49).png" width=200 height=400>

# Development Dependencies
## Linux
### GUI
- Python 3.8.5 (should already be installed on Ubuntu 20.04)
- python3-selenium (Ubuntu 20.04 package)
- python3-wxgtk4.0 (Ubuntu 20.04 package)

Install above via:
`sudo apt install python3-selenium python3-wxgtk4.0`

### Android Kivy app
For android part create new virtualenv and install from requirements.txt file.

    python3 -m venv myvenv
    source myvenv/bin/activate
    pip3 install -r requirements.txt

## Windows 10
### GUI
- Python 3.8.5
 
Install from win-requirements.txt.

    python -m venv myvenv
    venv\Scripts\activate.bat
    pip3 install -r win-requirements.txt

### Android Kivy app

    pip3 install -r requirements.txt

# Icons and resources used
* Icons: https://material.io/resources/icons/?style=baseline

