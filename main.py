# https://github.com/brycedrennan/imaginairy-normal-map
# https://github.com/artiprocher/sd-webui-fastblend

# need to add deflicker pass

from PIL import Image
import os
import cv2
from cv2 import VideoCapture
from pathlib import Path
from imaginairy_normal_map.model import create_normal_map_pil_img
from tqdm import tqdm
from FastBlend.api import smooth_video, interpolate_video

def create_and_save_normal_map(image, filename):
	normal = create_normal_map_pil_img(image)
	normal.save(filename)

def clean_directory(directory):
	try:
		for root, dirs, files in os.walk(directory, topdown=False):
			for file in files:
				file_path = os.path.join(root, file)
				if os.path.isfile(file_path):
					os.remove(file_path)
	except:
		raise Exception('Unable to clean frames directory.')

def video_to_frames(video_path, output_dir, prefix='frame'):
	Path(output_dir).mkdir(parents=True, exist_ok=True)
	if len(os.listdir(output_dir)) > 0:
		cont = str(input(f'\nFound Existing Frames. "y" to overwrite: '))
		if cont == 'y' or cont == 'Y' or cont == 'yes' or cont == 'YES':
			print(f'\nCleaning frames directory...')
			clean_directory('frames')
		else:
			print(f'\nSkipping frame extraction.')
			return

	video = VideoCapture(video_path)
	if not video.isOpened():
		raise Exception(f'Error: could not open video file {video_path}')

	frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
	width = int(video.get(cv2.CAP_PROP_FRAME_WIDTH))
	height = int(video.get(cv2.CAP_PROP_FRAME_HEIGHT))
	fps = video.get(cv2.CAP_PROP_FPS)

	frame_count = 0 

	while True:
		success, frame = video.read()

		if not success:
			break

		output_file = os.path.join(output_dir, f'{prefix}_{frame_count:06d}.png')
		cv2.imwrite(output_file, frame)
		frame_count += 1

		if frame_count % 100 == 0:
			progress = (frame_count / frames) * 100
			print(f'Progress: {progress:.1f}% ({frame_count}/{frames} frames)')

	video.release()
	return frame_count


if __name__ == '__main__':
	
	input_files = []

	prompt = str(input(f'\nConver Video File to Frames?: '))
	if prompt == 'y' or prompt == 'Y':
		print('\nExtracting frames...')
		video_to_frames('video.mp4', 'frames', prefix='frame')

	print("\nGenerating normal maps.")
	Path('normals').mkdir(parents=True, exist_ok=True)
	if len(os.listdir('normals')) > 0:
		cont = str(input(f'\nFound Existing Normals. "y" to overwrite: '))
		if cont == 'y' or cont == 'Y' or cont == 'yes' or cont == 'YES':
			print(f'\nCleaning normals directory...')
			clean_directory('normals')
		else:
			print(f'\nContinuing with populated output folder...')

	for root, dirs, files in os.walk('frames/', topdown=False):
		for idx, file in enumerate(tqdm(files)):
			print(f'\n{idx}/{len(files)})')
			image = Image.open(os.path.join(root, file))
			create_and_save_normal_map(image, f'normals/normal_{file}')

	use_deflicker = str(input(f'\nFinished processing, begin Deflicker: '))
	if use_deflicker == 'y' or use_deflicker == 'Y':
		smooth_video(video_guide = None, video_guide_folder = 'normals', video_style = None, video_style_folder = None, mode = "Fast", window_size = 15, batch_size = 16, tracking_window_size = 0, output_path = "deflicker", fps = None, minimum_patch_size = 5,	num_iter = 5, guide_weight = 10.0, initialize = "identity")
		#interpolate_video(frames_path = "normals", keyframes_path = "output", output_path = "deflicker", fps = None, batch_size = 16, tracking_window_size = 1, minimum_patch_size = 15, num_iter = 5, guide_weight = 10.0, initialize = "identity")