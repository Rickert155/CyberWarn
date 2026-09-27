import sys
from cyberwarn.cli import COMMANDS
from cyberwarn.core.core import divide_line
from cyberwarn.cms.wp_plugins import scanWordPressPlugins
from cyberwarn.cms.wp_version import scanWordPressVersion
from cyberwarn.social.search_users import search_users 
from cyberwarn.fuzz.fuzz_subdomain import fuzz_subdomains
from cyberwarn.fuzz.fuzz_dirs import fuzz_dirs
from cyberwarn.fuzz.get_links import get_links
from cyberwarn.fuzz.get_comments import get_comments
from cyberwarn.fuzz.bad_headers import bad_headers
from cyberwarn.phishing.clone_page import clone_page

def tests():
    user_url = None
    params = sys.argv[1:]
    if len(params) > 0:
        if params[0].startswith("https://") or params[0].startswith("http://"):
            user_url = params[0]
        
    counte_module = 0
    for command in COMMANDS:
        counte_module+=1

        module = COMMANDS[command]["module"]
        args = COMMANDS[command]["args"]
        template = COMMANDS[command]["template"]
        example_username = COMMANDS[command].get("example_username")
        example_source_headers = COMMANDS[command].get("example_source_headers")
        example_user_payloads = COMMANDS[command].get("example_user_payloads")
        example_page_name = COMMANDS[command].get("example_page_name")
        mode_test = COMMANDS[command].get("mode_test")

        if not mode_test:
            continue 
        
        if user_url:url = user_url
        else:url = COMMANDS[command]["example_url"]
        
        example_wordlist = COMMANDS[command].get("example_wordlist")
        
        data = {}
        data["template"] = template
        data["mode_test"] = mode_test
        data["--url"] = url
        data["--workers"] = 10

        if example_username:data["--user"] = example_username
        if example_source_headers:data["--headers"] = example_source_headers
        if example_user_payloads:data["--payloads"] = example_user_payloads
        if example_page_name:data["--page-name"] = example_page_name
        
        if example_wordlist:
            data["--wordlist"] = example_wordlist
        
        print(
                f"{divide_line()}\n"
                f"| Module [{counte_module}]: {command}"
                )
        
        module(args=data)
        

if __name__ == "__main__":
    try:
        tests()
    except KeyboardInterrupt:
        sys.exit("\nExit...")
