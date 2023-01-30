import cv2
import os
import yaml
import argparse
from pathlib import Path
from numpy import random

def do_split(video_source, video_dest_folder, width, height, probability, grayscale):
    print(f"Splitting {video_source} to {video_dest_folder}")
    source_stem = Path(video_source).stem

    # get file path for desired video and where to save frames locally
    cap = cv2.VideoCapture(video_source)
    path_to_save = os.path.abspath(video_dest_folder)

    os.makedirs(video_dest_folder, exist_ok=True)
    if (cap.isOpened() == False):
        print('Cap is not open')

    finished = False
    totsec = 0
    # cap opened successfully
    while not finished:
        flag_img = random.rand()
        if flag_img < probability:
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
                reduced_image = cv2.resize(image, (width, height))
                if grayscale:
                    reduced_image = cv2.cvtColor(reduced_image, cv2.COLOR_BGR2GRAY)

                print(f"Saving image to {path_to_save}/{name}")

                cv2.imwrite(os.path.join(path_to_save, name), reduced_image)

                # keep track of how many images you end up with
            else:
                finished = True
        totsec += 1

    # release capture
    cap.release()
    print('done')


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
            width = conf_info["width"]
            height = conf_info["height"]
            probability = conf_info.get("probability", 1)
            grayscale = conf_info.get("grayscale", False)


            for video_source in os.listdir(source_folder):
                dest_folder_ending = Path(video_source).stem
                video_dest_folder = os.path.join(dest_folder, dest_folder_ending)
                video_source_full_path = os.path.join(source_folder, video_source)
                do_split(video_source_full_path, video_dest_folder, width, height, probability, grayscale)