"""
Модуль: crawler
"""
import requests
import os
import sys
from cyberwarn.core.colors import RED, RESET, GREEN, BOLD, BLUE, YELLOW
from cyberwarn.core.core import get_proxy, divide_line
from cyberwarn.core.header import Headers

from bs4 import BeautifulSoup

RESULT_FILE = ""
SITEMAP_URLS = []
URLS = []

def recording_result(info:str) -> None:
    with open(RESULT_FILE, "a+") as file:
        file.write(f"{info}\n")

def get_url_from_robots(response:str, url:str):
    """
    Получение ссылок на индексируемый/не индексируемые 
    страницы и получение sitemap
    """
    global SITEMAP_URLS, URLS
    try:
        print(f"| {GREEN}Detected robots.txt!{RESET}")
        trigger_words = ["Allow", "Disallow"]

        robots_txt = response.split("\n")
        index_links = []
        for line in robots_txt:
            """Сбор индексируемы/не индексируемых ссылок"""
            for tw in trigger_words:
                if tw in line:
                    try:
                        link_path = line.split(f"{tw}: ")[1].strip()
                        if link_path not in index_links:
                            index_links.append(f"{link_path}")
                    except IndexError:pass

            """Сбор ссылок sitemap"""
            words = line.split()
            for word in words:
                if ("sitemap" in word and word.endswith(".xml")) and \
                        word not in SITEMAP_URLS:
                    SITEMAP_URLS.append(word)
            
        if len(index_links) != 0:
            count_link = 0
            print(f"| {BOLD}Index(not index) links{RESET}")
            for link in index_links:
                count_link+=1
                full_url = f"{url}{link}"
                if "*" in full_url:
                    output_result = f"{YELLOW}{full_url}{RESET}"
                else:
                    URLS.append(full_url)
                    output_result = f"{GREEN}{full_url}{RESET}"
                    recording_result(info=f"{full_url} -> robots.txt")

                print(f"| [{RED}{count_link}{RESET}] {output_result}")

    except Exception as err:
        print(f"| {RED}{err}{RESET}")

def get_sitemap(url:str) -> list[str]:
    """
    Определение путей до sitemap
    """
    proxy = get_proxy()
    robots_path = f"{url}/robots.txt"
    headers = Headers().create_headers()
    print(f"| {YELLOW}Check robots.txt: {robots_path}{RESET}")
    
    try:
        response = requests.get(robots_path, headers=headers, proxies=proxy)
        status_code = response.status_code
        if status_code == 200:    
            """Получаем список индексации/запрета индексации"""
            get_url_from_robots(response=response.text, url=url)

            if len(SITEMAP_URLS) != 0:
                count_sitemap_link = 0
                print(f"| {BOLD}Sitemap links{RESET}")
                for sitemap in SITEMAP_URLS:
                    count_sitemap_link+=1
                    print(
                            f"| {RED}[{count_sitemap_link}]{RESET} {sitemap}"
                            )
        
        elif status_code == 403:
            server = response.headers.get("Server")
            print(
                    f"| {RED}Warning! Detected WAF: {BOLD}{server}{RESET}"
                    )
        elif status_code == 404:
            print(f"| {RED}status code: {BOLD}{status_code}{RESET}")
        else:
            print(
                    f"| {RED}status code: {BOLD}{status_code}{RESET}, "
                    f"{RED}headers: {BOLD}{response.headers}{RESET}"
                    )
            print(f"| {RED}robots.txt not detected{RESET}")
        
        """Если не нашли sitemap"""
        if len(SITEMAP_URLS) == 0:
            SITEMAP_URLS.append(f"{url}/sitemap.xml")

        print(f"|{divide_line()[:-1]}")

    except Exception as err:
        sys.exit(f"| {RED}{err}{RESET}")

def parsing_sitemapxml() -> None:
    """Получаем данные из всех sitemap"""
    global SITEMAP_URLS, URLS
    proxy = get_proxy()

    content_ext = (
            ".jpg", 
            ".svg", 
            ".png", 
            ".jpeg", 
            ".mp4", 
            ".webp", 
            ".avif"
            )

    print(f"| {GREEN}Check sitemaps...{RESET}")
    
    count_link = 0
    for count, sitemap in enumerate(SITEMAP_URLS, start=1):
        print(
                f"| Sitemap: {RED}[{count}/{len(SITEMAP_URLS)}]{RESET} "
                f"{sitemap}")
        headers = Headers().create_headers()
        response = requests.get(sitemap, headers=headers, proxies=proxy)
        status_code = response.status_code
        if status_code == 404:
            print(f"| {RED}sitemap {sitemap}: not found!{RESET}")
        elif status_code == 403:
            print(
                    f"| {RED}status_code: {status_code}{RESET}, "
                    f"{RED}server: {BOLD}{response.headers.get('server')}{RESET}"
                    )
        
        elif status_code == 200:
            bs = BeautifulSoup(response.text, "xml")
            try:
                all_links = bs.find_all("loc")
                if all_links != None and len(all_links) > 0:
                    for link in all_links:
                        count_link+=1
                        link = link.get_text()
                        if ("sitemap" in link and link.endswith(".xml")) and \
                                link not in SITEMAP_URLS:
                            SITEMAP_URLS.append(link)
                        else:
                            if not link.endswith(content_ext) and\
                                    link not in URLS:
                                URLS.append(link)
                                recording_result(info=link)
                                print(f"| {GREEN}[{count_link}]{RESET} {link}")
            except Exception as err:
                print(f"| {RED}{err}{RESET}")
        
        else:
            print(
                    f"| {RED}status code: {BOLD}{status_code}{RESET}, "
                    f"| {RED}headers: {response.headers}{RESET}"
                    )
            

def crawler(args:dict[str]) -> None:
    global RESULT_FILE
    base_url = args["--url"]
    template = args["template"]
    if not base_url.startswith("https://") and not base_url.startswith("http://"):
        sys.exit(f"| {RED}Пример использования: {template}{RESET}")

    if base_url[-1] == "/":base_url = base_url[:-1]
    RESULT_FILE = base_url.split("://")[1]
    if "/" in RESULT_FILE:RESULT_FILE = RESULT_FILE.split("/")[0]
    RESULT_FILE = f"crawler-result.{RESULT_FILE}.txt"
    if os.path.exists(RESULT_FILE):os.remove(RESULT_FILE)
    
    get_sitemap(url=base_url)
    """Пассивная сборка ссылок - через sitemap"""
    parsing_sitemapxml()
     
