#!/usr/bin/python3
from subprocess import check_output, call
from os.path import expanduser, join
from time import sleep
from os import getuid
import configparser
import argparse

from screenutils import list_screens

CONFIG_PATH = "/etc/mcservers.conf"
HOME_CONFIG_PATH = ".mcservers.conf"
MCSERVER_WRAPPER = "mcserver-wrapper"
MCSERVER_LAUNCHER = "mcserver-launcher"
has_args = False


class SendCommand(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs):
        super(SendCommand, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string = None):
        global has_args
        has_args = True
        success = False
        if len(values) <= 1:
            print("There must be at least 2 arguments.")
            return
        for screen in list_screens():
            if screen.name == "mcs-{0}".format(values[0]):
                success = True
                screen.send_commands("")
                screen.send_commands(" ".join(values[1:]))
        if success:
            print("Successfully sent '{0}' to minecraft server {1}.".format(" ".join(values[1:]), values[0]))
        else:
            print("Minecraft server {0} not found.".format(values[0]))


class StartAll(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs):
        super(StartAll, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string = None):
        global has_args
        has_args = True
        if getuid() != 0:
            print("This command can only be run as root.".format(values))
            return

        for section in config.sections():
            user = config[section].get("User")
            config.read(join(expanduser("~{0}".format(user)), HOME_CONFIG_PATH))
            if config[section].getboolean("AutoStart"):
                call(["sudo", "-u", user, "mcserver-launcher", "-s", section])
            config.read(CONFIG_PATH)


class TerminateAll(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs):
        super(TerminateAll, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string = None):
        global has_args
        has_args = True
        if getuid() != 0:
            print("This command can only be run as root.".format(values))
            return
        output = check_output(
            "ps aux | grep -v SCREEN | grep {0} | grep -v grep | awk '{{print $2}}'".format(MCSERVER_WRAPPER),
            shell = True, universal_newlines = True).splitlines()
        for pid in output:
            print("Terminating PID {0}...".format(str(pid)))
        while len(output) != 0:
            for pid in output:
                call(["kill", str(pid)])
            sleep(1)
            output = check_output(
                "ps aux | grep -v SCREEN | grep {0} | grep -v grep | awk '{{print $2}}'".format(MCSERVER_WRAPPER),
                shell = True, universal_newlines = True).splitlines()
        print("Successfully terminated all minecraft servers.")


class AttachServer(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs):
        super(AttachServer, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string = None):
        global has_args
        has_args = True
        call(["screen", "-r", "mcs-{0}".format(values)])


class TerminateServer(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs):
        super(TerminateServer, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string = None):
        global has_args
        has_args = True
        success = False
        for screen in list_screens():
            if screen.name == "mcs-{0}".format(values):
                cmd = "ps aux | grep {0}$ | grep python | grep {1} " \
                      "| grep -v grep | awk '{{print $2}}'".format(values, MCSERVER_WRAPPER)
                result = check_output(cmd, shell = True).decode()
                pid = int(result)
                while screen.exists:
                    call(["kill", str(pid)])
                    sleep(1)
                success = True
                break
        if success:
            print("Successfully terminated minecraft server {0}.".format(values))
        else:
            print("Minecraft server {0} not found.".format(values))


class StartServer(argparse.Action):
    def __init__(self, option_strings, dest, **kwargs):
        super(StartServer, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string = None):
        global has_args
        has_args = True
        for screen in list_screens():
            if screen.name == "mcs-{0}".format(values):
                print("Minecraft server {0} already spawned.".format(values))
                return

        call(["screen", "-dmS", "mcs-{0}".format(values), MCSERVER_WRAPPER, values])
        sleep(0.05)
        success = False
        for screen in list_screens():
            if screen.name == "mcs-{0}".format(values):
                success = True
                break
        if success:
            print("Successfully spawned minecraft server {0}.\n'$ screen -r mcs-{0}' to attach the screen.".format(
                values))
        else:
            print("Failed to spawn minecraft server {0}.".format(values))


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    config.read(join(expanduser("~"), HOME_CONFIG_PATH))

    parser = argparse.ArgumentParser(description = 'CLI minecraft server manager.')
    parser.add_argument('-a', '--attach-server', metavar = 'IDENT', type = str,
                        help = "Attach to a server's screen.", action = AttachServer)
    parser.add_argument('-s', '--start-server', metavar = 'IDENT', type = str,
                        help = 'Starts a server.', action = StartServer)
    parser.add_argument('-t', '--terminate-server', metavar = 'IDENT', type = str,
                        help = 'Terminates a server.', action = TerminateServer)
    parser.add_argument('-c', '--send-command', metavar = 'IDENT_AND_COMMAND', type = str,
                        help = 'Sends a command to the screen.', action = SendCommand, nargs = '+')
    parser.add_argument('--start-all',
                        help = 'Starts all servers.', action = StartAll, nargs = '?', )
    parser.add_argument('--terminate-all',
                        help = 'Terminates all servers.', action = TerminateAll, nargs = '?', )
    args = parser.parse_args()
    if not has_args:
        parser.print_help()



