# -*- coding: utf-8 -*-
import argparse

from src.all.common_report import generate_report
from src.facebook.facebook_scraper_simple import main as facebook_scraper_main
from src.instagram.instagram_scraper_simple import main as insta_scraper_main
from src.other.other import main as other_main
from src.vk.vk_scrapper import main as vk_scrapper_main

if __name__ == '__main__':
    CLI = argparse.ArgumentParser()
    CLI.add_argument(
        "--facebook_accounts",  # name on the CLI - drop the `--` for positional/required parameters
        nargs="*",  # 0 or more values expected => creates a list
        type=str
    )
    CLI.add_argument(
        "--insta_usernames",  # name on the CLI - drop the `--` for positional/required parameters
        nargs="*",  # 0 or more values expected => creates a list
        type=str
    )
    CLI.add_argument(
        "--vk_groups",  # name on the CLI - drop the `--` for positional/required parameters
        nargs="*",  # 0 or more values expected => creates a list
        type=str
    )
    CLI.add_argument(
        "--vk_access_token",  # name on the CLI - drop the `--` for positional/required parameters
        nargs="*",  # 0 or more values expected => creates a list
        type=str
    )
    CLI.parse_args()

    try:
        vk_scrapper_main()
    except:
        print("unable to run vk scraper")

    try:
        insta_scraper_main()
    except:
        print("unable to run insta scraper")

    try:
        facebook_scraper_main()
    except:
        print("unable to run facebook scraper")

    try:
        other_main()
    except:
        print("unable to run other scraper")

    # run report
    generate_report()
