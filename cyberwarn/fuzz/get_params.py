"""
Module: params-finder
"""
import os
import sys
from cyberwarn.core.header import Headers
from cyberwarn.core.core import get_proxy
from cyberwarn.core.colors import RED, RESET, BOLD, BLUE, GREEN

def get_wordlist(wordlist_file:str) -> list[str]:
    wordlist = set()
    with open(wordlist_file, "r") as file:
        for line in file.readlines():
            payload = line.strip()
            wordlist.add(payload)
    return list(wordlist)

def check_response(url:str, payload:str):
    try:
        proxy = get_proxy()
        headers = Headers().create_headers()

        if url.endswith("/"):url = url[:-1]
        if url.endswith("?"):url = url[:-1]
        if payload.startswith("/"):payload = payload[1:]
        if payload.startswith("?"):payload = payload[1:]
        url = f"{url}?{payload}"
        print(url)

        #response = requests.get(url, )

    except Exception as err:
        print(f"| {RED}{err}{RESET}")

def params_finder(args:dict[str]):
    base_url = args["--url"]
    workers = args["--workers"]
    wordlist = args["--wordlist"]
    template = args["template"]

    try:
        workers = int(workers)
    except ValueError:
        sys.exit(f"| {RED}Значение workers должно быть числовым{RESET}")
    
    if not base_url.startswith("https://") and not base_url.startswith("http://"):
        sys.exit(f"| {RED}Пример использования: {template}{RESET}")

    if not os.path.exists(wordlist):
        sys.exit(f"| {RED}Файл {wordlist} не найден!{RESET}")

    wordlist = get_wordlist(wordlist_file=wordlist)
    
    for payload in wordlist:
        result = check_response(url=base_url, payload=payload)
