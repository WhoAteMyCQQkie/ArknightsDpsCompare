import numpy as np
import os

from manim import *

from JsonReader import StageData

#Todo:
#path finding
#special tiles (interactables, buff tiles)
#fenced off ground tiles
#add enemy details (animation or just image)
#add !status to see current progress, using /dev/shm/
#add this is already being processed
#text "finished job xxx"
#exceptions handler for weird stage mechanics like chapter 12 boss
#similar:exception handling for wrong enemy names in stages

config.disable_caching = True
config.frame_rate = 15

class StageAnimator(Scene):

	def construct(self):
		square_size = 1
		squares = []
		stage_data = StageData()
		stage_name = os.environ.get("STAGE_NAME", "Default text")
		try:
			road_blocks = [int(x) for x in os.environ.get("R_BLOCK","NOPE").split(',')]
		except ValueError:
			road_blocks = []
		animate = not (os.environ.get("DO_ANIM", "default") == "default")
		stage_layout = stage_data.get_stage_layout(stage_name, road_blocks)
		
		#set frame size
		self.camera.frame_height = stage_layout[1]
		self.camera.frame_width = stage_layout[0]
		#add offset for even tile sized maps
		x_offset = (stage_layout[0]+1)%2
		y_offset = (stage_layout[1]+1)%2
		self.camera.frame_center = np.array([-x_offset/2,-y_offset/2,0.0])
		try:
			extra_pos, extra_type = stage_data.get_special_layout(stage_name)
		except:
			extra_pos = []
			extra_type = []

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
				if stage_layout[counter] == 0: square.set_fill(BLUE, opacity=1.0) #blue box
				elif stage_layout[counter] == 1: square.set_fill(RED, opacity=1.0) #red box
				elif stage_layout[counter] == 2: square.set_fill(WHITE, opacity = 0.13) #tile forbidden
				elif stage_layout[counter] in [3,15]: square.set_fill(WHITE, opacity=0.8) #usable highground
				elif stage_layout[counter] == 4: square.set_fill(GREEN, opacity=0.7) #unusable highground
				elif stage_layout[counter] in [5,16]: square.set_fill(WHITE, opacity=0.3) #usable floor
				elif stage_layout[counter] == 6: square.set_fill(GRAY_BROWN, opacity=0.9) #unusable floor
				elif stage_layout[counter] == 7: square.set_fill(GREEN, opacity=0.8) #something nefarious
				elif stage_layout[counter] == 8: square.set_fill(BLACK, opacity=1.0) #hole
				elif stage_layout[counter] == 9: square.set_fill(PURPLE, opacity=0.6) #teleporter
				elif stage_layout[counter] == 10: square.set_fill(RED, opacity=0.5) #fly start
				elif stage_layout[counter] == 11: square.set_fill(LIGHT_BROWN, opacity=0.8) #sand tiles from EP
				elif stage_layout[counter] == 12: square.set_fill(DARK_BLUE, opacity=0.8) #deep sea water
				elif stage_layout[counter] == 13: #fenced melee tile
					square.side_length = 0.92 * square_size
					square.set_fill(WHITE, opacity=0.3)
					square.set_stroke(WHITE, opacity = 0.13, width = 8) 
				elif stage_layout[counter] == 14: square.set_fill(DARK_BLUE, opacity=0.6) #deep sea water, unusable
				elif stage_layout[counter] == 69: square.set_fill(ORANGE, opacity=0.9)
				
				if stage_layout[counter] in [15,16]:#show buff tiles
					top = (square.get_corner(UL)+square.get_corner(UR))/2
					lef = (square.get_corner(UL)+square.get_corner(DL))/2
					bot = (square.get_corner(DL)+square.get_corner(DR))/2
					rig = (square.get_corner(DR)+square.get_corner(UR))/2
					diag1 = Line(start=top, end=rig, color=ORANGE)
					diag2 = Line(start=rig, end=bot, color=ORANGE)
					diag3 = Line(start=bot, end=lef, color=ORANGE)
					diag4 = Line(start=lef, end=top, color=ORANGE)
					x_shape = VGroup(diag1, diag2, diag3, diag4)
					x_shape.set_z_index(1)
					self.add(x_shape)

				if stage_layout[counter] != 13: square.set_stroke(BLACK, opacity=0.9, width=1)
				
				counter += 1
				self.add(square)
				row_squares.append(square)
				
				#Including tokens
				if (counter-3 in extra_pos):
					special_type = extra_type[extra_pos.index(counter-3)]
					if special_type == 1:
						top_left = square.get_corner(UL)
						bottom_right = square.get_corner(DR)
						top_right = square.get_corner(UR)
						bottom_left = square.get_corner(DL)
						diag1 = Line(start=top_left, end=bottom_right, color=RED)
						diag2 = Line(start=top_right, end=bottom_left, color=RED)
						x_shape = VGroup(diag1, diag2)
						self.add(x_shape)
					else:#if special_type == 2:
						icon_shape = Square(side_length=square_size*0.7)
						icon_shape.move_to(square.get_center())
						icon_shape.set_stroke(GREEN,width = 10)
						self.add(icon_shape)

			squares.append(row_squares)
		
		label = Text(f"{stage_name.upper().replace('PSIM-','')}",font_size=20).move_to(np.array([-(stage_layout[0]-1)//2,(stage_layout[1]-1)//2,0]))
		self.add(label)

		# Doing the Animation
		if animate:
			entry_list = stage_data.get_enemy_pathing(stage_name, road_blocks)
			#entry["speed"] = 0.7
			#entry["path"] = [(1,0), (1,1), (3,1), (3,3)]
			#entry["start_time"] = 24.5
			#entry["idle_points"] = [0,3]  can be empty
			#entry["idle_time"] = [15.0,-3.0]   pos=idle time, neg=teleport time
			all_anims = []
			all_finish_times = []

			for entry in entry_list:
				path_coords = [squares[r][c].get_center() for r, c in entry["path"]]
				speed = entry["speed"]
				idle_map = dict(zip(entry["idle_points"], entry["idle_durations"]))

				anims = []
				finish_time = 0

				try:
					img = ImageMobject("Database/images/" + entry["image"] + ".png").scale(0.6).move_to(path_coords[0])
				except:
					img = ImageMobject("Database/images/default.png").scale(0.6).move_to(path_coords[0])
				
				# Wait before showing image
				if entry["start_time"] > 0:
					anims.append(Blink(img, blinks=1,time_on = 0.0, time_off = entry["start_time"]))
					finish_time += entry["start_time"]

				# Move + idle animations
				for i in range(0, len(path_coords)-1):
					if i in idle_map:
						finish_time += abs(idle_map[i])
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
					finish_time += time_for_segment

					anims.append(MoveAlongPath(img, seg, run_time=time_for_segment, rate_func=linear))

				anims.append(FadeOut(img))

				all_anims.append(Succession(*anims))
				all_finish_times.append(finish_time)
			
			#Add a counter to keep track of the enemies
			all_finish_times.sort()
			total = len(all_finish_times)
			counter_anims = []
			last_time = 0
			text = Text(f"0/{total}",font_size=20).move_to(np.array([(stage_layout[0]-1)//2,(stage_layout[1]-1)//2,0]))
			for i, time in enumerate(all_finish_times):
				counter_anims.append(Wait(time-last_time))
				last_time = time
				counter_anims.append(Transform(text,Text(f"{i+1}/{total}",font_size=20).move_to(np.array([(stage_layout[0]-1)//2,(stage_layout[1]-1)//2,0])),run_time=0))
			counter_anims.append(Transform(text,Text(f"{total}/{total}",font_size=20).move_to(np.array([(stage_layout[0]-1)//2,(stage_layout[1]-1)//2,0])),run_time=0))
			text_animation = Succession(*counter_anims)


			self.play(AnimationGroup(*all_anims, text_animation, lag_ratio=0))
			self.wait(1)

#This makes sure that multiple threads don't interfere with each other. It IS necessary.
#there are probably more elegant ways of doing this, but meh. Manim was never meant for this usecase anyway
class Handler0(StageAnimator):
	pass

class Handler1(StageAnimator):
	pass

class Handler2(StageAnimator):
	pass
