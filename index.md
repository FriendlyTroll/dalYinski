---
win_url_bin: https://github.com/FriendlyTroll/dalYinski/releases/download/v1.1/dalyinski-1.1.exe
win_url_zip: https://github.com/FriendlyTroll/dalYinski/releases/download/v1.1/dalyinski-1.1.zip
ubuntu_url: https://github.com/FriendlyTroll/dalYinski/releases/download/v1.1/dalyinski-1.1.deb
readme: https://github.com/FriendlyTroll/dalYinski/blob/master/README.md
---

## Instructions:
1. Install Firefox

2. Create new firefox profile

    In URL bar type "about:config" and click "Create a New Profile". Name it "selenium". Then click "Launch profile in new browser" and navigate to Youtube and login with your credentials.

3. Download and install server part for your Operating System

    ![ubuntu image]({{ site.github.url }}/assets/ubuntu-icon.png)
    [Ubuntu server app]({{ page.ubuntu_url }})

    ![win image]({{ site.github.url }}/assets/win10.png)
    [Windows server app (single .exe file) - see NOTE below]({{ page.win_url_bin }})

    ![win image]({{ site.github.url }}/assets/win10.png)
    [Windows server app (zipped folder)]({{ page.win_url_zip }})

    If you get a Windows Defender firewall window, check the box "Private networks, such as my home or work network" to allow the program to communicate with mobile app over your home network and check for updates.

    NOTE:
    After starting the app (single .exe file) on Windows you may get a popup "Windows protected your PC". Click on more info and choose "Run anyway". This happens because Windows incorrectly thinks the program is a virus so it might not allow you to run it. To get around this, click the Windows notification popup in the lower right and under "Affected items" select "Allow on device" in the Actions dropdown.

    If you are using some other antivirus software you might also get a warning from that software so you will need to allow the program to run in that specific antivirus software.

    To avoid the above issue (mostly), download the zipped folder, unzip it, find and run the dalyinski exe file that way. You can move this folder anywhere and create a shortcut to .exe on your desktop if you wish.

4. Install Android app 

<a href='https://play.google.com/store/apps/details?id=org.dalyinski.dalyinski&pcampaignid=pcampaignidMKT-Other-global-all-co-prtnr-py-PartBadge-Mar2515-1'><img alt='Get it on Google Play' src='https://play.google.com/intl/en_us/badges/static/images/badges/en_badge_web_generic.png' width="200" /></a>

5. In server app click on "Start server and open browser"
6. In the Android app tap "Connect to server" and wait a bit.

You should now be able to browse videos with the Android app.

Make sure the Firefox window remains open while you are using the app!







