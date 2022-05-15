# app.py

# Import lib e-paper
import os
import sys
sys.path.append('lib')
sys.path.append('font')
import logging
from waveshare_epd import epd7in5_V2
from PIL import Image, ImageFont, ImageDraw

# Import Flask API
from flask import Flask, request
import requests
import multiprocessing
import threading
import time

# Init API
app = Flask(__name__)

# Init e-paper
epd = epd7in5_V2.EPD()
epd.init()
epd.Clear()
KEY = 'ABC123'
IP = '192.168.1.11'
PORT = '80'
font60 = ImageFont.truetype('font/Font.ttc', 60)


def image_frame(path_bmp):
    epd.init()
    image = Image.new('1', (epd.width, epd.height), 255)
    bmp = Image.open(path_bmp)
    image.paste(bmp, (0,0))
    epd.display(epd.getbuffer(image))
    epd.sleep()

def config_frame():
    epd.init()
    sucess_image = Image.new('1', (epd.height, epd.width), 255)
    sucess_draw = ImageDraw.Draw(sucess_image)
    sucess_draw.text((25, 370), 'SUCESS CONFIG', font = font60, fill = 0)
    epd.display(epd.getbuffer(sucess_image))
    epd.sleep()


def boot_frame():
    ip_image = Image.new('1', (epd.height, epd.width), 255)
    ip_draw = ImageDraw.Draw(ip_image)
    ip_draw.text((25, 310), 'IP: '+IP, font = font60, fill = 0)
    ip_draw.text((25, 370), 'PORT: '+PORT, font = font60, fill = 0)
    ip_draw.text((25, 430), 'KEY: '+KEY, font = font60, fill = 0)
    epd.display(epd.getbuffer(ip_image))
    epd.sleep()


@app.get("/ip")
def get_ip():
    ip_address = request.environ["HTTP_HOST"]
    port = request.environ["SERVER_PORT"]
    return {"ip": ip_address, "port": port}, 200


@app.get("/")
def get_index():
    return {"sucess": True}, 200


@app.post("/config")
def add_config():
    form = request.form
    
    if form.get("key") == KEY and form.get("config"): 
        config_frame()
        return {'success': True}, 200
    else:
        return {'message': 'incorrect key', 'status': 400}, 400


@app.post("/picture")
def add_new_image():
    form = request.form
    bmp = request.files['bmp']

    if form.get("key") == KEY:
        bmp.save("image_bmp/"+bmp.filename)
        image_frame("image_bmp/"+bmp.filename)
        os.remove("image_bmp/"+bmp.filename)
        return {'success': True}, 200
    else:
        return {'message': 'incorrect key', 'status': 400}, 400



def API():
   print('In API')
   app.run(host='0.0.0.0', port=80)


if __name__ == "__main__":
    p = multiprocessing.Process(target=API)

    try:
        p.start()

        requests.get("http://127.0.0.1:80/ip")
        boot_frame()

    finally:
        print('Frame and API is ready')
