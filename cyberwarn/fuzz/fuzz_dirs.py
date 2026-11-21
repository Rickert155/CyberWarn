"""
Модуль: Сканнер директорий 
"""
import os
import json
import requests
import sys
from cyberwarn.core.header import Headers
from cyberwarn.core.colors import RED, RESET, BLUE, GREEN, BOLD, YELLOW
from cyberwarn.core.core import CoreSetting, get_proxy, divide_line
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

WARNING_WORDS = [
        "robots.txt", 
        ".env",
        ".htaccess"
        ]

def get_wordlist(wordlist_path:str):
    wordlist = set()
    try:
        with open(wordlist_path, "r") as file:
            for line in file.readlines():
                url = line.strip()
                if len(url) > 0:wordlist.add(url)
        return wordlist
    except Exception as err:
        sys.exit(f"{RED}{err}{RESET}")

COUNT_FIND = 0
COUNT_DIR = 0
LEN_LIST_DIR = 0
count_find_lock = Lock()
count_dir_lock = Lock()
update_txt_lock = Lock()

def check_url(url:str) -> list[bool, dict|str]:
    global COUNT_FIND, COUNT_DIR
    with count_dir_lock:
        COUNT_DIR+=1
    if COUNT_DIR % 100 == 0 or COUNT_DIR == LEN_LIST_DIR:
        print(f"{GREEN}| Progress: [{COUNT_DIR}/{LEN_LIST_DIR}]")
    try:
        headers = Headers().create_headers()
        proxy = get_proxy()
        response = requests.get(url, headers=headers, proxies=proxy)
        
        status_code = response.status_code
        server_headers = response.headers
        if status_code != 404:
            with count_find_lock:
                COUNT_FIND+=1
            print(
                    f"{GREEN}| [{COUNT_FIND}] {url} {status_code}{RESET}"
                    )
            
            text_headers = ""
            for key, value in server_headers.items():
                text_headers+=f"{key}: {value}\n"
            text_headers = text_headers.strip()

            with update_txt_lock:
                with open(RESULT_FILE, "a") as file:
                    file.write(
                            f"{url} {status_code}\n\n"
                            f"{text_headers}\n"
                            f"{'-'*50}\n"
                            )
    except requests.exceptions.ConnectionError as err:
        pass
    except Exception as err:
        print(f"{RED}| Error parsing url: {url}{RESET}")

RESULT_FILE = ""

def fuzz_dirs(args:dict[str]):
    global RESULT_FILE, LEN_LIST_DIR
    url = args["--url"]
    wordlist_path = args["--wordlist"]
    workers = args["--workers"]
    try:
        workers = int(workers)
    except ValueError:
        sys.exit(f"| {RED}Значение workers должно быть числовым{RESET}")
    template = args["template"]
    
    if not url.startswith("https://") and not url.startswith("http://"):
        sys.exit(f"| {RED}Пример использования: {template}{RESET}")
    
    if not os.path.exists(wordlist_path):
        sys.exit(f"{BOLD}{RED}wordlist not found: {wordlist_path}{RESET}")
    
    if url[-1] == "/":url = url[:-1]

    wordlist = get_wordlist(wordlist_path=wordlist_path)
    LEN_LIST_DIR = len(wordlist)
    
    RESULT_FILE = url.split("://")[1]+".fuzz_url.txt"
    if "/" in RESULT_FILE:RESULT_FILE = RESULT_FILE.split("/")[0]
    if os.path.exists(RESULT_FILE):os.remove(RESULT_FILE)
    
    full_list_url = []
    for count, word in enumerate(wordlist, start=1):
        full_url = f"{url}/{word}"
        full_list_url.append(full_url)

    with ThreadPoolExecutor(max_workers=workers) as execute:
        result = list(execute.map(
            check_url,
            full_list_url
            ))
