# Micah Lam
import math
import platform
import subprocess
import time

import cv2
import mediapipe as mp


def change_volume(amount):
	"""Adjust system volume by a small step."""
	system = platform.system()
	if system == "Darwin":
		sign = "+" if amount > 0 else "-"
		subprocess.run(
			["osascript", "-e", f"set volume output volume ((output volume of (get volume settings)) {sign} 5)"],
			check=False,
		)
	elif system == "Windows":
		import ctypes

		key = 0xAF if amount > 0 else 0xAE
		ctypes.windll.user32.keybd_event(key, 0, 0, 0)
		ctypes.windll.user32.keybd_event(key, 0, 2, 0)
	else:
		step = "5%+" if amount > 0 else "5%-"
		subprocess.run(["amixer", "-q", "sset", "Master", step], check=False)


hands_module = mp.solutions.hands
draw = mp.solutions.drawing_utils
camera = cv2.VideoCapture(0)
last_change = 0.0

with hands_module.Hands(
	max_num_hands=1,
	min_detection_confidence=0.7,
	min_tracking_confidence=0.7,
) as hands:
	while camera.isOpened():
		success, frame = camera.read()
		if not success:
			break

		frame = cv2.flip(frame, 1)
		result = hands.process(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))