import os

from config import MASTER_URL, CLIENT_HOST
from utils import (
    get_hostname,
    pull_master_request,
    push_master_request,
    kill_tor_processes,
    start_tor_process,
    terminate_tor_process,
    start_tor_client,
    fetch_url,
    log,
    sleep
)

'''
Script to scrape URLS results using Tor and Marionette
'''

class WebScraper:
    VERSION = '2.0.4'

    def __init__(self):
        self.tor_process = None
        self.tor_client = None

    def process_url(self):
        try:
            request_dict = pull_master_request(f'{MASTER_URL}/clients/urls/pull')
        except Exception as e:
            log(f'PullMasterRequest:error ({e})', 'red')
            return True # Normal return

        fetch_data = fetch_url(self.tor_client, request_dict['url'], 3)

        data = {
            'client_version': self.VERSION,
            'client_host': CLIENT_HOST,
            'client_port': int(os.getenv('CLIENT_PORT')),
            'client_hostname': get_hostname(),

            'request_url': request_dict['url'],
            'request_identifier': request_dict['identifier'],
            # 'request_keyword_id': request_dict['keyword_id'],
            # 'request_locality_id': request_dict['locality_id'],

            'response_duration': fetch_data['duration'],
            'response_increment': fetch_data['increment'],
            'response_status': 'true' if fetch_data['status'] else 'false',
            'response_screenshot_b64': fetch_data['screenshot_b64'] if fetch_data['screenshot_b64'] else '',
            'response_content_b64': fetch_data['content_b64'] if fetch_data['content_b64'] else '',
        }

        try:
            push_master_request(f'{MASTER_URL}/clients/urls/push', data)
        except Exception as e:
            log(f'PushMasterRequest:error ({e})', 'red')
            sleep(5)

        return fetch_data['status']

    def run(self):
        while True:
            if self.tor_process is None:
                kill_tor_processes()
                sleep(3)
                self.tor_process = start_tor_process()
                sleep(10)
                self.tor_client = start_tor_client()

            if self.process_url():
                sleep(5)
            else:
                terminate_tor_process(self.to_process)
                self.to_process = None
                sleep(5)


if __name__ == '__main__':
    scraper = WebScraper()
    scraper.run()
