"""docker-compose project on remote server"""

import os
from types import GeneratorType

from tempfile import NamedTemporaryFile
from zipfile import ZipFile

import requests
import click

@click.group()
def client():
    """pi-compose client"""

@client.command(context_settings={'ignore_unknown_options': True})
@click.argument('server_ip', nargs=1)
@click.argument('args', nargs=-1)
def up(server_ip, args): # pylint: disable=invalid-name
    """Send the project to docker-compose on another server"""

    if not server_ip.startswith('http://'):
        raise requests.exceptions.InvalidURL("Did you forget the 'http://' again?")

    args = ' '.join(args)

    project_dir = os.getcwd()
    os.chdir('../')

    project_folder = project_dir.split('/')[-1]

    with NamedTemporaryFile() as tmpfile:
        with ZipFile(tmpfile, 'w') as zip_file:

            for folder, _, filenames in os.walk(project_folder):
                for filename in filenames:
                    file_path = os.path.join(folder, filename)
                    zip_file.write(file_path)


        files = {
            'file': ('file.zip', open(tmpfile.name, 'rb'))
        }

        payload = {
            'args': args,
            'project_name': project_folder
        }

        output = requests.post(server_ip, files=files, data=payload).iter_lines()

    if isinstance(output, GeneratorType):
        for item in output:
            item = item.decode()
            item = item.replace('"', '')
            item = item.replace('\\n', '\n')

            click.echo(item)
    else:
        click.echo(output)
