import json

from selene import browser
from selene.support.jquery_style_selectors import s

import src.instagram.constants as constants


class UserPage(object):
    def __init__(self):
        self.body = s("body")

    def get_body(self, username):
        url = constants.USER_URL.format(username)
        browser.open_url(url)
        return json.loads(self.body.text)
