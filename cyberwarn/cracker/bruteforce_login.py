import os
import sys
import requests
from cyberwarn.core.core import log_server_response
from cyberwarn.core.colors import RED, RESET, BLUE, BOLD, GREEN, YELLOW
from cyberwarn.core.header import Headers
from cyberwarn.core.core import get_proxy
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

def get_wordlist(file_name:str) -> list[str]:
    if not os.path.exists(file_name):
        sys.exit(f"| {RED}File {file_name} not found!{RESET}")
    
    wordlist = set()
    with open(file_name, "r") as file:
        for line in file.readlines():
            wordlist.add(line.strip())
    print(f"| {GREEN}{file_name}: {BOLD}{len(wordlist)}{RESET}")
    return wordlist

LEN_USERS_LIST = 0
LEN_PASSWORD_LIST = 0
COUNT_CHECK_USER = 0
COUNT_CHECK_PASSWORD = 0
lock_count_check = Lock()

def send_form(full_info):
    global COUNT_CHECK_PASSWORD
    
    user = full_info["user"]
    password = full_info["password"]
    fail_message = full_info["fail_message"]
    url = full_info["url"]
    data_form = full_info["data_form"]

    if "&&" in fail_message:
        fail_message = fail_message.split("&&")
    else:
        fail_message = [fail_message]
    required_fields = ["USER", "PASSWORD"]
    for field in required_fields:
        if field not in data_form:
            sys.exit(
                    f"| {RED}missing required field: {BOLD}[{field}]{RESET}\n"
                    f"| {data_form}"
                    )
    fields = data_form.split("&")
    data = {}
    for field in fields:
        key, value = field.split("=")
        value = value.replace("[USER]", user).replace("[PASSWORD]", password)
        data[key] = value

    try:
        headers = Headers().create_headers()
        proxy = get_proxy()
        response_range_status = range(200, 400)
        response = requests.post(url, headers=headers, data=data, proxies=proxy)
        status_code = response.status_code

        with lock_count_check:
            COUNT_CHECK_PASSWORD+=1
            print(
                    f"| [{RED}{COUNT_CHECK_USER}{RESET}/{GREEN}{LEN_USERS_LIST}{RESET}]"
                    f"[{RED}{COUNT_CHECK_PASSWORD}{RESET}/"
                    f"{GREEN}{LEN_PASSWORD_LIST}{RESET}"
                    f"{GREEN}{RESET}]"
                    f" user: {user}\tpassword: {password}\n"
                    f"| {YELLOW}Response{RESET}: {BLUE}{status_code}{RESET}"
              )
        if status_code not in response_range_status:
            log_server_response(
                    url=url, 
                    status=status_code, 
                    headers=response.headers
                    )
        if status_code in response_range_status:
            html = response.text
            
            fail = False
            for message in fail_message:
                if message in html:
                    print(f"| detected message: {message}")
                    fail = True
            if not fail:
                sys.exit(f"| Check access: {user} : {password}")


    except Exception as err:
        print(f"| {RED}error send form: {BOLD}{err}{RESET}")

def bruteforce_login(args:dict[str]):
    url_login = args["--url"]
    users_file = args["--users"]
    passwords_file = args["--passwords"]
    fail_message = args["--fm"]
    data_form = args["--form"]
    workers = args["--workers"]

    global COUNT_CHECK_USER, LEN_PASSWORD_LIST, LEN_USERS_LIST
    
    try:
        workers = int(workers)
    except ValueError:
        sys.exit(f"| {RED}Значение workers должно быть числовым{RESET}")
    template = args["template"]

    users_list = get_wordlist(file_name=users_file)
    LEN_USERS_LIST = len(users_list)
    passwords_list = get_wordlist(file_name=passwords_file)
    LEN_PASSWORD_LIST = len(passwords_list)

    count_users = 0
    for user in users_list:
        COUNT_CHECK_USER+=1
        
        full_list = []
        for password in passwords_list:

            full_info = {
                    "user":user,
                    "password":password,
                    "fail_message":fail_message,
                    "url":url_login,
                    "data_form":data_form
                    }
            full_list.append(full_info)
    
        with ThreadPoolExecutor(max_workers=workers) as execute:
            result = list(execute.map(
                send_form,
                full_list
                ))
        COUNT_CHECK = 0
