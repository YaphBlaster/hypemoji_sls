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


def create_comic(event, context):
    try:
        list_im = []
        list_text = []

        for value in event['body']:
            list_im.append(BytesIO(requests.get(value['url']).content))
            list_text.append(value['text'])

        images = [Image.open(i) for i in list_im]

        s3 = boto3.resource('s3').Bucket('imgurupload')

        try:
            s3.download_file(
                'tmp/Hack-BoldOblique.ttf', '/tmp/font.ttf')
        except botocore.exceptions.ClientError as e:
            print("Error: ", e)

        # use a truetype font
        font = ImageFont.truetype('/tmp/font.ttf', 22)

        widths, heights = zip(*(i.size for i in images))

        total_height = sum(heights)
        max_width = max(widths)

        new_vertical_image = Image.new('RGB', (max_width, total_height))

        x_offset = 0
        y_offset = 0
        index = 0
        border_color = "black"
        for index, image, in enumerate(images):
            draw = ImageDraw.Draw(image, "RGBA")
            w, h = draw.textsize(list_text[index].upper(), font)
            # thicker border
            newWidth = (398-w)/2
            newHeight = (350-h)
            newText = list_text[index].upper()
            draw.text((newWidth+1, newHeight-1),
                      newText, font=font, fill=border_color)
            draw.text((newWidth-1, newHeight+1),
                      newText, font=font, fill=border_color)
            draw.text((newWidth+1, newHeight+1),
                      newText, font=font, fill=border_color)
            draw.text((newWidth-1, newHeight-1),
                      newText, font=font, fill=border_color)
            draw.text(((398-w)/2, (350-h)),
                      newText, font=font, fill=(255, 255, 255, 255))

            new_vertical_image.paste(image, (0, y_offset))
            x_offset += image.size[0]
            y_offset += image.size[1]

        new_vertical_image.save('/tmp/verticalImage.png',
                                format='PNG', subsampling=0, quality=100)

        LAMBDA_IMGUR_CLIENT_ID = os.environ['IMGUR_CLIENT_ID']
        LAMBDA_IMGUR_CLIENT_SECRET = os.environ['IMGUR_CLIENT_SECRET']
        client = ImgurClient(LAMBDA_IMGUR_CLIENT_ID,
                             LAMBDA_IMGUR_CLIENT_SECRET)

        uploaded_image = client.upload_from_path("/tmp/verticalImage.png")

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
