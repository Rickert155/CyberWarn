"""
Module: search-user
"""
import json
import os
import requests
import sys
from cyberwarn.core.colors import RED, RESET, GREEN, BOLD, YELLOW
from cyberwarn.core.core import CoreSetting, get_proxy, divide_line
from cyberwarn.core.header import Headers

from concurrent.futures import ThreadPoolExecutor
from threading import Lock

COUNT_FIND_USER=0
COUNT_CHECK_USER=0
lock_count_find_user = Lock()
lock_count_check_user = Lock()
lock_recording_result = Lock()

LEN_SOCIAL_SERVICES = 0

RESULT_JSON = "[USER].social.json"

def recording_result(service:dict[str], count:int) -> None:
    data = {}
    data["count"] = count
    data["user"] = service["user"]
    data["service"] = service["name"]
    data["category"] = service["category"]
    data["url"] = service["url"]

    user = service["user"]
    
    with lock_recording_result:
        if not os.path.exists(RESULT_JSON):
            with open(RESULT_JSON, "w") as file:
                json.dump([], file, indent=4)
        with open(RESULT_JSON, "r") as file:
            all_results = json.load(file)
        
        all_results.append(data)
        with open(RESULT_JSON, "w") as file:
            json.dump(all_results, file, indent=4)

def check_user(service:dict[str]) -> None:
    global COUNT_FIND_USER
    global COUNT_CHECK_USER

    with lock_count_check_user:
        COUNT_CHECK_USER+=1
    print(f"| [{COUNT_CHECK_USER}/{LEN_SOCIAL_SERVICES}]", end="\r")
    try:
        user = service["user"]
        url = service["url"]
        service_name = service["name"]
        category = service["category"]
        fail_status = service["fail"]
        fail_code = service["fail_code"]
        success_text = service["success_text"]
        success_code = service["success_code"]

        headers = Headers().create_headers()
        proxy = get_proxy()
        response = requests.get(
                url, 
                headers=headers, 
                proxies=proxy,
                timeout=5
                )

        text_result = response.text
        status_code = response.status_code

        if status_code in fail_code and success_text not in text_result:
            pass
        else:
            with lock_count_find_user:
                COUNT_FIND_USER+=1
            print(
                    f"| [{COUNT_FIND_USER}] user {GREEN}{user}: {url} {status_code}{RESET}"
                    )
            recording_result(service=service, count=COUNT_FIND_USER)
        
    except requests.exceptions.ReadTimeout:
        print(f"{RED}{url} connection error!{RESET}")
        return False
    except Exception as err:
        print(f"| {RED}{url} {err}{RESET}")
        return False


def search_users(args:dict[str]):
    global LEN_SOCIAL_SERVICES
    global RESULT_JSON

    try:
        user = args["--user"]
        workers = args["--workers"]
        
        RESULT_JSON = RESULT_JSON.replace("[USER]", user)

        if os.path.exists(RESULT_JSON):
            os.remove(RESULT_JSON)
        
        try:
            workers = int(workers)
        except ValueError:
            sys.exit(f"| {RED}Значение workers должно быть числовым{RESET}")

        services_info = CoreSetting().get_settings()["path_default_social_service"]

        with open(services_info, "r") as file:
            list_services = json.load(file)
        
        services = []
        for service in list_services:
            service["url"] = service["url"].replace("[USER]", user)
            service["user"] = user
            services.append(service)

        LEN_SOCIAL_SERVICES = len(services)

        with ThreadPoolExecutor(max_workers=workers) as executor:
            result = list(executor.map(
                check_user,
                services
                ))  
        if COUNT_FIND_USER == 0:
            sys.exit(
                    f"| [{COUNT_CHECK_USER}/{LEN_SOCIAL_SERVICES}] "
                    f"{RED}user {BOLD}{user}{RESET} {RED}not found{RESET}"
                    )

    except KeyboardInterrupt:
        sys.exit(f"{RED}\nExit...{RESET}")
