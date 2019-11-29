#!/usr/bin/python3

from distutils.core import setup
from setuptools.command.install import install
import os

class command(install):
    def run(self):
        print('Running custom command:')

        os.system('sudo cp -v bdtran/main.py /usr/bin/bdtran')
        install.run(self)

setup(
    name = "bdtran",
    version = "1.0",
    description = "Baidu translate",
    author = "poemdistance",
    author_email = "poemdistance@gmail.com",
    url = "",
    packages = ['bdtran'],
    cmdclass={'install':command}
)

