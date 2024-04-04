import json
from PIL import Image
import pygetwindow as gw
import pyautogui
from flask import Flask, jsonify, request

import threading
import multiprocessing
import time

import numpy as np

from scipy.spatial import KDTree

width = 676
height = 337

height_scale = 1.58
###
default_colors = {"#F0F0F0":1, "#F2B233":2, "#E57FD8":4,
                "#99B2F2":8, "#DEDE6C":16, "#7FCC19":32,
                "#F2B2CC":64, "#4C4C4C":128, "#999999":256,
                "#4C99B2":512, "#B266E5":1024,
                "#3366CC":2048, "#7F664C":4096, "#57A64E":8192,
                "#CC4C4C":16384, "#111111":32768}

target_colors = [
    (240, 240, 240),
    (242, 178, 51),
    (229, 127, 216),
    (153, 178, 242),
    (222, 222, 108),
    (127, 204, 25),
    (242, 178, 204),
    (76, 76, 76),
    (153, 153, 153),
    (76, 153, 178),
    (178, 102, 229),
    (51, 102, 204),
    (127, 102, 76),
    (87, 166, 78),
    (204, 76, 76),
    (17, 17, 17)
]

color_codes = [1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384, 32768]

target_tree = KDTree(target_colors)

title = "RuneLite"

window = gw.getWindowsWithTitle(title)[0]

currRgbMap = None

latest_monitor = []#could do a current_monitor based on last request and just send changes if needed

def capture(window_title):
    screenshot = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))
    return screenshot


def stretch_img(img, scale):
    img_width = img.size[0]
    #new_height = int(img.size[1]*scale)
    stretched = img.resize((width, height))
    return stretched

def kd_closest_color(pix):
    _, idx = target_tree.query(pix)
    return idx

def process_pixel(args):
    y, x = args
    color = color_codes[kd_closest_color(currRgbMap[(y*width)+x])]
    return y, x, color

def find_closest_match_par():
    total_map = [[None for _ in range(width)] for _ in range(height)]
    pool = multiprocessing.Pool()
    
    args_list = [(y, x) for y in range(height) for x in range(width)]
    
    res = pool.map(process_pixel, args_list)
    for y, x, col in res:
        total_map[y][x] = col
    pool.close()
    pool.join()
    """
    for y in range(height):
        for x in range(width):
            proc = multiprocessing.Process(target=process_pixel, args=(y, x))
            proc.start()
            processes.append(proc)
    for proc in processes:
        proc.join()
    while not result_queue.empty():
        y, x, color = result_queue.get()
        total_map[y][x] = color
    """
    return total_map

def get_color_map(img):
    global currRgbMap
    currRgbMap = img.getdata()
    return find_closest_match_par()

def update_monitor():
    im = capture(title)
    img = stretch_img(im, height_scale)
    latest_monitor = get_color_map(img)



def background_update():
    while True:
        update_monitor()


print("starting 1")
start = time.perf_counter()
for i in range(5):
    update_monitor()
end = time.perf_counter()
print("total time: " + str((end-start)))
