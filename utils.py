# TODO: Test on Linux and macOS.
import subprocess
from sys import platform


def _command_output(command):
    process = subprocess.run(command, shell=True, stdout=subprocess.PIPE,
                             universal_newlines=True)
    for line in process.stdout.splitlines():
        yield line.strip()


def get_ip_addresses():
    ip_addresses = []
    if platform.startswith('win') or platform == 'cygwin':
        for line in _command_output('ipconfig'):
            if line.startswith('IPv4'):
                ip_address = line.rsplit(' ', 1)[-1]
                ip_addresses.append(ip_address)
    elif platform.startswith('linux'):
        for line in _command_output('ip addr show | grep "inet "'):
            ip_address = line.split(' ')[1].split('/')[0]
            if ip_address != '127.0.0.1' and ip_address != '0.0.0.0':
                ip_addresses.append(ip_address)
    elif platform == 'darwin':
        for line in _command_output('ifconfig | grep "inet "'):
            ip_address = line.split(' ')[1]
            if ip_address != '127.0.0.1' and ip_address != '0.0.0.0':
                ip_addresses.append(ip_address)
    else:
        raise NotImplementedError
    return ip_addresses


def openfile(path):
    if platform.startswith('win') or platform == 'cygwin':
        subprocess.Popen(['explorer', '-p', '/select,', path])
    elif platform.startswith('linux'):
        subprocess.Popen(['xdg-open', path])
    elif platform.startswith('darwin'):
        subprocess.Popen(['open', path])
    else:
        raise NotImplementedError


def openfolder(path):
    if platform.startswith('win') or platform == 'cygwin':
        subprocess.Popen(['explorer', '/select,', path])
    elif platform.startswith('linux'):
        path = path.rsplit('/', 1)[0] + '/'
        subprocess.Popen(['xdg-open', path])
    elif platform.startswith('darwin'):
        path = path.rsplit('/', 1)[0] + '/'
        subprocess.Popen(['open', path])
    else:
        raise NotImplementedError
