import base64
import json
import datetime
import io
from marionette_driver import marionette
from PIL import Image
import requests
import subprocess
import socket
import time

from config import MASTER_URL

'''
Script to scrape Google search results using Tor and Selenium
'''

class WebScraper:
    VERSION = '1.0.3'

    def __init__(self):
        self.tor_process = None
        self.client = None

    @classmethod
    def get_hostname(obj):
        try:
            hostname = socket.gethostname()
        except:
            return 'unknown'
        else:
            return hostname

    @classmethod
    def kill_tor_processes(obj):
        ps_output = subprocess.check_output(["ps", "aux"]).decode('utf-8')
        for line in ps_output.split("\n"):
            if "marionette" in line:
                pid = int(line.split()[1])
                obj.log(f"Killing process with PID: {pid}")
                subprocess.run(["kill", '-9', str(pid)])
        obj.log("All Tor processes have been killed.", color='green')

    @classmethod
    def log(obj, content, color='blue'):
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

        hostname = obj.get_hostname()
        hostname = hostname if hostname else 'unknown'

        print(f'{color_code}{hostname} - {content}{end_code}')

    @classmethod
    def sleep(obj, seconds):
        obj.log(f'Sleep:{seconds}', 'cyan')
        time.sleep(seconds)

    def start_tor(self):
        self.log('Tor:start', 'blue')
        self.tor_process = subprocess.Popen('start-tor-browser', shell=True)

    def pull_master_request(self):
        pull_url = f'{MASTER_URL}/client/pull'
        self.log(f'PullMasterRequest:start ({pull_url})', 'blue')

        try:
            response = requests.get(pull_url, timeout=30)
        except Exception as e:
            self.log(f'PullMasterRequest:error({e})', 'red')
            self.sleep(10)
            return self.pull_master_request()
        else:
            try:
                response_json = response.json()
            except Exception as e:
                self.log(f'PullMasterRequest:error({e})', 'red')
                self.sleep(3)
                return self.pull_master_request()
            else:
                self.log(f'PullMasterRequest:end', 'green')
                return response_json

    def push_master_request(self, data):
        self.log(f'PushMasterRequest:start', 'blue')

        headers = {
            'Content-Type': 'application/json',
        }

        try:
            response = requests.post(f'{MASTER_URL}/c/push', json=json.dumps(data), headers=headers, timeout=10)
        except Exception as e:
            self.log(f'PushMasterRequest:error1({e})', 'magenta')
            return self.push_master_request(data)
        else:
            try:
                response_json = response.json()
                client_id = response_json['id']
            except Exception as e:
                self.log(f'PushMasterRequest:error2({e})', 'magenta')
                self.sleep(3)
                return self.push_master_request(data)
            else:
                self.log(f'PushMasterRequest:end (#{client_id})', 'green')
                return response_json

    def compress_and_convert_screenshot_to_base64(self, compress=True):
        screenshot_binary = self.client.screenshot(format='binary', full=True, scroll=True)

        if compress:
            image = Image.open(io.BytesIO(screenshot_binary))

            if image.mode == 'RGBA':
                image = image.convert('RGB')

            max_width = 600
            ratio = max_width / image.width
            new_height = int(image.height * ratio)

            try:
                parameter = Image.ANTIALIAS
            except :
                parameter = Image.Resampling.LANCZOS

            image = image.resize((max_width, new_height), parameter)

            with io.BytesIO() as output:
                image.save(output, format="JPEG", quality=40)
                compressed_screenshot = output.getvalue()

            screenshot_base64 = base64.b64encode(compressed_screenshot).decode('utf-8')
        else:
            screenshot_base64 = base64.b64encode(screenshot_binary).decode('utf-8')

        return screenshot_base64

    def google_fetch(self):
        fetch_from_datetime = datetime.datetime.now()
        fetch_increment = 0

        request_dict = self.pull_master_request()

        while True:
            fetch_increment += 1
            fetch_max_increment = 10

            try:
                self.log(f'GoogleFetch:start({fetch_increment}/{fetch_max_increment}) ({request_dict["url"]})')
                self.client.navigate(request_dict['url'])
            except Exception as e:
                self.log(f'GoogleFetch:error ({e})', 'red')
                self.sleep(5)

                if fetch_increment > fetch_max_increment:
                    self.log(f'GoogleFetch:max_increment_reached', 'red')
                    return False
            else:
                break

        fetch_to_datetime = datetime.datetime.now()
        fetch_duration = fetch_to_datetime - fetch_from_datetime

        html = self.client.page_source
        self.log(f'GoogleFetch:end', 'blue')

        status_ok = html.find('Nos systèmes ont détecté un') == -1 and html.find('Ce réseau est bloqué') == -1

        data = {
            'client_version': self.VERSION,
            'client_hostname': self.get_hostname(),

            'request_url': request_dict['url'],
            'request_keyword_id': request_dict['keywordId'],
            'request_locality_id': request_dict['localityId'],

            'response_duration': int(round(fetch_duration.total_seconds(), 0)),
            'response_increment': fetch_increment,
            'response_status': 'true' if status_ok else 'false',
            'response_screenshot_b64': self.compress_and_convert_screenshot_to_base64(),
            'response_contentB64': base64.b64encode(self.client.page_source.encode('utf-8')).decode('utf-8'),
        }

        if not status_ok:
            self.log(f'GoogleFetch:detected_traffic', 'blue')

        try:
            self.push_master_request(data)
        except Exception as e:
            self.log(f'PushMasterRequest:error ({e})', 'red')
            self.sleep(5)
        else:
            self.log(f'PushMasterRequest:success', 'green')

        return status_ok

    def run(self):
        while True:
            if self.tor_process is None:
                self.kill_tor_processes()

                self.sleep(3)

                self.start_tor()
                self.sleep(10)

                self.client = marionette.Marionette(host='localhost', port=2828, socket_timeout=60)
                self.client.start_session()

            if self.google_fetch():
                self.sleep(5)
            else:
                self.log('Tor:terminate', 'blue')
                self.tor_process.terminate()
                self.tor_process = None
                self.log('Tor:terminated', 'blue')
                self.sleep(5)


if __name__ == '__main__':
    scraper = WebScraper()
    scraper.run()
