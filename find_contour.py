import cv2
import os
import yaml
import argparse
from pathlib import Path
from numpy import random
import shutil
import numpy as np


def is_plausible(x,y,w,h):
    if abs(y-6) < 6 and abs(h-30) < 6 and abs(w-15) < 6:
        return True
    else:
        return False

def all_plausible_rectangles (x,y,w,h):
    all_rectangles = []
    for xx in range(x, x+w-9):
       all_rectangles.append((x,5,9,34))
    return all_rectangles


def retrieve_countrs_intervals(dir):

    rect_map = {}
    found_intervals = []
    xs = None
    for file_name in sorted(os.listdir(dir)):
        xf = None

        full_file_name = os.path.join(dir, file_name)
        basename_filename = os.path.basename(file_name)
        last_part = os.path.basename(dir)
        basename_filename_no_ext = os.path.splitext(basename_filename)[0]
        times = basename_filename_no_ext.split('_')[-3:]
        file_index = int(basename_filename_no_ext.split('_')[0])
        if times[0] == '00':
            times_str = f'{times[1]}:{times[2]}'
        else:
            times_str = f'{times[0]}:{times[1]}:{times[2]}'
        print(f"========= Processing {full_file_name} ========== ")
        image = cv2.imread(full_file_name)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = cv2.GaussianBlur(image, (5, 5), 0)

        ret, thresh = cv2.threshold(image, 160, 255, cv2.THRESH_BINARY)

        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        rect_map[file_name] = -1
        # Loop over contours and draw them on the original image
        for contour in contours:
            #approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)
            x, y, w, h = cv2.boundingRect(contour)

            if is_plausible(x, y, w, h):
                rect_map[file_name] = xf = x

        if xf != None:
            print(f"{file_index} __ {times_str}-> {xf}")
            if xs == None or xf > xs + 10:
                xs = xf
                just_appended = True
        # cv2.imwrite(output_file_name, thresh)
    return rect_map

def found_extremes_map(dmap):
    fmap, lmap = {}, {}
    last_seen_value, running_keys = -1, []
    for key, value in dmap.items():
        if value != -1:
            last_seen_value = value
            for run_key in running_keys:
                lmap[run_key] = value
            running_keys = []
        else:
            if last_seen_value != -1:
                running_keys.append(key)
                for run_key in running_keys:
                    fmap[run_key] = last_seen_value
    return fmap, lmap

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--config')  # option that takes a value
    args = parser.parse_args()


    if args.config == None:
        print("required argument --config <config>")
    else:
        with open(args.config, 'r') as confhandle:
            conf_info = yaml.safe_load(confhandle)
            source_folder = conf_info["source_folder"]
            dest_folder = conf_info["dest_folder"]
            input_dir = conf_info.get("input_dir", None)
            contours_imgdir = conf_info.get("contours_dir", None)
            os.makedirs(contours_imgdir, exist_ok=True)
            #for dir_name in sorted(os.listdir(input_dir)):

            rect_map = retrieve_countrs_intervals(input_dir)
            #print(found_intervals)

            #for found_interval in found_intervals:
            #    print(found_interval)
            print(rect_map)
            fmap, lmap = found_extremes_map(rect_map)
            print(fmap)
            print(lmap)
            mvalue = max(rect_map.values())
            for key, value in rect_map.items():
                if value == -1:
                    print(key, fmap.get(key,0), lmap.get(key,mvalue))