"""pi-compose command line application"""

import click

from .commands import client as _client
from .commands import server as _server

@click.group()
def pi_compose():
    """pi-compose command line application.

    An over-engineered solution for using docker-compose on a remote server.
    """

pi_compose.add_command(_client.client)
pi_compose.add_command(_server.server)
