"""
Модуль: Сканер плагинов WordPress
"""
import json
import requests
import os
import sys
import subprocess
import time
from cyberwarn.core.header import Headers
from cyberwarn.core.colors import RED, RESET, BLUE, GREEN, BOLD, YELLOW
from cyberwarn.core.core import CoreSetting, get_proxy, divide_line
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

def check_wordpress(url:str) -> bool:
    """Проверяем, на WordPress сайт или нет"""
    headers = Headers().create_headers()

    status_ok = [200, 403, 301, 302, 303, 308]

    try:
        wp_admin_url = f"{url}/wp-admin/"
        proxy = get_proxy()
        response = requests.get(url=wp_admin_url, headers=headers, proxies=proxy)
        status_code = response.status_code
        if status_code in status_ok:
            return True, status_code
        else:
            return False, status_code
    except requests.exceptions.InvalidURL:
        sys.exit(CyberHelp().help_wp_plugins(doc=__doc__))
    except requests.exceptions.ConnectionError:
        sys.exit(f"{RED}Проверь правильность адреса: {url}{RESET}")

def full_url_plugin(url:str, plugin:str) -> str:
    """Возвращает полный url до readme.md"""
    if url[-1] == "/":url = url[:-1]
    full_url = f"{url}/wp-content/plugins/{plugin}/readme.txt"
    return full_url

def full_list_plugins(mode_test:bool=False) -> list[str]:
    "Возвращает полный список доступных для проверки плагинов"
    list_plugins = []
    if mode_test != True:
        plugins_file = CoreSetting().get_settings()["path_default_wp_plugin"]
    else:
        plugins_file = CoreSetting().get_settings()["path_default__test_wp_plugin"]
    with open(plugins_file, "r") as file:
        for line in file.readlines():
            list_plugins.append(line.strip())
    return list_plugins

def parser_txt(response:str) -> dict[str]:
    """Парсер readme.txt, возвращает dict с именем и версией"""
    
    data = {
            "plugin_name":None,
            "plugin_version":None
            }
    
    readme = response.text
    all_line_readme = readme.split("\n")
    for count_line, line in enumerate(all_line_readme):
        if count_line == 0:
            if "<!" in line:
                return False
            plugin_name = line.replace("=", "").replace("\r", "").strip()
            data["plugin_name"] = plugin_name
        if "Stable tag: " in line:
            plugin_version = line.split("Stable tag: ")[1].strip()
            data["plugin_version"] = plugin_version

    return data

COUNT_PLUGINS = 0
LEN_LIST_PLUGINS = 0
COUNT_FIND_PLUGIN = 0

update_json_lock = Lock()
count_plugin_lock = Lock()
count_find_lock = Lock()

def parser_url(url_plugin):
    global COUNT_PLUGINS
    global COUNT_FIND_PLUGIN
    
    slug_plugin = url_plugin.split("/readme.txt")[0].split("/plugins/")[1]
    
    with count_plugin_lock:
        COUNT_PLUGINS+=1
        if COUNT_PLUGINS % 100 == 0 or COUNT_PLUGINS == LEN_LIST_PLUGINS:
            print(
                f"{GREEN}| Progress: [{RED}{COUNT_PLUGINS}{RESET}/"
                f"{GREEN}{LEN_LIST_PLUGINS}{RESET}]" 
                )
    try:
        headers = Headers().create_headers()
        proxy = get_proxy()
        response = requests.get(url_plugin, headers=headers, proxies=proxy)
        response.encoding = "utf-8"
        if response.status_code == 200:
            
            with count_find_lock:
                COUNT_FIND_PLUGIN+=1
            
            data = parser_txt(response=response)
            if data:
                plugin_name = data["plugin_name"]
                plugin_version = data["plugin_version"]
                print(
                        f"{GREEN}|{divide_line()[:-1]}{RESET}\n"
                        f"{GREEN}| {YELLOW}Plugin[{COUNT_FIND_PLUGIN}]:{RESET}\t{plugin_name}\n"
                        f"{GREEN}| {YELLOW}Version:{RESET}\t{plugin_version}"
                        )
                with update_json_lock:
                    if not os.path.exists(RESULT_FILE_JSON):
                        data = []
                        with open(RESULT_FILE_JSON, "w") as file:
                            json.dump(data, file, indent=4)
                    with open(RESULT_FILE_JSON, "r") as file:
                        data = json.load(file)
                    plugin = {
                            "number":COUNT_FIND_PLUGIN, 
                            "plugin":plugin_name,
                            "slug_plugin":slug_plugin,
                            "url_plugin":url_plugin,
                            "version":plugin_version
                            }
                    data.append(plugin)
                    with open(RESULT_FILE_JSON, "w") as file:
                        json.dump(data, file, indent=4)
    except requests.exceptions.ConnectionError:
        return None

RESULT_FILE_JSON = ""

def scan_list_plugin(url:str, workers:int, mode_test:bool=False) -> None:
    global LEN_LIST_PLUGINS
    global RESULT_FILE_JSON
    RESULT_FILE_JSON = f'{url.split("//")[1].split("/")[0]}.plugins.json'
    if os.path.exists(RESULT_FILE_JSON):
        os.remove(RESULT_FILE_JSON)
    headers = Headers()
    
    list_plugins = full_list_plugins(mode_test=mode_test)
   
    full_list_url_plugins = []

    for plugin in list_plugins:
        full_url = full_url_plugin(url=url, plugin=plugin)
        full_list_url_plugins.append(full_url)
    
    LEN_LIST_PLUGINS = len(full_list_url_plugins)

    with ThreadPoolExecutor(max_workers=workers) as executor:
        result = list(executor.map(
            parser_url,
            full_list_url_plugins,
            ))

def scanWordPressPlugins(args:dict[str]):
    url = args["--url"]
    template = args["template"]
    workers = args["--workers"]
    try:
        workers = int(workers)
    except ValueError:
        sys.exit(f"| {RED}Значение workers должно быть числовым{RESET}")
    mode_test = args.get("mode_test")
    if not url.startswith("https://") and not url.startswith("http://"):
        sys.exit(f"| {RED}Пример использования: {template}{RESET}")

    wp_status = check_wordpress(url=url)
    
    if wp_status[0] == True:
        scan_list_plugin(url=url, mode_test=mode_test, workers=workers)

    elif wp_status[0] != True and wp_status[1] >= 500:
        print(
                f"| {YELLOW}{url} Проблемы на стороне сервера: "
                f"{wp_status[1]}{RESET}"
                )
    else:
        print(
                f"| {YELLOW}{url} Сайт не на WordPress, "
                f"status: {wp_status[1]}{RESET}"
                )
