from ruckusCore import __version__
from distutils.core import setup
import setuptools
import os

def get_package_data():
    data = []
    for f in os.listdir(os.path.join(os.getcwd(), 'ruckusCore')):
        ## WHY ISNT THIS PROPER RECURSIVE?? cause you dont know how... cause you dont get it...
        if f == "__pycache__": continue
        if os.path.isdir(os.path.join(os.getcwd(), 'ruckusCore', f)):
            for f_1 in os.listdir(os.path.join(os.getcwd(), 'ruckusCore', f)):
                if os.path.isdir(os.path.join(os.getcwd(), 'ruckusCore', f, f_1)):
                    for f_2 in os.listdir(os.path.join(os.getcwd(), 'ruckusCore', f, f_1)):
                        data.append(f"./{f}/{f_1}/{f_2}")
                else:
                    data.append(f"./{f}/{f_1}")

        else:
            data.append(f"./{f}")
    return data

if True:
    setup(
        name              = 'ruckusCore',
        author            = "Ruckusist",
        author_email = "eric.alphagriffin@gmail.com",
        url = "https://github.com/Ruckusist/ruckusCore",
        version           = __version__,
        packages          = setuptools.find_packages(),
        
        install_requires  = [
            'jinja2',      # Used in page templating. --> TODO: make optional
            'youtube-dl',  # Used in the the BoobTube Mod.  --> TODO: make optional
            'stem',        # Used for Tor based Communication.  --> TODO: make optional
            'psutil',      # Used for inter-process inspection. --> TODO: make optional
	        'lxml',        # Used for web page parseing.  --> not optional.
            ],
        package_data      = {'ruckusCore': get_package_data()},
        license           = open('LICENSE.txt').read(),
        long_description  = open('README.md').read(),
        keywords = 'educational curses framework development',
        classifiers       = [
            'Development Status :: 3 - Alpha',
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Framework',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',  # development version.
            ],
        entry_points = {
            'console_scripts': [
                "ruckusCore = ruckusCore.cli:main"
            ]
        }
    )
