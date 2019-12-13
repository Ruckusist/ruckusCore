from ruckusCore import __version__
from distutils.core import setup
import setuptools
import os

setup(
    name              = 'ruckusCore',
    author            = "Ruckusist",
    author_email = "eric.alphagriffin@gmail.com",
    url = "https://github.com/Ruckusist/ruckusCore",
    version           = __version__,
    packages          = setuptools.find_packages(),
    install_requires  = ['jinja2'],
    package_data      = {'ruckusCore': [
        './templates/about.j2',
        ]},
    license           = open('LICENSE.txt').read(),
    long_description  = open('README.md').read(),
    keywords = 'educational curses framework development',
    classifiers       = [
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Framework',
        # 'License :: OSI Approved :: MIT License',
        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.4',
        # 'Programming Language :: Python :: 3.5',
        # 'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        # 'Programming Language :: Python :: 3.8',
        ],
    entry_points = {
        'console_scripts': [
            "ruckusCore = ruckusCore.cli:main"
        ]
    }
)