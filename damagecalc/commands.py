import io
import signal
import multiprocessing
from typing import Callable, List
import copy
import base64

import discord
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image

import damagecalc.utils as utils
from damagecalc.utils import DiscordSendable
from damagecalc.damage_formulas import op_dict
from damagecalc.healing_formulas import healer_dict

#These are a bunch of bad words that should not be used by the bot and might even get it banned. I wanted them included in the script itself, 
#but I also do not want them in clear text in an open source project, hence the base64 encoding.
encoded_profanity = ['bmVncm8=', 'bmlnZ2Vy', 'bmVnZXI=', 'bmlnbm9n', 'bmlnZ2E=', 'bmlnZXI=', 'bmlnYQ==', 'YWRvbGY=', 'aGl0bGVy', 'ZmFnZ290', 'Y3VudA==', 'c2hpdA==', 'ZnVjaw==', 'bmF6aQ==', 'cmV0YXJk', 'ZG93bnk=', 'Yml0Y2g=', 'd2hvcmU=', 'c2x1dA==', 'cmFwZQ==', 'cmFwaXN0', 'cGVkbw==']
profanity = [base64.b64decode(wort.encode("utf-8")).decode("utf-8") for wort in encoded_profanity]

modifiers = ["s0","s1","s2","s3","e0","e1","e2","p0","p1","p2","p3","p4","p5","p6","pot0","pot1","pot2","pot3","pot4","pot5","pot6","m0","m1","m2","m3","0","1","2","3","mod0","mod1","mod2","mod3","modlvl","modlvl1","modlvl2","modlvl3","modlv","modlv1","modlv2","modlv3","mod","x0","y0","x","x1","x2","x3","y","y1","y2","y3","d","a","d1","d2","d3","modx1","modx2","modx3","mody1","mody2","mody3","modd1","modd2","modd3","moda1","moda2","moda3","mod1","mod2","mod3","modx","mody","modd","moda","module","no","nomod","s1m0","s1m1","s1m2","s1m3","s2m0","s2m1","s2m2","s2m3","s3m0","s3m1","s3m2","s3m3","sl7","s7","slv7","l7","lv7","sl1","slv1","sl2","slv2","sl3","slv3","sl4","slv4","sl5","slv5","sl6","slv6"]
prompts = ["hide", "legend","big", "beeg", "large","repos", "reposition", "bottom", "left", "botleft", "position", "change", "changepos","small","font","tiny","sp","boost","recovery","spboost","spbuff","buffsp","numbers","dmgnumbers","damage","damagenumbers","delta","alpha",
		   "color","colour","colorblind","colourblind","blind","g:","global","global:","t","target","targets","t1","t2","t3","t4","t5","t6","t7","t8","t9","r","res","resis","resistance","l","low","h","high","low1","l1","lowtrait","traitlow","high1","h1","hightrait","traithigh","low2","l2","lowtalent","talentlow","lowtalent1","talent1low","high2","h2","hightalent","talenthigh","hightalent1","talent1high","low3","l3","talentlow","lowtalent2","talent2low","high3","h3","talenthigh","hightalent2","talent2high","low4","l4","lows","slow","lowskill","skilllow","high4","h4","highs","shigh","highskill","skillhigh","low5","l5","lowm","mlow","lowmod","modlow","lowmodule","modulelow","high5","h5","highm","mhigh","highmod","modhigh","highmodule","modulehigh","lowtalents","hightalents",
			"d","def","defense","shred","shreds","debuff","ignore","resshred","resdebuff","shredres","debuffres","reshred","resignore","defshred","defdebuff","shreddef","debuffdef","defignore","basebuff","baseatk","base","bbuff","batk","c0", "c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8", "c9", "c10", "c11", "c12", "c13", "c14", "c15","c16", "c17", "c18", "c19", "c20", "c21", "c22", "c23", "c24", "c25", "c26", "c27", "c28", "c29", "c30", "c31",
			 "lvl","level","lv","iaps","bonk","received","hits","hit","conditionals", "conditional","variation","variations","maxdef","limit","range","scale","healing","healingbonus","hb","bonus","avg","avgdmg","average","averagedmg","hp","hitpoints","stage","stage2","highlight","mark","marked","feature","alpha","is","modalpha","moddelta","situational", 
			  "b","buff","buffs","maxres","reslimit","limitres","scaleres","resscale","fixdef","fixeddef","fixdefense","fixeddefense","setdef","setdefense","split","split2","fixres","fixedres","fixresistance","fixedresistance","setres","resresistance","set","fix","fixed",
			   "atk","0%","attack","fragile","frag","dmg","aspd","apsd","speed","atkspeed","attackspeed","atkspd","reset","reset:","total","totaldmg","enemy","enemy2","chapter","chapter2","trust","skilllvl","skilllevel","skilllv","skillvl","skillevel","skillv","slv","slevel","slvl"]

