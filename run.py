import threading
import argparse
import time
import os
import subprocess


from datetime import datetime


class Runner:
    def log(self, message):
        """ Logs a message """
        print(f'Runner: {message}')

    def sleep(self, seconds):
        self.log(f'Sleeping {seconds}...')
        time.sleep(seconds)

    def create_pgpass_file(self):
        pgpass = '.pgpass'
        if not os.path.isfile(pgpass):
            with open (pgpass, 'w') as file:
                file.write(f"postgres:5432:*:postgres:{self.random_postgres_password}\n")

    def create_config_file(self):
        """ Creates the config.py file with necessary configurations """
        current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        config_file_path = '.env'

        if not os.path.isfile(config_file_path):
            with open(config_file_path, 'w') as file:
                self.log(f'Creating File: {config_file_path}')
                config_file_content = f"# Script Generated on {current_datetime}\n"
                config_file_content += '\n'

                config_file_content += 'TOR_COMMAND = \'start-tor-browser\'\n'
                config_file_content += 'GRAPHQL_URL = \'https://gb.shopdev.ca/graphql/v1/\''
                config_file_content += 'GRAPHQL_AUTHORIZATION = \'Basic ...\''

                file.write(config_file_content)

    def run_docker_compose(self):
        """ Runs Docker Compose commands to start or restart the environment """
        commands = ["docker", "compose", "-f", "compose-clients.yaml", "-p", self.docker_project]
        down_commands = commands + ["down"]
        self.log(f"Executing: {' '.join(down_commands)}")
        subprocess.run(down_commands)

        up_commands = commands + [ "up", "--detach", "--remove-orphans"]
        self.log(f"Executing: {' '.join(up_commands)}")
        subprocess.run(up_commands)

    def run_docker_app(self, number):
        exec_commands = [
            'docker',
            'exec',
            '-it',
            '-u',
            'abc',
            'googlebotwebtopclients-app%d-1' % number,
            'bash', '-c', "cd /app && python3 run.py"
        ]
        self.log(f"Executing: {' '.join(exec_commands)}")
        subprocess.run(exec_commands)
        # subprocess.Popen(exec_commands)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--build', action='store_true')
    parser.add_argument('--exec', action='store_true')
    args = parser.parse_args()

    runner = Runner()
    runner.docker_project = "googlebotwebtopclients"

    if args.build:
        runner.log('Building docker...')
        runner.create_config_file()
        runner.run_docker_compose()

    if args.exec:
        runner.log('Executing...')

        if args.build:
            runner.sleep(5)

        for i in range(1):
            app_number = i + 1
            runner.log(f'Starting app {app_number}...')
            thread = threading.Thread(target=runner.run_docker_app, args=(app_number,))
            thread.start()
