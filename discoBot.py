# First of all: Don't Judge me for this code, I know it's neither clean nor efficient, but with the limited amount of thought I put into it, this is the best architecture I could come up with.
# In order for the bot to work you need a "token.txt" file in the same directory as this file, which should contain your discord token (see last 3 lines of this file). Also Change line 48!

#TODO: Easy but tedious tasks that just take a lot of time
# implement the missing operators
# implement more healers (and probably fix the kwargs situation before many more are added)
# implement various total_dmg methods for operators

#TODO: specific Minijobs that really should be done asap
# hoederer/qiubai: low dmg showing their dps with their own application rate of the conditionals, instead of just ignoring it
# Mudrock: include the SP gains from the module for S2 damage calculations
# platinum: fix the dmg bonus, it counts from 0 to 2.5 seconds right now, which should be from 1 to 2.5 seconds i think
# kjera: fix freeze rate, applying cold on a frozen enemy does NOT refresh the duration
# Wisadel: Add S1 and S2, and maybe double check S3's aoe
# kaltsit: the true damage of S3 cant handle changes in max res
# add new modules for ifrit, gladiia.
# muelsyse melee clone. get name is bugged (just compare low mumu to conditionals mumu)

#TODO: bigger changes that may be complicated or even unrealistic
# add average_dmg methods (which include skill down time and ramp up times etc)
# clean up plotting, so that the parts are not scattered around in the code
# efficiency boost: restructure everything so that the atkbuff calculations are done only when instancing the operator, instead of with every call of the skilldps method (may interfere with bbuff)
# add !disclaimer prompt talking about the limits of the bots
# add detail prompt to give an explanation text for complicated graphs (like assumptions for santallas s2 hit-/freezeratio)
# change high/low into high/low/default for unrealistic conditionals (aka chongyue) -> better: add plus ultra prompt to show unrealistically high dmg
# stacks prompt (mlynar, lapluma, gavialter) to increment certain conditionals
# improve enemy prompt: still not good as it is (better formatting, showing enemy hp)
# add kwargs to make the bot understand more text (like "vs heavy" for rosa or "no mines" for ela)
# first collect the operators(aka parse through the entire input) and THEN draw the stuff.
# make it visible in the plot, where which part of the name comes from. (example: typhons text "all crits" gets turned green, green standing for talent2, so people know its lowtalent2 that removes it)
# make variable naming more consistent

import io
import itertools
import os
import signal
import subprocess

import discord
import matplotlib.pyplot as plt
import nltk
import numpy as np
from PIL import Image

import damageformulas as df
import healingformulas as hf

##############################################
#Bot Settings for the channels it will respond to
valid_channels = ['operation-room','bot-spam']
respond_to_dm = True

intents = discord.Intents.all()
client = discord.Client(intents=intents)

onPi = True
#this part is only needed because i use the same token on my pc for my testserver, whereas the script usually runs on a raspberry pi
try:
	with open("testrun.txt") as file:
		_ = file.readline()
		onPi = False
except:
	pass

#Operator data from the other scripts
op_dict = df.op_dict
operators = df.operators
healer_dict = hf.healer_dict
healers = hf.healers

#for the enemy/chapter prompt
enemy_dict = {"13": [[800,50,"01"],[100,40,"02"],[400,50,"03"],[350,50,"04"],[1200,0,"05"],[1500,0,"06"],[900,20,"07"],[1200,20,"08"],[150,40,"09"],[3000,90,"10"],[200,20,"11"],[250,60,"12"],[300,60,"13"],[300,50,"14"]],
		"zt": [[250,50,"01"],[200,15,"02"],[250,50,"03"],[200,15,"04"],[700,60,"05"],[300,50,"06"],[150,10,"07"],[250,15,"08"],[300,50,"09"],[250,15,"10"],[600,80,"11"],[300,50,"12"],[1000,60,"13"],[600,60,"14"],[350,50,"15"],[900,60,"16"],[550,60,"17"]],
		"is": [[250,40,"01"],[200,10,"02"],[180,10,"03"],[200,10,"04"],[250,40,"05"],[900,10,"06"],[120,10,"07"],[1100,10,"08"],[800,45,"09"],[500,25,"10"],[500,25,"11"],[1000,15,"12"],[1300,15,"13"],[800,45,"14"],[1000,60,"15"]]}

modifiers = ["s1","s2","s3","p1","p2","p3","p4","p5","p6","m0","m1","m2","m3","0","1","2","3","mod0","mod1","mod2","mod3","modlvl","modlvl1","modlvl2","modlvl3","modlv","modlv1","modlv2","modlv3","mod","x0","y0","x","x1","x2","x3","y","y1","y2","y3","d","d1","d2","d3","modx","mody","modd","module","no","nomod","s1m0","s1m1","s1m2","s1m3","s2m0","s2m1","s2m2","s2m3","s3m0","s3m1","s3m2","s3m3","sl7","s7","slv7","l7","lv7"]

#If some smartass requests more than 40 operators to be drawn
bot_mad_message = ["excuse me, what? <:blemi:1077269748972273764>", "why you do this to me? <:jessicry:1214441767005589544>", "how about you draw your own graphs? <:worrymad:1078503499983233046>", "<:pepe_holy:1076526210538012793>", "spare me, please! <:harold:1078503476591607888>"]


