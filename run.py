#!/usr/bin/python3
# -*-coding:utf-8 -*

import re
import os
import sys
import random
import datetime
import subprocess
import urllib.request

osImages = ["blinkfed","blinkubu"]
ubuntuName = "vivid"
fedoraName = "f21"

def checkInstallation():
    #Check the presence of the three main containers
    #and the two main OS images
    regExp = re.compile("Exited \(0\).*?blink(fonts|browsers|plugins).*?\\n")
    output = subprocess.check_output(["sudo","docker","ps","-a"]).decode()
    if len(regExp.findall(output)) != 3:
        sys.exit("Blink is not installed")

    output = subprocess.check_output(["sudo","docker","images"]).decode()
    for image in osImages :
        if image not in output:
            sys.exit("Blink is not installed")

    #If the installation is correct, we generate the LD Preload libraries
    generateLibrairies()


def generateLibrairies():

    #Fedora
    #We retrieve the kernel version of Fedora
    #ex: 3.18.5-201.fc21.x86_64
    fedKernel = ""
    #We write the header file
    subprocess.call(["echo","\"#define "+fedKernel+"\"",">","preload/modUname.h"])
    #We compile the library
    subprocess.call(["gcc","-Wall","-fPIC","-shared","-o","modFedUname.so","modUname.c"])

    #Ubuntu
    #We retrieve the kernel version of Ubuntu
    #ex: 3.13.0-24-generic
    ubuSource = urllib.request.urlopen("http://packages.ubuntu.com/search?keywords=linux-image&searchon=names&suite="+
                                       ubuntuName+"&section=main").read()
    ubuKernel = re.search("linux-image-(.*?)\">",str(ubuSource)).group(1)
    #We write the header file
    subprocess.call(["echo","\"#define "+ubuKernel+"\"",">","preload/modUname.h"])
    #We compile the library
    subprocess.call(["gcc","-Wall","-fPIC","-shared","-o","modUbuUname.so","modUname.c"])

    print("LD Preload libraries generated")

    #We write a file that indicates that the installation is complete
    #This file contains the date of last generation
    subprocess.call(["echo",datetime.date.today().toordinal(),">","installComplete"])
    print("installComplete file written")

def main():

    if not os.path.isfile("installComplete"):
        checkInstallation()
        print("Installation verified")
    else:
        #We check if the "LD preload" libraries have been compiled in the last 30 days
        #If not, we retrieve the latest version online and recompile the libraries
        with open('installComplete', 'r') as f:
            data = f.read()
        pastDate = datetime.date.fromordinal(int(data))
        nowDate = datetime.date.today()
        days = (nowDate-pastDate).days
        print("Days since last library regeneration : {}".format(days))
        if days > 30:
            generateLibrairies()

    print("Launching Blink browsing environment")
    downloadsPath =  os.path.abspath("data/downloads")
    profilePath = os.path.abspath("data/profile")
    ldpreloadPath = os.path.abspath("ldpreload")
    launchCommand = "sudo docker run -ti --rm -e DISPLAY " \
                    "-v /tmp/.X11-unix:/tmp/.X11-unix " \
                    "-v "+downloadsPath+":/home/blink/Downloads " \
                    "-v "+profilePath+":/home/blink/profile " \
                    "-v "+ldpreloadPath+":/home/blink/ldpreload "\
                    "--volumes-from blinkbrowsers " \
                    "--volumes-from blinkplugins " \
                    "--volumes-from blinkfonts "
    chosenImage = osImages[random.randint(0,len(osImages)-1)]
    print("Image "+chosenImage+" chosen")
    subprocess.call(launchCommand+chosenImage,shell=True)

    print("End of script")

if __name__ == "__main__":
    main()
