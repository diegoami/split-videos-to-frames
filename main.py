import cv2
import os
import argparse
from pathlib import Path

def do_split(source, dest_folder):

        # get file path for desired video and where to save frames locally
        cap = cv2.VideoCapture(source)
        path_to_save = os.path.abspath(dest_folder)

        current_frame = 1

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
                name = 'frame' + str(totsec) + '.jpg'
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

    # parse all args

        source = args.config["source"]
        dest_folder = args.config["dest_folder"]
        do_split(source, dest_folder)