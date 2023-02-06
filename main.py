import cv2
import os
import yaml
import argparse
from pathlib import Path
from numpy import random
from math import atan
import shutil


def get_length(cap):
    fps = cap.get(cv2.CAP_PROP_FPS)  # OpenCV v2.x used "CV_CAP_PROP_FPS"
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / fps
    return duration

def get_distance_from_extremes(current, duration):
    return min(current, duration-current)*2/duration
def do_split(video_source, video_dest_folder, width, height, probability, grayscale, clip_rect):
    print(f"Splitting {video_source} to {video_dest_folder}")
    source_stem = Path(video_source).stem

    # get file path for desired video and where to save frames locally
    cap = cv2.VideoCapture(video_source)
    duration = get_length(cap)
    path_to_save = os.path.abspath(video_dest_folder)

    os.makedirs(video_dest_folder, exist_ok=True)
    if (cap.isOpened() == False):
        print('Cap is not open')

    finished = False
    totsec = 0
    # cap opened successfully
    first_img, last_img = None, None

    while not finished:

        flag_img = random.rand()
        prob_mult = get_distance_from_extremes(totsec, duration)
        inv_log_func = 1 - atan(prob_mult)
        real_prob = probability * inv_log_func
        if flag_img < real_prob:
            print(f"{flag_img:.4f} < {real_prob:.4f}")
            cap.set(cv2.CAP_PROP_POS_MSEC, totsec * 1000)

            hasFrames, image = cap.read()
            # capture each frame
            if (hasFrames):

                hours = totsec // 3600
                minutes = (totsec - hours * 3600) // 60
                seconds = totsec - hours * 3600 - minutes * 60

                frame_str = f'{hours:02}_{minutes:02}_{seconds:02}'
                # Save frame as a jpg file
                name = source_stem + '_' + frame_str + '.jpg'
                if width and height:
                    image = cv2.resize(image, (width, height))
                if grayscale:
                    image = cv2.cvtColor(image , cv2.COLOR_BGR2GRAY)
                if clip_rect:
                    image = image[clip_rect["top"]:clip_rect["bottom"], clip_rect["left"]:clip_rect["right"],   ]

                full_path = os.path.join(path_to_save, name)
                print(f"Saving image to {full_path}")

                cv2.imwrite(full_path, image)
                if first_img is None:
                    first_img = full_path
                last_img = full_path
                # keep track of how many images you end up with
            else:
                finished = True
        totsec += 1

    # release capture
    cap.release()
    print('done')
    return first_img, last_img

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
            width = conf_info.get("width", None)
            height = conf_info.get("height", None)
            probability = conf_info.get("probability", 1)
            grayscale = conf_info.get("grayscale", False)
            cliprect = conf_info.get("cliprect", None)
            first_last_imgdir = conf_info.get("first_last_imgdir", None)

            for video_source in os.listdir(source_folder):
                dest_folder_ending = Path(video_source).stem
                video_dest_folder = os.path.join(dest_folder, dest_folder_ending)
                video_source_full_path = os.path.join(source_folder, video_source)
                first_img, last_img = do_split(video_source_full_path, video_dest_folder, width, height, probability, grayscale, cliprect)
                if first_last_imgdir:
                    os.makedirs(first_last_imgdir, exist_ok=True)
                    shutil.copy(first_img, first_last_imgdir)
                    shutil.copy(last_img, first_last_imgdir)

