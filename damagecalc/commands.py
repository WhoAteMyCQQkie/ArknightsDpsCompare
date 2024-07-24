import io
import itertools
import multiprocessing
from typing import Callable, List
import copy

import discord
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

import damagecalc.utils as utils
from damagecalc.utils import DiscordSendable
import damagecalc.damage_formulas as df
from damagecalc.damage_formulas import op_dict
from damagecalc.healing_formulas import healer_dict

#for the enemy/chapter prompt
enemy_dict = {"13": [[800,50,"01"],[100,40,"02"],[400,50,"03"],[350,50,"04"],[1200,0,"05"],[1500,0,"06"],[900,20,"07"],[1200,20,"08"],[150,40,"09"],[3000,90,"10"],[200,20,"11"],[250,60,"12"],[300,60,"13"],[300,50,"14"]],
		"zt": [[250,50,"01"],[200,15,"02"],[250,50,"03"],[200,15,"04"],[700,60,"05"],[300,50,"06"],[150,10,"07"],[250,15,"08"],[300,50,"09"],[250,15,"10"],[600,80,"11"],[300,50,"12"],[1000,60,"13"],[600,60,"14"],[350,50,"15"],[900,60,"16"],[550,60,"17"]],
		"is": [[250,40,"01"],[200,10,"02"],[180,10,"03"],[200,10,"04"],[250,40,"05"],[900,10,"06"],[120,10,"07"],[1100,10,"08"],[800,45,"09"],[500,25,"10"],[500,25,"11"],[1000,15,"12"],[1300,15,"13"],[800,45,"14"],[1000,60,"15"]]}

modifiers = ["s1","s2","s3","p1","p2","p3","p4","p5","p6","m0","m1","m2","m3","0","1","2","3","mod0","mod1","mod2","mod3","modlvl","modlvl1","modlvl2","modlvl3","modlv","modlv1","modlv2","modlv3","mod","x0","y0","x","x1","x2","x3","y","y1","y2","y3","d","d1","d2","d3","modx","mody","modd","module","no","nomod","s1m0","s1m1","s1m2","s1m3","s2m0","s2m1","s2m2","s2m3","s3m0","s3m1","s3m2","s3m3","sl7","s7","slv7","l7","lv7"]


#If some smartass requests more than 40 operators to be drawn
bot_mad_message = ["excuse me, what? <:blemi:1077269748972273764>", "why you do this to me? <:jessicry:1214441767005589544>", "how about you draw your own graphs? <:worrymad:1078503499983233046>", "<:pepe_holy:1076526210538012793>", "spare me, please! <:harold:1078503476591607888>"]

def simple(content: str) -> Callable[[List[str]], DiscordSendable]:
	return lambda args: DiscordSendable(content)

def calc_command(args: List[str]) -> DiscordSendable:

	# Note that multiprocessing may add quite a bit of overhead in spawning a worker thread, but also a lot of safety for a potentially risky computation.
	#start = time.time()
	pool = multiprocessing.Pool(processes=1)
	output = "Exceeded reasonable computation time"
 
	try:
		output = pool.apply_async(utils.calc_message, (' '.join(args),)).get(timeout=2) 
	except multiprocessing.context.TimeoutError:
		pass
	finally:
		pool.close()
	
	#output += "Completed in " + str(round((time.time() - start) * 1000)) + "ms"
	return DiscordSendable(output)

