"""
Модуль: crawler
"""
import requests
import os
import sys
import time
from cyberwarn.core.colors import RED, RESET, GREEN, BOLD, BLUE, YELLOW
from cyberwarn.core.core import get_proxy, divide_line
from cyberwarn.core.header import Headers

from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
from threading import Lock

BASE_URL = ""
SITEMAP_FILE = ""
RESULT_FILE = ""
SITEMAP_URLS = []
URLS = []
FULL_LIST_URLS = []

def recording_result(info:str) -> None:
    with open(SITEMAP_FILE, "a+") as file:
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
                    if word.startswith("/"):
                        word = f"{BASE_URL}{word}"
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
        try:
            response = requests.get(sitemap, headers=headers, proxies=proxy)
        except requests.exceptions.ConnectionError:
            print(f"| {RED}Connection error: {BOLD}{sitemap}{RESET}")
            return 
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
                            if not link.lower().endswith(content_ext) and\
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

PROGRESS_URL_COUNT = 0
progress_url_lock = Lock()
full_list_urls_lock = Lock()

def parser_page(url):
    global PROGRESS_URL_COUNT
    with progress_url_lock:
        PROGRESS_URL_COUNT+=1
        print(
                f"| [{RED}{PROGRESS_URL_COUNT}{RESET}"
                f"/{GREEN}{len(URLS)}{RESET}] "
                f"{BOLD}{url}{RESET}"
                )
    with full_list_urls_lock:
        if url not in FULL_LIST_URLS:
            FULL_LIST_URLS.append(url)
        with open(RESULT_FILE, "a+") as file:
            file.write(f"{url}\n")

    proxy = get_proxy()
    headers = Headers().create_headers()
    
    response = requests.get(url, headers=headers, proxies=proxy)
    status_code = response.status_code

    if status_code == 200:
        break_links = ("#", "tel:", "mailto:", "/#")
        bs = BeautifulSoup(response.text, "lxml")
        links = bs.find_all(["a", "link"])
        if len(links) != 0:
            for link in links:
                link = link.attrs.get("href")
                if link.startswith(break_links):
                    continue
                if BASE_URL not in link:
                    continue
                with full_list_urls_lock:
                    if link not in FULL_LIST_URLS:
                        FULL_LIST_URLS.append(link)
                        with open(RESULT_FILE, "a+") as file:
                            file.write(f"{link}\n")
                        print(f"| {GREEN}{link}{RESET}")


def check_all_links(workers:int) -> None:
    try:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            executor.map(parser_page, URLS)
    except Exception as err:
        print(f"| {RED}{err}{RESET}")

def crawler(args:dict[str]) -> None:
    global SITEMAP_FILE, RESULT_FILE, BASE_URL
    BASE_URL = args["--url"]
    workers = args["--workers"]
    template = args["template"]
    if not BASE_URL.startswith("https://") and not BASE_URL.startswith("http://"):
        sys.exit(f"| {RED}Пример использования: {template}{RESET}")

    try:
        workers = int(workers)
    except ValueError:
        sys.exit(f"| {RED}Значение workers должно быть числовым{RESET}")

    if BASE_URL[-1] == "/":BASE_URL = BASE_URL[:-1]
    
    sitemap_prefix = "crawler-tmp"
    crawler_prefix = "crawler"

    SITEMAP_FILE = BASE_URL.split("://")[1]
    if "/" in SITEMAP_FILE:SITEMAP_FILE = SITEMAP_FILE.split("/")[0]
    
    SITEMAP_FILE = f"{sitemap_prefix}.{SITEMAP_FILE}.txt"
    if os.path.exists(SITEMAP_FILE):os.remove(SITEMAP_FILE)
    RESULT_FILE = SITEMAP_FILE.replace(sitemap_prefix, crawler_prefix)
    if os.path.exists(RESULT_FILE):os.remove(RESULT_FILE)

    get_sitemap(url=BASE_URL)
    """Пассивная сборка ссылок - через sitemap"""
    parsing_sitemapxml()
    
    """Обход всех URL для составления карты сайта"""
    check_all_links(workers=workers)
    if os.path.exists(SITEMAP_FILE):os.remove(SITEMAP_FILE)
