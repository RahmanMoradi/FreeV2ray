import os
import random
from typing import List

from requests.exceptions import ProxyError
from urllib3.exceptions import HTTPError

from instagrapi import Client
from instagrapi.exceptions import (
    ClientConnectionError,
    ClientForbiddenError,
    ClientLoginRequired,
    ClientThrottledError,
    GenericRequestError,
    PleaseWaitFewMinutes,
    RateLimitError,
    SentryBlock,
)

from FreeV2ray.app import config

IG_CREDENTIAL_PATH = "./ig_settings.json"
IG_USERNAME = config.get('IG_USERNAME')
IG_PASSWORD = config.get('IG_PASSWORD')


class InstagramApi:
    def __init__(self):
        def next_proxy():
            with open("proxies.txt", "r") as f:
                proxies = ["http://" + proxy for proxy in f.readlines()]

            return random.choice(proxies)
        print("ok")
        self.client = Client(proxy=next_proxy())
        print("passed")
        if os.path.exists(IG_CREDENTIAL_PATH):
            self.client.load_settings(IG_CREDENTIAL_PATH)
            self.client.login(IG_USERNAME, IG_PASSWORD)
        else:
            self.client.login(IG_USERNAME, IG_PASSWORD)
            self.client.dump_settings(IG_CREDENTIAL_PATH)

        try:
            self.client.login("USERNAME", "PASSWORD")
        except (ProxyError, HTTPError, GenericRequestError, ClientConnectionError):
            # Network level
            self.client.set_proxy(next_proxy())
        except (SentryBlock, RateLimitError, ClientThrottledError):
            # Instagram limit level
            self.client.set_proxy(next_proxy())
        except (ClientLoginRequired, PleaseWaitFewMinutes, ClientForbiddenError):
            # Logical level
            self.client.set_proxy(next_proxy())

    def get_followers_usernames(self, amount: int = 0) -> List[str]:
        """
        Get bot's followers usernames

        Parameters
        ----------
        amount: int, optional
            Maximum number of media to return, default is 0 - Inf

        Returns
        -------
        List[str]
            List of usernames
        """
        followers = self.client.user_followers(str(self.client.user_id), amount=amount)
        return [user.username for user in followers.values()]


if __name__ == '__main__':
    app = InstagramApi()
    followers = app.get_followers_usernames()
    print(followers)







