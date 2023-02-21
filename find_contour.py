import cv2
import os
import yaml
import argparse
from pathlib import Path
from numpy import random
import shutil
import numpy as np


def is_plausible(x,y,w,h):
    if abs(y-6) < 7 and abs(h-30) < 7 and abs(w-15) < 7:
        return True
    else:
        return False

def all_plausible_rectangles (x,y,w,h):
    all_rectangles = []
    for xx in range(x, x+w-9):
       all_rectangles.append((x,5,9,34))
    return all_rectangles

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
            found_intervals = []
            xs = None
            just_appended = True
            for file_name in sorted(os.listdir(input_dir)):
                xf = None

                full_file_name = os.path.join(input_dir, file_name)
                basename_filename = os.path.basename(file_name)
                last_part = os.path.basename(input_dir)
                basename_filename_no_ext = os.path.splitext(basename_filename)[0]
                times =  basename_filename_no_ext.split('_')[-3:]
                file_index = int(basename_filename_no_ext.split('_')[0])
                if times[0] == '00':
                    times_str = f'{times[1]}:{times[2]}'
                else:
                    times_str = f'{times[0]}:{times[1]}:{times[2]}'
                if just_appended:
                    first_time_str = times_str
                    just_appended = False
                print(f"========= Processing {full_file_name} ========== ")
                image = cv2.imread(full_file_name)
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                ret, thresh = cv2.threshold(image, 160, 255, cv2.THRESH_BINARY)

                contours, hierarchy = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                # Loop over contours and draw them on the original image
                for contour in contours:
                    approx = cv2.approxPolyDP(contour, 0.01 * cv2.arcLength(contour, True), True)
                    x, y, w, h = cv2.boundingRect(contour)

                    #plaus_rects = all_plausible_rectangles(x,y,w,h)
                    #for x,y,w,h in plaus_rects:
                    if  is_plausible(x,y,w,h):
                        #roi = image[y:y+h, x:x+w]
                        #cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        xf = x
                #output_file_name = os.path.join(contours_imgdir, file_name)
                if xf != None:
                    print(f"{file_index} __ {times_str}-> {xf}")
                    if xs == None or xf > xs + 10:
                        xs = xf
                        found_intervals.append(f'{first_time_str}-{times_str}')
                        just_appended = True
                #cv2.imwrite(output_file_name, thresh)
            print(found_intervals)
            for found_interval in found_intervals:
                print(found_interval)