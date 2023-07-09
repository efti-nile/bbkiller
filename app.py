import cv2
import requests
import glob
import os
import utils
import logging
import requests
import re

import cfg


def find_bboxes(frames, bbox_colors, out_folder, theshold=15):
    utils.create_empty_folder(out_folder)
    found = {i: [] for i in range(len(frames))}
    for frame_idx, frame in enumerate(frames):
        for class_, color in bbox_colors.items():
            count = utils.count_pixels(frame, color)
            if count > theshold:
                mask = utils.morph_open(utils.get_mask(frame, color))
                found[frame_idx].append((class_, mask))
                cv2.imwrite(os.path.join(out_folder, f'F{frame_idx}.png'),
                            frame)
                cv2.imwrite(os.path.join(out_folder, f'F{frame_idx}M.png'),
                            mask)
                logging.debug(f'frame #{frame_idx}: found \'{class_}\'')
    return found


def process(in_folder, out_folder, video_format='*.mp4'):
    result = []
    videos = glob.glob(os.path.join(in_folder, video_format))
    for no, video in enumerate(videos, 1):
        logging.debug(f'({no}/{len(videos)}): {video}')
        frames = utils.get_frames(video)
        found_bboxes = find_bboxes(
            frames,
            cfg.bbox_colors,
            out_folder=os.path.join(out_folder, utils.get_only_filename(video))
        )
    result.append(found_bboxes)
    return result


def repair_image(image_path, mask_path):
    r = requests.post('https://clipdrop-api.co/cleanup/v1',
        files = {
            'image_file': ('image.jpg', open(image_path, 'rb'), 'image/jpeg'),
            'mask_file': ('mask.png', open(mask_path, 'rb'), 'image/png')
        },
        headers = {'x-api-key': '258b656190872bc446da3edbdd9ad3aeef2ca5bafe5372e7197dc6aafb05b63a0ebae53b37fd3e93b4232ff6672848a9'}
    )
    if (r.ok):
        repaired_path = utils.add_postfix_to_name(image_path, 'R')
        file = open(repaired_path, 'wb')
        file.write(r.content)
        file.close()
    else:
        r.raise_for_status()


def repair_image_folder(image_folder, image_format='png', mask_postfix='M'):
    for image_path in glob.glob(os.path.join(image_folder, f'**\\*.{image_format}')):
        if f'{mask_postfix}.{image_format}' not in image_path \
          and f'R.{image_format}' not in image_path:  # not a mask or repaired
            logging.debug(f'Processing \'{image_path}\'')
            mask_path = utils.add_postfix_to_name(image_path, mask_postfix)
            repair_image(image_path, mask_path)
        else:
            pass

def main():
    process('data\\top_l101',
            out_folder='data\\frames_l101')
    # repair_image_folder('data\\out')
    pass


if __name__ == '__main__':
    main()
    