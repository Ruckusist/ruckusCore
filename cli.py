# import ruckusCore
# ruckusCore.cli.main()
import subprocess
def command(command): return subprocess.Popen(command, shell=True, stdout=subprocess.PIPE).stdout.read().decode()

print(command("git status"))