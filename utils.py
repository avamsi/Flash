#OS X is untested
import subprocess
from sys import platform

def get_ip_addresses():
    ip_addresses = []
    if platform.startswith("win") or platform == "cygwin":
        ipconfig = subprocess.run('ipconfig', shell=True, stdout=subprocess.PIPE,
                                  universal_newlines=True)
        for line in ipconfig.stdout.splitlines():
            line = line.strip()
            if line.startswith('IPv4'):
                ip_address = line.rsplit(' ', 1)[-1]
                ip_addresses.append(ip_address)
    elif platform.startswith("linux"):
        ipconfig = subprocess.run('ip addr show | grep "inet "', shell=True, stdout=subprocess.PIPE,
                                  universal_newlines=True)
        for line in ipconfig.stdout.splitlines():
            line = line.strip()
            ip_address = line.split(' ')[1].split('/')[0]
            if ip_address != '127.0.0.1' and ip_address != '0.0.0.0':
                ip_addresses.append(ip_address)
    elif platform == "darwin":
        ipconfig = subprocess.run('ifconfig | grep "inet "', shell=True, stdout=subprocess.PIPE,
                                  universal_newlines=True)
        for line in ipconfig.stdout.splitlines():
            line = line.strip()
            ip_address = line.split(' ')[1]
            if ip_address != '127.0.0.1' and ip_address != '0.0.0.0':
                ip_addresses.append(ip_address)
    return ip_addresses


def openfile(path):
    if platform.startswith("win") or platform == "cygwin":
        subprocess.Popen(['explorer', '-p', '/select,', path])
    elif platform.startswith("linux"):
        subprocess.Popen(['xdg-open', path])
    elif platform.startswith("darwin"):
        subprocess.Popen(['open', path])


def openfolder(path):
    if platform.startswith("win") or platform == "cygwin":
        subprocess.Popen(['explorer', '/select,', path])
    elif platform.startswith("linux"):
        unprocessed_path = path[::-1].split('/', maxsplit=1)
        path = unprocessed_path[1][::-1] + '/'
        subprocess.Popen(['xdg-open',path])
    elif platform.startswith("darwin"):
        unprocessed_path = path[::-1].split('/', maxsplit=1)
        path = unprocessed_path[1][::-1] + '/'
        subprocess.Popen(['open', path])

