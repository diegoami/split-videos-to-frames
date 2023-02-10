Video Frame Splitter
====================

This script is used to split a video source into frames and save those frames as image files in a specified destination folder.

Requirements
------------

-   Python 3.x
-   argparse
-   yaml
-   os
-   pathlib
-   shutil

Usage
-----

phpCopy code

`python video_frame_splitter -c <config_file.yml> `

### Arguments

-   `-c, --config`: Required argument. This option takes the path to the configuration file as a value.

### Configuration File

The configuration file is a YAML file that contains the following fields:

-   `source_folder`: The folder that contains the video source(s) that need to be split into frames.
-   `dest_folder`: The folder where the frames will be saved.
-   `first_last_imgdir`: *(optional)* The folder where the first and last frame of each video source will be saved.
-   `width`: (int) The desired width of the frames in pixels. If not specified, the width of the original frames will be used.
-   `height`: (int) The desired height of the frames in pixels. If not specified, the height of the original frames will be used.
-   `resize_factor`: (float) A factor to resize the frames by. The new width and height of the frames will be calculated by multiplying the original width and height by this factor.
-   `probability`: (float) The probability that a frame will be selected to be saved. The closer the time of the frame is to the beginning or end of the video, the higher this probability will be.
-   `grayscale`: (bool) Whether to convert the frames to grayscale or not. If set to `True`, the frames will be saved in grayscale, otherwise they will be saved in color.
-   `clip_rect`: (dict) A dictionary that contains the top, bottom, left, and right positions of the rectangle to clip from the original frames. If not specified, the entire frame will be used.
-   `how_many`: (int) The number of frames to save from the beginning and end of the video.

### Output

For each video source, the script creates a subfolder in the `dest_folder` with the name of the video source (without the extension). The frames of the video source are saved in the corresponding subfolder. If the `first_last_imgdir` is specified in the configuration file, the first and last frame of each video source will be copied to this folder.

Functionality
-------------

The script first parses the required `config` argument and opens the configuration file. It then reads the values of the fields `source_folder`, `dest_folder`, and `first_last_imgdir` from the configuration file.

Next, the script loops through all the video sources in the `source_folder` and calls the function `do_split` on each video source. The function `do_split` splits the video source into frames and saves those frames as image files in the specified `video_dest_folder` (which is a subfolder of the `dest_folder` with the name of the video source).

Finally, if `first_last_imgdir` is specified in the configuration file, the script creates the folder (if it doesn't already exist) and copies the first and last frame of each video source to this folder.