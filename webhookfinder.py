import os
import re
import tkinter as tk
from tkinter import filedialog
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

WEBHOOK_PATTERN = re.compile(r"https://(?:discord|discordapp)\.com/api/webhooks/[0-9]+/[A-Za-z0-9_-]+")

def choose_directory() -> str:
    root = tk.Tk()
    root.withdraw()
    selected = filedialog.askdirectory(title="select folder to scan for discord webhooks")
    return selected or ""

def extract_webhooks_from_file(path: str) -> list:
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()
        return WEBHOOK_PATTERN.findall(text)
    except Exception:
        print(f"{Colors.WARNING}warning: could not read {path}{Colors.ENDC}")
        return []

def scan_directory_for_webhooks(directory: str) -> set:
    found = set()
    print(f"{Colors.OKBLUE}scanning '{directory}' for webhooks{Colors.ENDC}")
    file_paths = []
    for dirpath, _, filenames in os.walk(directory):
        for name in filenames:
            file_paths.append(os.path.join(dirpath, name))

    start_time = time.time()
    with ThreadPoolExecutor() as executor:
        futures = {executor.submit(extract_webhooks_from_file, path): path for path in file_paths}
        for future in as_completed(futures):
            path = futures[future]
            webhooks = future.result()
            if webhooks:
                print(f"{Colors.OKGREEN}found {len(webhooks)} webhooks in {path}{Colors.ENDC}")
                for url in webhooks:
                    if url not in found:
                        print(f"    -> {Colors.BOLD}{url}{Colors.ENDC}")
                        found.add(url)
    elapsed = time.time() - start_time
    print(f"\n{Colors.UNDERLINE}time taken: {elapsed:.2f} seconds{Colors.ENDC}")
    return found

def main():
    print(f"{Colors.HEADER}{Colors.BOLD}discord webhook scanner{Colors.ENDC}")
    directory = choose_directory()
    if not directory:
        print(f"{Colors.FAIL}no folder selected, exiting{Colors.ENDC}")
        return
    webhooks = scan_directory_for_webhooks(directory)
    if not webhooks:
        print(f"{Colors.WARNING}no webhooks found in '{directory}'{Colors.ENDC}")
    else:
        print(f"\n{Colors.OKGREEN}scan complete!{Colors.ENDC}")
        print(f"{Colors.BOLD}total unique webhooks found: {len(webhooks)}{Colors.ENDC}")

if __name__ == '__main__':
    main()
