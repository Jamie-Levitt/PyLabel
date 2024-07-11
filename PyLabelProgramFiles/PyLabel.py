#!/usr/bin/python3

import argparse, sys
from typing import Optional

from Printing import generate_image, printLabel
from Config import getConfigSetting, setConfigSetting

def handle_print(lines:Optional[str], aTL:Optional[bool]):
    linesList = lines.split(';')
    img = generate_image(linesList, 62, 2, aTL)
    printLabel(getConfigSetting('printer-ip'), getConfigSetting('printer-model'), img)

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

    parser_print = subparsers.add_parser('print')
    parser_print.add_argument('-l', '--lines', type=str, required=True)
    parser_print.add_argument('-a', '--authorityToLeave')

    parser_config = subparsers.add_parser('config', help='Configure settings')
    parser_config.add_argument('-m', '--printer_model', type=str)
    parser_config.add_argument('-i', '--printer_ip', type=str)

    args = parser.parse_args()

    if args.command == 'print':
        handle_print(args.lines, args.authorityToLeave)
    elif args.command == 'config':
        handle_config(pModel = args.printer_model, pIP = args.printer_ip)
    else:
        parser.print_help()
        sys.exit(1)
    
    return

if __name__ == '__main__':
    main()
