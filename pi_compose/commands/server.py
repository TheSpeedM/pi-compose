"""Start the server proces"""

# DISCLAIMER: This is probably very unsafe.
# It's meant for running on a trusted local network (on a Raspberry Pi perhaps?).
# ¯\_(ツ)_/¯

import os

from zipfile import ZipFile
from tempfile import TemporaryDirectory
from subprocess import run, Popen, PIPE

from flask import Flask, request
from flask_restful import Resource, Api, reqparse

import click

app = Flask(__name__)
api = Api(app)

ZIP_NAME = 'recieved{}.zip'
DOCKER_COMPOSE = ['docker-compose', 'up', '-d']
GUNICORN = ['gunicorn']

class _process():
    stderr = False
    pid = 'Something probably went wrong'

class GetFiles(Resource):
    """Recieve files via a post request"""

    def __init__(self):
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('args')
        self.parser.add_argument('project_name')

        self.cwd = os.getcwd()

        self.iters = 0

    def get(self):
        """Notify user about pi-compose server running"""
        return "pi-compose server is running at this adress..."

    def post(self):
        """Recieve and compose project folder"""
        args = self.parser.parse_args()
        self.iters += 1

        zip_file = request.files['file']
        command = list(DOCKER_COMPOSE)

        if args['args']:
            command.append(args['args'].replace('-d', ''))

        process = _process

        try:
            with TemporaryDirectory() as tmpdir:
                zip_abspath = os.path.abspath(os.path.join(tmpdir, ZIP_NAME.format(self.iters)))

                zip_file.save(zip_abspath)

                _unzip(zip_abspath, tmpdir)

                os.chdir(f"{tmpdir}/{args['project_name']}")
                process = run(command, stdout=PIPE, stderr=PIPE) # pylint: disable=subprocess-run-check
                output = process.stdout if process.stdout else process.stderr
                output = output.decode()

        except Exception as exception: # pylint: disable=broad-except
            if not process.stderr:
                output = exception

        finally:
            os.chdir(self.cwd)

        return output


def _unzip(zip_file, directory):
    with ZipFile(zip_file) as zip_ref:
        zip_ref.extractall(directory)

api.add_resource(GetFiles, '/')

@click.group()
def server():
    """pi-compose server side operation"""

@server.command(context_settings={'ignore_unknown_options': True})
@click.argument('ip', default='127.0.0.1')
@click.argument('port', default='5000')
@click.option('-d', '--detach', is_flag=True, help='Run the server detached. (recommended)')
@click.argument('gunicorn_args', nargs=-1)
def start(ip, port, detach, gunicorn_args):
    """Start Gunicorn WSGI HTTP server"""

    cwd = os.getcwd()
    process = _process
    stdout = 'Running server in detached mode!'
    stderr = 'PID: {}'

    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    try:
        bind = '-b '
        bind += ip
        bind += ':' if ':' not in port else ''
        bind += port

        process = Popen([*GUNICORN, bind, *gunicorn_args, 'server:app'], stdout=PIPE, stderr=PIPE)

        while process.poll() is None and not detach:
            stdout, stderr = process.communicate()
            click.echo(stdout)

        click.echo(stdout)
        click.echo(stderr.format(process.pid) if detach else stderr)

    finally:
        os.chdir(cwd)
