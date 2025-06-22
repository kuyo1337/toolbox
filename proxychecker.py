import requests
from concurrent.futures import ThreadPoolExecutor
import threading

proxy_file = "proxies.txt"
working_proxy_file = "working_proxies.txt"
test_url = "https://httpbin.org/ip"
timeout = 5

working_proxies = []
lock = threading.Lock()

def load_proxies(filename):
    with open(filename, "r") as f:
        return [line.strip() for line in f if line.strip()]

def save_working_proxy(proxy):
    with lock:
        working_proxies.append(proxy)
        with open(working_proxy_file, "a") as f:
            f.write(proxy + "\n")

def check_proxy(proxy):
    proxy_dict = {
        "http": f"http://{proxy}",
        "https": f"http://{proxy}",
    }
    try:
        response = requests.get(test_url, proxies=proxy_dict, timeout=timeout)
        if response.status_code == 200:
            print(f"[✓] WORKING: {proxy}")
            save_working_proxy(proxy)
        else:
            print(f"[✗] BAD (status {response.status_code}): {proxy}")
    except Exception:
        print(f"[✗] FAILED: {proxy}")

def main():
    open(working_proxy_file, "w").close()

    proxies = load_proxies(proxy_file)
    with ThreadPoolExecutor(max_workers=20) as executor:
        executor.map(check_proxy, proxies)

if __name__ == "__main__":
    main()
