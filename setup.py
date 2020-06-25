"""pi-compose - deploy docker-compose projects on remote Pi"""
from setuptools import setup, find_packages
from pip._internal.req import parse_requirements

install_requires = [str(item.req) for item in parse_requirements('requirements.txt', False)]

setup(
    name='pi_compose',
    version='0.1',
    description='docker-compose to remote pi',
    packages=find_packages(),
    install_requires=install_requires,
    entry_points={
        'console_scripts': [
            'pi-compose = pi_compose.cli:pi_compose'
        ],
    }
)
