import os


def get_ip_addresses():
    # TODO: cross platform.
    ip_addresses = []
    for line in os.popen('ipconfig'):
        line = line.strip()
        if line.startswith('IP'):
            ip_address = line.rsplit(' ', 1)[-1]
            ip_addresses.append(ip_address)

    return ip_addresses