#If some smartass requests more than 40 operators to be drawn
bot_mad_message = ["excuse me, what? <:blemi:1077269748972273764>", "why you do this to me? <:jessicry:1214441767005589544>", "how about you draw your own graphs? <:worrymad:1078503499983233046>", "<:pepe_holy:1076526210538012793>", "spare me, please! <:harold:1078503476591607888>"]

def calc_command(args: List[str]) -> DiscordSendable:
	manager = multiprocessing.Manager()
	return_dict = manager.dict()
    
	process = multiprocessing.Process(target=utils.calc_message, args=((' '.join(args)), return_dict))
	process.start()
    
    #if the process is still running after 2 seconds, kill it
	process.join(2)
	if process.is_alive():
		process.terminate()
		process.join()
		return DiscordSendable("Exceeded reasonable computation time.")
    
	return DiscordSendable(str(return_dict.get('result', 'No result')))

def calc_command_linux(args: List[str]) -> DiscordSendable:
	def handler(signum, frame):
		raise TimeoutError("Operation timed out")
	signal.signal(signal.SIGALRM, handler)
	signal.alarm(2)
	try:
		result = utils.calc_message((' '.join(args)), dict())
	except TimeoutError:
		result = "Exceeded reasonable computation time."
	finally:
		signal.alarm(0)
	return DiscordSendable(str(result))#return_dict.get('result', 'No result'))

