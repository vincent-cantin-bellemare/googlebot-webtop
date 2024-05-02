import os
import sentry_sdk

from config import CLIENT_HOST, MASTER_URL, SENTRY_DSN
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
Script to scrape Domains Queries using Tor and Marionette
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
            request_dict = pull_master_request(f'{MASTER_URL}/clients/domainsqueries/pull')
        except Exception as e:
            log(f'PullMasterRequest:error ({e})', 'red')
            return True # Normal return

        if request_dict['url']:
            fetch_data = fetch_url(self.tor_client, request_dict['url'], 3)

            data = {
                'client_version': self.VERSION,
                'client_host': CLIENT_HOST,
                'client_port': int(os.getenv('CLIENT_PORT')),
                'client_hostname': get_hostname(),

                'request_url': request_dict['url'],
                'request_identifier': request_dict['identifier'],

                'response_duration': fetch_data['duration'],
                'response_increment': fetch_data['increment'],
                'response_status': 'true' if fetch_data['status'] else 'false',
                'response_screenshot_b64': fetch_data['screenshot_b64'],
                'response_content_gzip_b64': fetch_data['content_gzip_b64'],
            }

            try:
                push_master_request(f'{MASTER_URL}/clients/domainsqueries/push', data)
            except Exception as e:
                log(f'PushMasterRequest:error ({e})', 'red')
                sleep(5)

            return fetch_data['status']
        else:
            sleep(5)
            return True

    def run(self):
        self.total_unsuccessful_requests = 0

        while True:
            if self.tor_process is None:
                kill_tor_processes()
                sleep(3)
                self.tor_process = start_tor_process()
                sleep(10)
                self.tor_client = start_tor_client()

            process_status = self.process_url()
            sleep(1)

            if process_status:
                self.total_unsuccessful_requests = 0
            else:
                self.total_unsuccessful_requests += 1

            if self.total_unsuccessful_requests >= 5:
                terminate_tor_process(self.tor_process)
                self.tor_process = None
                sleep(5)

if __name__ == '__main__':
    scraper = WebScraper()
    scraper.run()
