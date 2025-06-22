#imagine skidding this goofy ahh code
import psutil
import subprocess
import sys
from pyinjector import inject
import time
from pystyle import *
import os
program = input("enter process name: ")
dll = input("dll (must be in the same folder as the injector): ")

def find_process_id(process_name):
    for proc in psutil.process_iter(['name', 'pid']):
        if proc.info['name'] == process_name:
            return proc.info['pid']
    return None

def inject_dll(pid, dll_path):
    try:
        inject(pid, dll_path)
        print("injected")
    except Exception as e:
        print(f"failed to inject dll: {e}")

        
pid = find_process_id(program)

def on_inject(dll):
    pid = find_process_id(program)
    if pid:
        print(f"pid:{pid}")
        inject_dll(pid, dll)
    else:
        print(f"could not find process: {process_name}")
def art():
    banner = """
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣴⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⣷⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⣿⣿⣷⣀⣀⣀⣀⠀⠀⠀⠀⣀⣀⣀⣀⣠⣤⡤
⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⢰⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⠋⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⠿⠋⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⢰⡇⣿⣿⣿⣿⣿⣿⡿⠟⣻⣿⣿⣿⣿⣿⣥⣄⣀⣀⣀⡀
⠀⢀⣴⣶⣶⣦⣤⣄⠀⢷⣼⣿⣿⡿⠻⠁⠀⠀⣿⣿⣿⣿⣿⣿⣿⣿⠿⠛⠁⠀made by kuyo/spoofedotp 
⢀⣿⡿⢻⣿⣿⠿⠟⠀⠀⠟⠛⢿⠿⠿⠷⡶⠚⢻⣿⣿⣿⣿⣿⣋⣁⠀⠀⠀⠀https://github.com/mcc-loader 
⠹⡟⠀⠸⡿⠁⠀⠀⠀⠀⠈⢄⠈⠀⠀⠀⠁⢀⣾⣿⣿⣿⣿⠿⠋⠁⠀⠀⠀⠀ press "enter" to countinue
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠑⠶⣤⣤⣶⣟⣿⣻⣿⣿⣿⡀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣴⣿⣿⣿⣿⣿⡾⣿⣿⡣⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣿⠟⢻⣿⣿⢿⣿⣿⡝⠻⢷⣄⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠃⠀⢸⡿⠁⠀⣿⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⠁⠀⠀⡟⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
    """
    Anime.Fade(Center.Center(banner), Colors.white_to_black, Colorate.Vertical, enter=True)

if __name__ == "__main__":
    art()
    time.sleep(2)
    on_inject(dll)
    print("closing in 5 seconds")
    time.sleep(5)