def plot_graph(operator, buffs=[0,0,0,0], defens=[-1], ress=[-1], graph_type=0, max_def = 3000, max_res = 120, fixval = 40, alreadyDrawnOps =[], shreds = [1,0,1,0], enemies = [],basebuffs=[1,0],normal_dps = True, plotnumbers = 0):
	accuracy = 1 + 30 * 6
	style = '-'
	if plotnumbers > 9: style = '--'
	if plotnumbers > 19: style = '-.'
	if plotnumbers > 29: style = ':'

	#Setting the name of the operator
	op_name = ""
	if buffs[0] > 0: op_name += f" atk+{int(100*buffs[0])}%"
	if buffs[0] < 0: op_name += f" atk{int(100*buffs[0])}%"
	if buffs[1] > 0: op_name += f" atk+{buffs[1]}"
	if buffs[1] < 0: op_name += f" atk{buffs[1]}"
	if buffs[2] > 0: op_name += f" aspd+{buffs[2]}"
	if buffs[2] < 0: op_name += f" aspd{buffs[2]}"
	if buffs[3] > 0: op_name += f" dmg+{int(100*buffs[3])}%"
	if buffs[3] < 0: op_name += f" dmg{int(100*buffs[3])}%"
	if shreds[0] != 1: op_name += f" -{int(100*(1-shreds[0])+0.0001)}%def"
	if shreds[1] != 0: op_name += f" -{int(shreds[1])}def"
	if shreds[2] != 1: op_name += f" -{int(100*(1-shreds[2])+0.0001)}%res"
	if shreds[3] != 0: op_name += f" -{int(shreds[3])}res"
	if basebuffs[0] != 1: 
		op_name += f" +{int(100*(basebuffs[0]-1))}%bAtk"
		operator.base_atk *= basebuffs[0]
	if basebuffs[1] != 0: 
		op_name += f" +{int(basebuffs[1])}bAtk"
		operator.base_atk += basebuffs[1]
	if not normal_dps and operator.skill_dps(100,100) != operator.total_dmg(100,100): op_name += " totalDMG" #redneck way of checking if the total dmg method is implemented
	op_name = operator.get_name() + op_name
	if op_name in alreadyDrawnOps: return False
	alreadyDrawnOps.append(op_name)
	if len(op_name) > 65: #formatting issue for too long names
		op_name = op_name[:int(len(op_name)/2)] + "\n" + op_name[int(len(op_name)/2):]
	
	defences = np.clip(np.linspace(-shreds[1],(max_def-shreds[1])*shreds[0], accuracy), 0, None)
	resistances = np.clip(np.linspace(-shreds[3],(max_res-shreds[3])*shreds[2], accuracy), 0, None)
	damages = np.zeros(2*accuracy) if graph_type in [1,2] else np.zeros(accuracy)
	
	############### Normal DPS graph ################################
	if graph_type == 0:
		if normal_dps: damages=operator.skill_dps(defences,resistances)*(1+buffs[3])
		else: damages=operator.total_dmg(defences,resistances)*(1+buffs[3])
		xaxis = np.linspace(0,max_def, accuracy)
		p = plt.plot(xaxis, damages, label=op_name,linestyle=style)
		
		for defen in defens:
			if defen >= 0:
				if normal_dps: demanded = operator.skill_dps(max(0,defen-shreds[1])*shreds[0],max(defen/max_def*max_res-shreds[3],0)*shreds[2])*(1+buffs[3])
				else: demanded = operator.total_dmg(max(0,defen-shreds[1])*shreds[0],max(defen/max_def*max_res-shreds[3],0)*shreds[2])*(1+buffs[3])
				plt.text(defen,demanded,f"{int(demanded)}",size=9, c=p[0].get_color())
		for res in ress:
			if res >= 0:
				if normal_dps: demanded = operator.skill_dps(max(0,res/max_res*max_def-shreds[1])*shreds[0],max(res-shreds[3],0)*shreds[2])*(1+buffs[3])
				else: demanded = operator.total_dmg(max(0,res/max_res*max_def-shreds[1])*shreds[0],max(res-shreds[3],0)*shreds[2])*(1+buffs[3])
				plt.text(res*25/3000*max_def/max_res*120,demanded,f"{int(demanded)}",size=9, c=p[0].get_color())
	
	############### Increments defense and THEN res ################################
	elif graph_type == 1: 
		fulldef = np.full(accuracy, max(0,max_def-shreds[1])*shreds[0])
		newdefences = np.concatenate((defences,fulldef))
		newresistances = np.concatenate((np.zeros(accuracy),resistances))
		
		if normal_dps: damages = operator.skill_dps(newdefences,newresistances)*(1+buffs[3])
		else: damages = operator.total_dmg(newdefences,newresistances)*(1+buffs[3])
		xaxis = np.linspace(0,max_def, 2*accuracy)
		p = plt.plot(xaxis, damages, label=op_name)
		
		for defen in defens:
			if defen >= 0:
				defen = min(max_def-1,defen)
				if normal_dps: demanded = operator.skill_dps(max(0,defen-shreds[1])*shreds[0],0)*(1+buffs[3])
				else: demanded = operator.total_dmg(max(0,defen-shreds[1])*shreds[0],0)*(1+buffs[3])
				plt.text(defen/2,demanded,f"{int(demanded)}",size=9, c=p[0].get_color())
		for res in ress:
			if res >= 0:
				res = min(119,res)
				if normal_dps: demanded = operator.skill_dps(max(0,max_def-shreds[1])*shreds[0],max(res-shreds[3],0)*shreds[2])*(1+buffs[3])
				else: demanded = operator.total_dmg(max(0,max_def-shreds[1])*shreds[0],max(res-shreds[3],0)*shreds[2])*(1+buffs[3])
				plt.text(max_def/2+res*25/6000/max_res*120*max_def,demanded,f"{int(demanded)}",size=9, c=p[0].get_color())
	
	############### Increments Res and THEN defense ################################
	elif graph_type == 2:
		fullres = np.full(accuracy, max(max_res-shreds[3],0)*shreds[2])
		newdefences = np.concatenate((np.zeros(accuracy), defences))
		newresistances = np.concatenate((resistances, fullres))
		
		if normal_dps: damages=operator.skill_dps(newdefences,newresistances)*(1+buffs[3])
		else: damages=operator.total_dmg(newdefences,newresistances)*(1+buffs[3])
		xaxis = np.linspace(0,max_def, 2*accuracy)
		p = plt.plot(xaxis, damages, label=op_name)
		
		for defen in defens:
			if defen >= 0:
				defen = min(max_def-1,defen)
				if normal_dps: demanded = operator.skill_dps(max(0,defen-shreds[1])*shreds[0],max(max_res-shreds[3],0)*shreds[2])*(1+buffs[3])
				else: demanded = operator.total_dmg(max(0,defen-shreds[1])*shreds[0],max(max_res-shreds[3],0)*shreds[2])*(1+buffs[3])
				plt.text(max_def/2+defen/2,demanded,f"{int(demanded)}",size=9, c=p[0].get_color())
		for res in ress:
			if res >= 0:
				res = min(max_res-1,res)
				if normal_dps: demanded = operator.skill_dps(0,max(res-shreds[3],0)*shreds[2])*(1+buffs[3])
				else: demanded = operator.total_dmg(0,max(res-shreds[3],0)*shreds[2])*(1+buffs[3])
				plt.text(res*25/6000/max_res*120*max_def,demanded,f"{int(demanded)}",size=9, c=p[0].get_color())
	
	############### DPS graph with a fixed defense value ################################
	elif graph_type == 3:
		defences = np.empty(accuracy); 
		defences.fill(max(0,fixval-shreds[1])*shreds[0])
		
		if normal_dps: damages=operator.skill_dps(defences,resistances)*(1+buffs[3])
		else: damages=operator.total_dmg(defences,resistances)*(1+buffs[3])
		xaxis = np.linspace(0,max_def, accuracy)
		p = plt.plot(xaxis, damages, label=op_name)
		
		for res in ress:
			if res >= 0:
				demanded = operator.skill_dps(max(0,fixval-shreds[1])*shreds[0],max(res-shreds[3],0)*shreds[2])*(1+buffs[3])
				plt.text(res*25/3000*max_def/max_res*120,demanded,f"{int(demanded)}",size=9, c=p[0].get_color())
	
	############### DPS graph with a fixed res value ################################
	elif graph_type == 4:
		resistances = np.empty(accuracy); 
		resistances.fill(max(fixval-shreds[3],0)*shreds[2])
		
		if normal_dps: damages = operator.skill_dps(defences,resistances)*(1+buffs[3])
		else: damages = operator.total_dmg(defences,resistances)*(1+buffs[3])
		xaxis = np.linspace(0,max_def, accuracy)
		p = plt.plot(xaxis, damages, label=op_name)
		
		for defen in defens:
			if defen >= 0:
				demanded = operator.skill_dps(max(0,defen-shreds[1])*shreds[0],max(fixval-shreds[3],0)*shreds[2])*(1+buffs[3])
				plt.text(defen,demanded,f"{int(demanded)}",size=9, c=p[0].get_color())
	
	############### Graph with images of enemies -> enemy prompt ################################
	elif graph_type == 5:
		defences = [i[0] for i in enemies]
		resistances = [i[1] for i in enemies]
		xaxis = np.arange(len(enemies))
		damages = np.zeros(len(enemies))

		damages = operator.skill_dps(np.array(defences),np.array(resistances))*(1+buffs[3])
		p = plt.plot(xaxis,damages, marker=".", linestyle = "", label=op_name)
		plt.plot(xaxis,damages, alpha = 0.2, c=p[0].get_color())
		for i in range(len(enemies)):
			demanded = operator.skill_dps(enemies[i][0],enemies[i][1])*(1+buffs[3])
			plt.text(i,demanded,f"{int(demanded)}",size=9, c=p[0].get_color())
	return True	


