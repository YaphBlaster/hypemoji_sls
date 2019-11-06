try:
    import unzip_requirements
except ImportError:
    pass

import numpy as np
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO
from imgurpython import ImgurClient
import boto3
import botocore
import os
import json


def create_comic(event, context):
    is_remote = False
    if __name__ != "__main__":
        is_remote = True;

    try:
        list_im = []
        list_text = []

        for value in event['body']:
            list_im.append(BytesIO(requests.get(value['url']).content))
            list_text.append(value['text'])

        images = [Image.open(i) for i in list_im]
        
        if(is_remote):
            s3 = boto3.resource('s3').Bucket('imgurupload')
            try:
                s3.download_file(
                    'tmp/Hack-BoldOblique.ttf', '/tmp/font.ttf')
            except botocore.exceptions.ClientError as e:
                print("Error: ", e)
            font = ImageFont.truetype('/tmp/font.ttf', 21)
            
            LAMBDA_IMGUR_CLIENT_ID = os.environ['IMGUR_CLIENT_ID']
            LAMBDA_IMGUR_CLIENT_SECRET = os.environ['IMGUR_CLIENT_SECRET']
            client = ImgurClient(LAMBDA_IMGUR_CLIENT_ID, LAMBDA_IMGUR_CLIENT_SECRET)
        else:
            font = ImageFont.truetype("arial.ttf", 21)
 
        widths, heights = zip(*(i.size for i in images))
        gap_in_pixels = 5 if (len(images) > 1) else 0
        total_height = sum(heights) + (gap_in_pixels * (len(images) -1))
        print(total_height)
        max_width = max(widths)
        min_width = min(widths)

        new_vertical_image = Image.new('RGB', (min_width, total_height))
        border_color = "black"

        y_offset = 0;
        for index, image, in enumerate(images):
            draw = ImageDraw.Draw(image, "RGBA")

            w, h = draw.textsize(list_text[index].upper(), font)
            width, height = image.size;
            # thicker border
            newWidth = (width-w)/2
            newHeight = (height-h) - 10
            newText = list_text[index].upper()
            draw.text((newWidth+1, newHeight-1),
                    newText, font=font, fill=border_color)
            draw.text((newWidth-1, newHeight+1),
                    newText, font=font, fill=border_color)
            draw.text((newWidth+1, newHeight+1),
                    newText, font=font, fill=border_color)
            draw.text((newWidth-1, newHeight-1),
                    newText, font=font, fill=border_color)
            draw.text((newWidth, newHeight),
                    newText, font=font, fill=(255, 255, 255, 255))

            new_vertical_image.paste(image, (0, y_offset))
            y_offset += image.size[1] + (gap_in_pixels if len(images) -1 > index else 0)
        
        new_vertical_image.save('/tmp/verticalImage.png' if is_remote else 'tmp/verticalImage.png',
                                format='PNG', subsampling=0, quality=100)

        if(is_remote):
            uploaded_image = client.upload_from_path("/tmp/verticalImage.png")
        else:
            uploaded_image = {'link': "tmp/verticalImage.png"}

        response = {
            'statusCode': 200,
            'body': uploaded_image['link']
        }

    except Exception as e:
        response = {
            "statusCode": 500,
            "body": e
        }

    return response


if __name__ == "__main__":
    with open('createComicTest.json') as f:
        data = json.load(f)
    print(create_comic(data, ''))
