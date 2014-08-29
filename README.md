Minecraft Server Launcher
=========================

A Minecraft server(s) launcher written in Python.

Dependencies
=========================
- Any linux distro with python3 installed
- python3: screenutils

Usage
=========================
```
usage: mcserver-launcher [-h] [-a IDENT] [-s IDENT] [-t IDENT]
                         [--start-all [START_ALL]]
                         [--terminate-all [TERMINATE_ALL]]

CLI minecraft server manager.

optional arguments:
  -h, --help            show this help message and exit
  -a IDENT, --attach-server IDENT
                        Attach to a server's screen.
  -s IDENT, --start-server IDENT
                        Starts a server.
  -t IDENT, --terminate-server IDENT
                        Terminates a server.
  --start-all [START_ALL]
                        Starts all servers.
  --terminate-all [TERMINATE_ALL]
                        Terminates all servers.
```
```
usage: mcserver-wrapper [-h] IDENT

Starts and wraps a minecraft server.

positional arguments:
  IDENT       Identifying string.

optional arguments:
  -h, --help  show this help message and exit
```

/etc/mcservers.conf
=========================
```
[urs-test]
User = saren
Path = /home/saren/minecraft/craftbukkit-urs-test/spigot.jar
MaxRamMB = 2048
AutoStart = True

[urs]
User = saren
Path = /home/saren/minecraft/craftbukkit-urs/spigot.jar
MaxRamMB = 6144
AutoStart = True

[hub]
User = saren
Path = /home/saren/minecraft/craftbukkit-hub/spigot.jar
MaxRamMB = 512
AutoStart = True

[bungee]
User = saren
Path = /home/saren/minecraft/bungeecord/BungeeCord.jar
MaxRamMB = 512
AutoStart = True

[cbl]
User = combatlife
Path = /home/combatlife/minecraft/craftbukkit/spigot.jar
MaxRamMB = 1024
AutoStart = True
```

~/.mcservers.conf
=========================
```
[urs-test]
MaxRamMB = 1024
AutoStart = False
```

Example systemd service file
=========================
```
[Unit]
Description=All Minecraft servers
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/bin/mcserver-launcher --start-all
ExecStop=/usr/bin/mcserver-launcher --terminate-all
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```
