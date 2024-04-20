from datetime import datetime
import threading
import argparse
import time
import os
import subprocess


class Runner:
    CLIENTS_NB = 10
    PROJECT_NAME = "googlebotwebtop"

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
        commands = ["docker", "compose", "-f", "compose.yaml", "-p", self.PROJECT_NAME]
        down_commands = commands + ["down"]
        self.log(f"Executing: {' '.join(down_commands)}")
        subprocess.run(down_commands)

        up_commands = commands + [ "up", "--detach", "--remove-orphans"]
        self.log(f"Executing: {' '.join(up_commands)}")
        subprocess.run(up_commands)

    def run_docker_app_abc(self, number, command):
        # docker exec -it -u abc googlebotwebtop-client6-1 bash -c "cd /app && python3 run.py"
        exec_commands = [
            'docker',
            'exec',
            '-it',
            '-u',
            'abc',
            f'{self.PROJECT_NAME}-client{number}-1',
            'bash', '-c', command
        ]
        self.log(f"Executing: {' '.join(exec_commands)}")
        subprocess.run(exec_commands)

    def run_docker_app_root(self, number):
        # nohup docker exec -it -u root googlebotwebtop-client6-1 bash -c "cd /app && bash install.sh" &
        exec_commands = [
            'docker',
            'exec',
            '-it',
            f'{self.PROJECT_NAME}-client{number}-1',
            'bash',
            '-c',
            'cd /app && bash install.sh'
        ]
        self.log(f"Executing: {' '.join(exec_commands)}")
        subprocess.run(exec_commands)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--build', action='store_true')
    parser.add_argument('--runstart', action='store_true')
    parser.add_argument('--runscript', action='store_true')
    parser.add_argument('--nb', type=int, default=10, help='Sets the nb of clients value (default: 10)')

    args = parser.parse_args()

    runner = Runner()

    if args.build:
        runner.log('Building docker...')
        runner.create_config_file()
        runner.run_docker_compose()

        for i in range(runner.CLIENTS_NB):
            runner.sleep(5)
            app_number = i + 1
            runner.log(f'Starting app {app_number}/{runner.CLIENTS_NB}...')
            thread = threading.Thread(target=runner.run_docker_app_root, args=(app_number,))
            thread.start()

    elif args.runstart:
        runner.log('Executing...')

        for i in range(runner.nb):
            app_number = i + 1
            runner.log(f'Starting app {app_number}/{runner.nb}...')
            thread = threading.Thread(target=runner.run_docker_app_abc, args=(app_number, "start-tor-browser",))
            thread.start()
    elif args.runscript:
        runner.log('Executing...')

        for i in range(runner.nb):
            app_number = i + 1
            runner.log(f'Starting app {app_number}/{runner.nb}...')
            thread = threading.Thread(target=runner.run_docker_app_abc, args=(app_number, "cd /app && python3 run.py",))
            thread.start()
