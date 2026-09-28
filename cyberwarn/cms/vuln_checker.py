import os
import json
import requests
import sys
from cyberwarn.core.header import Headers
from cyberwarn.core.core import get_proxy
from cyberwarn.core.colors import RED, RESET, GREEN, BOLD


COUNT_REQUEST = 0
LEN_LIST = 0
RESULT_FILE = ""

def get_plugins_info(file_name:str):
    list_plugins = []
    with open(file_name, "r") as file:
        data = json.load(file)
    for obj in data:
        plugin_name = obj["plugin"]
        plugin_version = obj["version"]
        url_plugin = obj.get("url_plugin")
        if len(plugin_name) == 0:
            continue
        
        info = {
                "name":plugin_name, 
                "version":plugin_version, 
                "url_plugin":url_plugin
                } 
        if info not in list_plugins:
            list_plugins.append(info)
    
    return list_plugins

def recorerding_result(result:dict[str]) -> None:
    if not os.path.exists(RESULT_FILE):
        with open(RESULT_FILE, "w") as file:
            json.dump([], file, indent=4)
    
    with open(RESULT_FILE, "r") as file:
        data = json.load(file)
    
    data.append(result)
    with open(RESULT_FILE, "w") as file:
        json.dump(data, file, indent=4)

def parser_result(response:dict[str]) -> list[str] | None:
    vulns = response["response"][0]["grid"]["vulnerabilities"]
    if len(vulns) == 0:
        return None
    list_vuln = []
    for vuln in vulns:
        cve = vuln["cve"]["id"]
        list_vuln.append(cve)

    return list_vuln


def response_vuln(plugin:dict[str], cms:str) -> dict[str]:
    global COUNT_REQUEST
    COUNT_REQUEST+=1

    url = (
            f"https://nvd.nist.gov/public/service/rest/json/nvd/cve/search/"
            f"results?keyword={cms} [PLUGIN]&resultType=records"
            )
    name, version = plugin["name"], plugin["version"]
    if " - " in name:name = name.split(" - ", 1)[0]
    if " (" in name:name = name.split(" (", 1)[0]
    if ": " in name:name = name.split(": ", 1)[0].replace(":", "")
    name = name.replace("# ", "")

    query = f"{name} {version}"
    update_url = url.replace("[PLUGIN]", query)
    
    headers = Headers().create_headers()
    proxy = get_proxy()
    
    response = requests.get(update_url, headers=headers, proxies=proxy)
    

    print(
            f"| [{RED}{COUNT_REQUEST}{RESET}/{GREEN}{LEN_LIST}{RESET}] "
            f"{name}: {version}"
            )
    result = parser_result(response=response.json())
    if result != None:
        
        data = {
                "plugin":name,
                "version":version,
                "vulns":result
                }
        
        output_vuln = ""
        for vuln in result:
            output_vuln+=f"|\t{RED}{BOLD}{vuln}{RESET}\n"
        
        output_vuln = output_vuln.strip()
        print(
                f"|\t{RED}{name}{RESET}: {version}\n{BOLD}{output_vuln}{RESET}"
                )
        return data

def vuln_check(args:dict[str]):
    global LEN_LIST, RESULT_FILE

    plugins_json_file = args["--plugins-json"]
    cms = args["--cms"]

    if not os.path.exists(plugins_json_file):
        sys.exit(f"| {RED}Файл не найден: {BOLD}{plugins_json_file}{RESET}")

    list_plugins_info = get_plugins_info(file_name=plugins_json_file)
    LEN_LIST = len(list_plugins_info)
    RESULT_FILE = (
            f"{cms}-"
            f"{list_plugins_info[0]['url_plugin'].split('://')[1].split('/', 1)[0]}"
            f".json"
            )
    if os.path.exists(RESULT_FILE):os.remove(RESULT_FILE)

    for plugin in list_plugins_info:
        result = response_vuln(plugin=plugin, cms=cms)
        if result != None:
            recorerding_result(result=result)

