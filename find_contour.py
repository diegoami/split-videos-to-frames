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
    lx, li = -1, -1
    times_strs = []
    first_start = False
    first_scene = False
    keys = sorted(rect_map.keys())
    first_index, last_index = 0, len(keys)-1
    for index, key in enumerate(keys):
        xx = rect_map[key]
        file_name = key

        basename_filename = os.path.basename(file_name)
        basename_filename_no_ext = os.path.splitext(basename_filename)[0]
        times = basename_filename_no_ext.split('_')[-3:]

        if times[0] == '00':
            times_str = f'{times[1]}:{times[2]}'
        else:
            times_str = f'{times[0]}:{times[1]}:{times[2]}'
        if index != first_index and index != last_index and xx == -1:
            continue
        if lx == -1 or xx > lx + (index - li ) / 4 + 1  or not first_start:
            if not first_start:
                first_start = True

            file_index = int(basename_filename_no_ext.split('_')[0])


            print(times_str, xx, lx)

            times_strs.append(times_str)
            if xx != -1:
                lx = xx
                li = index
    times_strs.append(times_str)
    return times_strs

def retrieve_countrs_intervals(dir, line_rect):

    if not line_rect:
        line_rect = {"YY" : 1, "HH": 10, "WW" : 3}

    YY, HH, WW = line_rect["YY"], line_rect["HH"], line_rect["WW"]
    rect_map = {}

    found_first_line, found_last_line = False, False
    lx = 0
    for image_index, file_name in enumerate(sorted(os.listdir(dir))):
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
        #print(f"========= Processing {full_file_name} ========== ")
        image = cv2.imread(full_file_name)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = cv2.GaussianBlur(image, (5, 5), 0)

        ret, thresh = cv2.threshold(image, 160, 255, cv2.THRESH_BINARY)

        contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        rect_map[file_name] = -1
        # Loop over contours and draw them on the original image
        vcs = []
        for contour in contours:
            #approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)
            x, y, w, h = cv2.boundingRect(contour)
            if x > 100 and not found_first_line:
                continue
            #(x1,y1,w1,h1), (x2,y2,w2,h2) = get_rects_to_checks(contour)
            (x1,y1,w1,h1), (x2,y2,w2,h2), (x3,y3,w3,h3), (x4,y4,w4,h4) = (x,YY,WW,HH), (x+w-WW,YY,WW,HH), (x+w-WW//2,YY,WW,HH), (x+WW//2, YY, WW, HH)

            #if is_plausible(x, y, w, h):
            #    rect_map[file_name] = xf = x
            rimg1, rimg2, rimg3, rimg4 = image[y1:y1+h1, x1:x1+w1], image[y2:y2+h2, x2:x2+w2], image[y3:y3+h3, x3:x3+w3], image[y4:y4+h4, x4:x4+w4]

            if np.mean(rimg1) > 140 and x1 >= lx:
                vcs.append((x1, np.mean(rimg1)))
            elif np.mean(rimg2) > 140 and x2 >= lx:
                vcs.append((x2, np.mean(rimg2)))
            elif np.mean(rimg3) > 140 and x3 >= lx:
                vcs.append((x3, np.mean(rimg3)))
            elif np.mean(rimg4) > 140 and x4 >= lx:
                vcs.append((x4, np.mean(rimg4)))

        vcss = sorted(vcs, key=lambda x: x[1], reverse=True)
        print(f"Contours at {image_index}: {vcss}")
        if vcss:
            lx = vcss[0][0]
            found_first_line = True
            rect_map[file_name] = lx
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


def save_intervals(input_dir, intervals_dir, line_rect):
    rect_map = retrieve_countrs_intervals(input_dir, line_rect)
    # print(found_intervals)
    # print(rect_map)
    input_list = process_rect_map(rect_map)
    output_list = [f"{input_list[i]}-{input_list[i + 1]}: XXXXXXXX\n" for i in range(len(input_list) - 1)]
    os.makedirs(intervals_dir, exist_ok=True)
    intervals_file = os.path.join(intervals_dir, 'intervals.txt')
    with open(intervals_file, 'w') as f:
        for item in output_list:
            print(item)
            f.write(item)


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
            line_rect = conf_info.get("line_rect", None)
#            contours_imgdir = conf_info.get("contours_dir", None)
            intervals_dir = conf_info.get("intervals_dir", None)

 #           os.makedirs(contours_imgdir, exist_ok=True)
            for dir_name in sorted(os.listdir(input_dir), key=lambda x: int(x.split('_')[0])):
                input_dir_loop = os.path.join(input_dir, dir_name)
                intervals_dir_loop = os.path.join(intervals_dir, dir_name)

                save_intervals(input_dir_loop, intervals_dir_loop, line_rect)
                break