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

		if result.multi_hand_landmarks:
			hand = result.multi_hand_landmarks[0]
			thumb = hand.landmark[hands_module.HandLandmark.THUMB_TIP]
			index = hand.landmark[hands_module.HandLandmark.INDEX_FINGER_TIP]
			distance = math.hypot(thumb.x - index.x, thumb.y - index.y)

			# Pinched fingers lower volume; separated fingers raise it.
			direction = 1 if distance > 0.22 else -1 if distance < 0.12 else 0
			now = time.monotonic()
			if direction and now - last_change >= 0.2:
				change_volume(direction)
				last_change = now

			cv2.line(
				frame,
				(int(thumb.x * frame.shape[1]), int(thumb.y * frame.shape[0])),
				(int(index.x * frame.shape[1]), int(index.y * frame.shape[0])),
				(0, 255, 0),
				3,
			)
			cv2.putText(frame, f"Distance: {distance:.2f}", (20, 40),
						cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
			draw.draw_landmarks(frame, hand, hands_module.HAND_CONNECTIONS)

		cv2.imshow("Hand Volume Control - press Q to quit", frame)
		if cv2.waitKey(1) & 0xFF == ord("q"):
			break

camera.release()
cv2.destroyAllWindows()