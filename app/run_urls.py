import base64
import json
import datetime
import os
import io
from marionette_driver import marionette
from PIL import Image
import requests
import subprocess

from config import MASTER_URL, CLIENT_HOST
from utils import get_hostname, kill_tor_processes, log, sleep

'''
Script to scrape Google search results using Tor and Selenium
'''

class WebScraper:
    VERSION = '1.0.4'

    def __init__(self):
        self.tor_process = None
        self.client = None

    def start_tor(self):
        log('Tor:start', 'blue')
        self.tor_process = subprocess.Popen('start-tor-browser', shell=True)

    def pull_master_request(self):
        pull_url = f'{MASTER_URL}/clients/urls/pull'
        log(f'PullMasterRequest:start ({pull_url})', 'blue')

        try:
            response = requests.get(pull_url, timeout=30)
        except Exception as e:
            log(f'PullMasterRequest:error({e})', 'red')
            sleep(10)
            return self.pull_master_request()
        else:
            try:
                response_json = response.json()
            except Exception as e:
                log(f'PullMasterRequest:error({e})', 'red')
                sleep(3)
                return self.pull_master_request()
            else:
                log(f'PullMasterRequest:end', 'green')
                return response_json

    def push_master_request(self, data):
        log(f'PushMasterRequest:start', 'blue')

        headers = {
            'Content-Type': 'application/json',
        }

        try:
            response = requests.post(f'{MASTER_URL}/clients/urls/push', data=json.dumps(data), headers=headers, timeout=10)
        except Exception as e:
            log(f'PushMasterRequest:error1({e})', 'magenta')
            return self.push_master_request(data)
        else:
            try:
                response_json = response.json()
            except Exception as e:
                log(f'PushMasterRequest:error2({e})', 'red')
                sleep(3)
                return self.push_master_request(data)
            else:
                try:
                    client_status = response_json['status']
                except:
                    log(f'PushMasterRequest:error3({e})', 'red')
                    sleep(3)
                    return self.push_master_request(data)

                if client_status is False:
                    log(f'PushMasterRequest:error4(status=False)', 'red')
                    sleep(3)
                    return self.push_master_request(data)
                else:
                    try:
                        client_identifier = response_json['identifier']
                    except Exception as e:
                        log(f'PushMasterRequest:error5({e})', 'red')
                        sleep(3)
                        return self.push_master_request(data)
                    else:
                        log(f'PushMasterRequest:end ({client_identifier})', 'green')

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
                image.save(output, format="JPEG", quality=60)
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
                log(f'GoogleFetch:start({fetch_increment}/{fetch_max_increment}) ({request_dict["url"]})')
                self.client.navigate(request_dict['url'])
            except Exception as e:
                log(f'GoogleFetch:error ({e})', 'red')
                sleep(20)

                if fetch_increment > fetch_max_increment:
                    log(f'GoogleFetch:max_increment_reached', 'red')
                    return False
            else:
                break

        fetch_to_datetime = datetime.datetime.now()
        fetch_duration = fetch_to_datetime - fetch_from_datetime

        html = self.client.page_source
        log(f'GoogleFetch:end', 'blue')

        status_ok = html.find('Nos systèmes ont détecté un') == -1 and html.find('Ce réseau est bloqué') == -1

        data = {
            'client_version': self.VERSION,
            'client_host': CLIENT_HOST,
            'client_port': int(os.getenv('CLIENT_PORT')),
            'client_hostname': get_hostname(),

            'request_url': request_dict['url'],
            'request_identifier': request_dict['identifier'],
            # 'request_keyword_id': request_dict['keyword_id'],
            # 'request_locality_id': request_dict['locality_id'],

            'response_duration': int(round(fetch_duration.total_seconds(), 0)),
            'response_increment': fetch_increment,
            'response_status': 'true' if status_ok else 'false',
            'response_screenshot_b64': self.compress_and_convert_screenshot_to_base64(),
            'response_content_b64': base64.b64encode(self.client.page_source.encode('utf-8')).decode('utf-8'),
        }

        if not status_ok:
            log(f'GoogleFetch:detected_traffic', 'blue')

        try:
            self.push_master_request(data)
        except Exception as e:
            log(f'PushMasterRequest:error ({e})', 'red')
            sleep(5)
        else:
            log(f'PushMasterRequest:success', 'green')

        return status_ok

    def run(self):
        while True:
            if self.tor_process is None:
                kill_tor_processes()

                sleep(3)

                self.start_tor()
                sleep(10)

                self.client = marionette.Marionette(host='localhost', port=2828, socket_timeout=60)
                self.client.start_session()

            if self.google_fetch():
                sleep(5)
            else:
                log('Tor:terminate', 'blue')
                self.tor_process.terminate()
                self.tor_process = None
                log('Tor:terminated', 'blue')
                sleep(5)


if __name__ == '__main__':
    scraper = WebScraper()
    scraper.run()
