from mastodon import Mastodon
import os

url="https://s.noyuno.space"
def create():
    Mastodon.create_app(
        'pleromabot',
        api_base_url = url,
        to_file = 'pytooter_clientcred.secret'
    )

def main():
    mastodon = Mastodon(
        client_id = 'pytooter_clientcred.secret',
        api_base_url = url
    )
    email=""
    password=""
    with open("user.secret","r") as f:
        r=f.readlines()
        email=r[0].replace("\n","")
        password=r[1].replace("\n","")

    print(email)
    print(password)

    mastodon.log_in(
        email,
        password,
        to_file = 'pytooter_usercred.secret'
    )

    # Create actual API instance
    mastodon = Mastodon(
        client_id = 'pytooter_clientcred.secret',
        access_token = 'pytooter_usercred.secret',
        api_base_url = url
    )
    mastodon.toot('ちゃろー')

if __name__ == '__main__':
    if os.path.exists("pytooter_clientcred.secret") == False:
        create()
    main()

