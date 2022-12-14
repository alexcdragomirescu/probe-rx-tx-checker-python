import logging

logger = logging.getLogger(__name__)

import paramiko


class SSH(object):
    def __init__(self, hostname, username, password=None, key=None):
        self.hostname = hostname
        self.username = username
        self.password = password
        self.key = key

        self.__transport = None
        self._ssh = None
        self._sftp = None

    def openTransport(self):
        transport = paramiko.Transport((self.hostname, 22))

        if self.key is None:
            transport.connect(username=self.username, password=self.password)
        else:
            self.auth = paramiko.RSAKey.from_private_key_file(username=self.username, pkey = self.key)

        self.__transport = transport

    def openSSH(self):
        self._ssh = paramiko.SSHClient()
        self._ssh._transport = self.__transport

    def openSFTP(self):
        self._sftp = paramiko.SFTPClient.from_transport(self.__transport)

    def execCmd(self, command):
        stdin, stdout, stderr = self._ssh.exec_command(command)
        return stdout.readlines()

    def closeTransport(self):
        self.__transport.close()
