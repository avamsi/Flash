# TODO: cross platform.
import subprocess


def get_ip_addresses():
    ip_addresses = []
    ipconfig = subprocess.run('ipconfig',
                              shell=True,
                              stdout=subprocess.PIPE,
                              universal_newlines=True)
    for line in ipconfig.stdout.splitlines():
        line = line.strip()
        if line.startswith('IP'):
            ip_address = line.rsplit(' ', 1)[-1]
            ip_addresses.append(ip_address)
    return ip_addresses


def openfile(path):
    subprocess.Popen(['explorer', '-p', '/select,', path])


def openfolder(path):
    subprocess.Popen(['explorer', '/select,', path])
