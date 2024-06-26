import base64
import datetime
import time
import io
import json
import requests
import gzip
import socket
import redis
import subprocess
import os

from marionette_driver import marionette
from PIL import Image


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

def kill_firefox_processes():
    ps_output = subprocess.check_output(["ps", "aux"]).decode('utf-8')
    for line in ps_output.split("\n"):
        if "marionette" in line:
            pid = int(line.split()[1])
            log(f"Killing process with PID: {pid}")
            subprocess.run(["kill", '-9', str(pid)])

    log("All Tor processes have been killed.", color='green')


def fetch_url(tor_client, url):
    fetch_from_datetime = datetime.datetime.now()
    status_ok = None
    html = None
    screenshot_b64 = ''
    content_gzip_b64 = ''

    log(f'FetchUrl:start ({url})', 'blue')

    try:
        tor_client.navigate(url)
    except Exception as e:
        log(f'FetchUrl:error ({e})', 'red')
        sleep(3.6)
        status_ok = False
    else:
        log(f'FetchUrl:success ({url})', 'green')

        html = tor_client.page_source
        status_ok = \
            html.find('Nos systèmes ont détecté un') == -1 and \
            html.find('Ce réseau est bloqué') == -1 and \
            html.find('Before you continue to Google') == -1 and \
            html.find('Voordat je verdagaat') == -1 and \
            html.find('Bevor Sie zu Google') == -1 and \
            html.find('https://consent.google.com/ml?continue') == -1

        screenshot_b64 = compress_and_convert_screenshot_to_base64(tor_client)
        content_b64 = get_response_content_base64(tor_client)
        content_gzip_b64 = get_response_content_gzip_base64(tor_client)

        log('FetchUrl:content_len (%d/%d)' % (len(content_b64), len(content_gzip_b64)))

    fetch_to_datetime = datetime.datetime.now()
    fetch_duration = fetch_to_datetime - fetch_from_datetime

    return {
        'increment': 1,
        'duration': int(round(fetch_duration.total_seconds(), 0)),
        'status': status_ok,
        'html': html,
        'screenshot_b64': screenshot_b64,
        'content_gzip_b64': content_gzip_b64,
        'content_gzip_b64_len': len(content_gzip_b64),
    }

def start_tor_process():
    log('Tor:start', 'blue')
    return subprocess.Popen('start-tor-browser', shell=True)

def start_firefox_process():
    log('Firefox:start', 'blue')
    return subprocess.Popen('start-firefox', shell=True)


def start_tor_client():
    tor_client = marionette.Marionette(host='localhost', port=2828, socket_timeout=60)
    tor_client.start_session()
    return tor_client

def start_firefox_client():
    firefox_client = marionette.Marionette(host='localhost', port=2828, socket_timeout=60)
    firefox_client.start_session()
    return firefox_client


def terminate_tor_process(tor_process):
    log('Tor:terminate', 'blue')
    tor_process.terminate()
    log('Tor:terminated', 'blue')


def terminate_firefox_process(firefox_process):
    log('Firefox:terminate', 'blue')
    firefox_process.terminate()
    log('Firefox:terminated', 'blue')


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

    out = f'{color_code}{port} ({hostname}) - {content}{end_code}'
    print(out)

    redis_client = redis.Redis(host='redis', port=6379, db=0)
    redis_client.rpush(f'client:client_{port}', content)


def pull_master_request(pull_url):
    log(f'PullMasterRequest:start ({pull_url})', 'blue')
    response = requests.get(pull_url, timeout=10)
    log(f'PullMasterRequest:end ({pull_url})', 'blue')
    return response.json()


def push_master_request(push_url, data):
    log('PushMasterRequest:start', 'blue')

    headers = {
        'Content-Type': 'application/json',
    }

    response = requests.post(push_url, data=json.dumps(data), headers=headers, timeout=10)
    log('PushMasterRequest:end', 'blue')
    return response.json()


def compress_and_convert_screenshot_to_base64(tor_client, compress=True):
    screenshot_binary = tor_client.screenshot(format='binary', full=True, scroll=True)

    if compress:
        try:
            image = Image.open(io.BytesIO(screenshot_binary))
        except Exception as e:
            log(f'CompressAndConvertScreenshotToBase64:error ({e})', 'red')
            return ''

        if image.mode == 'RGBA':
            image = image.convert('RGB')

        max_width = 1000
        ratio = max_width / image.width
        new_height = int(image.height * ratio)

        try:
            parameter = Image.ANTIALIAS
        except Exception:
            parameter = Image.Resampling.LANCZOS

        image = image.resize((max_width, new_height), parameter)

        with io.BytesIO() as output:
            image.save(output, format="JPEG", quality=70)
            compressed_screenshot = output.getvalue()

        screenshot_base64 = base64.b64encode(compressed_screenshot).decode('utf-8')
    else:
        screenshot_base64 = base64.b64encode(screenshot_binary).decode('utf-8')

    return screenshot_base64


def get_response_content_base64(tor_client):
    return base64.b64encode(tor_client.page_source.encode('utf-8')).decode('utf-8')


def get_response_content_gzip_base64(tor_client):
    gzip_content = gzip.compress(tor_client.page_source.encode('utf-8'))
    return base64.b64encode(gzip_content).decode('utf-8')


def sleep(seconds):
    log(f'Sleep:{seconds}', 'cyan')
    time.sleep(seconds)
