import time
import socket
import subprocess
import os


def get_hostname():
    try:
        hostname = socket.gethostname()
    except:
        return 'unknown'
    else:
        return hostname


def kill_tor_processes():
    ps_output = subprocess.check_output(["ps", "aux"]).decode('utf-8')
    for line in ps_output.split("\n"):
        if "marionette" in line:
            pid = int(line.split()[1])
            log(f"Killing process with PID: {pid}")
            subprocess.run(["kill", '-9', str(pid)])
    log("All Tor processes have been killed.", color='green')


def log(content, color='blue'):
    colors = {
        "red": "\033[91m",
        "green": "\033[92m",
        "yellow": "\033[93m",
        "blue": "\033[94m",
        "magenta": "\033[95m",
        "cyan": "\033[96m",
        "white": "\033[97m",
        "end": "\033[0m",  # Reset la couleur
    }

    color_code = colors.get(color, "")
    end_code = colors["end"]

    hostname = get_hostname()
    hostname = hostname if hostname else 'unknown'
    port = os.getenv('CLIENT_PORT')

    print(f'{color_code}{port} ({hostname}) - {content}{end_code}')


def sleep(seconds):
    log(f'Sleep:{seconds}', 'cyan')
    time.sleep(seconds)
