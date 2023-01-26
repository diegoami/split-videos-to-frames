import os
import numpy as np
import argparse
import cv2

def main():

    # parse all args
    parser = argparse.ArgumentParser()
    parser.add_argument('source', type=str, help='Path to source video')
    parser.add_argument('dest_folder', type=str, help='Path to destination folder')
    args = parser.parse_args()

    # get file path for desired video and where to save frames locally
    cap = cv2.VideoCapture(args.source)
    path_to_save = os.path.abspath(args.dest_folder)
    
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
    main()
