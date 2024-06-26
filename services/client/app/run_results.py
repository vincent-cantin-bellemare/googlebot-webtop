import os
import sentry_sdk

from config import MASTER_URL, SENTRY_DSN, CLIENT_HOST
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
    VERSION = '2.0.5'

    def __init__(self):
        self.tor_process = None
        self.tor_client = None
        self.__init_sentry()

    def __init_sentry(self):
        if SENTRY_DSN:
            sentry_sdk.init(
                dsn=SENTRY_DSN,
                traces_sample_rate=1.0,
            )

    def process_url(self):
        try:
            request_dict = pull_master_request(f'{MASTER_URL}/clients/results/pull')
        except Exception as e:
            log(f'PullMasterRequest:error ({e})', 'red')
            sleep(3.8)
            return True # Normal return, will attempt later

        fetch_data = fetch_url(self.tor_client, request_dict['url'])

        data = {
            'client_version': self.VERSION,
            'client_host': CLIENT_HOST,
            'client_port': int(os.getenv('CLIENT_PORT')),
            'client_hostname': get_hostname(),

            'request_url': request_dict['url'],
            'request_keyword_id': request_dict['keyword_id'],
            'request_locality_id': request_dict['locality_id'],

            'response_duration': fetch_data['duration'],
            'response_increment': fetch_data['increment'],
            'response_status': 'true' if fetch_data['status'] else 'false',
            'response_screenshot_b64': fetch_data['screenshot_b64'],
            'response_content_gzip_b64': fetch_data['content_gzip_b64'],
        }

        try:
            push_master_request(f'{MASTER_URL}/clients/results/push', data)
        except Exception as e:
            log(f'PushMasterRequest:error ({e})', 'red')
            sleep(5.5)

        log(f'Fetch Data: {fetch_data["status"]}', 'red')
        return fetch_data['status']

    def run(self):
        log('Starting Script', 'white')

        while True:
            log('Enter into infinite loop', 'white')

            if self.tor_process is None:
                kill_tor_processes()
                sleep(3.2)
                self.tor_process = start_tor_process()
                sleep(11.2)
                self.tor_client = start_tor_client()

            process_status = self.process_url()
            sleep(1.1)

            if not process_status:
                log('Process status is False', 'red')
                terminate_tor_process(self.tor_process)
                self.tor_process = None
                sleep(5.6)

if __name__ == '__main__':
    while True:
        try:
            scraper = WebScraper()
            scraper.run()
        except Exception as e:
            log(f'Global Error: {e}', 'red')
            sleep(30.1)
