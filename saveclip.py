
from concurrent.futures import ThreadPoolExecutor
import io
import os.path as path
import cv2
import time
from datetime import datetime
from collections import deque
from copy import copy

class ClipRecorder:
	def __init__(self, name, executor, clip_dir, resolution=(640, 480), framerate=16):
		# initialize the camera and stream
		self.name = name

		# dir to save clips
		self.clip_dir = clip_dir

		self.resolution = resolution
		self.framerate = framerate

		self.frameBuffer = deque(maxlen=80)
		self.recordingFrameBuffer = deque(maxlen=160)
		self.framesSinceLastDetection = 0

		# executor for saving clip without blocking current thread
		self.executor = executor

	def clip_file_name(self, frame_count):
		ts = datetime.now().strftime("%Y.%m.%dT%H.%M.%S")
		return '{}_{}_{:03d}.avi'.format(self.name, ts, frame_count)

	def save_clip(self, file_name, frameBufferToSave):
		s = time.time()
		clip_path = path.join(self.clip_dir, file_name)
		clip_out = cv2.VideoWriter(clip_path, cv2.VideoWriter_fourcc('M','J','P','G'), self.framerate, self.resolution)
		while len(frameBufferToSave) > 0:
			clip_out.write(frameBufferToSave.popleft())

		clip_out.release()
		print('saved video clip {} in {}s'.format(file_name, time.time() - s))

	def add_frame(self, frame, objects_detected):
		is_recording = len(self.recordingFrameBuffer) > 0 or self.framesSinceLastDetection < 80

		if is_recording:
			self.recordingFrameBuffer.append(frame)

			if objects_detected:
				self.framesSinceLastDetection = 0
			else:
				self.framesSinceLastDetection += 1

			if len(self.recordingFrameBuffer) == 160 or self.framesSinceLastDetection == 80:
				# save video clip
				file_name = self.clip_file_name(len(self.recordingFrameBuffer))
				frameBufferToSave = copy(self.recordingFrameBuffer)
				self.recordingFrameBuffer.clear()

				print('saving clip {}'.format(file_name))
				self.executor.submit(self.save_clip, file_name, frameBufferToSave)

		else:
			# add the new frame to corresponding frame buffer
			self.frameBuffer.append(frame)

			if objects_detected:
				print('objects_detected in {}'.format(self.name))
				self.recordingFrameBuffer.extend(self.frameBuffer)
				self.frameBuffer.clear()
				self.framesSinceLastDetection = 0