def dps_command2(args: List[str])-> DiscordSendable:
	global_parameters = utils.PlotParametersSet()
	already_drawn_ops = []
	plt.clf()
	plt.style.use('default')
	already_drawn_ops = [] #this is a global variable edited the utils.plot_graph function. probably not a good solution
	plot_size = 4 #plot height in inches
	show = True
	bottomleft = False
	textsize = 10

	i = 0
	for word in args:
		if word in ["hide", "legend"]:
			show = False
		elif word in ["big", "beeg", "large"]:
			plot_size = 8
		elif word in ["repos", "reposition", "bottom", "left", "botleft", "position", "change", "changepos"]:
			bottomleft = True
		elif word in ["small","font","tiny"]:
			textsize = 6
		elif word in ["color","colour","colorblind","colourblind","blind"]:
			plt.style.use('tableau-colorblind10')

	#fix typos in operator names
	for i in range(len(args)):
		if utils.fix_typos(args[i], op_dict.keys()) != "":
			args[i] = utils.fix_typos(args[i], op_dict.keys())
	
	#TODO: try to fix other input errors (wrong order, missing spaces, typos in prompts)
	
	#Find scopes where which parameter set is active
	global_scopes = [0]
	local_scopes = []
	for i, arg in enumerate(args):
		if arg in op_dict.keys():
			local_scopes.append(i)
		elif arg in ["g:","global","global:"]:
			global_scopes.append(i)
	scopes = list(set(global_scopes + local_scopes))
	scopes.sort()
	scopes.append(len(args)-1)

	#TODO get plot formatting

	plot_numbers = 0
	#getting setting the plot parameters and plotting the units
	utils.parse_plot_essentials(global_parameters, args)
	for i in range(len(scopes)-1):
		if scopes[i] in local_scopes:
			local_parameters = copy.deepcopy(global_parameters)
			if (scopes[i]+1) not in scopes:
				utils.parse_plot_parameters(local_parameters, args[scopes[i]:scopes[i+1]])		
			for parameters in local_parameters.get_plot_parameters():
				if utils.apply_plot(op_dict[args[scopes[i]]],parameters,already_drawn_ops,True,plot_numbers):
					plot_numbers += 1
					if plot_numbers > 40:
						plt.close()
						l = len(bot_mad_message)
						return DiscordSendable(bot_mad_message[np.random.randint(0,l)])
		elif scopes[i] in global_scopes:
			global_parameters = utils.PlotParametersSet()
			utils.parse_plot_essentials(global_parameters, args)
			utils.parse_plot_parameters(global_parameters, args[scopes[i]:scopes[i+1]])

	#prevent the legend from messing up the graphs format
	legend_columns = 1
	if plot_numbers < 2: plot_size = 4
	if plot_numbers > 15 and plot_size == 4:
		textsize = 6
	if plot_numbers > 26 and plot_size == 4:
		legend_columns = 2
	if plot_numbers > 52 and plot_size == 4:
		legend_columns = 1
	if plot_numbers > 30 and plot_size == 8 and textsize == 10:
		legend_columns = 2
	
	plt.grid(visible=True)
	if show:
		if not bottomleft: plt.legend(loc="upper right",fontsize=textsize,ncol=legend_columns,framealpha=0.7)
		else: plt.legend(loc="lower left",fontsize=textsize,ncol=legend_columns,framealpha=0.7)
	
	if global_parameters.graph_type != 5:
		plt.xlabel("Defense\nRes")
		plt.ylabel("DPS" , rotation=0)
	if global_parameters.graph_type == 3: 
		plt.xlabel("Res")
		plt.ylabel(f"DPS (vs {global_parameters.fix_value}def)" , rotation=0)
	if global_parameters.graph_type == 4: 
		plt.xlabel("Defense")
		plt.ylabel(f"DPS (vs {global_parameters.fix_value}res)" , rotation=0)
	
	max_def = global_parameters.max_def
	max_res = global_parameters.max_res
	fixval = global_parameters.fix_value
	graph_type = global_parameters.graph_type

	ax = plt.gca()
	ax.set_ylim(ymin = 0)
	ax.set_xlim(xmin = 0)
	if graph_type != 5:
		ax.set_xlim(xmin = 0, xmax = max_def)
	ax.xaxis.set_label_coords(0.08/plot_size*4, -0.025/plot_size*4)
	ax.yaxis.set_label_coords(-0.04/plot_size*4, 1+0.01/plot_size*4)
	if graph_type == 3: #properly align the DPS comment
		ax.yaxis.set_label_coords(0.02, 1.02)
		if fixval > 999: ax.yaxis.set_label_coords(0.03, 1.02)
		if fixval < 100: ax.yaxis.set_label_coords(0.01, 1.02)
		if fixval < 10: ax.yaxis.set_label_coords(0.0, 1.02)
	if graph_type == 4: 
		ax.yaxis.set_label_coords(0.01, 1.02)
		if fixval < 10: ax.yaxis.set_label_coords(0.0, 1.02)
		
	
	#Setting the x-axis labels	
	if graph_type == 0:
		tick_labels=["0\n0",f"{int(max_def/6)}\n{int(max_res/6)}",f"{int(max_def/3)}\n{int(max_res/3)}",f"{int(max_def/2)}\n{int(max_res/2)}",f"{int(max_def*4/6)}\n{int(max_res*4/6)}",f"{int(max_def*5/6)}\n{int(max_res*5/6)}",f"{int(max_def)}\n{int(max_res)}"]
	if graph_type == 1:
		tick_labels=["0\n0",f"{int(max_def/3)}\n0",f"{int(max_def*4/6)}\n0",f"{int(max_def)}\n0",f"{int(max_def)}\n{int(max_res*2/6)}",f"{int(max_def)}\n{int(max_res*4/6)}",f"{int(max_def)}\n{int(max_res)}"]
	if graph_type == 2:
		tick_labels=["0\n0",f"0\n{int(max_res*2/6)}",f"0\n{int(max_res*4/6)}",f"0\n{int(max_res)}",f"{int(max_def*2/6)}\n{int(max_res)}",f"{int(max_def*4/6)}\n{int(max_res)}",f"{int(max_def)}\n{int(max_res)}"]
	if graph_type == 3:
		tick_labels=["0",f"{int(max_res/6)}",f"{int(max_res/3)}",f"{int(max_res/2)}",f"{int(max_res*4/6)}",f"{int(max_res*5/6)}",f"{int(max_res)}"]
	if graph_type == 4:
		tick_labels=["0",f"{int(max_def/6)}",f"{int(max_def/3)}",f"{int(max_def/2)}",f"{int(max_def*4/6)}",f"{int(max_def*5/6)}",f"{int(max_def)}"]
	if graph_type != 5:
		tick_locations = np.linspace(0,max_def,7)
		plt.xticks(tick_locations, tick_labels)

	fig = plt.gcf()
	fig.set_size_inches(2 * plot_size, plot_size)
	plt.tight_layout()
	
	#Generate image and send it to the channel
	buf = io.BytesIO()
	plt.savefig(buf,format='png')
	buf.seek(0)
	file = discord.File(buf, filename='plot.png')
	plt.close()
	return DiscordSendable(file=file)






