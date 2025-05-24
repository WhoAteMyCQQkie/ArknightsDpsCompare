import numpy as np
import os

from manim import *

from JsonReader import StageData


class StageAnimator(Scene):

	def construct(self):
		square_size = 1
		squares = []
		stage_data = StageData()
		text_to_display = os.environ.get("MY_TEXT", "Default text")
		# === Create Grid ===
		testinput = [11, 7, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 3, 3, 3, 5, 5, 5, 5, 5, 6, 1, 2, 3, 5, 5, 5, 3, 3, 3, 3, 2, 2, 0, 5, 5, 2, 5, 5, 5, 5, 5, 6, 1, 2, 3, 5, 5, 5, 3, 3, 3, 3, 2, 2, 2, 3, 3, 3, 5, 5, 5, 5, 5, 6, 1, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
		testinput = stage_data.get_stage_layout(text_to_display)

		counter = 2
		for row in range(testinput[1]):
			row_squares = []
			for col in range(testinput[0]):
				square = Square(side_length=square_size)
				square.move_to(
					RIGHT * (col - testinput[0] // 2) * square_size +
					DOWN * (testinput[1] // 2 - row) * square_size
				)
				square.set_fill(WHITE, opacity=0.3)
				if testinput[counter] == 0: square.set_fill(BLUE, opacity=1.0)
				elif testinput[counter] == 1: square.set_fill(RED, opacity=1.0)
				elif testinput[counter] == 2: square.set_fill(BLACK, opacity=0.8)
				elif testinput[counter] == 3: square.set_fill(WHITE, opacity=0.8)
				elif testinput[counter] == 4: square.set_fill(WHITE, opacity=0.7)
				elif testinput[counter] == 5: square.set_fill(WHITE, opacity=0.4)
				elif testinput[counter] == 6: square.set_fill(WHITE, opacity=0.3)
				elif testinput[counter] == 7: square.set_fill(GREEN, opacity=0.8)
				counter += 1
				square.set_stroke(BLACK, width=1)
				self.add(square)
				row_squares.append(square)
			squares.append(row_squares)

		# === Define Entries ===
		entry_list = [
			{
				"image": "enemy_pic.png",
				"path": [(5,10), (5,4), (4, 4), (4, 2), (3, 2), (3,0)],
				"start_time": 1,
				"speed": 1.0,  # squares per second
				"idle_points": [],  # index in path
				"idle_durations": [],
			},
			{
				"image": "enemy_pic.png",
				"path": [(0, 0), (1, 1), (2, 2), (3, 2), (4, 2)],
				"start_time": 3,
				"speed": 0.8,
				"idle_points": [1,2],
				"idle_durations": [4.1, 0.4],
			},
		]
		#entry_list = [{'start_time': 6.0, 'speed': 1.0, 'path': [(5, 10), (5, 4), (4, 4), (4, 2), (3, 2), (3, 0)], 'idle_points': [], 'idle_durations': [], 'image': 'enemy_1007_slime_2'}, {'start_time': 12.0, 'speed': 1.0, 'path': [(1, 10), (1, 4), (2, 4), (2, 2), (3, 2), (3, 0)], 'idle_points': [], 'idle_durations': [], 'image': 'enemy_1007_slime_2'}, {'start_time': 13.0, 'speed': 1.0, 'path': [(1, 10), (1, 4), (2, 4), (2, 2), (3, 2), (3, 0)], 'idle_points': [], 'idle_durations': [], 'image': 'enemy_1007_slime_2'}, {'start_time': 18.0, 'speed': 1.0, 'path': [(3, 10), (3, 4), (4, 4), (4, 2), (3, 2), (3, 0)], 'idle_points': [], 'idle_durations': [], 'image': 'enemy_1007_slime_2'}, {'start_time': 23.0, 'speed': 1.0, 'path': [(3, 10), (3, 4), (4, 4), (4, 2), (3, 2), (3, 0)], 'idle_points': [], 'idle_durations': [], 'image': 'enemy_1007_slime_2'}, {'start_time': 19.0, 'speed': 1.0, 'path': [(3, 10), (3, 4), (2, 4), (2, 2), (3, 2), (3, 0)], 'idle_points': [], 'idle_durations': [], 'image': 'enemy_1007_slime_2'}, {'start_time': 24.0, 'speed': 1.0, 'path': [(3, 10), (3, 4), (2, 4), (2, 2), (3, 2), (3, 0)], 'idle_points': [], 'idle_durations': [], 'image': 'enemy_1007_slime_2'}, {'start_time': 11.0, 'speed': 1.1, 'path': [(5, 10), (5, 4), (4, 4), (4, 2), (3, 2), (3, 0)], 'idle_points': [], 'idle_durations': [], 'image': 'enemy_1027_mob'}, {'start_time': 18.0, 'speed': 1.1, 'path': [(5, 10), (5, 4), (4, 4), (4, 2), (3, 2), (3, 0)], 'idle_points': [], 'idle_durations': [], 'image': 'enemy_1027_mob'}, {'start_time': 14.0, 'speed': 1.1, 'path': [(1, 10), (1, 4), (2, 4), (2, 2), (3, 2), (3, 0)], 'idle_points': [], 'idle_durations': [], 'image': 'enemy_1002_nsabr'}, {'start_time': 21.0, 'speed': 1.1, 'path': [(1, 10), (1, 4), (2, 4), (2, 2), (3, 2), (3, 0)], 'idle_points': [], 'idle_durations': [], 'image': 'enemy_1002_nsabr'}, {'start_time': 16.0, 'speed': 1.0, 'path': [(5, 10), (5, 4), (4, 4), (4, 2), (3, 2), (3, 0)], 'idle_points': [], 'idle_durations': [], 'image': 'enemy_1028_mocock'}, {'start_time': 16.0, 'speed': 1.0, 'path': [(1, 10), (1, 4), (2, 4), (2, 2), (3, 2), (3, 0)], 'idle_points': [], 'idle_durations': [], 'image': 'enemy_1028_mocock'}, {'start_time': 19.0, 'speed': 1.1, 'path': [(3, 10), (3, 4), (4, 4), (4, 2), (3, 2), (3, 0)], 'idle_points': [], 'idle_durations': [], 'image': 'enemy_1002_nsabr'}, {'start_time': 22.0, 'speed': 1.1, 'path': [(3, 10), (3, 4), (2, 4), (2, 2), (3, 2), (3, 0)], 'idle_points': [], 'idle_durations': [], 'image': 'enemy_1002_nsabr'}, {'start_time': 22.0, 'speed': 1.1, 'path': [(5, 10), (5, 4), (4, 4), (4, 2), (3, 2), (3, 0)], 'idle_points': [], 'idle_durations': [], 'image': 'enemy_1027_mob'}, {'start_time': 22.0, 'speed': 1.1, 'path': [(1, 10), (1, 4), (2, 4), (2, 2), (3, 2), (3, 0)], 'idle_points': [], 'idle_durations': [], 'image': 'enemy_1027_mob'}, {'start_time': 28.0, 'speed': 1.1, 'path': [(5, 10), (5, 4), (4, 4), (4, 2), (3, 2), (3, 0)], 'idle_points': [], 'idle_durations': [], 'image': 'enemy_1002_nsabr'}, {'start_time': 28.0, 'speed': 1.0, 'path': [(1, 10), (1, 4), (2, 4), (2, 2), (3, 2), (3, 0)], 'idle_points': [], 'idle_durations': [], 'image': 'enemy_1029_shdsbr'}, {'start_time': 32.0, 'speed': 1.0, 'path': [(3, 10), (3, 4), (4, 4), (4, 2), (3, 2), (3, 0)], 'idle_points': [], 'idle_durations': [], 'image': 'enemy_1007_slime_2'}, {'start_time': 34.0, 'speed': 1.0, 'path': [(3, 10), (3, 4), (4, 4), (4, 2), (3, 2), (3, 0)], 'idle_points': [], 'idle_durations': [], 'image': 'enemy_1007_slime_2'}, {'start_time': 36.0, 'speed': 1.0, 'path': [(3, 10), (3, 4), (4, 4), (4, 2), (3, 2), (3, 0)], 'idle_points': [], 'idle_durations': [], 'image': 'enemy_1007_slime_2'}, {'start_time': 38.0, 'speed': 1.0, 'path': [(3, 10), (3, 4), (4, 4), (4, 2), (3, 2), (3, 0)], 'idle_points': [], 'idle_durations': [], 'image': 'enemy_1007_slime_2'}, {'start_time': 40.0, 'speed': 1.0, 'path': [(3, 10), (3, 4), (4, 4), (4, 2), (3, 2), (3, 0)], 'idle_points': [], 'idle_durations': [], 'image': 'enemy_1007_slime_2'}, {'start_time': 33.0, 'speed': 1.0, 'path': [(3, 10), (3, 4), (2, 4), (2, 2), (3, 2), (3, 0)], 'idle_points': [], 'idle_durations': [], 'image': 'enemy_1007_slime_2'}, {'start_time': 35.0, 'speed': 1.0, 'path': [(3, 10), (3, 4), (2, 4), (2, 2), (3, 2), (3, 0)], 'idle_points': [], 'idle_durations': [], 'image': 'enemy_1007_slime_2'}, {'start_time': 37.0, 'speed': 1.0, 'path': [(3, 10), (3, 4), (2, 4), (2, 2), (3, 2), (3, 0)], 'idle_points': [], 'idle_durations': [], 'image': 'enemy_1007_slime_2'}, {'start_time': 39.0, 'speed': 1.0, 'path': [(3, 10), (3, 4), (2, 4), (2, 2), (3, 2), (3, 0)], 'idle_points': [], 'idle_durations': [], 'image': 'enemy_1007_slime_2'}, {'start_time': 41.0, 'speed': 1.0, 'path': [(3, 10), (3, 4), (2, 4), (2, 2), (3, 2), (3, 0)], 'idle_points': [], 'idle_durations': [], 'image': 'enemy_1007_slime_2'}, {'start_time': 43.0, 'speed': 1.1, 'path': [(5, 10), (5, 4), (4, 4), (4, 2), (3, 2), (3, 0)], 'idle_points': [], 'idle_durations': [], 'image': 'enemy_1002_nsabr'}, {'start_time': 44.0, 'speed': 1.1, 'path': [(1, 10), (1, 4), (2, 4), (2, 2), (3, 2), (3, 0)], 'idle_points': [], 'idle_durations': [], 'image': 'enemy_1002_nsabr'}, {'start_time': 26.0, 'speed': 1.0, 'path': [(5, 10), (5, 4), (4, 4), (4, 2), (3, 2), (3, 0)], 'idle_points': [], 'idle_durations': [], 'image': 'enemy_1028_mocock'}, {'start_time': 26.0, 'speed': 1.0, 'path': [(1, 10), (1, 4), (2, 4), (2, 2), (3, 2), (3, 0)], 'idle_points': [], 'idle_durations': [], 'image': 'enemy_1028_mocock'}, {'start_time': 31.0, 'speed': 0.8, 'path': [(3, 10), (3, 4), (4, 4), (4, 2), (3, 2), (3, 0)], 'idle_points': [], 'idle_durations': [], 'image': 'enemy_1030_wteeth'}, {'start_time': 40.0, 'speed': 0.8, 'path': [(3, 10), (3, 4), (2, 4), (2, 2), (3, 2), (3, 0)], 'idle_points': [], 'idle_durations': [], 'image': 'enemy_1030_wteeth'}, {'start_time': 39.0, 'speed': 1.0, 'path': [(1, 10), (1, 4), (2, 4), (2, 2), (3, 2), (3, 0)], 'idle_points': [], 'idle_durations': [], 'image': 'enemy_1007_slime_2'}, {'start_time': 40.0, 'speed': 1.0, 'path': [(1, 10), (1, 4), (2, 4), (2, 2), (3, 2), (3, 0)], 'idle_points': [], 'idle_durations': [], 'image': 'enemy_1007_slime_2'}, {'start_time': 41.0, 'speed': 1.0, 'path': [(1, 10), (1, 4), (2, 4), (2, 2), (3, 2), (3, 0)], 'idle_points': [], 'idle_durations': [], 'image': 'enemy_1007_slime_2'}, {'start_time': 48.0, 'speed': 1.0, 'path': [(5, 10), (5, 4), (4, 4), (4, 2), (3, 2), (3, 0)], 'idle_points': [], 'idle_durations': [], 'image': 'enemy_1007_slime_2'}, {'start_time': 49.0, 'speed': 1.0, 'path': [(5, 10), (5, 4), (4, 4), (4, 2), (3, 2), (3, 0)], 'idle_points': [], 'idle_durations': [], 'image': 'enemy_1007_slime_2'}, {'start_time': 50.0, 'speed': 1.0, 'path': [(5, 10), (5, 4), (4, 4), (4, 2), (3, 2), (3, 0)], 'idle_points': [], 'idle_durations': [], 'image': 'enemy_1007_slime_2'}]
		entry_list = stage_data.get_enemy_pathing(text_to_display)
		# === Build animations for all entries ===
		all_anims = []

		for entry in entry_list:
			print(entry)
			path_coords = [squares[r][c].get_center() for r, c in entry["path"]]
			speed = entry["speed"]
			idle_map = dict(zip(entry["idle_points"], entry["idle_durations"]))

			anims = []

			# Wait before showing image
			try:
				img = ImageMobject("images/" + entry["image"] + ".png").scale(0.6).move_to(path_coords[0])
			except:
				img = ImageMobject("images/W.png").scale(0.6).move_to(path_coords[0])
			if entry["start_time"] > 0:
				anims.append(Blink(img, blinks=1,time_on = 0.0, time_off = entry["start_time"]))

			# Move + idle animations
			for i in range(1, len(path_coords)):
				seg = VMobject().set_points_as_corners([path_coords[i - 1], path_coords[i]])
				dist = np.linalg.norm(path_coords[i] - path_coords[i - 1])
				time_for_segment = dist / square_size / speed

				anims.append(MoveAlongPath(img, seg, run_time=time_for_segment, rate_func=linear))

				if i in idle_map: #TODO add Blink to make the teleport possible
					anims.append(Wait(idle_map[i]))

			# Fade out
			anims.append(FadeOut(img))

			all_anims.append(Succession(*anims))

		# === Run all animations simultaneously ===
		self.play(AnimationGroup(*all_anims, lag_ratio=0))
		self.wait(1)
