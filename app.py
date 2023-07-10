import glob
import logging
import os
import re
import sys

import cv2
import dotenv
import requests

import cfg
import utils
from video_writer import VideoWriter


def extract(video_folder, frames_folder):
    result = []
    videos = glob.glob(os.path.join(video_folder, '*.mp4'))
    for no, video in enumerate(videos, 1):
        logging.debug(f'({no}/{len(videos)}): {video}')
        frames = utils.get_frames(video)
        found_bboxes = find_bboxes(
            frames,
            cfg.bbox_colors,
            out_folder=os.path.join(frames_folder, utils.get_only_filename(video))
        )
    result.append(found_bboxes)
    return result


def repair(folder):
    for image_path in glob.glob(os.path.join(folder, f'**\\*.png')):
        if 'M.png' not in image_path and 'R.png' not in image_path:  # not a mask or repaired
            logging.debug(f'Processing {image_path}')
            mask_path = utils.add_postfix_to_name(image_path, 'M')
            repair_image(image_path, mask_path)


def encode(video_folder, frames_folder, out_folder, fps=6):
    utils.create_empty_folder(out_folder)
    for video_path in glob.glob(os.path.join(video_folder, '*')):
        logging.debug(f'Video {video_path}')
        video_name = utils.get_only_filename(video_path)
        repaired_frames = get_repaired_frames(frames_folder, video_name)
        out_path = os.path.join(out_folder, f'{video_name}.mp4')
        orig_frames = utils.get_frames(video_path)
        logging.debug(f'frames: {len(orig_frames)}, repaired: {len(repaired_frames)}')
        writer = VideoWriter(out_path, fps)
        for i, frame in enumerate(orig_frames):
            if i in repaired_frames:
                writer.write(repaired_frames[i])
            else:
                writer.write(frame)
        writer.close()
        logging.debug(f'Written {out_path}')


def main():
    dotenv.load_dotenv()
    if sys.argv[1] == 'extract':
        extract(f'data\\{sys.argv[2]}', f'data\\{sys.argv[3]}')
    elif sys.argv[1] == 'repair':
        repair(f'data\\{sys.argv[2]}')
    elif sys.argv[1] == 'encode':
        encode(f'data\\{sys.argv[2]}', f'data\\{sys.argv[3]}', f'data\\{sys.argv[4]}')
        

def get_repaired_frames(frames_folder, video_name):
    result = {}
    frames_wildcard = os.path.join(frames_folder, video_name, 'F*M.png')
    for frame_path in glob.glob(frames_wildcard):
        filename = utils.get_only_filename(frame_path)
        frame_idx = int(re.findall(r'\d+', filename)[0])
        frame = cv2.imread(frame_path)
        result[frame_idx] = frame
    return result


def find_bboxes(frames, bbox_colors, out_folder, theshold=15):
    utils.create_empty_folder(out_folder)
    found = {i: [] for i in range(len(frames))}
    for frame_idx, frame in enumerate(frames):
        for class_, color in bbox_colors.items():
            count = utils.count_pixels(frame, color)
            if count > theshold:
                mask = utils.get_mask(frame, color)
                mask = utils.morph_open(mask)
                mask = utils.morph_dilate(mask, kernel_size=9, iterations=3)
                found[frame_idx].append((class_, mask))
                cv2.imwrite(os.path.join(out_folder, f'F{frame_idx}.png'),
                            frame)
                cv2.imwrite(os.path.join(out_folder, f'F{frame_idx}M.png'),
                            mask)
                logging.debug(f'frame #{frame_idx}: found \'{class_}\'')
    return found


def repair_image(image_path, mask_path):
    r = requests.post('https://clipdrop-api.co/cleanup/v1',
        files = {
            'image_file': ('image.png', open(image_path, 'rb'), 'image/png'),
            'mask_file': ('mask.png', open(mask_path, 'rb'), 'image/png')
        },
        headers = {'x-api-key': os.environ.get('API_TOKEN')}
    )
    if (r.ok):
        repaired_path = utils.add_postfix_to_name(image_path, 'R')
        file = open(repaired_path, 'wb')
        file.write(r.content)
        file.close()
    else:
        r.raise_for_status()


if __name__ == '__main__':
    main()
    