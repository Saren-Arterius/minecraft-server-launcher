#!/usr/bin/python
from subprocess import Popen
from os.path import dirname, isfile, expanduser, join
from time import sleep
from os import access, W_OK, getuid
from sys import exit
import configparser
import argparse
import signal

from screenutils import list_screens

from pwd import getpwnam

EXIT_FLAG = False
WAITING_FOR_RESTART = False
CONFIG_PATH = "/etc/mcservers.conf"
HOME_CONFIG_PATH = ".mcservers.conf"


def handler(signum = None, frame = None):
    global EXIT_FLAG
    global args
    if signum == 2 and not WAITING_FOR_RESTART:
        print("Will spawn process again.")
        EXIT_FLAG = False
        return
    print("Will not spawn process again.")
    EXIT_FLAG = True
    for screen in list_screens():
        if screen.name == "mcs-{0}".format(args.ident):
            screen.send_commands("")
            screen.send_commands("stop")
            screen.send_commands("end")
            return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = 'Starts and wraps a minecraft server.')
    parser.add_argument('ident', metavar = 'IDENT', type = str,
                        help = 'Identifying string.')
    args = parser.parse_args()

    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)

    if args.ident not in config.sections():
        exit("IDENT '{0}' is not in config.".format(args.ident))

    if getuid() == 0:
        try:
            run_user = config[args.ident].get("User")
            getpwnam(run_user)
            config.read(join(expanduser("~{0}".format(run_user)), HOME_CONFIG_PATH))
        except KeyError as e:
            exit("Run user is invalid: {0}.".format(str(e)))
    else:
        config.read(join(expanduser("~"), HOME_CONFIG_PATH))

    path = config[args.ident].get("Path")
    if path is None:
        exit("Server path is none.")
    if not isfile(path):
        exit("Server jar does not exist.")
    if not access(dirname(path), W_OK):
        exit("You don't have write access to server path.")

    max_ram = config[args.ident].get("MaxRamMB")
    try:
        max_ram = int(max_ram)
    except ValueError:
        exit("Error parsing max ram usage: {0}.".format(max_ram))
    if max_ram < 256:
        exit("Max ram usage is too small: {0}MB.".format(max_ram))
    if max_ram > 10240:
        exit("Max ram usage is too big: {0}MB.".format(max_ram))

    for sig in [signal.SIGTERM, signal.SIGINT, signal.SIGHUP, signal.SIGQUIT]:
        signal.signal(sig, handler)
    while not EXIT_FLAG:
        WAITING_FOR_RESTART = False
        if getuid() == 0:
            proc = Popen(
                ["sudo", "-u", run_user, "java", "-server", "-Xmx{0}m".format(max_ram), "-jar", path, "nogui", "-o",
                 "false"],
                cwd = dirname(path))
        else:
            proc = Popen(["java", "-server", "-Xmx{0}m".format(max_ram), "-jar", path, "nogui", "-o", "false"],
                         cwd = dirname(path))

        outs, errs = proc.communicate()
        WAITING_FOR_RESTART = True
        for i in range(3, 0, -1):
            if EXIT_FLAG:
                break
            print("{0}...".format(i))
            sleep(1)
    print("Exiting...")