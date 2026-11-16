"""
Модуль: get links
"""
import os
import requests
import sys
from cyberwarn.core.header import Headers
from cyberwarn.core.core import get_proxy
from cyberwarn.core.colors import RED, RESET, BLUE, GREEN, BOLD, YELLOW
from bs4 import BeautifulSoup

def recording_urls(file_name:str, urls:[]=None) -> None:
    with open(file_name, "w") as file:
        for url in urls:
            file.write(f"{url}\n")

def create_full_link(link:str, url:str):
    if link[0] == "/":link = link[1:]
    if "http" not in link and "://" not in link:
        link = f"{url}/{link}"
    return link

def extract_links(response:str, url:str) -> list[str] | None:
    list_links = []
    try:
        bs = BeautifulSoup(response, "lxml")
        href_links = bs.find_all(["a", "link"])
        src_links = bs.find_all(["script"])
        
        if len(href_links) > 0:
            for link in href_links:
                if link == None:continue
                link = link.attrs["href"]
                link = create_full_link(link=link, url=url)
                if link not in list_links:list_links.append(link)
        if len(src_links) > 0:
            for link in src_links:
                if link == None:continue
                link = link.attrs["src"]
                link = create_full_link(link=link, url=url)
                if link not in list_links:list_links.append(link)
        return list_links
    except Exception as err:
        print(f"| {RED}ERROR Extraction: {err}{RESET}")
        return list_links

def get_links(args:dict[str]) -> None:
    url = args["--url"]
    template = args["template"]
    if not url.startswith("https://") and not url.startswith("http://"):
        sys.exit(f"| {RED}Пример использования: {template}{RESET}")

    if url[-1] == "/":url = url[:-1]
    try:
        headers = Headers().create_headers()
        headers["Host"] = url.split("://")[1]
        proxy = get_proxy()

        response = requests.get(url, headers=headers, proxies=proxy)
        status_code = response.status_code
        if response.status_code == 200:
            links = extract_links(response=response.text, url=url)
            if len(links) > 0:
                file_name = f"{url.split("://")[1]}.links.txt"
                recording_urls(urls=links, file_name=file_name)
                for count, link in enumerate(links, start=1):
                    print(f"| [{count}] {GREEN}{link}{RESET}")
            else:
                sys.exit(f"| {RED}Ссылки не обнаружены!{RESET}")

    except KeyboardInterrupt:
        sys.exit(f"| {RED}\nExit...{RESET}")
    except requests.exceptions.ConnectionError:
        sys.exit(f"| {RED}{url}: Connection Error{RESET}")
