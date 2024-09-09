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
try:
	from damagecalc.black_list import profanity
except:
	profanity = []

modifiers = ["s1","s2","s3","e0","e1","e2","p1","p2","p3","p4","p5","p6","m0","m1","m2","m3","0","1","2","3","mod0","mod1","mod2","mod3","modlvl","modlvl1","modlvl2","modlvl3","modlv","modlv1","modlv2","modlv3","mod","x0","y0","x","x1","x2","x3","y","y1","y2","y3","d","d1","d2","d3","modx1","modx2","modx3","mody1","mody2","mody3","modd1","modd2","modd3","mod1","mod2","mod3","modx","mody","modd","module","no","nomod","s1m0","s1m1","s1m2","s1m3","s2m0","s2m1","s2m2","s2m3","s3m0","s3m1","s3m2","s3m3","sl7","s7","slv7","l7","lv7","sl1","slv1","sl2","slv2","sl3","slv3","sl4","slv4","sl5","slv5","sl6","slv6"]
prompts = ["hide", "legend","big", "beeg", "large","repos", "reposition", "bottom", "left", "botleft", "position", "change", "changepos","small","font","tiny","sp","boost","recovery","spboost","spbuff","buffsp",
		   "color","colour","colorblind","colourblind","blind","g:","global","global:","t","target","targets","t1","t2","t3","t4","t5","t6","t7","t8","t9","r","res","resis","resistance","l","low","h","high","low1","l1","lowtrait","traitlow","high1","h1","hightrait","traithigh","low2","l2","lowtalent","talentlow","lowtalent1","talent1low","high2","h2","hightalent","talenthigh","hightalent1","talent1high","low3","l3","talentlow","lowtalent2","talent2low","high3","h3","talenthigh","hightalent2","talent2high","low4","l4","lows","slow","lowskill","skilllow","high4","h4","highs","shigh","highskill","skillhigh","low5","l5","lowm","mlow","lowmod","modlow","lowmodule","modulelow","high5","h5","highm","mhigh","highmod","modhigh","highmodule","modulehigh","lowtalents","hightalents",
			"d","def","defense","shred","shreds","debuff","ignore","resshred","resdebuff","shredres","debuffres","reshred","resignore","defshred","defdebuff","shreddef","debuffdef","defignore","basebuff","baseatk","base","bbuff","batk",
			 "lvl","level","lv","iaps","bonk","received","hits","hit","conditionals", "conditional","variation","variations","maxdef","limit","range","scale",
			  "b","buff","buffs","maxres","reslimit","limitres","scaleres","resscale","fixdef","fixeddef","fixdefense","fixeddefense","setdef","setdefense","split","split2","fixres","fixedres","fixresistance","fixedresistance","setres","resresistance","set","fix","fixed",
			   "atk","attack","fragile","frag","dmg","aspd","speed","atkspeed","attackspeed","atkspd","reset","reset:","total","totaldmg","enemy","enemy2","chapter","chapter2","trust","skilllvl","skilllevel","skilllv","skillvl","skillevel","skillv","slv","slevel","slvl"]

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

