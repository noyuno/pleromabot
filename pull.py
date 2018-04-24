from mastodon import Mastodon
import os
import sys

url=""
email=""
password=""
secret=""

def create(filename):
    global url
    global email
    global password
    global secret
    with open(filename,"r") as f:
        r=f.readlines()
        secret=r[0].replace("\n", "") + ".secret"
        url="https://"+r[0].replace("\n","")
        email=r[1].replace("\n","")
        password=r[2].replace("\n","")
    if os.path.exists(secret) == False:
        Mastodon.create_app(
            'pleromabot',
            api_base_url = url,
            to_file = secret
        )

def toot():
    global url
    global email
    global password
    mastodon = Mastodon(
        client_id = secret, 
        api_base_url = url
    )

    mastodon.log_in(
        email,
        password,
        to_file = 'user.secret'
    )

    mastodon = Mastodon(
        client_id = secret,
        access_token = 'user.secret',
        api_base_url = url
    )
    mastodon.toot('ちゃろー')

if __name__ == '__main__':
    create(sys.argv[1])
    toot()

