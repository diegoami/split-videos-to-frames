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

def do_split(video_source, video_dest_folder, conf_info):
    """
    This function do_split is used to split a video source into frames and save those frames as image files in a specified destination folder. The function takes in three arguments: video_source which is the path to the video file, video_dest_folder which is the folder to save the images in, and conf_info which is a dictionary that contains configuration information such as the desired frame size, whether to convert the images to grayscale, and how many frames to keep.
    The function first sets default values for the width, height, resize factor, probability of capturing a frame, grayscale flag, clip rect, and how many frames to keep using the get method of the conf_info dictionary. Then, the function creates a folder at the specified destination, opens the video source using OpenCV's cv2.VideoCapture method, and splits the video into frames by looping through the video and saving a frame every second. The frame is saved as an image file in the destination folder with the name formatted as the video source's stem plus the hour, minute, and second of the frame.
    The function also implements a probability calculation to determine whether a frame should be saved or not based on the current time in the video and the duration of the video. If the probability calculation passes, the frame is processed by resizing and converting it to grayscale if specified in the configuration information, and then saved to the destination folder.
    The function returns the first how_many and last how_many frames.
    """

    width = conf_info.get("width", None)
    height = conf_info.get("height", None)
    resize_factor = conf_info.get("resize_factor", 1)

    probability = conf_info.get("probability", 1)
    grayscale = conf_info.get("grayscale", False)
    clip_rect = conf_info.get("cliprect", None)
    how_many = conf_info.get("how_many", 1)

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
    first_imgs, last_imgs = None, None
    all_imgs = []
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
                if clip_rect:
                    new_image = image[clip_rect["top"]:clip_rect["bottom"], clip_rect["left"]:clip_rect["right"]]
                    image = new_image
                if grayscale:
                    image = cv2.cvtColor(image , cv2.COLOR_BGR2GRAY)

                if resize_factor:
                    new_width = int(image.shape[1] * resize_factor)
                    new_height = int(image.shape[0] * resize_factor)
                    print(image.shape)
                    dim = (new_width, new_height)
                    new_image = cv2.resize(image, dim)
                    image = new_image
                full_path = os.path.join(path_to_save, name)
                print(f"Saving image to {full_path}")

                cv2.imwrite(full_path, image)
                all_imgs.append(full_path)
                # keep track of how many images you end up with
            else:
                finished = True
        totsec += 1

    # release capture
    cap.release()
    print('done')
    return all_imgs[:how_many] + all_imgs[-how_many:]

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
            first_last_imgdir = conf_info.get("first_last_imgdir", None)


            for video_source in os.listdir(source_folder):
                dest_folder_ending = Path(video_source).stem
                video_dest_folder = os.path.join(dest_folder, dest_folder_ending)
                video_source_full_path = os.path.join(source_folder, video_source)
                imgs  = do_split(video_source_full_path, video_dest_folder, conf_info)
                if first_last_imgdir:
                    os.makedirs(first_last_imgdir, exist_ok=True)
                    for img in imgs:
                        shutil.copy(img, first_last_imgdir)

