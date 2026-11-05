"""
Module: params-finder
"""
import os
import sys
import requests
from cyberwarn.core.header import Headers
from cyberwarn.core.core import get_proxy, divide_line, log_server_response
from cyberwarn.core.colors import RED, RESET, BOLD, BLUE, GREEN
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

BASE_URL = ""
RESULT_LOG_FILE = ""
DEFAULT_STATUS_CODE = 0

COUNT_PARAMS = 0
LEN_LIST_PARAMS = 0

count_params_lock = Lock()

def get_wordlist(wordlist_file:str) -> list[str]:
    global LEN_LIST_PARAMS
    wordlist = set()
    with open(wordlist_file, "r") as file:
        for line in file.readlines():
            payload = line.strip()
            wordlist.add(payload)
    LEN_LIST_PARAMS = len(wordlist)
    return list(wordlist)

def check_response(payload):
    global BASE_URL, COUNT_PARAMS
    try:
        with count_params_lock:
            COUNT_PARAMS+=1
            
        proxy = get_proxy()
        headers = Headers().create_headers()

        if BASE_URL.endswith("?"):BASE_URL = BASE_URL[:-1]
        if BASE_URL.endswith("/"):BASE_URL = BASE_URL[:-1]
        if payload.startswith("?"):payload = payload[1:]
        if payload.startswith("/"):payload = payload[1:]
        url = f"{BASE_URL}?{payload}"

        response = requests.get(url, headers=headers, proxies=proxy, timeout=20)
        
        status_code = response.status_code
        content_length = response.headers.get("content-length")
        body_size = len(response.text)
        server = response.headers.get("server")
        if status_code != DEFAULT_STATUS_CODE:
            log_server_response(
                    status=status_code, 
                    headers=response.headers,
                    url=url,
                    file_name=RESULT_LOG_FILE
                    )
            status_code = f"{RED}{status_code}{RESET}"
        print(
                f"| [{RED}{COUNT_PARAMS}{RESET}/"
                f"{GREEN}{LEN_LIST_PARAMS}{RESET}] "
                f"{url}\n"
                f"| Status code:        {BOLD}{status_code}{RESET}\n"
                f"| Content-Length:     {BOLD}{content_length}{RESET}\n"
                f"| Body size:          {BOLD}{body_size}{RESET}\n"
                f"| Server:             {BOLD}{server}{RESET}\n"
                f"|{divide_line()}"
                )
        return True
    except Exception as err:
        print(f"| {RED}{err}{RESET}")
        return False

def params_finder(args:dict[str]):
    global BASE_URL, DEFAULT_STATUS_CODE, RESULT_LOG_FILE
    BASE_URL = args["--url"]
    workers = args["--workers"]
    wordlist = args["--wordlist"]
    template = args["template"]

    try:
        workers = int(workers)
    except ValueError:
        sys.exit(f"| {RED}Значение workers должно быть числовым{RESET}")
    
    if not BASE_URL.startswith("https://") and not BASE_URL.startswith("http://"):
        sys.exit(f"| {RED}Пример использования: {template}{RESET}")

    if not os.path.exists(wordlist):
        sys.exit(f"| {RED}Файл {wordlist} не найден!{RESET}")

    RESULT_LOG_FILE = BASE_URL.split("://")[1]
    if "/" in RESULT_LOG_FILE:RESULT_LOG_FILE = RESULT_LOG_FILE.split("/")[0]
    RESULT_LOG_FILE = f"url-params-{RESULT_LOG_FILE}.log"

    wordlist = get_wordlist(wordlist_file=wordlist)
    
    try:
        response = requests.get(
                BASE_URL, 
                headers=Headers().create_headers(),
                proxies=get_proxy()
                )
        DEFAULT_STATUS_CODE = response.status_code
    except Exception as err:
        sys.exit(
                f"| Ошибка при подключении к {BASE_URL}: \n"
                f"| {err}"
                )

    with ThreadPoolExecutor(max_workers=workers) as executor:
        executor.map(check_response, wordlist)
