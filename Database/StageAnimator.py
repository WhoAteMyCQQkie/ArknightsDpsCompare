import numpy as np
import os

from manim import *

from JsonReader import StageData

#Todo:
#better default image
#optimize animation, so that things only spawn when theyre supposed to (questionable gains from that)
#path finding
#extra thread or extra script to handle a queue
#holes and other special tiles
#teleports and idle starts
#add enemy details animation
#plot dimensions in large maps

class StageAnimator(Scene):

	def construct(self):
		square_size = 1
		squares = []
		stage_data = StageData()
		stage_name = os.environ.get("STAGE_NAME", "Default text")
		animate = not (os.environ.get("DO_ANIM", "default") == "default")
		stage_layout = stage_data.get_stage_layout(stage_name)

		counter = 2 #the first 2 elements contain the dimensions of the plot
		for row in range(stage_layout[1]):
			row_squares = []
			for col in range(stage_layout[0]):
				square = Square(side_length=square_size)
				square.move_to(
					RIGHT * (col - stage_layout[0] // 2) * square_size +
					DOWN * (stage_layout[1] // 2 - row) * square_size
				)
				square.set_fill(WHITE, opacity=0.3)
				if stage_layout[counter] == 0: square.set_fill(BLUE, opacity=1.0)
				elif stage_layout[counter] == 1: square.set_fill(RED, opacity=1.0)
				elif stage_layout[counter] == 2: square.set_fill(WHITE, opacity=0.1)
				elif stage_layout[counter] == 3: square.set_fill(WHITE, opacity=0.8)
				elif stage_layout[counter] == 4: square.set_fill(WHITE, opacity=0.7)
				elif stage_layout[counter] == 5: square.set_fill(WHITE, opacity=0.4)
				elif stage_layout[counter] == 6: square.set_fill(WHITE, opacity=0.3)
				elif stage_layout[counter] == 7: square.set_fill(GREEN, opacity=0.8)
				counter += 1
				square.set_stroke(BLACK, width=1)
				self.add(square)
				row_squares.append(square)
			squares.append(row_squares)

		# === Define Entries ===
		entry_list = stage_data.get_enemy_pathing(stage_name)
		# === Build animations for all entries ===
		all_anims = []

		for entry in entry_list:
			path_coords = [squares[r][c].get_center() for r, c in entry["path"]]
			speed = entry["speed"]
			idle_map = dict(zip(entry["idle_points"], entry["idle_durations"]))

			anims = []

			# Wait before showing image
			try:
				img = ImageMobject("Database/images/" + entry["image"] + ".png").scale(0.6).move_to(path_coords[0])
			except:
				img = ImageMobject("Database/images/W.png").scale(0.6).move_to(path_coords[0])
			if entry["start_time"] > 0:
				anims.append(Blink(img, blinks=1,time_on = 0.0, time_off = entry["start_time"]))

			# Move + idle animations
			for i in range(0, len(path_coords)-1):
				if i in idle_map:
					if idle_map[i] > 0:
						anims.append(Wait(idle_map[i]))
					else:
						anims.append(Blink(img, blinks=1,time_on = 0.0, time_off = abs(idle_map[i])))

				seg = VMobject().set_points_as_corners([path_coords[i], path_coords[i + 1]])
				dist = np.linalg.norm(path_coords[i + 1] - path_coords[i])
				time_for_segment = dist / square_size / speed
				if i in idle_map:
					if idle_map[i] < 0:
						time_for_segment = 0

				anims.append(MoveAlongPath(img, seg, run_time=time_for_segment, rate_func=linear))

				

			# Fade out
			anims.append(FadeOut(img))

			all_anims.append(Succession(*anims))

		# === Run all animations simultaneously ===
		if animate:
			self.play(AnimationGroup(*all_anims, lag_ratio=0))
			self.wait(1)