def dps_command(args: List[str])-> DiscordSendable:
	global_parameters = utils.PlotParametersSet()
	already_drawn_ops = []
	plt.clf()
	plt.style.use('default')
	plot_size = 4 #plot height in inches
	show = True
	bottomleft = False
	textsize = 10
	short_names = False

	#Adding the text prompt
	for i, word in enumerate(args):
		if word in ["text", "title"]:
			plot_title = f"{' '.join(args[i+1:])}"
			add_title = True
			for bad_word in profanity:
				if bad_word in plot_title.lower():
					add_title = False
			if add_title: plt.title(plot_title)
			args = args[:i]

	#fix typos in operator names
	for i in range(len(args)):
		if utils.fix_typos(args[i], op_dict.keys()) != "":
			args[i] = utils.fix_typos(args[i], op_dict.keys())
	
	#fixing missing spaces
	entries = len(args)
	j = 0
	while j < entries:
		if args[j] in prompts or args[j] in op_dict.keys() or args[j] in modifiers or utils.is_float(args[j]):
			pass
		elif args[j][0] in "-123456789" and not args[j][-1] in "0123456789%": #missing space like buff 90exusiai
			numberpos = 1
			while args[j][numberpos] in "-0123456789.%":
				numberpos += 1
			temp = args[j]
			args[j] = args[j][numberpos:]
			args.insert(j,temp[:numberpos])
			entries += 1
		elif not args[j][0] in "-123456789" and args[j][-1] in "0123456789%": #missing space like aspd100 gg
			numberpos = 2
			wordlen = len(args[j])
			while args[j][-numberpos] in "-0123456789.%":
				numberpos += 1
			temp = args[j]
			args[j] = args[j][(wordlen-numberpos+1):]
			args.insert(j,temp[:(wordlen-numberpos+1)])
			entries += 1
		j += 1
	
	#fix typos in prompts
	for i in range(len(args)):
		if args[i] not in op_dict.keys() and args[i] not in prompts and len(args[i]) > 3:
			for prompt in prompts:
				if utils.levenshtein(args[i],prompt) == 1:
					args[i] = prompt
					break	

	#Get plot settings
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
		elif word in ["short"]:
			short_names = True

	#Find scopes where which parameter set is active (global vs local)
	global_scopes = [0]
	local_scopes = []
	for i, arg in enumerate(args):
		if arg in op_dict.keys():
			local_scopes.append(i)
		elif arg in ["g:","global","global:","reset","reset:"]:
			global_scopes.append(i)
	scopes = list(set(global_scopes + local_scopes))
	scopes.sort()
	scopes.append(len(args))

	#Fixing the order of input prompts (such as !dps horn 5 targets) TODO: so far only the first error in each scope is corrected. should be enough for most cases though
	if (utils.is_float(args[0]) or args[0].endswith("%")) and args[1] in ["t","target","targets","def","defense","res","resistance","limit","maxres","maxdef","hits","hit","aspd","fragile","atk"] and not args[0] in "0123":
		tmp = args[1]
		args[1] = args[0]
		args[0] = tmp
	for i in range(1,len(args)-2):
		if i in scopes and (utils.is_float(args[i+1]) or args[i+1].endswith("%")) and args[i+2] in ["t","target","targets","def","defense","res","resistance","limit","maxres","maxdef","hits","hit","aspd","fragile","atk"]  and not args[i+1] in "0123":
			tmp = args[i+1]
			args[i+1] = args[i+2]
			args[i+2] = tmp

	
	plot_numbers = 0
	#getting setting the plot parameters and plotting the units
	utils.parse_plot_essentials(global_parameters, args)
	for i in range(len(scopes)-1):
		if scopes[i] in local_scopes:
			local_parameters = copy.deepcopy(global_parameters)
			if (scopes[i]+1) not in scopes:
				utils.parse_plot_parameters(local_parameters, args[scopes[i]:scopes[i+1]])
			for parameters in local_parameters.get_plot_parameters():
				if utils.apply_plot(op_dict[args[scopes[i]]],parameters,already_drawn_ops,plot_numbers,short_names):
					plot_numbers += 1
					if plot_numbers > 40:
						plt.close()
						l = len(bot_mad_message)
						return DiscordSendable(bot_mad_message[np.random.randint(0,l)])
		elif scopes[i] in global_scopes:
			if args[scopes[i]] in ["reset","reset:"]:
				global_parameters = utils.PlotParametersSet()
				utils.parse_plot_essentials(global_parameters, args)
			utils.parse_plot_parameters(global_parameters, args[scopes[i]:scopes[i+1]])
	if plot_numbers == 0: return DiscordSendable() #maybe return a "no operator found, use !guide" hint instead?

	#find unused parts
	parsing_errors = "" 
	test_parameters = utils.PlotParametersSet()
	unparsed_inputs = utils.parse_plot_parameters(test_parameters, args) &  utils.parse_plot_essentials(test_parameters, args)
	for pos in unparsed_inputs:
		if not args[pos] in op_dict.keys() and not pos in scopes[1:-1] and not args[pos] in ["short", "hide", "legend","big", "beeg", "large","repos", "reposition", "bottom", "left", "botleft", "position", "change", "changepos","small","font","tiny","color","colour","colorblind","colourblind","blind"]:
			parsing_errors += (args[pos]+", ")
	
	parsing_error = False
	if parsing_errors != "":
		parsing_error = True
		parsing_errors = "Could not use the following prompts: " + parsing_errors[:-2]
		for bad_word in profanity:
			if bad_word in parsing_errors.lower():
				parsing_errors = "Could not use some of the prompts"
				break



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
	enemies = global_parameters.enemies
	enemy_key = global_parameters.enemy_key

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

	fig = plt.gcf()
	fig.set_size_inches(2 * plot_size, plot_size)
	plt.tight_layout()
	
	#Generate image and send it to the channel
	buf = io.BytesIO()
	plt.savefig(buf,format='png')
	buf.seek(0)
	file = discord.File(buf, filename='plot.png')
	plt.close()
	#return DiscordSendable(file=file)
	if parsing_error:
		return DiscordSendable(content=parsing_errors, file=file)
	else:
		return DiscordSendable(file=file)


