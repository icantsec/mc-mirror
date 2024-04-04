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


def stretch_img(img):
    stretched = img.resize((width, height))
    return stretched

def kd_closest_color(pix):
    _, idx = target_tree.query(pix)
    return idx


def find_closest_match_par():
    total_map = np.zeros((height, width), dtype=int)
    
    img_data = np.array(currRgbMap)
    img_data = img_data.reshape(height, width, 3)  # Reshape the 1D data to a 3D image array

    _, idx = target_tree.query(img_data.reshape(-1, 3))  # Flatten and query all pixels at once
    color_idx_map = np.array(color_codes)[idx]  # Convert color_codes to a NumPy array and index with idx
    
    total_map = color_idx_map.reshape(height, width)  # Reshape the 1D result to 2D total_map

    return total_map.tolist()  # Convert the NumPy array back to a regular Python list


def get_color_map(img):
    global currRgbMap
    currRgbMap = img.getdata()
    return find_closest_match_par()

def rle_img(data):
    enc = []
    for row in data:
        enc_row = []
        curr_val = row[0]
        count = 1
        for val in row[1:]:
            if val == curr_val:
                count += 1
            else:
                enc_row.append((curr_val, count))
                curr_val = val
                count = 1
        enc_row.append((curr_val, count))
        enc.append(enc_row)
    return enc

def update_monitor():
    im = capture(title)
    img = stretch_img(im)
    global latest_monitor
    latest_monitor = rle_img(get_color_map(img))
    


def background_update():
    update_monitor()
  

app = Flask(__name__)

@app.route('/getRS')
def getRS():
    global latest_monitor
    task_thread = threading.Thread(target=background_update)
    task_thread.daemon = True
    task_thread.start()
    return jsonify(latest_monitor)

@app.route('/post')
def useInput():
    inp = request.args.get('query').lower()
    inp = inp.replace(".20.", " ")
    if inp[0] == "m":
        if inp[1] == "c":
            if inp[2] == "l":
                pyautogui.click()
                return jsonify("did left-click")
            elif inp[2] == "r":
                pyautogui.click(button="right")
                return jsonify("did right-click")
        else:
            toMove = int(inp.split(" ")[1])
            direction = inp[1]
            xMove = 0
            yMove = 0
            if inp[1] == "u":
                yMove -= toMove
            elif inp[1] == "d":
                yMove += toMove
            elif inp[1] == "r":
                xMove += toMove
            elif inp[1] == "l":
                xMove -= toMove
            else:
                return jsonify("invalid command")
            pyautogui.moveRel(xMove, yMove)
            return jsonify("moved mouse relative: (" + str(xMove) + ", " + str(yMove) + ")")
    elif "ctrl" in inp and inp.index("ctrl") == 0:
        pyautogui.typewrite(["ctrlleft"], inp.split("ctrl")[1]) 
        return jsonify("did ctrl+" + inp.split("ctrl")[1])
    elif inp == "enter":
        pyautogui.typewrite(["enter"])
        return jsonify("sent enter")
    else:
        pyautogui.typewrite(inp)
        return jsonify("typed " + inp)

if __name__ == '__main__':
    task_thread = threading.Thread(target=background_update)
    task_thread.daemon = True
    task_thread.start()
    app.run()


"""
if __name__ == "__main__":
    print("starting 1")
    start = time.perf_counter()
    print("start: " + str(start))
    for i in range(1):
        update_monitor()
    end = time.perf_counter()
    print("total time: " + str((end-start)))
"""