from typing import Optional

from PIL import Image, ImageDraw, ImageFont
from brother_ql.conversion import convert
from brother_ql.backends.helpers import send
from brother_ql.raster import BrotherQLRaster

import os

if os.sep == '\\':
    robotoPath = os.path.abspath('Program Files\PyLabel\RobotoRegular.ttf')
elif os.sep == '/':
    robotoPath = '/usr/local/PyLabel/RobotoRegular.ttf'

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

def generate_image(text_list, image_width_mm, spacing_mm, aTL: Optional[bool] = True):
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

    for text in text_list:
        max_font_size = get_max_font_size(text, image_width_px, 'arial.ttf', draw)
        font_size = max_font_size if max_font_size < font_size else font_size
        font = ImageFont.truetype('arial.ttf', max_font_size)
        text_bbox = draw.textbbox((0, 0), text, font=font, align='left')
        text_height = text_bbox[3] - text_bbox[1]
    
    total_height_px = (text_height + spacing_px) * (len(text_list))
    
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
