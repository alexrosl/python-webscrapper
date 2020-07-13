from selene.support.jquery_style_selectors import s


class SecureArea(object):
    def __init__(self):
        self.avatar = s("img[data-testid='user-avatar']")
