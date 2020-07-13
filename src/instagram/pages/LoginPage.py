from selene import browser
from selene.support.jquery_style_selectors import s

import src.instagram.constants as constants
from src.instagram.pages.SecureArea import SecureArea


class LoginPage(object):
    def __init__(self):
        self.username_input = s("input[name='username']")
        self.password_input = s("input[name='password']")
        self.login_btn = s("button[type='submit']")

    def open(self):
        browser.open_url(constants.BASE_URL + "accounts/login/")
        return self

    def login_as(self, user_login, user_password):
        self.username_input.set(user_login)
        self.password_input.set(user_password)
        self.login_btn.click()
        return SecureArea()
