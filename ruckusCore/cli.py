import ruckusCore
import os
import sys

def build_init_file():
    print("Setup ruckusCore Init.")
    with open('.log', 'aw') as log:
        if not os.path.exists(os.path.join(os.getcwd(), "archive")):
            log.write("Creating empty 'archive' folder.")
            os.mkdir(os.path.join(os.getcwd(), "archive"))
        if not os.path.exists(os.path.join(os.getcwd(), "project")):
            log.write("Creating 'project' folder for source files.")
            os.mkdir(os.path.join(os.getcwd(), "project"))
        if not os.path.exists(os.path.join(os.getcwd(), "setup.py")):
            with open('setup.py', 'aw') as File:
                File.write(
                    """
                    
                    from distutils.core import setup
                    import setuptools
                    import os

                    setup(
                        name              = 'TESTPROJ',
                        version           = __version__,
                        packages          = setuptools.find_packages(),
                        entry_points      = {
                            'console_scripts': [
                                "TESTPROJ = project.cli:main"
                            ]
                        }
                    )
                    """
                )
        if not os.path.exists(os.path.join(os.getcwd(), "project", "cli.py")):
            with open(os.path.join(os.getcwd(), "project", "cli.py"), 'aw') as File:
                File.write(
                    """
                    import TESTPROJ

                    def main():
                        app = TESTPROJ.Main()
                        app.run()
                    """
                )
        if not os.path.exists(os.path.join(os.getcwd(), "project", "__init__.py")):
            with open(os.path.join(os.getcwd(), "project", "__init__.py"), 'aw') as File:
                File.write(
                    """
                    from .main import *

                    __version__ = 0.0.1dev
                    """
                )
        if not os.path.exists(os.path.join(os.getcwd(), "project", "main.py")):
            with open(os.path.join(os.getcwd(), "project", "main.py"), 'aw') as File:
                File.write(
                    """
                    import ruckusCore
                    from .mod import Mod

                    class Main(ruckusCore.App):
                        def __init__(self):
                            super().__init__(self)
                    """
                )
        if not os.path.exists(os.path.join(os.getcwd(), "project", "mod.py")):
            with open(os.path.join(os.getcwd(), "project", "mod.py"), 'aw') as File:
                File.write(
                    """
                    import ruckusCore

                    class Mod(ruckusCore.Module):
                        def __init__(self):
                            super().__init__(self)
                    """
                )
        log.write("Starting New Project. Good Luck.")
    return

def main():
    """Main Entry Point for ruckusCore CLi"""
    data = sys.argv

    if 'init' == data[1]:
        build_init_file()

    elif '.' in data[1][-3:]:
        print("This is probably a filename.")

    else:
        print("Raise: Not Implemented Error.")


if __name__ == "__main__":
    main()