def dps_command(args: List[str])-> DiscordSendable:
	if len(args) == 0: return DiscordSendable("use !ops to see the available operators, use !guide for details on the prompts")
	global_parameters = utils.PlotParametersSet()
	already_drawn_ops = []
	plt.clf()
	plt.style.use('default')
	plot_size = 4 #plot height in inches
	show = True
	bottomleft = False
	textsize = 10
	short_names = False

	#Adding the title prompt
	for i, word in enumerate(args):
		if word in ["text", "title"]:
			plot_title = f"{' '.join(args[i+1:])}"
			add_title = True
			for bad_word in profanity:
				if bad_word in plot_title.lower():
					add_title = False
			if add_title: plt.title(plot_title)
			args = args[:i]

	args = [str(item).lower() for item in args]

	#some more error correction with wrong spaces
	for i in range(len(args)-1):
		if args[i] == "no" or args[i+1] == "alter" or args[i] == "-" or (args[i] in ["la","zuo"] and args[i+1] in ["pluma","le"]):
			args[i] = args[i]+args[i+1]
			args[i+1] = "null"
		if args[i+1].startswith("+"): args[i+1] = args[i+1][1:]
	
	#error correction: remove illegal inputs
	for i in range(len(args)-1):
		if args[i] in ["+",",","!dps"]:
			args[i] = "null"
		elif args[i][0] in ["+",","]:
			args[i] = args[i][1:]
		elif args[i][-1] in ["+",","]:
			args[i] = args[i][:-1]

	#fix typos in operator names
	for i in range(len(args)):
		if not args[i] in prompts:
			if utils.fix_typos(args[i], op_dict.keys()) != "":
				args[i] = utils.fix_typos(args[i], op_dict.keys())
	
	#fixing missing spaces
	entries = len(args)
	j = 0
	while j < entries:
		if args[j] in prompts or args[j] in op_dict.keys() or args[j] in modifiers or utils.is_float(args[j]):
			pass
		elif args[j][0] in "-123456789" and not args[j][-1] in "0123456789%" and not args[j].endswith("cm"): #missing space like buff 90exusiai
			numberpos = 1
			while args[j][numberpos] in "-0123456789.%":
				numberpos += 1
			temp = args[j]
			args[j] = args[j][numberpos:]
			args.insert(j,temp[:numberpos])
			entries += 1
		elif not args[j][0] in "-123456789" and args[j][-1] in "0123456789%" and (j == 0 or not args[j-1] in ["stage","stage2","enemy","enemy2","chapter","chapter2"]): #missing space like aspd100 gg
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
		if args[i] not in op_dict.keys() and args[i] not in prompts and len(args[i]) > 3 and not utils.is_float(args[i]):
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
	if len(scopes) > 40: return(DiscordSendable())

	#Fixing the order of input prompts (such as !dps horn 5 targets) TODO: so far only the first error in each scope is corrected. should be enough for most cases though
	if (utils.is_float(args[0]) or args[0].endswith("%")) and args[1] in ["t","target","targets","def","defense","res","resistance","hits","hit","aspd","fragile","atk"] and not args[0] in "0123":
		tmp = args[1]
		args[1] = args[0]
		args[0] = tmp
	for i in range(1,len(args)-2):
		if i in scopes and (utils.is_float(args[i+1]) or args[i+1].endswith("%")) and args[i+2] in ["t","target","targets","def","defense","res","resistance","hits","hit","aspd","fragile","atk"]  and not args[i+1] in "0123":
			tmp = args[i+1]
			args[i+1] = args[i+2]
			args[i+2] = tmp

	
	plot_numbers = 0
	###################################################################### The actual potting happens here, complicated by Muelsyse cloning the previous op
	#getting setting the plot parameters and plotting the units
	utils.parse_plot_essentials(global_parameters, args)
	previous_operator = None
	previous_parameters = None
	for i in range(len(scopes)-1):
		if scopes[i] in local_scopes:
			local_parameters = copy.deepcopy(global_parameters)
			if (scopes[i]+1) not in scopes:
				utils.parse_plot_parameters(local_parameters, args[scopes[i]:scopes[i+1]])
			for parameters in local_parameters.get_plot_parameters():
				if op_dict[args[scopes[i]]].__name__.startswith("Muel") and previous_operator != None: parameters.input_kwargs["prev_op"] = previous_operator(previous_parameters)
				if utils.apply_plot(op_dict[args[scopes[i]]],parameters,already_drawn_ops,plot_numbers,short_names):
					if not op_dict[args[scopes[i]]].__name__.startswith("Muel"): 
						previous_operator = op_dict[args[scopes[i]]]
						previous_parameters = parameters
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

	#find unused parts for the error message
	error_message = "" 
	test_parameters = utils.PlotParametersSet()
	unparsed_inputs = utils.parse_plot_parameters(test_parameters, args) &  utils.parse_plot_essentials(test_parameters, args)
	for pos in unparsed_inputs:
		if not args[pos] in op_dict.keys() and not pos in scopes[1:-1] and not args[pos] in ["short", "hide", "legend","big", "beeg", "large","repos", "reposition", "bottom", "left", "botleft", "position", "change", "changepos","small","font","tiny","color","colour","colorblind","colourblind","blind","numbers","dmgnumbers","damage","damagenumbers","null"]:
			error_message += (args[pos]+", ")
	
	parsing_error = False
	if error_message != "":
		parsing_error = True
		error_message = "The following inputs are not part of the standard prompts and may have had no effect: " + error_message[:-2]
		for bad_word in profanity:
			if bad_word in error_message.lower():
				error_message = "Could not use some of the prompts."
				break


	#prevent the legend from messing up the graphs format, aka forcing the legend to be small enough to fit inside the plot
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
	
	#Adding the axis description
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
			ph = len(enemies)-1
			mim_size = max(ph,12)
			offset = 0.2 if ph < 12 else 0.4
			img = np.asarray(Image.open('Database/images/' + enemies[i][5] + '.png'))
			if plot_size == 4: ax = fig.add_axes([offset*xl+1.1*(xh-xl)/ph*(i), 0 ,2.1*(xh-xl)/mim_size ,2.1*(xh-xl)/mim_size])
			else: ax = fig.add_axes([0.1*xl+1.22*(xh-xl)/ph*(i), 0 ,2.1*(xh-xl)/mim_size ,2.1*(xh-xl)/mim_size])
			ax.axison = False
			ax.imshow(img)

	fig = plt.gcf()
	fig.set_size_inches(2 * plot_size, plot_size)
	plt.tight_layout()
	if graph_type == 5: plt.subplots_adjust(bottom=1.7/max(12,len(enemies)))
	
	#Generate image and send it to the channel
	buf = io.BytesIO()
	plt.savefig(buf,format='png')
	buf.seek(0)
	file = discord.File(buf, filename='plot.png')
	plt.close()
	if parsing_error:
		return DiscordSendable(content=error_message, file=file)
	else:
		return DiscordSendable(file=file)


