#!/usr/bin/python3

import argparse, sys, os, json
from typing import Optional

from Printing import generate_image, printLabel
from Config import getConfigSetting, setConfigSetting

if os.sep == '\\':
    tempPath = ('C:\\Program Files\\PyLabel\\temp.json')
elif os.sep == '/':
    tempPath = '/usr/local/PyLabel/temp.json'

def add_line(line:str):
    if os.path.isfile(tempPath) is False:
        os.chdir('C:\Program Files\PyLabel')
        with open('temp.json', 'w') as file:
            temp = {'lines':[]}
            json.dump(temp, file)
            file.close()
    
    tempFile = open(tempPath)
    tempData = json.load(tempFile)
    lines = tempData['lines']
    lines.append(line)
    tempFile.close()

    with open(tempPath, 'w') as file:
        json.dump({'lines': lines}, file)
        file.close()

def handle_print(aTL:Optional[bool]):
    tempFile = open(tempPath)
    tempData = json.load(tempFile)
    lines = tempData['lines']

    img = generate_image(lines, 62, 2, aTL)
    printLabel(getConfigSetting('printer-ip'), getConfigSetting('printer-model'), img)
    with open(tempPath, 'w') as file:
        json.dump({'lines': []}, file)
        file.close()

def handle_config(pModel:Optional[str] = None, pIP:Optional[str] = None):
    if pModel is not None:
        setConfigSetting('printer-model', pModel)
        print('Printer Model has been set to ' + getConfigSetting('printer-model'))
    if pIP is not None:
        setConfigSetting('printer-ip', pIP)
        print('Printer IP has been set to ' + getConfigSetting('printer-ip'))

def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='command')

    parser_print = subparsers.add_parser('addLine')
    parser_print.add_argument('-l', '--line')

    parser_print = subparsers.add_parser('print')
    parser_print.add_argument('-a', '--authorityToLeave')

    parser_config = subparsers.add_parser('config', help='Configure settings')
    parser_config.add_argument('-m', '--printer_model', type=str)
    parser_config.add_argument('-i', '--printer_ip', type=str)

    args = parser.parse_args()

    if args.command == 'addLine':
        add_line(args.line)
    if args.command == 'print':
        handle_print(args.authorityToLeave)
    elif args.command == 'config':
        handle_config(pModel = args.printer_model, pIP = args.printer_ip)
    else:
        parser.print_help()
        sys.exit(1)
    
    return

if __name__ == '__main__':
    main()