def dps_command(args: List[str])-> DiscordSendable:
	#reset plot parameters
	plt.clf()
	plt.style.use('default')
	already_drawn_ops = [] #this is a global variable edited the utils.plot_graph function. probably not a good solution
	plot_size = 4 #plot height in inches
	add_title = False
	title = ""
	show = True
	bottomleft = False
	textsize = 10
	
	#Read the input message
	entries = len(args)
	i = 0
	parsing_error = False
	error_message = "Could not use the following prompts: "

	#Values of prefix prompts (buff, level, shred, etc.)
	res = [-1]
	defen = [-1]
	lvl = -10
	contains_data = 0
	buffs = [0,0,0,0] #atk% flatatk aspd fragile hitsreceived. the hitsreceived should be moved to a kwarg soon
	basebuffs = [1,0]
	active_operator_kit_aspects = [True,True,True,True,True] #trait talent1 talent2 skill module
	all_conditionals = False
	targets = 1
	shreds = [1,0,1,0] #def% def res% res. percent values are multiplied to dmg, so 20% shred = 0.8
	normal_dps = True #normal dps vs total dmg
	input_kwargs = dict()  #for now only hits, soon the shreds are added to correct calculations for flat shredders, later maybe also stacks and other operator specific boni (looking at you, mumu)
	
	#Values for the axis of the plot
	graph_type = 0 #plot type from 0 to 5: normal, split(def first), split(res first), fixed def, fixed res, enemy prompt
	max_def = 3000
	max_res = 120
	fixval = 40
	enemies = [] #list of [def,res,"imageIndex"]
	enemy_key = "" #ZT, is, 13 ...
	number_request = False #For Scaling issues, makes sure that res/def draw calls only appear AFTER setting the scale (to prevent stuff like res 90 maxres 40)
	
	
	#Parsing the input
	while i < entries:
		if args[i] in op_dict and i+1==entries:
			if all_conditionals:
				for combos in itertools.product([True,False], repeat = 5):
					if utils.plot_graph((op_dict[args[i]](lvl,-1, -1, 3,-1,3, targets, list(combos),buffs,**input_kwargs)), buffs, defen, res, graph_type, max_def, max_res, fixval,already_drawn_ops,shreds,enemies,basebuffs,normal_dps,contains_data): contains_data += 1
			else:
				if utils.plot_graph((op_dict[args[i]](lvl,-1, -1, 3,-1,3, targets, active_operator_kit_aspects,buffs,**input_kwargs)), buffs, defen, res, graph_type, max_def, max_res, fixval,already_drawn_ops,shreds,enemies,basebuffs,normal_dps,contains_data): contains_data += 1
		elif args[i] in op_dict and not args[i+1] in modifiers:
			if all_conditionals:
				for combos in itertools.product([True,False], repeat = 5):
					if utils.plot_graph((op_dict[args[i]](lvl,-1, -1, 3,-1,3, targets, list(combos),buffs,**input_kwargs)), buffs, defen, res, graph_type, max_def, max_res, fixval,already_drawn_ops,shreds,enemies,basebuffs,normal_dps,contains_data): contains_data += 1
			else:
				if utils.plot_graph((op_dict[args[i]](lvl,-1, -1, 3,-1,3, targets, active_operator_kit_aspects,buffs,**input_kwargs)), buffs, defen, res, graph_type, max_def, max_res, fixval,already_drawn_ops,shreds,enemies,basebuffs,normal_dps,contains_data): contains_data += 1 
			if contains_data > 40: break
		elif args[i] in op_dict and args[i+1] in modifiers:
			tmp = i
			i+=1
			skills = {-1}
			masteries = {-1}
			modlvls = {-1}
			pots = {-1}
			mods = {-1}
			while i < entries and args[i] in modifiers:
				if args[i] in ["s1","s2","s3"]: 
					skills.add(int(args[i][1]))
					skills.discard(-1)
				elif args[i] in ["p1","p2","p3","p4","p5","p6"]: 
					pots.add(int(args[i][1]))
					pots.discard(-1)
				elif args[i] in ["1","2","3"]: 
					modlvls.add(int(args[i]))
					modlvls.discard(-1)
				elif args[i] in ["modlvl1","modlvl2","modlvl3","modlv1","modlv2","modlv3",]: 
					modlvls.add(int(args[i][-1]))
					modlvls.discard(-1)
				elif args[i] in ["m0","m1","m2","m3"]: 
					masteries.add(int(args[i][1]))
					masteries.discard(-1)
				elif args[i] in ["sl7","s7","slv7","l7","lv7"]:
					masteries.add(0)
					masteries.discard(-1)
				elif args[i] in ["mod0","mod1","mod2","mod3"]:
					mods.add(int(args[i][3]))
					mods.discard(-1)
				elif args[i] in ["modx","x"]:
					mods.add(1)
					mods.discard(-1)
				elif args[i] in ["x1","x2","x3"]: 
					mods.add(1)
					mods.discard(-1)
					modlvls.add(int(args[i][1]))
					modlvls.discard(-1)
				elif args[i] in ["y1","y2","y3"]: 
					mods.add(2)
					mods.discard(-1)
					modlvls.add(int(args[i][1]))
					modlvls.discard(-1)
				elif args[i] in ["mody","y"]:
					mods.add(2)
					mods.discard(-1)
				elif args[i] in ["modd","d"]:
					mods.add(3)
					mods.discard(-1)
				elif args[i] in ["d1","d2","d3"]: 
					mods.add(3)
					mods.discard(-1)
					modlvls.add(int(args[i][1]))
					modlvls.discard(-1)
				elif args[i] in ["0","no","mod","module","nomod","modlvl","modlv","x0","y0"]:
					mods.add(0)
					mods.discard(-1)
				elif args[i] in ["s1m0","s1m1","s1m2","s1m3","s2m0","s2m1","s2m2","s2m3","s3m0","s3m1","s3m2","s3m3"]:
					skills.add(int(args[i][1]))
					skills.discard(-1)
					masteries.add(int(args[i][3]))
					masteries.discard(-1)
				i+=1
			if not -1 in modlvls and 0 in mods and len(mods) == 1:
				mods.add(-1)
			for pot, skill, mastery, mod, modlvl in itertools.product(pots, skills, masteries, mods, modlvls):
				if all_conditionals:
					for combos in itertools.product([True,False], repeat = 5):
						if utils.plot_graph((op_dict[args[tmp]](lvl,pot,skill,mastery,mod,modlvl, targets, list(combos),buffs,**input_kwargs)), buffs, defen, res, graph_type, max_def, max_res, fixval,already_drawn_ops,shreds,enemies,basebuffs,normal_dps,contains_data): contains_data += 1						
				else:
					if utils.plot_graph((op_dict[args[tmp]](lvl,pot,skill,mastery,mod,modlvl,targets,active_operator_kit_aspects,buffs,**input_kwargs)), buffs, defen, res, graph_type, max_def, max_res, fixval,already_drawn_ops,shreds,enemies,basebuffs,normal_dps,contains_data): contains_data += 1
				if contains_data > 40: break
			i-=1
		elif args[i] in ["b","buff","buffs"]:
			i+=1
			buffcount=0
			buffs=[0,0,0,0]
			while i < entries and buffcount < 4:
				try:
					buffs[buffcount] = int(args[i])
					buffcount +=1
				except ValueError:
					break
				if buffcount == 1: buffs[0] = buffs[0]/100
				if buffcount == 4: buffs[3] = buffs[3]/100
				i+=1
			i-=1
		elif args[i] in ["t","target","targets"]:
			i+=1
			targets = 1
			while i < entries:
				try:
					targets = int(args[i])
				except ValueError:
					break
				i+=1
			i-=1
		elif args[i] in ["t1","t2","t3","t4","t5","t6","t7","t8","t9"]: targets = int(args[i][1])
		elif args[i] in ["r","res","resis","resistance"]:
			i+=1
			res = [-10]
			number_request = True
			while i < entries:
				try:
					res.append(min(max_res,int(args[i])))
				except ValueError:
					break
				i+=1
			i-=1
		elif args[i] in ["d","def","defense"]:
			i+=1
			number_request = True
			defen = [-10]
			while i < entries:
				try:
					defen.append(min(max_def,int(args[i])))
				except ValueError:
					break
				i+=1
			i-=1
		
		elif args[i] in ["shred","shreds","debuff","ignore"]:
			i+=1
			shreds = [1,0,1,0]
			while i < entries:
				if args[i][-1] == "%":
					try:
						shreds[0] = max(0,(1-float(args[i][:-1])/100))
						shreds[2] = max(0,(1-float(args[i][:-1])/100))
					except ValueError:
						break
				else:
					try:
						val = float(args[i])
						if val > 0 and val < 1:
							shreds[0] = 1 - val
							shreds[2] = 1 - val
						if val > 2:
							shreds[1] = val
							shreds[3] = val
					except ValueError:
						break
				i+=1
			i-=1
			input_kwargs["shreds"] = shreds
		elif args[i] in ["resshred","resdebuff","shredres","debuffres","reshred","resignore"]:
			i+=1
			shreds[2] = 1
			shreds[3] = 0
			while i < entries:
				if args[i][-1] == "%":
					try:
						shreds[2] = max(0,(1-float(args[i][:-1])/100))
					except ValueError:
						break
				else:
					try:
						val = float(args[i])
						if val > 0 and val < 1:
							shreds[2] = 1 - val
						if val > 2:
							shreds[3] = val
					except ValueError:
						break
				i+=1
			i-=1
			input_kwargs["shreds"] = shreds
		elif args[i] in ["defshred","defdebuff","shreddef","debuffdef","defignore"]:
			i+=1
			shreds[0] = 1
			shreds[1] = 0
			while i < entries:
				if args[i][-1] == "%":
					try:
						shreds[0] = max(0,(1-float(args[i][:-1])/100))
					except ValueError:
						break
				else:
					try:
						val = float(args[i])
						if val > 0 and val < 1:
							shreds[0] = 1 - val
						if val > 2:
							shreds[1] = val
					except ValueError:
						break
				i+=1
			i-=1
			input_kwargs["shreds"] = shreds
		elif args[i] in ["basebuff","baseatk","base","bbuff","batk"]:
			i+=1
			basebuffs[0] = 1
			basebuffs[1] = 0
			while i < entries:
				if args[i][-1] == "%":
					try:
						basebuffs[0] = max(0,(1+float(args[i][:-1])/100))
					except ValueError:
						break
				else:
					try:
						val = float(args[i])
						if val > 0 and val < 1:
							basebuffs[0] = 1 + val
						if val > 2:
							basebuffs[1] = val
					except ValueError:
						break
				i+=1
			i-=1
		elif args[i] in ["lvl","level","lv"]:
			i+=1
			lvl = -10
			while i < entries:
				try:
					lvl = int(args[i])
				except ValueError:
					break
				i+=1
			i-=1
		elif args[i] in ["iaps","bonk","received","hits","hit"]:
			i+=1
			while i < entries:
				try:
					input_kwargs["hits"] = float(args[i])
				except ValueError:
					if "/" in args[i]:
						new_strings = args[i].split("/")
						try:
							input_kwargs["hits"] = (float(new_strings[0]) / float(new_strings[1]))
						except ValueError:
							break
					else:
						break
				i+=1
			i-=1
		elif args[i] in ["stack","stacks"]:
			i+=1
			while i < entries:
				try:
					input_kwargs["stacks"] = int(args[i])
				except ValueError:
					break
				i+=1
			i-=1
		elif args[i] in ["plus","ultra","plusultra","peak","bonus","max"]:
			input_kwargs["bonus"] = True
		elif args[i] in ["ptilo","boost","spboost","spbuff","sp","buffsp"]:
			i+=1
			while i < entries:
				if args[i][-1] == "%":
					try:
						input_kwargs["boost"] = float(args[i][:-1])/100
						shreds[0] = max(0,(1-float(args[i][:-1])/100))
					except ValueError:
						break
				else:
					try:
						val = float(args[i])
						if val > 0 and val < 1:
							input_kwargs["boost"] = val
					except ValueError:
						break
				i+=1
			i-=1		
		elif args[i] in ["l","low"]:
			active_operator_kit_aspects = [False,False,False,False,False]
		elif args[i] in ["h","high"]:
			active_operator_kit_aspects = [True,True,True,True,True]
		elif args[i] in ["low1","l1","lowtrait","traitlow"]:
			active_operator_kit_aspects[0] = False
		elif args[i] in ["high1","h1","hightrait","traithigh"]:
			active_operator_kit_aspects[0] = True
		elif args[i] in ["low2","l2","lowtalent","talentlow","lowtalent1","talent1low"]:
			active_operator_kit_aspects[1] = False
		elif args[i] in ["high2","h2","hightalent","talenthigh","hightalent1","talent1high"]:
			active_operator_kit_aspects[1] = True
		elif args[i] in ["low3","l3","talentlow","lowtalent2","talent2low"]:
			active_operator_kit_aspects[2] = False
		elif args[i] in ["high3","h3","talenthigh","hightalent2","talent2high"]:
			active_operator_kit_aspects[2] = True
		elif args[i] in ["low4","l4","lows","slow","lowskill","skilllow"]:
			active_operator_kit_aspects[3] = False
		elif args[i] in ["high4","h4","highs","shigh","highskill","skillhigh"]:
			active_operator_kit_aspects[3] = True
		elif args[i] in ["low5","l5","lowm","mlow","lowmod","modlow","lowmodule","modulelow"]:
			active_operator_kit_aspects[4] = False
		elif args[i] in ["high5","h5","highm","mhigh","highmod","modhigh","highmodule","modulehigh"]:
			active_operator_kit_aspects[4] = True
		elif args[i] == "lowtalents":
			active_operator_kit_aspects[1] = False
			active_operator_kit_aspects[2] = False
		elif args[i] == "hightalents":
			active_operator_kit_aspects[1] = True
			active_operator_kit_aspects[2] = True
		elif args[i] in ["total", "totaldmg"]:
			normal_dps = not normal_dps
		elif args[i] in ["hide", "legend"]:
			show = False
		elif args[i] in ["big", "beeg", "large"]:
			plot_size = 8
		elif args[i] in ["repos", "reposition", "bottom", "left", "botleft", "position", "change", "changepos"]:
			bottomleft = True
		elif args[i] in ["conditionals", "conditional","variation","variations"]:
			all_conditionals = True
		elif args[i] == "split":
			if not contains_data: graph_type = 1
		elif args[i] == "split2":
			if not contains_data: graph_type = 2
		elif args[i] in ["small","font","tiny"]:
			textsize = 6
		elif args[i] in ["color","colour","colorblind","colourblind","blind"]:
			plt.style.use('tableau-colorblind10')
		elif args[i] in ["maxdef","limit","range","scale"]:
			if contains_data == 0 and not number_request:
				i+=1
				max_def = 3000
				while i < entries:
					try:
						max_def = min(69420,max(100, int(args[i])))
					except ValueError:
						break
					i+=1
				i-=1
		elif args[i] in ["maxres","reslimit","limitres","scaleres","resscale"]:
			if contains_data == 0 and not number_request:
				i+=1
				max_res = 120
				while i < entries:
					try:
						max_res = min(400,max(5, int(args[i])))
					except ValueError:
						break
					i+=1
				i-=1
		elif args[i] in ["enemy","chapter"]:
			if args[i+1] in enemy_dict and contains_data == 0:
				enemy_key = args[i+1]
				graph_type = 5
				enemies = enemy_dict[args[i+1]]
				enemies.sort(key=lambda tup: tup[0], reverse=False)
				i += 1
		elif args[i] in ["enemy2","chapter2"]:
			if args[i+1] in enemy_dict and contains_data == 0:
				enemy_key = args[i+1]
				graph_type = 5
				enemies = enemy_dict[args[i+1]]
				enemies.sort(key=lambda tup: tup[1], reverse=False)
				i += 1
		elif args[i] in ["fixdef","fixeddef","fixdefense","fixeddefense","setdef","setdefense"]:
			if contains_data == 0: 
				try:
					graph_type = 3
					fixval = int(args[i+1])
					fixval = max(0,min(50000,fixval))
					i+=1
				except ValueError:
					pass
			
		elif args[i] in ["fixres","fixedres","fixresistance","fixedresistance","setres","resresistance"]:
			if contains_data == 0: 
				try:
					graph_type = 4
					fixval = int(args[i+1])
					fixval = max(0,min(400,fixval))
					i+=1
				except ValueError:
					pass
		elif args[i] in ["set","fix","fixed"]:
			if contains_data == 0: 
				try:
					fixval = int(args[i+1])
					graph_type = 3 if fixval >= 100 else 4
					fixval = max(0,min(50000,fixval))
					i+=1
				except ValueError:
					pass
		elif args[i] in ["title","text","label"]:
			i+=1
			add_title = True
			while i < entries:
				title += args[i] + " "
				i+=1								
		elif args[i] in modifiers:
			parsing_error = True
			error_message += " " + args[i] + ","
		elif args[i][0] in ["1","2","3","4","5","6","7","8","9"] and not args[i][-1] in ["0","1","2","3","4","5","6","7","8","9"]: 
			##################try to fix a missing space after an integer like "buff 90surtr" (should not have a leading 0. if the entire number is 0: should be ignorable)
			numberpos = 1
			while args[i][numberpos] in ["0","1","2","3","4","5","6","7","8","9","."]:
				numberpos += 1
			temp = args[i]
			args[i] = args[i][numberpos:]
			args.insert(i,temp[:numberpos])
			entries += 1
			backsteps = 1
			while backsteps < 5:
				try:
					_ = int(args[i-backsteps]) #to cause a valueerror #redneckcoding
					backsteps +=1
				except ValueError:
					backsteps +=1
					break
			i-=backsteps
		elif not args[i][0] in ["0","1","2","3","4","5","6","7","8","9"] and args[i][-1] in ["0","1","2","3","4","5","6","7","8","9","."]: 
			#####################try to fix a missing space after buff/hits etc
			numberpos = 2
			wordlen = len(args[i])
			while args[i][-numberpos] in ["0","1","2","3","4","5","6","7","8","9","."]:
				numberpos += 1
			temp = args[i]
			args[i] = args[i][(wordlen-numberpos+1):]
			args.insert(i,temp[:(wordlen-numberpos+1)])
			entries += 1
			i -= 1
		elif args[i].isdigit() and (i + 1) < entries: 
			######################swap around numbers and prompts, for cases like "5 targets"
			if args[i+1] in ["t","target","targets","def","defense","res","resistance","limit","maxres","maxdef","hits","hit","iaps"]:
				tmp = args[i]
				args[i] = args[i+1]
				args[i+1] = tmp
				i -= 1
		else:
			my_keys = list(op_dict.keys()) ### Try some autocorrection for typos in the operator name
			#lev_dist = 1000
			errorlimit = 0
			promptlength = len(args[i])
			prompt = args[i]
			found_fit = False 
			optimizer = False #True when a solution was found, but we still search for a better solution.
			optimize_error = -10
			if promptlength > 3: errorlimit = 1
			if promptlength > 5: errorlimit = 2
			if promptlength > 8: errorlimit = 3
			if promptlength < 15:
				for key in my_keys:
					if optimizer:
						if df.levenshtein(key, prompt) < optimize_error: #dont just stop at the first fit, but rather at the best fit.
							args[i] = key
							optimize_error = df.levenshtein(key, prompt)
					elif df.levenshtein(key, prompt) <= errorlimit:
						args[i] = key
						i-=1
						optimizer = True
						optimize_error = df.levenshtein(key, prompt)
						found_fit = True
			if not found_fit:
				parsing_error = True
				error_message += " " + args[i] + ","
		i+=1
	
	
	#Cases where no plot is generated: no inputs or too many inputs
	if contains_data == 0:
		plt.close()
		return DiscordSendable()
	if contains_data > 40:
		plt.close()
		l = len(bot_mad_message)
		return DiscordSendable(bot_mad_message[np.random.randint(0,l)])


	
	#prevent the legend from messing up the graphs format
	legend_columns = 1
	if contains_data < 2: plot_size = 4
	if contains_data > 15 and plot_size == 4:
		textsize = 6
	if contains_data > 26 and plot_size == 4:
		legend_columns = 2
	if contains_data > 52 and plot_size == 4:
		legend_columns = 1
	if contains_data > 30 and plot_size == 8 and textsize == 10:
		legend_columns = 2
	
	plt.grid(visible=True)
	if show:
		if not bottomleft: plt.legend(loc="upper right",fontsize=textsize,ncol=legend_columns,framealpha=0.7)
		else: plt.legend(loc="lower left",fontsize=textsize,ncol=legend_columns,framealpha=0.7)
	
	if graph_type != 5:
		plt.xlabel("Defense\nRes")
		plt.ylabel("DPS" , rotation=0)
	if graph_type == 3: 
		plt.xlabel("Res")
		plt.ylabel(f"DPS (vs {fixval}def)" , rotation=0)
	if graph_type == 4: 
		plt.xlabel("Defense")
		plt.ylabel(f"DPS (vs {fixval}res)" , rotation=0)
	
	ax = plt.gca()
	ax.set_ylim(ymin = 0)
	ax.set_xlim(xmin = 0)
	if graph_type != 5:
		ax.set_xlim(xmin = 0, xmax = max_def)
	ax.xaxis.set_label_coords(0.08/plot_size*4, -0.025/plot_size*4)
	ax.yaxis.set_label_coords(-0.04/plot_size*4, 1+0.01/plot_size*4)
	if graph_type == 3: #properly align the DPS comment
		ax.yaxis.set_label_coords(0.02, 1.02)
		if fixval > 999: ax.yaxis.set_label_coords(0.03, 1.02)
		if fixval < 100: ax.yaxis.set_label_coords(0.01, 1.02)
		if fixval < 10: ax.yaxis.set_label_coords(0.0, 1.02)
	if graph_type == 4: 
		ax.yaxis.set_label_coords(0.01, 1.02)
		if fixval < 10: ax.yaxis.set_label_coords(0.0, 1.02)
		
	
	#Setting the x-axis labels	
	if graph_type == 0:
		tick_labels=["0\n0",f"{int(max_def/6)}\n{int(max_res/6)}",f"{int(max_def/3)}\n{int(max_res/3)}",f"{int(max_def/2)}\n{int(max_res/2)}",f"{int(max_def*4/6)}\n{int(max_res*4/6)}",f"{int(max_def*5/6)}\n{int(max_res*5/6)}",f"{int(max_def)}\n{int(max_res)}"]
	if graph_type == 1:
		tick_labels=["0\n0",f"{int(max_def/3)}\n0",f"{int(max_def*4/6)}\n0",f"{int(max_def)}\n0",f"{int(max_def)}\n{int(max_res*2/6)}",f"{int(max_def)}\n{int(max_res*4/6)}",f"{int(max_def)}\n{int(max_res)}"]
	if graph_type == 2:
		tick_labels=["0\n0",f"0\n{int(max_res*2/6)}",f"0\n{int(max_res*4/6)}",f"0\n{int(max_res)}",f"{int(max_def*2/6)}\n{int(max_res)}",f"{int(max_def*4/6)}\n{int(max_res)}",f"{int(max_def)}\n{int(max_res)}"]
	if graph_type == 3:
		tick_labels=["0",f"{int(max_res/6)}",f"{int(max_res/3)}",f"{int(max_res/2)}",f"{int(max_res*4/6)}",f"{int(max_res*5/6)}",f"{int(max_res)}"]
	if graph_type == 4:
		tick_labels=["0",f"{int(max_def/6)}",f"{int(max_def/3)}",f"{int(max_def/2)}",f"{int(max_def*4/6)}",f"{int(max_def*5/6)}",f"{int(max_def)}"]
	if graph_type != 5:
		tick_locations = np.linspace(0,max_def,7)
		plt.xticks(tick_locations, tick_labels)
	else: #The part below this handles the enemy prompt
		ax.set_xticklabels([])
		#pylint: disable=unused-variable
		xl, yl, xh, yh=np.array(ax.get_position()).ravel()
		fig = plt.gcf()
		axes = [None] * len(enemies)
		for i,ax in enumerate(axes):
			ph = len(enemies)
			img = np.asarray(Image.open('arkbotimages/' + enemy_key + '_' + enemies[i][2] + '.png'))
			#ax = fig.add_axes([1/(len(enemies)+1)*(i+0.67), 0, 0.1, 0.1])
			if plot_size ==4: ax = fig.add_axes([0.4*xl+1.174*(xh-xl)/ph*(i), 0 ,2.1*(xh-xl)/ph ,2.1*(xh-xl)/ph])
			else: ax = fig.add_axes([0.1*xl+1.22*(xh-xl)/ph*(i), 0 ,2.1*(xh-xl)/ph ,2.1*(xh-xl)/ph])
			ax.axison = False
			ax.imshow(img)


	if add_title:
		plt.title(title)
	fig = plt.gcf()
	fig.set_size_inches(2 * plot_size, plot_size)
	plt.tight_layout()
	
	#Generate image and send it to the channel
	buf = io.BytesIO()
	plt.savefig(buf,format='png')
	buf.seek(0)
	file = discord.File(buf, filename='plot.png')
	plt.close()
	if parsing_error:
		return DiscordSendable(content=error_message[:-1], file=file)
	else:
		return DiscordSendable(file=file)
  