def hps_command_new(args: List[str]) -> DiscordSendable:
	global_parameters = utils.PlotParametersSet()
	healer_message = ""

	#fix typos in operator names
	for i in range(len(args)):
		if utils.fix_typos(args[i], healer_dict.keys()) != "":
			args[i] = utils.fix_typos(args[i], healer_dict.keys())
	
	#fixing missing spaces
	entries = len(args)
	j = 0
	while j < entries:
		if args[j] in prompts or args[j] in healer_dict.keys() or args[j] in modifiers or utils.is_float(args[j]):
			pass
		elif args[j][0] in "-123456789" and not args[j][-1] in "0123456789%": #missing space like buff 90exusiai
			numberpos = 1
			while args[j][numberpos] in "-0123456789.%":
				numberpos += 1
			temp = args[j]
			args[j] = args[j][numberpos:]
			args.insert(j,temp[:numberpos])
			entries += 1
		elif not args[j][0] in "-123456789" and args[j][-1] in "0123456789%": #missing space like aspd100 gg
			numberpos = 2
			wordlen = len(args[j])
			while args[j][-numberpos] in "-0123456789.%":
				numberpos += 1
			temp = args[j]
			args[j] = args[j][(wordlen-numberpos+1):]
			args.insert(j,temp[:(wordlen-numberpos+1)])
			entries += 1
		j += 1
	
	#fix typos in prompts
	for i in range(len(args)):
		if args[i] not in healer_dict.keys() and args[i] not in prompts and len(args[i]) > 3:
			for prompt in prompts:
				if utils.levenshtein(args[i],prompt) == 1:
					args[i] = prompt
					break	


	#Find scopes where which parameter set is active (global vs local)
	global_scopes = [0]
	local_scopes = []
	for i, arg in enumerate(args):
		if arg in healer_dict.keys():
			local_scopes.append(i)
		elif arg in ["g:","global","global:","reset","reset:"]:
			global_scopes.append(i)
	scopes = list(set(global_scopes + local_scopes))
	scopes.sort()
	scopes.append(len(args))

	#Fixing the order of input prompts (such as !dps horn 5 targets) TODO: so far only the first error in each scope is corrected. should be enough for most cases though
	if (utils.is_float(args[0]) or args[0].endswith("%")) and args[1] in ["t","target","targets","def","defense","res","resistance","limit","maxres","maxdef","hits","hit","aspd","fragile","atk"] and not args[0] in "0123":
		tmp = args[1]
		args[1] = args[0]
		args[0] = tmp
	for i in range(1,len(args)-2):
		if i in scopes and (utils.is_float(args[i+1]) or args[i+1].endswith("%")) and args[i+2] in ["t","target","targets","def","defense","res","resistance","limit","maxres","maxdef","hits","hit","aspd","fragile","atk"]  and not args[i+1] in "0123":
			tmp = args[i+1]
			args[i+1] = args[i+2]
			args[i+2] = tmp

	
	plot_numbers = 0
	#getting setting the plot parameters and plotting the units
	utils.parse_plot_essentials(global_parameters, args)
	for i in range(len(scopes)-1):
		if scopes[i] in local_scopes:
			local_parameters = copy.deepcopy(global_parameters)
			if (scopes[i]+1) not in scopes:
				utils.parse_plot_parameters(local_parameters, args[scopes[i]:scopes[i+1]])
			for parameters in local_parameters.get_plot_parameters():
				new_text = (healer_dict[args[scopes[i]]](parameters)).skill_hps() + "\n"
				if not new_text in healer_message:
					healer_message += new_text
					plot_numbers += 1
		elif scopes[i] in global_scopes:
			if args[scopes[i]] in ["reset","reset:"]:
				global_parameters = utils.PlotParametersSet()
				utils.parse_plot_essentials(global_parameters, args)
			utils.parse_plot_parameters(global_parameters, args[scopes[i]:scopes[i+1]])
	if plot_numbers == 0: return DiscordSendable() #maybe return a "no operator found, use !guide" hint instead?

	#find unused parts
	parsing_errors = "" 
	test_parameters = utils.PlotParametersSet()
	unparsed_inputs = utils.parse_plot_parameters(test_parameters, args) &  utils.parse_plot_essentials(test_parameters, args)
	for pos in unparsed_inputs:
		if not args[pos] in healer_dict.keys() and not pos in scopes[1:-1] and not args[pos] in ["short", "hide", "legend","big", "beeg", "large","repos", "reposition", "bottom", "left", "botleft", "position", "change", "changepos","small","font","tiny","color","colour","colorblind","colourblind","blind"]:
			parsing_errors += (args[pos]+", ")
	
	parsing_error = False
	if parsing_errors != "":
		parsing_error = True
		parsing_errors = "Could not use the following prompts: " + parsing_errors[:-2]
		for bad_word in profanity:
			if bad_word in parsing_errors.lower():
				parsing_errors = "Could not use some of the prompts"
				break

	if parsing_error:
		healer_message = parsing_errors + "\n" + healer_message
	healer_message = "Heals per second - **skill active**/skill down/*averaged* \n" + healer_message		
	if plot_numbers > 19 : healer_message = healer_message + "Only the first 20 entries are shown."
	return DiscordSendable(healer_message)





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
