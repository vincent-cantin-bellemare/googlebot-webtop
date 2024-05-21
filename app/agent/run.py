import threading
import argparse
import time
import subprocess
import logging
import os


class Runner:
    PROJECT_NAME = "googlebot-webtop"

    def __init__(self):
        self.setup_logging()

    def setup_logging(self):
        logging.basicConfig(level=logging.INFO,
                            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                            handlers=[
                                logging.FileHandler(f"/logs/agent_{os.environ['AGENT_ID']}.log"),
                                logging.StreamHandler()
                            ])
        self.logger = logging.getLogger(self.PROJECT_NAME)

    def log(self, message):
        """ Logs a message """
        self.logger.info(message)

    def sleep(self, seconds):
        self.log(f'Sleeping {seconds}...')
        time.sleep(seconds)

    def run_docker_app_abc(self, number, commands):
        exec_commands = [
            'docker',
            'exec',
            '-u',
            'abc',
            f'{self.PROJECT_NAME}-client{number}-1',
        ] + commands
        self.log(f"Executing: {' '.join(exec_commands)}")
        result = subprocess.run(exec_commands, capture_output=True, text=True)
        if result.stdout:
            self.log(f"Output: {result.stdout}")
        if result.stderr:
            self.log(f"Error: {result.stderr}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--execresults', action='store_true')
    parser.add_argument('--execurls', action='store_true')
    parser.add_argument('--execdomainsqueries', action='store_true')
    parser.add_argument('--fromindex', type=int, default=1)
    parser.add_argument('--toindex', type=int, default=20)
    args = parser.parse_args()
    runner = Runner()

    if args.execresults:
        runner.log('Exec Results...')

        for client_id in range(args.fromindex, args.toindex + 1):
            runner.log(f'Starting app {client_id}/{args.toindex}...')
            thread = threading.Thread(target=runner.run_docker_app_abc, args=(client_id, ['bash', '-c', "cd /app && /venv/bin/python3.11 run_results.py"]))
            thread.start()
            runner.sleep(5)
    elif args.execurls:
        runner.log('Exec Urls...')

        for client_id in range(args.fromindex, args.toindex + 1):
            runner.log(f'Starting app {client_id}/{args.toindex}...')
            thread = threading.Thread(target=runner.run_docker_app_abc, args=(client_id, ['bash', '-c', "cd /app && /venv/bin/python3.11 run_urls.py"]))
            thread.start()
            runner.sleep(5)
    elif args.execdomainsqueries:
        runner.log('Exec Domains Queries...')

        for client_id in range(args.fromindex, args.toindex + 1):
            runner.log(f'Starting app {client_id}/{args.toindex}...')
            thread = threading.Thread(target=runner.run_docker_app_abc, args=(client_id, ['bash', '-c', "cd /app && /venv/bin/python3.11 run_domainsqueries.py"]))
            thread.start()
            runner.sleep(5)
    else:
        runner.log('No Action Specified. Exiting...')

    runner.log('Script Finished')
    runner.sleep(3600)
