import cv2
import os
import yaml
import argparse
from pathlib import Path
def do_split(source, dest_folder):
    source_stem = Path(source).stem

    # get file path for desired video and where to save frames locally
    cap = cv2.VideoCapture(source)
    path_to_save = os.path.abspath(dest_folder)

    os.makedirs(dest_folder, exist_ok=True)
    if (cap.isOpened() == False):
        print('Cap is not open')

    finished = False
    totsec = 0
    # cap opened successfully
    while not finished:
        cap.set(cv2.CAP_PROP_POS_MSEC, totsec * 1000)
        hasFrames, image = cap.read()
        # capture each frame
        ret, frame = cap.read()
        if (hasFrames):

            # Save frame as a jpg file
            name = source_stem + '_' + str(totsec) + '.jpg'
            cv2.imwrite(os.path.join(path_to_save, name), frame)

            # keep track of how many images you end up with
            totsec += 1

        else:
            break

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
            source = conf_info["source"]
            dest_folder = conf_info["dest_folder"]
            do_split(source, dest_folder)