def hps_command(args: List[str]) -> DiscordSendable:
	global_parameters = utils.PlotParametersSet()
	healer_message = ""

	args = [str(item).lower() for item in args]

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
	if (utils.is_float(args[0]) or args[0].endswith("%")) and args[1] in ["t","target","targets","def","defense","res","resistance","hits","hit","aspd","fragile","atk"] and not args[0] in "0123":
		tmp = args[1]
		args[1] = args[0]
		args[0] = tmp
	for i in range(1,len(args)-2):
		if i in scopes and (utils.is_float(args[i+1]) or args[i+1].endswith("%")) and args[i+2] in ["t","target","targets","def","defense","res","resistance","hits","hit","aspd","fragile","atk"]  and not args[i+1] in "0123":
			tmp = args[i+1]
			args[i+1] = args[i+2]
			args[i+2] = tmp

	
	plot_numbers = 0
	#getting setting the plot parameters and plotting the units
	for i in range(len(scopes)-1):
		if scopes[i] in local_scopes:
			local_parameters = copy.deepcopy(global_parameters)
			if (scopes[i]+1) not in scopes:
				utils.parse_plot_parameters(local_parameters, args[scopes[i]:scopes[i+1]])
			for parameters in local_parameters.get_plot_parameters():
				new_text = (healer_dict[args[scopes[i]]](parameters, **parameters.input_kwargs)).skill_hps() + "\n"
				if not new_text in healer_message:
					healer_message += new_text
					plot_numbers += 1
					if plot_numbers > 19: break
		elif scopes[i] in global_scopes:
			if args[scopes[i]] in ["reset","reset:"]:
				global_parameters = utils.PlotParametersSet()
			utils.parse_plot_parameters(global_parameters, args[scopes[i]:scopes[i+1]])
		if plot_numbers > 19: break
	if plot_numbers == 0: return DiscordSendable() #maybe return a "no operator found, use !guide" hint instead?

	#find unused parts
	error_message = "" 
	test_parameters = utils.PlotParametersSet()
	unparsed_inputs = utils.parse_plot_parameters(test_parameters, args) &  utils.parse_plot_essentials(test_parameters, args)
	for pos in unparsed_inputs:
		if not args[pos] in healer_dict.keys() and not pos in scopes[1:-1] and not args[pos] in ["short", "hide", "legend","big", "beeg", "large","repos", "reposition", "bottom", "left", "botleft", "position", "change", "changepos","small","font","tiny","color","colour","colorblind","colourblind","blind"]:
			error_message += (args[pos]+", ")
	
	parsing_error = False
	if error_message != "":
		parsing_error = True
		error_message = "Could not use the following prompts: " + error_message[:-2]
		for bad_word in profanity:
			if bad_word in error_message.lower():
				error_message = "Could not use some of the prompts"
				break

	healer_message = "Heals per second - **skill active**/skill down/*averaged* \n" + healer_message
	if parsing_error:
		healer_message =  error_message + "\n" + healer_message
	if plot_numbers > 19 : healer_message = healer_message + "Only the first 20 entries are shown."
	return DiscordSendable(healer_message)


def stage_command(args: List[str]) -> DiscordSendable:
	from Database.JsonReader import StageData
	stage_data = StageData()
	if len(args) == 0:
		text = "Use !stage <prefix> to get a list of the available stages. You can then use stage <stageLabel> as a prompt for !dps or just write !stage <stageLabel> to see def/res numbers. Note that !dps with a stage takes up to 90s on the first call(afterwards ~8s) \nHere are the available prefixes:\n"
		stage_prefixes = list(stage_data.stage_prefixes)
		stage_prefixes.sort()
		for entry in stage_prefixes:
			text += str(entry) + ", "
		return DiscordSendable(text[:-2])

	if args[0].upper() in stage_data.stages.keys():
			import os
			import subprocess
			#if os.path.exists('media/images/StageAnimator/StageAnimator_ManimCE_v0.19.0.png'):
			#	os.remove('media/images/StageAnimator/StageAnimator_ManimCE_v0.19.0.png')

			#download images
			#utils.get_enemies(args[0])
			#possible todo: add enemy info to image
			#os.system(f"STAGE_NAME={args[0]} manim -ql Database/StageAnimator.py StageAnimator")
			subprocess.run(f"STAGE_NAME={args[0]} manim -ql Database/StageAnimator.py StageAnimator", shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

			#return the output
			file = discord.File(fp = 'media/images/StageAnimator/StageAnimator_ManimCE_v0.19.0.png', filename = 'media/images/StageAnimator/StageAnimator_ManimCE_v0.19.0.png')

			return DiscordSendable(file=file)

	
	if len(stage_data.get_stages(args[0])) > 0:
		text = "These are the available stages:\n"
		for entry in stage_data.get_stages(args[0]):
			text += str(entry) + ", "
		return DiscordSendable(text[:-2])
	return DiscordSendable()

def animate_command(args: List[str]) -> DiscordSendable:
	from Database.JsonReader import StageData
	stage_data = StageData()
	if args[0].upper() in stage_data.stages.keys():
		import os
		#check if the file already exists
		if not os.path.isfile(f'media/videos/StageAnimator/480p15/{args[0].upper()}.mp4'):
			#download images
			utils.get_enemies(args[0])
			#Do the animation
			os.system(f"STAGE_NAME={args[0]} DO_ANIM='YES' manim -ql Database/StageAnimator.py StageAnimator")
			#rename the file
			os.rename('media/videos/StageAnimator/480p15/StageAnimator.mp4', f'media/videos/StageAnimator/480p15/{args[0].upper()}.mp4')

		file = discord.File(fp = f'media/videos/StageAnimator/480p15/{args[0].upper()}.mp4', filename=f'media/videos/StageAnimator/480p15/{args[0].upper()}.mp4')
		return DiscordSendable(file=file)
	else:
		return DiscordSendable("Not a valid stage, check !stage to see available stages")