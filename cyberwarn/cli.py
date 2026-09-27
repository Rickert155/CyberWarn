"""
Модуль: CLI меню
"""
import textwrap
import sys
from cyberwarn.core.core import init, divide_line, greeting
from __init__ import __project__
from cyberwarn.core.colors import RED, RESET, BLUE, GREEN, BOLD, YELLOW
from cyberwarn.cms.wp_plugins import scanWordPressPlugins
from cyberwarn.cms.wp_version import scanWordPressVersion
from cyberwarn.cracker.bruteforce_login import bruteforce_login
from cyberwarn.social.search_users import search_users
from cyberwarn.fuzz.fuzz_subdomain import fuzz_subdomains
from cyberwarn.fuzz.fuzz_dirs import fuzz_dirs
from cyberwarn.fuzz.get_links import get_links
from cyberwarn.fuzz.get_comments import get_comments
from cyberwarn.fuzz.bad_headers import bad_headers
from cyberwarn.phishing.clone_page import clone_page


COMMANDS = {
        "fuzz-subdomains":{
            "name":"Сканер поддоменов",
            "module":fuzz_subdomains,
            "args":["--url=", "--wordlist=", "--workers="],
            "example_url":"http://example.com",
            "example_wordlist":"data/wordlist/web/subdomains.txt",
            "mode_test":True,
            "template":(
                "python3 -m cyberwarn fuzz-subdomains "
                "--url=https://example.com --wordlist=data/wordlist/web/subdomains.txt --workers=20"
                )
            },
        "fuzz-dirs":{
            "name":"Сканер директорий",
            "module":fuzz_dirs,
            "args":["--url=", "--wordlist=", "--workers="],
            "example_url":"http://example.com",
            "example_wordlist":"data/wordlist/web/dir.txt",
            "mode_test":True,
            "template":(
                "python3 -m cyberwarn fuzz-dirs "
                "--url=https://example.com --wordlist=data/wordlist/web/dir_959.txt --workers=20"
                )
            },
        "get-links":{
            "name":"Сборщик ссылок",
            "module":get_links,
            "args":["--url="],
            "example_url":"http://example.com",
            "mode_test":True,
            "template":"python3 -m cyberwarn get-links --url=https://example.com"
            },
        "get-comments":{
            "name":"Сборщик комментариев",
            "module":get_comments,
            "args":["--url="],
            "example_url":"http://example.com",
            "mode_test":True,
            "template":"python3 -m cyberwarn get-comments --url=https://example.com"
            },
        "wp-plugins":{
            "name":"Сканер плагинов WordPress",
            "module":scanWordPressPlugins,
            "args":["--url=", "--workers="],
            "example_url":"http://example.com",
            "mode_test":True,
            "template":"python3 -m cyberwarn wp-plugins --url=https://example.com --workers=10"
            },
        "wp-version":{
            "name":"Сканер версии WordPress",
            "module":scanWordPressVersion,
            "args":["--url="],
            "example_url":"http://example.com",
            "mode_test":True,
            "template":"python3 -m cyberwarn wp-version --url=https://example.com"
            },
        "bruteforce-login":{
                "name":"Brute Force логина/пароля",
                "module":bruteforce_login,
                "args":["--url=", "--users=", "--passwords=", "--form=", "--fm="],
                "example_url":"https://example.com",
                "template":"python3 -m cyberwarn bruteforce-login --url=https://example.com --users=users.txt --passwords=passwords.txt --form=\"username=[USER]&password=[PASSWORD]\" --fm=\"Incorrect password\""
                },
        "bad-headers":{
                "name":"Фаззинг заголовков",
                "module":bad_headers,
                "args":["--url=", "--headers=", "--payloads="], 
                "example_url":"https://example.com",
                "example_source_headers":"data/bad_headers_temapltes/source-headers.txt",
                "example_user_payloads":"data/bad_headers_temapltes/user-payloads.txt",
                "mode_test":True,
                "template":"python3 -m cyberwarn bad-headers --url=https://example.com --headers=headers.txt --payloads=new-headers.txt"
                },
        "search-user":{
                "name":"Поиск по никнейму",
                "module":search_users,
                "args":["--user=", "--workers="],
                "mode_test":True,
                "example_username":"tester",
                "template":"python3 -m cyberwarn search-user --user=username"
                },
        "clone-page":{
                "name":"Клонирование страницы",
                "module":clone_page,
                "args":["--url=", "--page-name="],
                "mode_test":True,
                "example_url":"https://example.com",
                "example_page_name":"/index.html",
                "template":"python3 -m cyberwarn clone-page --url=https://example.com --page-name=index.html"
                }
        }

def show_menu(helper:bool=False) -> str:
    commands_text = (
            f"| {BOLD}{__project__}{RESET}\n"
            )
    count_command = 0
    for command in COMMANDS:
        count_command+=1
        commands_text+=(
                f"| [{count_command}] {GREEN}{COMMANDS[command]["name"]}:"
                f" {YELLOW}{command}{RESET}\n"
                )
        if helper:
            commands_text+=f"| {BLUE}{COMMANDS[command]["template"]}{RESET}\n"
    commands_text = commands_text.strip()
    return commands_text 

def main():
    print(f"{greeting()}\n|{divide_line()}")
    init()
    params = sys.argv[1:]
    if len(params) == 0:
        print(show_menu())
    
    elif len(params) > 0 and "--help" in params[0]:
        print(show_menu(helper=True))

    elif params[0] not in COMMANDS:
        commands_list = ""
        for command in COMMANDS:
            commands_list+=f"|\t{BOLD}{command}{BOLD}\n"
        commands_list = commands_list.strip()
        print(f"{RED}| Список доступных модулей:\n{commands_list}{RESET}")

    elif params[0] in COMMANDS:
        if len(COMMANDS[params[0]]["args"])+1 == len(params):
            data = {}
            for user_commands in params[1:]:
                try:
                    key, value = user_commands.split("=", 1)
                    data[key] = value
                    data["template"] = COMMANDS[params[0]]["template"]
                except ValueError:
                    sys.exit(
                            f"| {RED}Необходимо корректно передать аргументы:{RESET} "
                            f"{COMMANDS[params[0]]["args"]}\n"
                            f"| {BLUE}{COMMANDS[params[0]]["template"]}{RESET}"
                            )
                if key+"=" not in COMMANDS[params[0]]["args"]:
                    sys.exit(
                            f"| {RED}Необходимо передать аргументы: {RESET}"
                            f"{COMMANDS[params[0]]["args"]}\n"
                            f"| {COMMANDS[params[0]]["template"]}"
                            )
            COMMANDS[params[0]]["module"](args=data)
        else:
            sys.exit(
                    f"| {RED}Необходимо передать аргументы: {RESET}"
                    f"{COMMANDS[params[0]]["args"]}\n"
                    f"| {COMMANDS[params[0]]["template"]}"
                    )
