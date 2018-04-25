from mastodon import Mastodon
import os
import sys
import requests
import time
import pprint
import git

"""
file format

domain
username
password

"""

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

def toot():
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

    r = requests.post(url + "/oauth/token", params={
        "name":user, # no email address
        "password":password, 
        "grant_type":"password", 
        "client_id":clientid, 
        "client_secret":clientsecret
    })
    s = r.json()

    bot = Mastodon(
        client_id = secret,
        access_token = s["access_token"],
        api_base_url = url
    )
    #bot.toot('ちゃろー')
    current_id=0
    toots = bot.timeline_home(since_id=current_id)
    for i in toots:
        current_id = max(current_id, i["id"])
    print("current_id: "+ str(current_id))
    while True:
        refresh = False
        time.sleep(30)
        toots = bot.timeline_home(since_id=current_id)
        # get refresh request
        for i in toots:
            if i["account"]["username"] == "noyuno":
                if ("@" + user) in i["content"]:
                    if "refresh" in i["content"] or \
                        "更新" in i["content"]:
                        refresh = True
            current_id = max(current_id, i["id"])

        if refresh:
            bot.toot("@noyuno りょーかいです！")
            pprint.pprint(toots)
            try:
                g = git.Repo(os.getenv("HOME") + "/pleroma")
                g.remotes.origin.pull()
                subprocess.call(["systemctl", "--user", "restart", "pleroma"])
                g = git.Repo(os.getenv("HOME") + "/mastofe")
                g.remotes.origin.pull()
                subprocess.call(["systemctl", "--user", "restart", "mastofe"])
                sleep(30)
                bot.toot("@noyuno 更新完了")
            except Exception as e:
                bot.toot("@noyuno エラー：" + e)

if __name__ == '__main__':
    create(sys.argv[1])
    toot()

