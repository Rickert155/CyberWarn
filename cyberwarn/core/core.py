import textwrap
import os
import json
import shutil
import time
from cyberwarn.core.colors import RED, RESET, BOLD, GREEN
from cyberwarn.core.config import LOG_FILE
from __init__ import (
        __author__, 
        __version__, 
        __project__, 
        __authorurl__,
        __license__
        )

class CoreSetting:
    
    def __init__(self):
        self.settings_path = "data/settings.json"

    def get_settings(self, show_settings:bool=False):
        """
        Получаем данные из настроек/создаем дефолтный json
        show_settings - отобразить настройки - True, по умолчанию 
        не выводятся
        """
        if not os.path.exists(self.settings_path):
            data = {
                    "path_default_useragent_txt":"data/useragent.txt",
                    "path_default_useragent_json":"data/agent.json",
                    "path_default_wp_plugin":"data/wp_plugins.txt",
                    "path_default__test_wp_plugin":"data/test_wp_plugins.txt",
                    "path_default_social_service":"data/social_services.json",
                    "path_sites_dir":"sites",
                    "proxy":None
                    }
            with open(self.settings_path, "w") as file:
                json.dump(data, file, indent=4)
        with open(self.settings_path, "r") as file:
            data = json.load(file)

        if show_settings:
            print(f"\n| settings:")
            for key, value in data.items():
                print(f"| {key}:\t{value}")

        return data

    def update_settings(self, user_key:str, user_value:str):
        """Обновление настроек по ключу и значению"""
        try:
            with open(self.settings_path, "r") as file:
                data = json.load(file)

            data[user_key] = user_value
            with open(self.settings_path, "w") as file:
                json.dump(data, file, indent=4)
            return "ok"
        except Exception as error:
            return error
    
    def check_path_config(self) -> list[ list[str] | None ]:
        """Проверка наличия пользовательских файлов конфигураций"""
        with open(self.settings_path, "r") as file:
            data = json.load(file)

        found_config = []
        not_found_config = []
        for key, value in data.items():
            if "path" in key:
                if os.path.exists(value):
                    found_config.append(value)
                    #print(f"| {GREEN}[OK] config: {value}{RESET}")
                else:
                    not_found_config.append(value)
                    print(f"| {RED}[WARNING] dir/file not found: {value}{RESET}")

        return found_config, not_found_config

def get_proxy() -> dict[str]|None:
    proxy = CoreSetting().get_settings()["proxy"]
    if proxy:
        return {"http":proxy}
    else:
        return None

def divide_line() -> str:
    len_line = int(shutil.get_terminal_size().columns)-1
    line = "-"*len_line
    return line

def current_time() -> str:
    return time.strftime("%d/%m/%Y %H:%M:%S")


def log_server_response(status:int, headers:str, url:str):
    line = "-"*60
    
    headers_text = ""
    for key, value in headers.items():
        headers_text+=f"{key}: {value}\n"

    text = (
            f"{line}\n"
            f"[{current_time()}] {url} {status}\n"
            f"{headers_text}\n"
            )
    with open(LOG_FILE, "a+") as file:
        file.write(text)

def greeting() -> str:
    greet_text = f"""\
    |{divide_line()}
    | {BOLD}author:       {__author__}{RESET}\t{GREEN}{__authorurl__}{RESET}
    | {BOLD}project:      {__project__}{RESET}\t{GREEN}{__license__}{RESET}      
    | {BOLD}version:      {__version__}{RESET} \
    """
    greet_text = textwrap.dedent(greet_text)
    return greet_text

def init():
    settings = CoreSetting()
    settings.get_settings(show_settings=False)
    settings.check_path_config()


