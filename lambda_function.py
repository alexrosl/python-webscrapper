import os

from src.facebook.facebook_scraper_simple import main as facebook_scraper_main
from src.instagram.instagram_scraper_simple import main as insta_scraper_main
from src.other.other import main as other_main
from src.vk.vk_scrapper import main as vk_scrapper_main


def lambda_handler(event=None, context=None):
    vk_groups = os.getenv('VK_GROUPS').split()
    vk_access_token = os.getenv("VK_ACCESS_TOKEN")
    insta_usernames = os.getenv("INSTA_USERNAMES").split()
    facebook_accounts = os.getenv("FACEBOOK_ACCOUNTS").split()

    print(", ".join(vk_groups) + " " + vk_access_token + " " + ", ".join(insta_usernames) + " " + ", ".join(facebook_accounts))

    try:
        vk_scrapper_main(vk_groups, vk_access_token)
    except:
        raise

    try:
        insta_scraper_main(insta_usernames)
    except:
        print("unable to run insta scraper")

    try:
        facebook_scraper_main(facebook_accounts)
    except:
        raise

    try:
        other_main()
    except:
        raise

