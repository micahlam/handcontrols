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