@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
	if message.author == client.user:
		return
	
	if onPi:
		if type(message.channel)==discord.channel.DMChannel and respond_to_dm:
			pass
		elif not message.channel.name in valid_channels: return
	else:
		if not message.channel.name == 'privatebottest': return

	
	if message.content.lower().startswith('!ping'): await message.channel.send('Pong!')
	if message.content.lower().startswith('!marco'): await message.channel.send('Polo!')

	
	if message.content.lower().startswith('!ops'):
		allops = "These are the currently available operators:"
		for op in operators:
			allops += " " + op + ","
		allops = allops[:-1]
		allops += "\n(Not all operators have all their skills implemented, check the legend of the graph)"
		await message.channel.send(allops)

	
	if message.content.lower().startswith('!hops'):
		allops = "These are the currently available healers:"
		for op in healers:
			allops += " " + op + ","
		allops = allops[:-1]
		await message.channel.send(allops)

		
	if message.content.lower().startswith('!help'):
		text = """General use: !dps <opname1> <opname2> ... 
Spaces are used as delimiters, so make sure to keep operator names in one word. The bot can only handle E2 ops with skill lvl 7+ and the result is purely mathematical (no frame counting etc, so the reality typically differs a bit from the result, not that one would notice a < 5% difference ingame):
example: !dps def 0 targets 3 lapluma p4 s2 m1 x2 low ulpianus s2
!guide will show you the available modifiers to the graphs, !ops lists the available operators.
There is also a handful healers implemented. !hps <opname> ... works similar to !dps. !hops shows the available healers.
Errors do happen, so feel free to double check the results. The Bot will also respond to DMs.
If you want to see how the bot works or expand it, it has a public repository: github.com/WhoAteMyCQQkie/ArknightsDpsCompare
"""
		await message.channel.send(text)

	
	if message.content.lower().startswith('!prompt') or message.content.lower().startswith('!guide'):
		text = """**Suffixes placed after the operator, affecting only that operator:**
S1,S2,S3, sl7,M0,..,M3, P1,..,P6, mod0,modx,mody,modd or just 0,x1,x2,x3,y1,y2,y3,d1,d2,d3
**Prefixes that affect all following operators (not adding a value resets to default values):**
targets <value>, res <value>/def <value>, buff <atk%> <flatAtk> <aspd> <fragile>, level <OpLevel>, hits <receivedHitsPerSecond> (either like 0.33 or 1/3), bbuff <value> (base atk, flat:123, percentage: 25% or 0.25), resshred/defshred (same as bbuff, percent or flat)
**Conditional damage prefixes, affecting all following operators:**
lowtrait/hightrait, lowtalent1/hightalent1, lowtalent2/hightalent2, lowskill/highskill, lowmodule/highmodule
*(just writing low/high sets all 5. you can also use low1,..,low5 or high1,..,high5 for trait,talent1,talent2,skill,module)*
**Prompts for the axis scale, that need to be added before any operators:** maxdef/maxres <value>, split/split2, fix/fixdef/fixres <value> (fix chooses res <100, else def)
**Other prompts:** hide,left,tiny (for the legend),  color (for colorblind people, at the start), text (puts everything after the prompt as title of the graph)
*Most prefix prompts can also be shortened: buff -> b, low/high -> l/h, targets ->t, level -> lv, ...*
"""
		await message.channel.send(text)
       		

	if message.content.lower().startswith('!mumu') or message.content.lower().startswith('!muelsyse'):
		text = """There are multiple clones available. The cloned operator will be have the same level,pot and module-lvl as Mumu. Lowtrait removes Mumus bonus trait dmg, lowtalent1 removes the main clone, lowtalent2 removes the stolen atk if the cloned op is melee. lowskill will remove 2 clones from skill 3 or completely remove the extra clones for skill 1/2, otherwise it will assume the main clone is always attacking and calculate the damage with the expected average amount of clones during the skill duration.
As operator input use mumuX or mumuOPERATOR with X:OPERATOR being the following: **1:Dorothy, 2:Ebenholz, 3:Ceobe, 4:Mudrock, 5:Rosa, 6:Skadi, 7:Schwarz**
Adding new ops is not a big deal, so ask WhoAteMyCQQkie if there is one you desperately want."""
		await message.channel.send(text)

	
	if message.content.lower().startswith('!calc'):
		
		#Check, that the input really is just a simple calculation and not possibly malicious code, using a context free grammar
		grammar = nltk.CFG.fromstring("""
			S -> N | '(' S ')' | S '+' S | S '-' S | S '*' S | S '/' S | S '*' '*' S
			B -> '.' D | 
			N -> V L B | V '0' B
			V -> '+' | '-' | 
			D -> D D | '0' | Z
			L -> L D | Z
			Z -> '1' | '2' | '3' | '4' | '5' | '6' | '7' | '8' | '9'
		""")
		parser = nltk.ChartParser(grammar)
		sentence = message.content.lower()[5:]
		output = []
		
		#turn the input string into a format the grammar parser can read.
		for letter in sentence:
			if letter == ",": output.append(".")
			elif letter == "^": 
				output.append("*")
				output.append("*")
			elif letter == "x": output.append("*")
			elif letter == " ": continue
			else: output.append(letter)
		
		
		#this stops the code after 2 seconds, but doesnt work on windows, because only unix has SIGALRM
		#you can remove this, but an input of for example 5x5x5x5x[....]x5x5x5x5 will kill your program and possibly crash your device, because it will eat all of your memory
		def handler(signum, frame):
			raise TimeoutError("Operation timed out")
		signal.signal(signal.SIGALRM, handler)
		signal.alarm(2)
		
		try:
			is_valid = any(parser.parse(output))
			if is_valid:
				command = ""
				for letter in output:
					command += letter
				command = "print("+command+")"
				result = subprocess.run(['python', '-c', command], capture_output=True, text=True,timeout=1)
				if "ZeroDivisionError" in result.stderr: raise ZeroDivisionError
				if(len(str(result.stdout)) < 200):
					await message.channel.send(str(result.stdout))
				else:
					await message.channel.send("Result too large.")
			else:
				await message.channel.send("Invalid syntax.")
		except ValueError:
			await message.channel.send("Only numbers and +-x/*^() are allowed as inputs.")
		except ZeroDivisionError:
			await message.channel.send("Congrats, you just divided by zero.")
		except TimeoutError:
			await message.channel.send("Exceeded reasonable computation time.")
		except subprocess.TimeoutExpired:
			await message.channel.send("The thread did not survive trying to process this request.")
		finally:
			signal.alarm(0)

		
	if message.content.lower().startswith('!dps'):
		
		#reset plot parameters
		plt.clf()
		plt.style.use('default')
		alreadyDrawnOps = [] #this is a global variable edited the plot_graph function. probably not a good solution
		plot_size = 4 #plot height in inches
		add_title = False
		title = ""
		show = True
		bottomleft = False
		textsize = 10
		
		#Read the input message
		parsed_message = message.content.lower().split()[1:]
		entries = len(parsed_message)
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
		TrTaTaSkMo = [True,True,True,True,True] #trait talent1 talent2 skill module
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
			if parsed_message[i] in op_dict and i+1==entries:
				if all_conditionals:
					for combos in itertools.product([True,False], repeat = 5):
						if plot_graph((op_dict[parsed_message[i]](lvl,-1, -1, 3,-1,3, targets, list(combos),buffs,**input_kwargs)), buffs, defen, res, graph_type, max_def, max_res, fixval,alreadyDrawnOps,shreds,enemies,basebuffs,normal_dps,contains_data): contains_data += 1
				else:
					if plot_graph((op_dict[parsed_message[i]](lvl,-1, -1, 3,-1,3, targets, TrTaTaSkMo,buffs,**input_kwargs)), buffs, defen, res, graph_type, max_def, max_res, fixval,alreadyDrawnOps,shreds,enemies,basebuffs,normal_dps,contains_data): contains_data += 1
			elif parsed_message[i] in op_dict and not (parsed_message[i+1] in modifiers):
				if all_conditionals:
					for combos in itertools.product([True,False], repeat = 5):
						if plot_graph((op_dict[parsed_message[i]](lvl,-1, -1, 3,-1,3, targets, list(combos),buffs,**input_kwargs)), buffs, defen, res, graph_type, max_def, max_res, fixval,alreadyDrawnOps,shreds,enemies,basebuffs,normal_dps,contains_data): contains_data += 1
				else:
					if plot_graph((op_dict[parsed_message[i]](lvl,-1, -1, 3,-1,3, targets, TrTaTaSkMo,buffs,**input_kwargs)), buffs, defen, res, graph_type, max_def, max_res, fixval,alreadyDrawnOps,shreds,enemies,basebuffs,normal_dps,contains_data): contains_data += 1 
				if contains_data > 40: break
			elif parsed_message[i] in op_dict and parsed_message[i+1] in modifiers:
				tmp = i
				i+=1
				skills = {-1}
				masteries = {-1}
				modlvls = {-1}
				pots = {-1}
				mods = {-1}
				while i < entries and parsed_message[i] in modifiers:
					if parsed_message[i] in ["s1","s2","s3"]: 
						skills.add(int(parsed_message[i][1]))
						skills.discard(-1)
					elif parsed_message[i] in ["p1","p2","p3","p4","p5","p6"]: 
						pots.add(int(parsed_message[i][1]))
						pots.discard(-1)
					elif parsed_message[i] in ["1","2","3"]: 
						modlvls.add(int(parsed_message[i]))
						modlvls.discard(-1)
					elif parsed_message[i] in ["modlvl1","modlvl2","modlvl3","modlv1","modlv2","modlv3",]: 
						modlvls.add(int(parsed_message[i][-1]))
						modlvls.discard(-1)
					elif parsed_message[i] in ["m0","m1","m2","m3"]: 
						masteries.add(int(parsed_message[i][1]))
						masteries.discard(-1)
					elif parsed_message[i] in ["sl7","s7","slv7","l7","lv7"]:
						masteries.add(0)
						masteries.discard(-1)
					elif parsed_message[i] in ["mod0","mod1","mod2","mod3"]:
						mods.add(int(parsed_message[i][3]))
						mods.discard(-1)
					elif parsed_message[i] in ["modx","x"]:
						mods.add(1)
						mods.discard(-1)
					elif parsed_message[i] in ["x1","x2","x3"]: 
						mods.add(1)
						mods.discard(-1)
						modlvls.add(int(parsed_message[i][1]))
						modlvls.discard(-1)
					elif parsed_message[i] in ["y1","y2","y3"]: 
						mods.add(2)
						mods.discard(-1)
						modlvls.add(int(parsed_message[i][1]))
						modlvls.discard(-1)
					elif parsed_message[i] in ["mody","y"]:
						mods.add(2)
						mods.discard(-1)
					elif parsed_message[i] in ["modd","d"]:
						mods.add(3)
						mods.discard(-1)
					elif parsed_message[i] in ["d1","d2","d3"]: 
						mods.add(3)
						mods.discard(-1)
						modlvls.add(int(parsed_message[i][1]))
						modlvls.discard(-1)
					elif parsed_message[i] in ["0","no","mod","module","nomod","modlvl","modlv","x0","y0"]:
						mods.add(0)
						mods.discard(-1)
					elif parsed_message[i] in ["s1m0","s1m1","s1m2","s1m3","s2m0","s2m1","s2m2","s2m3","s3m0","s3m1","s3m2","s3m3"]:
						skills.add(int(parsed_message[i][1]))
						skills.discard(-1)
						masteries.add(int(parsed_message[i][3]))
						masteries.discard(-1)
					i+=1
				if not -1 in modlvls and 0 in mods and len(mods) == 1:
					mods.add(-1)
				for pot, skill, mastery, mod, modlvl in itertools.product(pots, skills, masteries, mods, modlvls):
					if all_conditionals:
						for combos in itertools.product([True,False], repeat = 5):
							if plot_graph((op_dict[parsed_message[tmp]](lvl,pot,skill,mastery,mod,modlvl, targets, list(combos),buffs,**input_kwargs)), buffs, defen, res, graph_type, max_def, max_res, fixval,alreadyDrawnOps,shreds,enemies,basebuffs,normal_dps,contains_data): contains_data += 1						
					else:
						if plot_graph((op_dict[parsed_message[tmp]](lvl,pot,skill,mastery,mod,modlvl,targets,TrTaTaSkMo,buffs,**input_kwargs)), buffs, defen, res, graph_type, max_def, max_res, fixval,alreadyDrawnOps,shreds,enemies,basebuffs,normal_dps,contains_data): contains_data += 1
					if contains_data > 40: break
				i-=1
			elif parsed_message[i] in ["b","buff","buffs"]:
				i+=1
				buffcount=0
				buffs=[0,0,0,0]
				while i < entries and buffcount < 4:
					try:
						buffs[buffcount] = int(parsed_message[i])
						buffcount +=1
					except ValueError:
						break
					if buffcount == 1: buffs[0] = buffs[0]/100
					if buffcount == 4: buffs[3] = buffs[3]/100
					i+=1
				i-=1
			elif parsed_message[i] in ["t","target","targets"]:
				i+=1
				targets = 1
				while i < entries:
					try:
						targets = int(parsed_message[i])
					except ValueError:
						break
					i+=1
				i-=1
			elif parsed_message[i] in ["t1","t2","t3","t4","t5","t6","t7","t8","t9"]: targets = int(parsed_message[i][1])
			elif parsed_message[i] in ["r","res","resis","resistance"]:
				i+=1
				res = [-10]
				number_request = True
				while i < entries:
					try:
						res.append(min(max_res,int(parsed_message[i])))
					except ValueError:
						break
					i+=1
				i-=1
			elif parsed_message[i] in ["d","def","defense"]:
				i+=1
				number_request = True
				defen = [-10]
				while i < entries:
					try:
						defen.append(min(max_def,int(parsed_message[i])))
					except ValueError:
						break
					i+=1
				i-=1
			
			elif parsed_message[i] in ["shred","shreds","debuff","ignore"]:
				i+=1
				shreds = [1,0,1,0]
				while i < entries:
					if parsed_message[i][-1] == "%":
						try:
							shreds[0] = max(0,(1-float(parsed_message[i][:-1])/100))
							shreds[2] = max(0,(1-float(parsed_message[i][:-1])/100))
						except ValueError:
							break
					else:
						try:
							val = float(parsed_message[i])
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
			elif parsed_message[i] in ["resshred","resdebuff","shredres","debuffres","reshred","resignore"]:
				i+=1
				shreds[2] = 1
				shreds[3] = 0
				while i < entries:
					if parsed_message[i][-1] == "%":
						try:
							shreds[2] = max(0,(1-float(parsed_message[i][:-1])/100))
						except ValueError:
							break
					else:
						try:
							val = float(parsed_message[i])
							if val > 0 and val < 1:
								shreds[2] = 1 - val
							if val > 2:
								shreds[3] = val
						except ValueError:
							break
					i+=1
				i-=1
				input_kwargs["shreds"] = shreds
			elif parsed_message[i] in ["defshred","defdebuff","shreddef","debuffdef","defignore"]:
				i+=1
				shreds[0] = 1
				shreds[1] = 0
				while i < entries:
					if parsed_message[i][-1] == "%":
						try:
							shreds[0] = max(0,(1-float(parsed_message[i][:-1])/100))
						except ValueError:
							break
					else:
						try:
							val = float(parsed_message[i])
							if val > 0 and val < 1:
								shreds[0] = 1 - val
							if val > 2:
								shreds[1] = val
						except ValueError:
							break
					i+=1
				i-=1
				input_kwargs["shreds"] = shreds
			elif parsed_message[i] in ["basebuff","baseatk","base","bbuff","batk"]:
				i+=1
				basebuffs[0] = 1
				basebuffs[1] = 0
				while i < entries:
					if parsed_message[i][-1] == "%":
						try:
							basebuffs[0] = max(0,(1+float(parsed_message[i][:-1])/100))
						except ValueError:
							break
					else:
						try:
							val = float(parsed_message[i])
							if val > 0 and val < 1:
								basebuffs[0] = 1 + val
							if val > 2:
								basebuffs[1] = val
						except ValueError:
							break
					i+=1
				i-=1
			elif parsed_message[i] in ["lvl","level","lv"]:
				i+=1
				lvl = -10
				while i < entries:
					try:
						lvl = int(parsed_message[i])
					except ValueError:
						break
					i+=1
				i-=1
			elif parsed_message[i] in ["iaps","bonk","received","hits","hit"]:
				i+=1
				while i < entries:
					try:
						input_kwargs["hits"] = float(parsed_message[i])
					except ValueError:
						if "/" in parsed_message[i]:
							newStrings = parsed_message[i].split("/")
							try:
								input_kwargs["hits"] = (float(newStrings[0]) / float(newStrings[1]))
							except ValueError:
								break
						else:
							break
					i+=1
				i-=1
			elif parsed_message[i] in ["stack","stacks"]:
				i+=1
				while i < entries:
					try:
						input_kwargs["stacks"] = int(parsed_message[i])
					except ValueError:
						break
					i+=1
				i-=1
			elif parsed_message[i] in ["plus","ultra","plusultra","peak","bonus","max"]:
				input_kwargs["bonus"] = True
			elif parsed_message[i] in ["ptilo","boost","spboost","spbuff","sp","buffsp"]:
				i+=1
				while i < entries:
					if parsed_message[i][-1] == "%":
						try:
							input_kwargs["boost"] = float(parsed_message[i][:-1])/100
							shreds[0] = max(0,(1-float(parsed_message[i][:-1])/100))
						except ValueError:
							break
					else:
						try:
							val = float(parsed_message[i])
							if val > 0 and val < 1:
								input_kwargs["boost"] = val
						except ValueError:
							break
					i+=1
				i-=1		
			elif parsed_message[i] in ["l","low"]:
				TrTaTaSkMo = [False,False,False,False,False]
			elif parsed_message[i] in ["h","high"]:
				TrTaTaSkMo = [True,True,True,True,True]
			elif parsed_message[i] in ["low1","l1","lowtrait","traitlow"]:
				TrTaTaSkMo[0] = False
			elif parsed_message[i] in ["high1","h1","hightrait","traithigh"]:
				TrTaTaSkMo[0] = True
			elif parsed_message[i] in ["low2","l2","lowtalent","talentlow","lowtalent1","talent1low"]:
				TrTaTaSkMo[1] = False
			elif parsed_message[i] in ["high2","h2","hightalent","talenthigh","hightalent1","talent1high"]:
				TrTaTaSkMo[1] = True
			elif parsed_message[i] in ["low3","l3","talentlow","lowtalent2","talent2low"]:
				TrTaTaSkMo[2] = False
			elif parsed_message[i] in ["high3","h3","talenthigh","hightalent2","talent2high"]:
				TrTaTaSkMo[2] = True
			elif parsed_message[i] in ["low4","l4","lows","slow","lowskill","skilllow"]:
				TrTaTaSkMo[3] = False
			elif parsed_message[i] in ["high4","h4","highs","shigh","highskill","skillhigh"]:
				TrTaTaSkMo[3] = True
			elif parsed_message[i] in ["low5","l5","lowm","mlow","lowmod","modlow","lowmodule","modulelow"]:
				TrTaTaSkMo[4] = False
			elif parsed_message[i] in ["high5","h5","highm","mhigh","highmod","modhigh","highmodule","modulehigh"]:
				TrTaTaSkMo[4] = True
			elif parsed_message[i] == "lowtalents":
				TrTaTaSkMo[1] = False
				TrTaTaSkMo[2] = False
			elif parsed_message[i] == "hightalents":
				TrTaTaSkMo[1] = True
				TrTaTaSkMo[2] = True
			elif parsed_message[i] in ["total", "totaldmg"]:
				normal_dps = not normal_dps
			elif parsed_message[i] in ["hide", "legend"]:
				show = False
			elif parsed_message[i] in ["big", "beeg", "large"]:
				plot_size = 8
			elif parsed_message[i] in ["repos", "reposition", "bottom", "left", "botleft", "position", "change", "changepos"]:
				bottomleft = True
			elif parsed_message[i] in ["conditionals", "conditional","variation","variations"]:
				all_conditionals = True
			elif parsed_message[i] == "split":
				if not contains_data: graph_type = 1
			elif parsed_message[i] == "split2":
				if not contains_data: graph_type = 2
			elif parsed_message[i] in ["small","font","tiny"]:
				textsize = 6
			elif parsed_message[i] in ["color","colour","colorblind","colourblind","blind"]:
				plt.style.use('tableau-colorblind10')
			elif parsed_message[i] in ["maxdef","limit","range","scale"]:
				if contains_data == 0 and not number_request:
					i+=1
					max_def = 3000
					while i < entries:
						try:
							max_def = min(69420,max(100, int(parsed_message[i])))
						except ValueError:
							break
						i+=1
					i-=1
			elif parsed_message[i] in ["maxres","reslimit","limitres","scaleres","resscale"]:
				if contains_data == 0 and not number_request:
					i+=1
					max_res = 120
					while i < entries:
						try:
							max_res = min(400,max(5, int(parsed_message[i])))
						except ValueError:
							break
						i+=1
					i-=1
			elif parsed_message[i] in ["enemy","chapter"]:
				if parsed_message[i+1] in enemy_dict and contains_data == 0:
					enemy_key = parsed_message[i+1]
					graph_type = 5
					enemies = enemy_dict[parsed_message[i+1]]
					enemies.sort(key=lambda tup: tup[0], reverse=False)
					i += 1
			elif parsed_message[i] in ["enemy2","chapter2"]:
				if parsed_message[i+1] in enemy_dict and contains_data == 0:
					enemy_key = parsed_message[i+1]
					graph_type = 5
					enemies = enemy_dict[parsed_message[i+1]]
					enemies.sort(key=lambda tup: tup[1], reverse=False)
					i += 1
			elif parsed_message[i] in ["fixdef","fixeddef","fixdefense","fixeddefense","setdef","setdefense"]:
				if contains_data == 0: 
					try:
						graph_type = 3
						fixval = int(parsed_message[i+1])
						fixval = max(0,min(50000,fixval))
						i+=1
					except ValueError:
						pass
				
			elif parsed_message[i] in ["fixres","fixedres","fixresistance","fixedresistance","setres","resresistance"]:
				if contains_data == 0: 
					try:
						graph_type = 4
						fixval = int(parsed_message[i+1])
						fixval = max(0,min(400,fixval))
						i+=1
					except ValueError:
						pass
			elif parsed_message[i] in ["set","fix","fixed"]:
				if contains_data == 0: 
					try:
						fixval = int(parsed_message[i+1])
						graph_type = 3 if fixval >= 100 else 4
						fixval = max(0,min(50000,fixval))
						i+=1
					except ValueError:
						pass
			elif parsed_message[i] in ["title","text","label"]:
				i+=1
				add_title = True
				while i < entries:
					title += parsed_message[i] + " "
					i+=1								
			elif parsed_message[i] in modifiers:
				parsing_error = True
				error_message += " " + parsed_message[i] + ","
			elif parsed_message[i][0] in ["1","2","3","4","5","6","7","8","9"] and not parsed_message[i][-1] in ["0","1","2","3","4","5","6","7","8","9"]: 
				##################try to fix a missing space after an integer like "buff 90surtr" (should not have a leading 0. if the entire number is 0: should be ignorable)
				numberpos = 1
				while parsed_message[i][numberpos] in ["0","1","2","3","4","5","6","7","8","9","."]:
					numberpos += 1
				temp = parsed_message[i]
				parsed_message[i] = parsed_message[i][numberpos:]
				parsed_message.insert(i,temp[:numberpos])
				entries += 1
				backsteps = 1
				while backsteps < 5:
					try:
						_ = int(parsed_message[i-backsteps]) #to cause a valueerror #redneckcoding
						backsteps +=1
					except ValueError:
						backsteps +=1
						break
				i-=backsteps
			elif not parsed_message[i][0] in ["0","1","2","3","4","5","6","7","8","9"] and parsed_message[i][-1] in ["0","1","2","3","4","5","6","7","8","9","."]: 
				#####################try to fix a missing space after buff/hits etc
				numberpos = 2
				wordlen = len(parsed_message[i])
				while parsed_message[i][-numberpos] in ["0","1","2","3","4","5","6","7","8","9","."]:
					numberpos += 1
				temp = parsed_message[i]
				parsed_message[i] = parsed_message[i][(wordlen-numberpos+1):]
				parsed_message.insert(i,temp[:(wordlen-numberpos+1)])
				entries += 1
				i -= 1
			elif parsed_message[i].isdigit() and (i + 1) < entries: 
				######################swap around numbers and prompts, for cases like "5 targets"
				if parsed_message[i+1] in ["t","target","targets","def","defense","res","resistance","limit","maxres","maxdef","hits","hit","iaps"]:
					tmp = parsed_message[i]
					parsed_message[i] = parsed_message[i+1]
					parsed_message[i+1] = tmp
					i -= 1
			else:
				myKeys = list(op_dict.keys()) ### Try some autocorrection for typos in the operator name
				lev_dist = 1000
				errorlimit = 0
				promptlength = len(parsed_message[i])
				prompt = parsed_message[i]
				foundFit = False 
				optimizer = False #True when a solution was found, but we still search for a better solution.
				optimize_error = -10
				if promptlength > 3: errorlimit = 1
				if promptlength > 5: errorlimit = 2
				if promptlength > 8: errorlimit = 3
				if promptlength < 15:
					for key in myKeys:
						if optimizer:
							if df.levenshtein(key, prompt) < optimize_error: #dont just stop at the first fit, but rather at the best fit.
								parsed_message[i] = key
								optimize_error = df.levenshtein(key, prompt)
						elif df.levenshtein(key, prompt) <= errorlimit:
							parsed_message[i] = key
							i-=1
							optimizer = True
							optimize_error = df.levenshtein(key, prompt)
							foundFit = True
				if not foundFit:
					parsing_error = True
					error_message += " " + parsed_message[i] + ","
			i+=1
		
		
		#Cases where no plot is generated: no inputs or too many inputs
		if contains_data == 0:
			plt.close()
			return
		if contains_data > 40:
			plt.close()
			l = len(bot_mad_message)
			nope = bot_mad_message[np.random.randint(0,l)]
			await message.channel.send(nope)
			return
		
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
			await message.channel.send(error_message[:-1], file=file)
		else:
			await message.channel.send(file=file)
		
		
		
	###############################################################################################################################################################################
	if message.content.lower().startswith('!hps'):
		#read the message
		parsed_message = message.content.lower().split()[1:]
		entries = len(parsed_message)
		i = 0
		res = [-1]
		defen = [-1]
		lvl = -10
		targets = 1
		mastery = 3
		modlvl = 3
		contains_data = 0
		buffs = [0,0,0,0]
		TrTaTaSkMo = [True,True,True,True,True] #trait talent1 talent2 skill module
		boost = 0
		healer_message = ""
		parsing_error = False
		error_message = "Could not use the following prompts: "
		
		while i < entries:
			if parsed_message[i] in healer_dict and i+1==entries:
				healer_message += (healer_dict[parsed_message[i]](lvl,-1, -1, 3,-1,3,targets,buffs,boost)).skill_hps() + "\n"
				contains_data += 1
				if contains_data > 19: break
			elif parsed_message[i] in healer_dict and not (parsed_message[i+1] in modifiers):
				contains_data += 1
				healer_message += (healer_dict[parsed_message[i]](lvl,-1, -1, 3,-1,3,targets,buffs,boost)).skill_hps() + "\n"
				if contains_data > 19: break
			elif parsed_message[i] in healer_dict and parsed_message[i+1] in modifiers:
				tmp = i
				i+=1
				skills = {-1}
				masteries = {-1}
				modlvls = {-1}
				pots = {-1}
				mods = {-1}
				while i < entries and parsed_message[i] in modifiers:
					if parsed_message[i] in ["s1","s2","s3"]: 
						skills.add(int(parsed_message[i][1]))
						skills.discard(-1)
					elif parsed_message[i] in ["p1","p2","p3","p4","p5","p6"]: 
						pots.add(int(parsed_message[i][1]))
						pots.discard(-1)
					elif parsed_message[i] in ["1","2","3"]: 
						modlvls.add(int(parsed_message[i]))
						modlvls.discard(-1)
					elif parsed_message[i] in ["modlvl1","modlvl2","modlvl3","modlv1","modlv2","modlv3",]: 
						modlvls.add(int(parsed_message[i][-1]))
						modlvls.discard(-1)
					elif parsed_message[i] in ["m0","m1","m2","m3"]: 
						masteries.add(int(parsed_message[i][1]))
						masteries.discard(-1)
					elif parsed_message[i] in ["sl7","s7","slv7","l7","lv7"]:
						masteries.add(0)
						masteries.discard(-1)
					elif parsed_message[i] in ["mod0","mod1","mod2","mod3"]:
						mods.add(int(parsed_message[i][3]))
						mods.discard(-1)
					elif parsed_message[i] in ["modx","x"]:
						mods.add(1)
						mods.discard(-1)
					elif parsed_message[i] in ["x1","x2","x3"]: 
						mods.add(1)
						mods.discard(-1)
						modlvls.add(int(parsed_message[i][1]))
						modlvls.discard(-1)
					elif parsed_message[i] in ["y1","y2","y3"]: 
						mods.add(2)
						mods.discard(-1)
						modlvls.add(int(parsed_message[i][1]))
						modlvls.discard(-1)
					elif parsed_message[i] in ["mody","y"]:
						mods.add(2)
						mods.discard(-1)
					elif parsed_message[i] in ["modd","d"]:
						mods.add(3)
						mods.discard(-1)
					elif parsed_message[i] in ["d1","d2","d3"]: 
						mods.add(3)
						mods.discard(-1)
						modlvls.add(int(parsed_message[i][1]))
						modlvls.discard(-1)
					elif parsed_message[i] in ["0","no","mod","module","nomod","modlvl","modlv","x0","y0"]:
						mods.add(0)
						mods.discard(-1)
					elif parsed_message[i] in ["s1m0","s1m1","s1m2","s1m3","s2m0","s2m1","s2m2","s2m3","s3m0","s3m1","s3m2","s3m3"]:
						skills.add(int(parsed_message[i][1]))
						skills.discard(-1)
						masteries.add(int(parsed_message[i][3]))
						masteries.discard(-1)
					i+=1
				if not -1 in modlvls and 0 in mods and len(mods) == 1:
					mods.add(-1)
				for pot, skill, mastery, mod, modlvl in itertools.product(pots, skills, masteries, mods, modlvls):
					healer_message += (healer_dict[parsed_message[tmp]](lvl,pot, skill, mastery,mod,modlvl,targets,buffs,boost)).skill_hps() + "\n"
					contains_data += 1
					if contains_data > 19: break
				if contains_data > 19: break
			elif parsed_message[i] in ["b","buff","buffs"]:
				i+=1
				buffcount=0
				buffs=[0,0,0,0]
				while i < entries and buffcount < 4:
					if parsed_message[i]=="":
						pass
					else:
						try:
							buffs[buffcount] = int(parsed_message[i])
							buffcount +=1
						except ValueError:
							break
					if buffcount == 1: buffs[0] = buffs[0]/100
					if buffcount == 4: buffs[3] = max(0, buffs[3])/100
					i+=1
				i-=1
			elif parsed_message[i] in ["t","target","targets"]:
				i+=1
				targets = 1
				while i < entries:
					try:
						targets = int(parsed_message[i])
					except ValueError:
						break
					i+=1
				i-=1
			elif parsed_message[i] in ["t1","t2","t3","t4","t5","t6","t7","t8","t9"]: targets = int(parsed_message[i][1])	
			elif parsed_message[i] in ["lvl","level","lv"]:
				i+=1
				lvl = -10
				while i < entries:
					if parsed_message[i]=="":
						pass
					else:
						try:
							lvl = int(parsed_message[i])
						except ValueError:
							break
					i+=1
				i-=1
			elif parsed_message[i] in ["sp","boost","recovery","spboost","spbuff","buffsp"]:
				i+=1
				boost = 0
				while i < entries:
					if parsed_message[i]=="":
						pass
					else:
						try:
							boost = float(parsed_message[i])
						except ValueError:
							break
					i+=1
				i-=1								
			elif parsed_message[i] == "":
				continue
			elif len(parsed_message[i]) < 3:
				parsing_error = True
				error_message += " " + parsed_message[i] + ","
			elif parsed_message[i][0] in ["1","2","3","4","5","6","7","8","9"] and not parsed_message[i][-1] in ["0","1","2","3","4","5","6","7","8","9"]: #try to fix a missing space after an integer (should not have a leading 0. if the entire number is 0: should be ignorable)
				numberpos = 1
				while parsed_message[i][numberpos] in ["0","1","2","3","4","5","6","7","8","9","."]:
					numberpos += 1
				temp = parsed_message[i]
				parsed_message[i] = parsed_message[i][numberpos:]
				parsed_message.insert(i,temp[:numberpos])
				entries += 1
				backsteps = 1
				while backsteps < 5:
					try:
						idc = int(parsed_message[i-backsteps])
						backsteps +=1
					except ValueError:
						backsteps +=1
						break
				i-=backsteps
			elif not parsed_message[i][0] in ["0","1","2","3","4","5","6","7","8","9"] and  parsed_message[i][-2] in ["0","1","2","3","4","5","6","7","8","9","."]: #try to fix a missing space after buff/hits etc
				numberpos = 2
				wordlen = len(parsed_message[i])
				while parsed_message[i][-numberpos] in ["0","1","2","3","4","5","6","7","8","9","."]:
					numberpos += 1
				temp = parsed_message[i]
				parsed_message[i] = parsed_message[i][(wordlen-numberpos+1):]
				parsed_message.insert(i,temp[:(wordlen-numberpos+1)])
				entries += 1
				i -= 1
			else:
				myKeys = list(healer_dict.keys()) ### Try some autocorrection
				lev_dist = 1000
				errorlimit = 0
				promptlength = len(parsed_message[i])
				prompt = parsed_message[i]
				foundFit = False
				optimizer = False
				optimize_error = -10
				if promptlength > 3: errorlimit = 1
				if promptlength > 5: errorlimit = 2
				if promptlength > 8: errorlimit = 3
				if promptlength < 15:
					for key in myKeys:
						if optimizer:
							if df.levenshtein(key, prompt) < optimize_error: #dont just stop at the first fit, but rather at the best fit.
								parsed_message[i] = key
								optimize_error = df.levenshtein(key, prompt)
						elif df.levenshtein(key, prompt) <= errorlimit:
							parsed_message[i] = key
							i-=1
							optimizer = True
							optimize_error = df.levenshtein(key, prompt)
							foundFit = True
				if not foundFit:
					parsing_error = True
					error_message += " " + parsed_message[i] + ","
			
			i+=1	
		if contains_data == 0: return
		
		healer_message = "Heals per second - **skill active**/skill down/*averaged* \n" + healer_message		
		if contains_data > 19 : healer_message = healer_message + "Only the first 20 entries are shown."
		await message.channel.send(healer_message)
		
with open("token.txt") as file:
	token = file.readline()
client.run(token)


