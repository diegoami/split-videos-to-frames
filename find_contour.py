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


def get_rects_to_checks(vertices):
    left_most, right_most = 0, 3000
    for vertex in vertices:
        x, y = vertex[0]
        if x < left_most:
            left_most = x
        if x > right_most:
            right_most = x
    rects_to_check = [(left_most,7,8,26),(right_most-8,7,8,26)]
    return rects_to_check

def process_rect_map(rect_map):
    lx = 0
    times_strs = []
    first_start = False
    first_scene = False
    keys = sorted(rect_map.keys())
    first_index, last_index = 0, len(keys)-1
    for index, key in enumerate(keys):
        xx = rect_map[key]
        if index != first_index and index != last_index and xx == -1:
            continue
        if lx == 0 or xx > lx+ 5 or not first_start:
            file_name = key
            if not first_start:
                first_start = True

            basename_filename = os.path.basename(file_name)
            basename_filename_no_ext = os.path.splitext(basename_filename)[0]
            times = basename_filename_no_ext.split('_')[-3:]
            file_index = int(basename_filename_no_ext.split('_')[0])

            if times[0] == '00':
                times_str = f'{times[1]}:{times[2]}'
            else:
                times_str = f'{times[0]}:{times[1]}:{times[2]}'
            print(times_str, xx, lx)

            times_strs.append(times_str)
        if xx != -1:
            lx = xx
    return times_strs

def retrieve_countrs_intervals(dir):

    rect_map = {}

    found_first_line, found_last_line = False, False
    lx = 0
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
            if x > 10 and not found_first_line:
                continue
            #(x1,y1,w1,h1), (x2,y2,w2,h2) = get_rects_to_checks(contour)
            (x1,y1,w1,h1), (x2,y2,w2,h2) = (x,7,8,26), (x+w-8,7,8,26)

            #if is_plausible(x, y, w, h):
            #    rect_map[file_name] = xf = x
            rimg1, rimg2 = image[y1:y1+h1, x1:x1+w1], image[y2:y2+h2, x2:x2+w2]
            if np.mean(rimg1) > 128 and x1 >= lx:
                rect_map[file_name] = x1
                lx = x1
                found_first_line = True

            elif np.mean(rimg2) > 128  and x2 >= lx:
                rect_map[file_name] = x2
                lx = x2
                found_first_line = True

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
            #fmap, lmap = found_extremes_map(rect_map)
            #print(fmap)
            #print(lmap)
            #mvalue = max(rect_map.values())
            #for key, value in rect_map.items():
            #    if value == -1:
            #        print(key, fmap.get(key,0), lmap.get(key,mvalue))
            input_list = process_rect_map(rect_map)
            output_list = [f"{input_list[i]}-{input_list[i+1]}" for i in range(len(input_list)-1)]

            print(output_list)
            for item in output_list:
                print(item)