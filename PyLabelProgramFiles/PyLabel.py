#!/usr/bin/python3

import argparse, sys
from typing import Optional

import os, json

if os.sep == '\\':
    configPath = ('C:\Program Files\PyLabel\config.json')
elif os.sep == '/':
    configPath = '/usr/local/PyLabel/config.json'

def loadConfig() -> dict:
    if os.path.isfile(configPath) is False:
        os.chdir('C:\Program Files\PyLabel')
        with open('config.json', 'w') as file:
            config = {
                'printer-model': "QL-820NWB",
                'printer-ip': "192.168.0.51"
            }
            json.dump(config, file)
            file.close()
    configFile = open(configPath)
    configData = json.load(configFile)

    config = {
                'printer-model': configData['printer-model'],
                'printer-ip': configData['printer-ip']
    }

    configFile.close()
    return config

def getConfigSetting(setting:str) -> str:
    config = loadConfig()
    return config[setting]

def setConfigSetting(setting:str, value:str):
    config = loadConfig()
    config[setting] = value

    with open(configPath, 'w') as configFile:
        json.dump(config, configFile)

from PIL import Image, ImageDraw, ImageFont
from brother_ql.conversion import convert
from brother_ql.backends.helpers import send
from brother_ql.raster import BrotherQLRaster

def mm_to_pixels(mm, dpi=300):
    return int(mm * dpi / 25.4)

def get_max_font_size(text, max_width, font_path, draw):
    font_size = 1
    font = ImageFont.truetype(font_path, font_size)
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    while text_width < max_width and font_size < 64:
        font_size += 1 
        font = ImageFont.truetype(font_path, font_size)
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
    return font_size - 1

def generate_image(text_list:list, image_width_mm:int, spacing_mm:int, aTL: Optional[bool] = True):
    dpi = 300
    image_width_px = mm_to_pixels(image_width_mm, dpi)
    spacing_px = mm_to_pixels(spacing_mm, dpi)
    
    temp_image = Image.new("RGB", (image_width_px, 1))
    draw = ImageDraw.Draw(temp_image)
    
    total_height_px = 0
    font_size = 999

    '''if aTL == False:
        max_font_size = get_max_font_size('NO AUTHORITY TO LEAVE', image_width_px, 'arial.ttf', draw)
        font_size = max_font_size if max_font_size < font_size else font_size
        font = ImageFont.truetype('arial.ttf', max_font_size)
        text_bbox = draw.textbbox((0, 0), 'NO AUTHORITY TO LEAVE', font=font)
        text_height = text_bbox[3] - text_bbox[1]
        total_height_px += text_height + spacing_px'''
    
    current_height_px = 0

    for text in text_list:
        max_font_size = get_max_font_size(text, image_width_px, 'arial.ttf', draw)
        font_size = max_font_size if max_font_size < font_size else font_size
        font = ImageFont.truetype('arial.ttf', font_size)
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_height = text_bbox[3] - text_bbox[1]
        draw.text((5, current_height_px), text, font=font, fill="black", align='left')
        current_height_px += text_height + spacing_px

    current_height_px = 0

    for text in text_list:
        font = ImageFont.truetype('arial.ttf', font_size)
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_height = text_bbox[3] - text_bbox[1]
        draw.text((5, current_height_px), text, font=font, fill="black", align='left')
        current_height_px += text_height + spacing_px

    total_height_px = current_height_px
    
    image = Image.new("RGB", (image_width_px, total_height_px), color="white")
    draw = ImageDraw.Draw(image)

    '''text =
    for i, item in enumerate(text_list):
        text += item
        if i < len(text_list):
            text += '\n'

    draw.text((0,0), text, font = ImageFont.truetype('arial.ttf', font_size), align='left')'''
    
    current_height_px = 0

    '''if aTL == False:
        max_font_size = get_max_font_size('NO AUTHORITY TO LEAVE', image_width_px, 'arial.ttf', draw)
        font = ImageFont.truetype('arial.ttf', max_font_size)
        text_bbox = draw.textbbox((0, 0), 'NO AUTHORITY TO LEAVE', font=font)
        text_height = text_bbox[3] - text_bbox[1]
        draw.text((0, current_height_px), 'NO AUTHORITY TO LEAVE', font=font, fill=(255, 0, 0))
        current_height_px += text_height + spacing_px'''

    for text in text_list:
        font = ImageFont.truetype('arial.ttf', font_size)
        text_bbox = draw.textbbox((0, 0), text, font=font)
        text_height = text_bbox[3] - text_bbox[1]
        draw.text((5, current_height_px), text, font=font, fill="black", align='left')
        current_height_px += text_height + spacing_px

    #image.show()
    #image.save("C:\\Users\\jamie\\Desktop\\img.png")
    
    return image

def printLabel(pIP: str, pModel: str, lblImage: Image):
    backend = 'network'
    printer = 'tcp://' + pIP

    qlr = BrotherQLRaster(pModel)
    qlr.exception_on_warning = True

    instructions = convert(
        qlr=qlr, 
        images=[lblImage],  # Takes a list of file names or PIL objects.
        label='62', 
        rotate='0',  # 'Auto', '0', '90', '270'
        threshold=70.0,  # Black and white threshold in percent.
        dither=False, 
        compress=False, 
        dpi_600=False, 
        red=True,
        hq=True,  # False for low quality.
        cut=True
    )  

    send(instructions=instructions, printer_identifier=printer, backend_identifier=backend, blocking=True)


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
