#!/usr/bin/env python3

try:
    from mastodon import Mastodon
    import os
    import sys
    import requests
    import time
    import pprint
    import git
    from datetime import datetime
    import logging
    import subprocess
except:
    print("please pip3 install mastodon.py GitPython")

#file format
#
#domain
#username
#password


url=""
user=""
password=""
secret=""

def create(filename):
    global url
    global user
    global password
    global secret
    with open(filename,"r") as f:
        r=f.readlines()
        secret=r[0].replace("\n", "") + ".secret"
        url="https://"+r[0].replace("\n","")
        user=r[1].replace("\n","")
        password=r[2].replace("\n","")
    if os.path.exists(secret) == False:
        Mastodon.create_app(
            'pleromabot',
            api_base_url = url,
            to_file = secret
        )

def toot(bot, text):
    try:
        t="@noyuno " + text
        logging.debug("toot :" + t)
        bot.status_post(status=t, visibility="unlisted")
    except Exception as e:
        logging.error("unable to toot: " + t + "," + str(e))

def execute(command):
    logging.debug("execute: " + " ".join(command))
    o=subprocess.check_output(command,stderr=subprocess.STDOUT).decode("UTF-8")
    logging.debug(o)
    return o

def main():
    global url
    global user
    global password
    global secret
    bot = Mastodon(
        client_id = secret, 
        api_base_url = url
    )

    # does not work in pleroma
    #bot.log_in(
    #    email,
    #    password,
    #    to_file = 'user.secret'
    #)

    # login
    clientid=""
    clientsecret=""
    with open(secret,"r") as f:
        r=f.readlines()
        clientid=r[0].replace("\n", "")
        clientsecret=r[1].replace("\n", "")

    try:
        logging.debug("auth")
        auth = requests.post(url + "/oauth/token", params={
            "name":user, # no email address
            "password":password, 
            "grant_type":"password", 
            "client_id":clientid, 
            "client_secret":clientsecret
        }).json()
    except Exception as e:
        logging.error("unable to auth:"+str(e))

    bot = Mastodon(
        client_id = secret,
        access_token = auth["access_token"],
        api_base_url = url
    )
    lastauth = datetime.now()
    toot(bot, 'ちゃろー')
    current_id=0
    toots = bot.timeline_home(since_id=current_id)
    for i in toots:
        current_id = max(current_id, i["id"])
    logging.debug("current_id: "+ str(current_id))
    while True:
        refresh = False
        time.sleep(30)
        # check require auth
        if datetime.now().timestamp() - lastauth.timestamp() > auth["expires_in"] - 120:
            try:
                logging.debug("reauth")
                auth = requests.post(url + "/oauth/token", params={
                    "name":user, # no email address
                    "password":password, 
                    "grant_type":"password", 
                    "client_id":clientid, 
                    "client_secret":clientsecret
                }).json()
                lastauth = datetime.now()
            except Exception as e:
                logging.error("unable to auth:"+str(e))
        toots = bot.timeline_home(since_id=current_id)
        if len(toots) > 0:
            logging.debug(str(len(toots)) +" new toots")
        # get refresh request
        for i in toots:
            if i["account"]["username"] == "noyuno":
                if user in i["content"]:
                    logging.debug("noyuno says to " + user + ": " + i["content"])
                    if "update" in i["content"] or \
                        "更新" in i["content"]:
                        refresh = True
            current_id = max(current_id, i["id"])

        if refresh:
            toot(bot,"りょーかいです！")
            #pprint.pprint(toots)
            try:
                os.chdir("/var/pleroma/pleroma")
                execute(["sudo","-u","pleroma","git","pull","origin","noyuno"])
                o=execute(["git","show","-s","--format=%h"])
                toot(bot,"pull完了(commit id={0})．再起動します．".format(o.replace("\n","")))
                execute(["systemctl", "restart", "pleroma"])
                execute(["systemctl", "restart", "pleromabot"])
                # killed
                #bot.toot("@noyuno 更新完了")
            except Exception as e:
                toot(bot,"エラー：" + str(e))
                logging.error(e)

        logging.debug("current_id: "+ str(current_id))

if __name__ == '__main__':
    logging.basicConfig(filename="/var/log/pleromabot.log",
                        level=logging.WARNING)
    create("/var/pleroma/pleromabot/pleromabot.secret")
    main()

