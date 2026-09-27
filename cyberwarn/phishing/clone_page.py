import os
import requests
import sys
from cyberwarn.core.header import Headers
from cyberwarn.core.core import CoreSetting, get_proxy
from cyberwarn.core.colors import RESET, RED, BLUE, GREEN, BOLD

SITE_DIR = ""

def download_page(url:str, page_name:str) -> None:
    try:
        if page_name.startswith("/"):page_name = page_name[1:]
        page_name = f"{SITE_DIR}/{page_name}"
        
        protocol, base_url = url.split("://")
        if "/" in base_url:base_url = base_url.split("/")[0]
        base_url = f"{protocol}://{base_url}"

        headers = Headers().create_headers()
        proxy = get_proxy()
        response = requests.get(url, headers=headers, proxies=proxy)

        html_page = response.text
        html_page = html_page.replace('href="/', f'href="{base_url}/')
        html_page = html_page.replace('href="../', f'href="{base_url}/')
        html_page = html_page.replace('src="/', f'src="{base_url}/')
        html_page = html_page.replace('src = "/', f'src="{base_url}/')
        
        with open(page_name, "w") as file:
            file.write(html_page)

        print(f"| {GREEN}Результат: {page_name}{RESET}")
        
    except Exception as err:
        sys.exit(f"| {RED}{err}{RESET}")

def clone_page(args:dict[str]):
    global SITE_DIR

    url = args["--url"]
    page_name = args["--page-name"]
    template = args["template"]

    sites_dir = CoreSetting().get_settings()["path_sites_dir"]
    
    if not url.startswith("https://") and not url.startswith("http://"):
        sys.exit(f"| {RED}Пример использования: {template}{RESET}")
    if url.endswith("/"):url = url[:-1]

    domain = url.split("://")[1]
    if "/" in domain:domain = domain.split("/")[0]
    SITE_DIR = f"{sites_dir}/{domain}"
    if not os.path.exists(sites_dir):os.makedirs(sites_dir)
    if not os.path.exists(SITE_DIR):os.makedirs(SITE_DIR)

    download_page(url=url, page_name=page_name)