def hps_command(args: List[str]) -> DiscordSendable:
	#read the message
	entries = len(args)
	i = 0
	#res = [-1]
	#defen = [-1]
	lvl = -10
	targets = 1
	mastery = 3
	modlvl = 3
	contains_data = 0
	buffs = [0,0,0,0]
	#active_operator_kit_aspects = [True,True,True,True,True] #trait talent1 talent2 skill module
	boost = 0
	healer_message = ""
	#parsing_error = False
	error_message = "Could not use the following prompts: "
	
	while i < entries:
		if args[i] in healer_dict and i+1==entries:
			healer_message += (healer_dict[args[i]](lvl,-1, -1, 3,-1,3,targets,buffs,boost)).skill_hps() + "\n"
			contains_data += 1
			if contains_data > 19: break
		elif args[i] in healer_dict and not args[i+1] in modifiers:
			contains_data += 1
			healer_message += (healer_dict[args[i]](lvl,-1, -1, 3,-1,3,targets,buffs,boost)).skill_hps() + "\n"
			if contains_data > 19: break
		elif args[i] in healer_dict and args[i+1] in modifiers:
			tmp = i
			i+=1
			skills = {-1}
			masteries = {-1}
			modlvls = {-1}
			pots = {-1}
			mods = {-1}
			while i < entries and args[i] in modifiers:
				if args[i] in ["s1","s2","s3"]: 
					skills.add(int(args[i][1]))
					skills.discard(-1)
				elif args[i] in ["p1","p2","p3","p4","p5","p6"]: 
					pots.add(int(args[i][1]))
					pots.discard(-1)
				elif args[i] in ["1","2","3"]: 
					modlvls.add(int(args[i]))
					modlvls.discard(-1)
				elif args[i] in ["modlvl1","modlvl2","modlvl3","modlv1","modlv2","modlv3",]: 
					modlvls.add(int(args[i][-1]))
					modlvls.discard(-1)
				elif args[i] in ["m0","m1","m2","m3"]: 
					masteries.add(int(args[i][1]))
					masteries.discard(-1)
				elif args[i] in ["sl7","s7","slv7","l7","lv7"]:
					masteries.add(0)
					masteries.discard(-1)
				elif args[i] in ["mod0","mod1","mod2","mod3"]:
					mods.add(int(args[i][3]))
					mods.discard(-1)
				elif args[i] in ["modx","x"]:
					mods.add(1)
					mods.discard(-1)
				elif args[i] in ["x1","x2","x3"]: 
					mods.add(1)
					mods.discard(-1)
					modlvls.add(int(args[i][1]))
					modlvls.discard(-1)
				elif args[i] in ["y1","y2","y3"]: 
					mods.add(2)
					mods.discard(-1)
					modlvls.add(int(args[i][1]))
					modlvls.discard(-1)
				elif args[i] in ["mody","y"]:
					mods.add(2)
					mods.discard(-1)
				elif args[i] in ["modd","d"]:
					mods.add(3)
					mods.discard(-1)
				elif args[i] in ["d1","d2","d3"]: 
					mods.add(3)
					mods.discard(-1)
					modlvls.add(int(args[i][1]))
					modlvls.discard(-1)
				elif args[i] in ["0","no","mod","module","nomod","modlvl","modlv","x0","y0"]:
					mods.add(0)
					mods.discard(-1)
				elif args[i] in ["s1m0","s1m1","s1m2","s1m3","s2m0","s2m1","s2m2","s2m3","s3m0","s3m1","s3m2","s3m3"]:
					skills.add(int(args[i][1]))
					skills.discard(-1)
					masteries.add(int(args[i][3]))
					masteries.discard(-1)
				i+=1
			if not -1 in modlvls and 0 in mods and len(mods) == 1:
				mods.add(-1)
			for pot, skill, mastery, mod, modlvl in itertools.product(pots, skills, masteries, mods, modlvls):
				healer_message += (healer_dict[args[tmp]](lvl,pot, skill, mastery,mod,modlvl,targets,buffs,boost)).skill_hps() + "\n"
				contains_data += 1
				if contains_data > 19: break
			if contains_data > 19: break
		elif args[i] in ["b","buff","buffs"]:
			i+=1
			buffcount=0
			buffs=[0,0,0,0]
			while i < entries and buffcount < 4:
				if args[i]=="":
					pass
				else:
					try:
						buffs[buffcount] = int(args[i])
						buffcount +=1
					except ValueError:
						break
				if buffcount == 1: buffs[0] = buffs[0]/100
				if buffcount == 4: buffs[3] = max(0, buffs[3])/100
				i+=1
			i-=1
		elif args[i] in ["t","target","targets"]:
			i+=1
			targets = 1
			while i < entries:
				try:
					targets = int(args[i])
				except ValueError:
					break
				i+=1
			i-=1
		elif args[i] in ["t1","t2","t3","t4","t5","t6","t7","t8","t9"]: targets = int(args[i][1])	
		elif args[i] in ["lvl","level","lv"]:
			i+=1
			lvl = -10
			while i < entries:
				if args[i]=="":
					pass
				else:
					try:
						lvl = int(args[i])
					except ValueError:
						break
				i+=1
			i-=1
		elif args[i] in ["sp","boost","recovery","spboost","spbuff","buffsp"]:
			i+=1
			boost = 0
			while i < entries:
				if args[i]=="":
					pass
				else:
					try:
						boost = float(args[i])
					except ValueError:
						break
				i+=1
			i-=1								
		elif args[i] == "":
			continue
		elif len(args[i]) < 3:
			parsing_error = True
			error_message += " " + args[i] + ","
		elif args[i][0] in ["1","2","3","4","5","6","7","8","9"] and not args[i][-1] in ["0","1","2","3","4","5","6","7","8","9"]: #try to fix a missing space after an integer (should not have a leading 0. if the entire number is 0: should be ignorable)
			numberpos = 1
			while args[i][numberpos] in ["0","1","2","3","4","5","6","7","8","9","."]:
				numberpos += 1
			temp = args[i]
			args[i] = args[i][numberpos:]
			args.insert(i,temp[:numberpos])
			entries += 1
			backsteps = 1
			while backsteps < 5:
				try:
					int(args[i-backsteps])
					backsteps +=1
				except ValueError:
					backsteps +=1
					break
			i-=backsteps
		elif not args[i][0].isdigit() and  args[i][-2].isdigit(): #try to fix a missing space after buff/hits etc
			numberpos = 2
			wordlen = len(args[i])
			while args[i][-numberpos].isdigit():
				numberpos += 1
			temp = args[i]
			args[i] = args[i][(wordlen-numberpos+1):]
			args.insert(i,temp[:(wordlen-numberpos+1)])
			entries += 1
			i -= 1
		else:
			my_keys = list(healer_dict.keys()) ### Try some autocorrection
			#lev_dist = 1000
			errorlimit = 0
			promptlength = len(args[i])
			prompt = args[i]
			found_fit = False
			optimizer = False
			optimize_error = -10
			if promptlength > 3: errorlimit = 1
			if promptlength > 5: errorlimit = 2
			if promptlength > 8: errorlimit = 3
			if promptlength < 15:
				for key in my_keys:
					if optimizer:
						if df.levenshtein(key, prompt) < optimize_error: #dont just stop at the first fit, but rather at the best fit.
							args[i] = key
							optimize_error = df.levenshtein(key, prompt)
					elif df.levenshtein(key, prompt) <= errorlimit:
						args[i] = key
						i-=1
						optimizer = True
						optimize_error = df.levenshtein(key, prompt)
						found_fit = True
			if not found_fit:
				parsing_error = True
				error_message += " " + args[i] + ","
		
		i+=1	
	if contains_data == 0: return DiscordSendable()
	
	healer_message = "Heals per second - **skill active**/skill down/*averaged* \n" + healer_message		
	if contains_data > 19 : healer_message = healer_message + "Only the first 20 entries are shown."
	return DiscordSendable(healer_message)
