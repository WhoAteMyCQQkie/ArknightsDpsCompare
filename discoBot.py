# First of all: Don't Judge me for this code, I know it's neither clean nor efficient, but with the limited amount of thought I put into it, this is the best architecture I could come up with.
# In order for the bot to work you need a "token.txt" file in the same directory as this file, which should contain your discord token (see last 3 lines of this file).
# The start of the on_message method (lines 143ff) probably needs to be changed aswell. The upper 3 lines are used for DMs and DragonGJYs server, the 4th line is for private testing (with the same token).

#TODO: Easy but tedious tasks that just take a lot of time
# implement the missing operators
# implement more healers (and probably fix the kwargs situation before many more are added)
# implement various total_dmg methods for operators
# defshred/resshred compatible with operators doing that on their own (-> pass on as kwarg and read the kward for those operators)

#TODO: specific Minijobs that really should be done asap
# hoederer/qiubai: low dmg showing their dps with their own application rate of the conditionals, instead of just ignoring it
# Mudrock: include the SP gains from the module for S2 damage calculations
# platinum: fix the dmg bonus, it counts from 0 to 2.5 seconds right now, which should be from 1 to 2.5 seconds i think
# kjera: fix freeze rate, applying cold on a frozen enemy does NOT refresh the duration
# Wisadel: Add S1 and S2, and maybe double check S3's aoe
# kaltsit: the true damage of S3 cant handle changes in max res 

#TODO: bigger changes that may be complicated or even unrealistic
# add average_dmg methods (which include skill down time and ramp up times etc)
# clean up plotting, so that the parts are not scattered around in the code
# efficiency boost: restructure everything so that the atkbuff calculations are done only when instancing the operator, instead of with every call of the skilldps method (may interfere with bbuff)
# add !disclaimer prompt talking about the limits of the bots
# optional: add detail prompt to give explanation text for complicated graphs (like assumptions for santallas s2 hit-/freezeratio)
# change high/low into high/low/default for unrealistic conditionals (aka chongyue)
# stacks prompt (mlynar, lapluma, gavialter) to increment certain conditionals
# !div  (!div a b results in : a is XX% more than b etc), so that people can calc relative gains. maybe even a universal calc with some safety measures
# improve enemy prompt: still not good as it is (better formatting, showing enemy hp)
# cleanup: make more things kwargs. anything not used by ALL operators should probably be a kwarg
# add kwargs to make the bot understand more text (like "vs heavy" for rosa or "no mines" for ela)
# first collect the operators(aka parse through the entire input) and THEN draw the stuff.

import discord
import os
import numpy as np
import pylab as pl
from PIL import Image
import damageformulas as df
import healingformulas as hf
import io
import itertools

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

modifiers = ["s1","s2","s3","p1","p2","p3","p4","p5","p6","m0","m1","m2","m3","0","1","2","3","mod0","mod1","mod2","mod3","modlvl","modlvl1","modlvl2","modlvl3","modlv","modlv1","modlv2","modlv3","mod","x","x1","x2","x3","y","y1","y2","y3","d","d1","d2","d3","modx","mody","modd","module","no","nomod","s1m0","s1m1","s1m2","s1m3","s2m0","s2m1","s2m2","s2m3","s3m0","s3m1","s3m2","s3m3","sl7","s7","slv7","l7","lv7"]

#If some smartass requests more than 40 operators to be drawn
bot_mad_message = ["excuse me, what? <:blemi:1077269748972273764>", "why you do this to me? <:jessicry:1214441767005589544>", "how about you draw your own graphs? <:worrymad:1078503499983233046>", "<:pepe_holy:1076526210538012793>", "spare me, please! <:harold:1078503476591607888>"]


def plot_graph(operator, buffs, defens, ress, split, limit = 3000, limit2 = 120, fixval = 40, alreadyDrawnOps =[], shreds = [1,0,1,0], enemies = [],basebuffs=[1,0],normal_dps = True, plotnumbers = 0):
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
	if shreds[0] != 1: op_name += f" -{int(100*(1-shreds[0]))}%def"
	if shreds[1] != 0: op_name += f" -{int(shreds[1])}def"
	if shreds[2] != 1: op_name += f" -{int(100*(1-shreds[2]))}%res"
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
	if len(op_name) > 70: #formatting issue for too long names
		op_name = op_name[:int(len(op_name)/2)] + "\n" + op_name[int(len(op_name)/2):]
	
	if split == 0: #normal dps graph
		defences = np.linspace(0,limit,accuracy)
		damages = np.zeros(accuracy)
		resistances = np.linspace(0,limit2,accuracy)
		for i in range(accuracy):
			if normal_dps: damages[i]=operator.skill_dps(max(0,defences[i]-shreds[1])*shreds[0],max(resistances[i]-shreds[3],0)*shreds[2])*(1+buffs[3])
			else: damages[i]=operator.total_dmg(max(0,defences[i]-shreds[1])*shreds[0],max(resistances[i]-shreds[3],0)*shreds[2])*(1+buffs[3])
		xaxis = np.linspace(0,limit, accuracy)
		p = pl.plot(xaxis, damages, label=op_name,linestyle=style)
		
		for defen in defens:
			if defen >= 0:
				if normal_dps: demanded = operator.skill_dps(max(0,defen-shreds[1])*shreds[0],max(defen/limit*limit2-shreds[3],0)*shreds[2])*(1+buffs[3])
				else: demanded = operator.total_dmg(max(0,defen-shreds[1])*shreds[0],max(defen/limit*limit2-shreds[3],0)*shreds[2])*(1+buffs[3])
				pl.text(defen,demanded,f"{int(demanded)}",size=9, c=p[0].get_color())
		for res in ress:
			if res >= 0:
				if normal_dps: demanded = operator.skill_dps(max(0,res/limit2*limit-shreds[1])*shreds[0],max(res-shreds[3],0)*shreds[2])*(1+buffs[3])
				else: demanded = operator.total_dmg(max(0,res/limit2*limit-shreds[1])*shreds[0],max(res-shreds[3],0)*shreds[2])*(1+buffs[3])
				pl.text(res*25/3000*limit/limit2*120,demanded,f"{int(demanded)}",size=9, c=p[0].get_color())
	
	elif split == 1: #split into defense first then resistance
		zeroes = np.zeros(accuracy)
		resistances = np.linspace(0,limit2,accuracy)
		fullres = np.full(accuracy, limit2)
		defences = np.linspace(0,limit,accuracy)
		fulldef = np.full(accuracy, limit)
		newdefences = np.concatenate((defences,fulldef))
		newresistances = np.concatenate((zeroes,resistances))
		damages = np.zeros(2*accuracy)
		for i in range(2*accuracy):
			if normal_dps: damages[i] = operator.skill_dps(newdefences[i],newresistances[i])*(1+buffs[3])
			else: operator.total_dmg(newdefences[i],newresistances[i])*(1+buffs[3])
		xaxis = np.linspace(0,limit, 2*accuracy)
		p = pl.plot(xaxis, damages, label=op_name)
		
		for defen in defens:
			if defen >= 0:
				defen = min(limit-1,defen)
				if normal_dps: demanded = operator.skill_dps(defen,0)*(1+buffs[3])
				else: demanded = operator.total_dmg(defen,0)*(1+buffs[3])
				pl.text(defen/2,demanded,f"{int(demanded)}",size=9, c=p[0].get_color())
		for res in ress:
			if res >= 0:
				res = min(119,res)
				if normal_dps: demanded = operator.skill_dps(limit,res)*(1+buffs[3])
				else: demanded = operator.total_dmg(limit,res)*(1+buffs[3])
				pl.text(limit/2+res*25/6000/limit2*120*limit,demanded,f"{int(demanded)}",size=9, c=p[0].get_color())
	
	elif split == 2: #split into resistance first then defefense
		zeroes = np.zeros(accuracy) #yes i know this is repetitive
		resistances = np.linspace(0,limit2,accuracy)
		fullres = np.full(accuracy, limit2)
		defences = np.linspace(0,limit,accuracy)
		fulldef = np.full(accuracy, limit)
		newdefences = np.concatenate((zeroes, defences))
		newresistances = np.concatenate((resistances, fullres))
		damages = np.zeros(2*accuracy)
		for i in range(2*accuracy):
			if normal_dps: damages[i]=operator.skill_dps(newdefences[i],newresistances[i])*(1+buffs[3])
			else: damages[i]=operator.total_dmg(newdefences[i],newresistances[i])*(1+buffs[3])
		xaxis = np.linspace(0,limit, 2*accuracy)
		p = pl.plot(xaxis, damages, label=op_name)
		
		for defen in defens:
			if defen >= 0:
				defen = min(limit-1,defen)
				if normal_dps: demanded = operator.skill_dps(defen,limit2)*(1+buffs[3])
				else: demanded = operator.total_dmg(defen,limit2)*(1+buffs[3])
				pl.text(limit/2+defen/2,demanded,f"{int(demanded)}",size=9, c=p[0].get_color())
		for res in ress:
			if res >= 0:
				res = min(limit2-1,res)
				if normal_dps: demanded = operator.skill_dps(0,res)*(1+buffs[3])
				else: demanded = operator.total_dmg(0,res)*(1+buffs[3])
				pl.text(res*25/6000/limit2*120*limit,demanded,f"{int(demanded)}",size=9, c=p[0].get_color())
	
	elif split == 3: #graph with a fixed defense value
		damages = np.zeros(accuracy)
		resistances = np.linspace(0,limit2,accuracy)
		for i in range(accuracy):
			damages[i]=operator.skill_dps(fixval,resistances[i])*(1+buffs[3])
		xaxis = np.linspace(0,limit, accuracy)
		p = pl.plot(xaxis, damages, label=op_name)
		
		for res in ress:
			if res >= 0:
				demanded = operator.skill_dps(fixval,res)*(1+buffs[3])
				pl.text(res*25/3000*limit/limit2*120,demanded,f"{int(demanded)}",size=9, c=p[0].get_color())
	
	elif split == 4: #graph with a fixed resistance value
		defences = np.linspace(0,limit,accuracy)
		damages = np.zeros(accuracy)
		for i in range(accuracy):
			damages[i]=operator.skill_dps(defences[i],fixval)*(1+buffs[3])
		xaxis = np.linspace(0,limit, accuracy)
		p = pl.plot(xaxis, damages, label=op_name)
		
		for defen in defens:
			if defen >= 0:
				demanded = operator.skill_dps(defen,fixval)*(1+buffs[3])
				pl.text(defen,demanded,f"{int(demanded)}",size=9, c=p[0].get_color())
	
	elif split == 5: #graph with the values of certain enemies -> enemy prompt
		defences = [i[0] for i in enemies]
		resistances = [i[1] for i in enemies]
		xaxis = np.arange(len(enemies))
		damages = np.zeros(len(enemies))
		for i in range(len(enemies)):
			damages[i] = operator.skill_dps(defences[i],resistances[i])*(1+buffs[3])
		p = pl.plot(xaxis,damages, marker=".", linestyle = "", label=op_name)
		pl.plot(xaxis,damages, alpha = 0.2, c=p[0].get_color())
		for i in range(len(enemies)):
			demanded = operator.skill_dps(enemies[i][0],enemies[i][1])*(1+buffs[3])
			pl.text(i,demanded,f"{int(demanded)}",size=9, c=p[0].get_color())
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
	
	if message.content.lower().startswith('!ping'):
		await message.channel.send('Pong!')
	if message.content.lower().startswith('!marco'):
		await message.channel.send('Polo!')
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
"""
		await message.channel.send(text)
	
	if message.content.lower().startswith('!prompt') or message.content.lower().startswith('!guide'):
		text = """**Suffixes placed after the operator, affecting only that operator:**
S1,S2,S3, sl7,M0,..,M3, P1,..,P6, mod0,modx,mody,modd or just 0,x1,x2,x3,y1,y2,y3,d1,d2,d3
**Prefixes that affect all following operators (not adding a value resets to default values):**
targets <value>, res <value>/def <value>, buff <atk%> <flatAtk> <aspd> <fragile>, level <OpLevel>, hits <receivedHitsPerSecond> (either like 0.33 or 1/3), bbuff <value> (base atk, flat:123, percentage: 25% or 0.25), resshred/defshred (same as bbuff, this does currently not scale correctly with operators having shred themselves)
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
	
	if message.content.lower().startswith('!code'):
		if type(message.channel)==discord.channel.DMChannel:
			disclaimer = "make sure to read the commentary at the beginning of discoBot.py"
			await message.channel.send(disclaimer, file=discord.File('discoBot.py'))
			await message.channel.send(file=discord.File('damageformulas.py'))
			await message.channel.send(file=discord.File('healingformulas.py'))
		
	if message.content.lower().startswith('!dps'):
		#read the message
		pl.clf()
		pl.style.use('default')
		parsed_message = message.content.lower().split()[1:]
		alreadyDrawnOps = []
		entries = len(parsed_message)
		i = 0

		res = [-1]
		defen = [-1]
		lvl = -10
		mastery = 3
		modlvl = 3
		contains_data = 0
		buffs = [0,0,0,0,0]
		basebuffs = [1,0]
		TrTaTaSkMo = [True,True,True,True,True] #trait talent1 talent2 skill module
		targets = 1
		split = 0
		parsing_error = False
		error_message = "Could not use the following prompts: "
		scale = 3000
		scale2= 120
		show = True
		bottomleft = False
		textsize = 10
		fixval = 40
		number_request = False #For Scaling issues, makes sure that res/def draw calls only appear AFTER setting the scale (to prevent stuff like res 90 maxres 40)
		shreds = [1,0,1,0] #def% def res% res
		beegness = 4
		enemies = []
		enemy_key = ""
		normal_dps = True
		bonus_dmg = False
		add_title = False
		title = ""

		while i < entries:
			if parsed_message[i] in op_dict and i+1==entries:
				if plot_graph((op_dict[parsed_message[i]](lvl,-1, -1, 3,-1,3, targets, TrTaTaSkMo,buffs,bonus=bonus_dmg)), buffs, defen, res, split, scale, scale2, fixval,alreadyDrawnOps,shreds,enemies,basebuffs,normal_dps,contains_data): contains_data += 1
			elif parsed_message[i] in op_dict and not (parsed_message[i+1] in modifiers):
				if contains_data > 40: break
				if plot_graph((op_dict[parsed_message[i]](lvl,-1, -1, 3,-1,3, targets, TrTaTaSkMo,buffs,bonus=bonus_dmg)), buffs, defen, res, split, scale, scale2, fixval,alreadyDrawnOps,shreds,enemies,basebuffs,normal_dps,contains_data): contains_data += 1 
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
					elif parsed_message[i] in ["0","no","mod","module","nomod","modlvl","modlv"]:
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
					if plot_graph((op_dict[parsed_message[tmp]](lvl,pot,skill,mastery,mod,modlvl,targets,TrTaTaSkMo,buffs,bonus=bonus_dmg)), buffs, defen, res, split, scale, scale2, fixval,alreadyDrawnOps,shreds,enemies,basebuffs,normal_dps,contains_data): contains_data += 1
					if contains_data > 40: break
				i-=1
			elif parsed_message[i] in ["b","buff","buffs"]:
				i+=1
				buffcount=0
				buffs=[0,0,0,0,buffs[4]]
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
					if parsed_message[i]=="":
						pass
					else:
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
					if parsed_message[i]=="":
						pass
					else:
						try:
							res.append(min(scale2,int(parsed_message[i])))
						except ValueError:
							break
					i+=1
				i-=1
			elif parsed_message[i] in ["d","def","defense"]:
				i+=1
				number_request = True
				defen = [-10]
				while i < entries:
					if parsed_message[i]=="":
						pass
					else:
						try:
							defen.append(min(scale,int(parsed_message[i])))
						except ValueError:
							break
					i+=1
				i-=1
			
			elif parsed_message[i] in ["shred","shreds","debuff","ignore"]:
				i+=1
				shreds = [1,0,1,0]
				while i < entries:
					if parsed_message[i]=="":
						pass
					elif parsed_message[i][-1] == "%":
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
			elif parsed_message[i] in ["resshred","resdebuff","shredres","debuffres","reshred","resignore"]:
				i+=1
				shreds[2] = 1
				shreds[3] = 0
				while i < entries:
					if parsed_message[i]=="":
						pass
					elif parsed_message[i][-1] == "%":
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
			elif parsed_message[i] in ["defshred","defdebuff","shreddef","debuffdef","defignore"]:
				i+=1
				shreds[0] = 1
				shreds[1] = 0
				while i < entries:
					if parsed_message[i]=="":
						pass
					elif parsed_message[i][-1] == "%":
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
			elif parsed_message[i] in ["basebuff","baseatk","base","bbuff","batk"]:
				i+=1
				basebuffs[0] = 1
				basebuffs[1] = 0
				while i < entries:
					if parsed_message[i]=="":
						pass
					elif parsed_message[i][-1] == "%":
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
					if parsed_message[i]=="":
						pass
					else:
						try:
							lvl = int(parsed_message[i])
						except ValueError:
							break
					i+=1
				i-=1
			elif parsed_message[i] in ["iaps","bonk","received","hits","hit"]:
				i+=1
				buffs[4] = 0
				while i < entries:
					if parsed_message[i]=="":
						pass
					else:
						try:
							buffs[4] = float(parsed_message[i])
						except ValueError:
							if "/" in parsed_message[i]:
								newStrings = parsed_message[i].split("/")
								try:
									buffs[4] = float(newStrings[0]) / float(newStrings[1])
								except ValueError:
									break
							else:
								break
					i+=1
				i-=1						
			elif parsed_message[i] == "":
				continue
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
			elif parsed_message[i] in ["bonus", "bonusdmg"]:
				bonus_dmg = True
			elif parsed_message[i] in ["hide", "legend"]:
				show = False
			elif parsed_message[i] in ["big", "beeg", "large"]:
				beegness = 8
			elif parsed_message[i] in ["repos", "reposition", "bottom", "left", "botleft", "position", "change", "changepos"]:
				bottomleft = True
			elif parsed_message[i] == "split":
				if not contains_data: split = 1
			elif parsed_message[i] == "split2":
				if not contains_data: split = 2
			elif parsed_message[i] in ["small","font","tiny"]:
				textsize = 6
			elif parsed_message[i] in ["color","colour","colorblind","colourblind","blind"]:
				pl.style.use('tableau-colorblind10')
			elif parsed_message[i] in ["maxdef","limit","range","scale"]:
				if contains_data == 0 and not number_request:
					i+=1
					scale = 3000
					while i < entries:
						if parsed_message[i]=="":
							pass
						else:
							try:
								scale = min(69420,max(100, int(parsed_message[i])))
							except ValueError:
								break
						i+=1
					i-=1
			elif parsed_message[i] in ["maxres","reslimit","limitres","scaleres","resscale"]:
				if contains_data == 0 and not number_request:
					i+=1
					scale2 = 120
					while i < entries:
						if parsed_message[i]=="":
							pass
						else:
							try:
								scale2 = min(200,max(5, int(parsed_message[i])))
							except ValueError:
								break
						i+=1
					i-=1
			elif parsed_message[i] in ["enemy","chapter"]:
				if parsed_message[i+1] in enemy_dict:
					enemy_key = parsed_message[i+1]
					split = 5
					enemies = enemy_dict[parsed_message[i+1]]
					enemies.sort(key=lambda tup: tup[0], reverse=False)
					i += 1
			elif parsed_message[i] in ["enemy2","chapter2"]:
				if parsed_message[i+1] in enemy_dict:
					enemy_key = parsed_message[i+1]
					split = 5
					enemies = enemy_dict[parsed_message[i+1]]
					enemies.sort(key=lambda tup: tup[1], reverse=False)
					i += 1
			elif parsed_message[i] in ["fixdef","fixeddef","fixdefense","fixeddefense","setdef","setdefense"]:
				if contains_data == 0: 
					try:
						split = 3
						fixval = int(parsed_message[i+1])
						fixval = max(0,min(9000,fixval))
						i+=1
					except ValueError:
						pass
				
			elif parsed_message[i] in ["fixres","fixedres","fixresistance","fixedresistance","setres","resresistance"]:
				if contains_data == 0: 
					try:
						split = 4
						fixval = int(parsed_message[i+1])
						fixval = max(0,min(200,fixval))
						i+=1
					except ValueError:
						pass
			elif parsed_message[i] in ["set","fix","fixed"]:
				if contains_data == 0: 
					try:
						fixval = int(parsed_message[i+1])
						split = 3 if fixval >= 100 else 4
						fixval = max(0,min(9000,fixval))
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
						idc = int(parsed_message[i-backsteps]) #to cause a valueerror #redneckcoding
						backsteps +=1
					except ValueError:
						backsteps +=1
						break
				i-=backsteps
			elif not parsed_message[i][0] in ["0","1","2","3","4","5","6","7","8","9"] and  parsed_message[i][-1] in ["0","1","2","3","4","5","6","7","8","9","."]: #try to fix a missing space after buff/hits etc
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
				if parsed_message[i+1] in ["t","target","targets","def","defense","res","resistance","limit","maxres","maxdef","hits","hit","iaps"]:
					tmp = parsed_message[i]
					parsed_message[i] = parsed_message[i+1]
					parsed_message[i+1] = tmp
					i -= 1
			else:
				
				myKeys = list(op_dict.keys()) ### Try some autocorrection
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
		
		#Set final plot parameters
		if contains_data == 0:
			pl.close()
			return
		if contains_data > 40:
			pl.close()
			l = len(bot_mad_message)
			nope = bot_mad_message[np.random.randint(0,l)]
			await message.channel.send(nope)
			return
			
		spalten = 1
		if contains_data < 2: beegness = 4
		if contains_data > 15 and beegness == 4:
			textsize = 6
		if contains_data > 26 and beegness == 4:
			spalten = 2
		if contains_data > 52 and beegness == 4:
			spalten = 1
		if contains_data > 30 and beegness == 8 and textsize == 10:
			spalten = 2
		
		if split != 5:
			pl.xlabel("Defense\nRes")
			pl.ylabel("DPS" , rotation=0)
		if split == 3: 
			pl.xlabel("Res")
			pl.ylabel(f"DPS (vs {fixval}def)" , rotation=0)
		if split == 4: 
			pl.xlabel("Defense")
			pl.ylabel(f"DPS (vs {fixval}res)" , rotation=0)
		
		ax = pl.gca()
		ax.set_ylim(ymin = 0)
		ax.set_xlim(xmin = 0)
		if split != 5:
			ax.set_xlim(xmin = 0, xmax = scale)
		ax.xaxis.set_label_coords(0.08/beegness*4, -0.025/beegness*4)
		ax.yaxis.set_label_coords(-0.04/beegness*4, 1+0.01/beegness*4)
		if split == 3: #properly align the DPS comment
			ax.yaxis.set_label_coords(0.02, 1.02)
			if fixval > 999: ax.yaxis.set_label_coords(0.03, 1.02)
			if fixval < 100: ax.yaxis.set_label_coords(0.01, 1.02)
			if fixval < 10: ax.yaxis.set_label_coords(0.0, 1.02)
		if split == 4: 
			ax.yaxis.set_label_coords(0.01, 1.02)
			if fixval < 10: ax.yaxis.set_label_coords(0.0, 1.02)
			
		pl.grid(visible=True)
		if show:
			if not bottomleft: pl.legend(loc="upper right",fontsize=textsize,ncol=spalten)
			else: pl.legend(loc="lower left",fontsize=textsize,ncol=spalten)
		if add_title:
			pl.title(title)
		
		#Setting the x-axis labels	
		if split == 0:
			tick_labels=["0\n0",f"{int(scale/6)}\n{int(scale2/6)}",f"{int(scale/3)}\n{int(scale2/3)}",f"{int(scale/2)}\n{int(scale2/2)}",f"{int(scale*4/6)}\n{int(scale2*4/6)}",f"{int(scale*5/6)}\n{int(scale2*5/6)}",f"{int(scale)}\n{int(scale2)}"]
		if split == 1:
			tick_labels=["0\n0",f"{int(scale/3)}\n0",f"{int(scale*4/6)}\n0",f"{int(scale)}\n0",f"{int(scale)}\n{int(scale2*2/6)}",f"{int(scale)}\n{int(scale2*4/6)}",f"{int(scale)}\n{int(scale2)}"]
		if split == 2:
			tick_labels=["0\n0",f"0\n{int(scale2*2/6)}",f"0\n{int(scale2*4/6)}",f"0\n{int(scale2)}",f"{int(scale*2/6)}\n{int(scale2)}",f"{int(scale*4/6)}\n{int(scale2)}",f"{int(scale)}\n{int(scale2)}"]
		if split == 3:
			tick_labels=["0",f"{int(scale2/6)}",f"{int(scale2/3)}",f"{int(scale2/2)}",f"{int(scale2*4/6)}",f"{int(scale2*5/6)}",f"{int(scale2)}"]
		if split == 4:
			tick_labels=["0",f"{int(scale/6)}",f"{int(scale/3)}",f"{int(scale/2)}",f"{int(scale*4/6)}",f"{int(scale*5/6)}",f"{int(scale)}"]
		if split != 5:
			tick_locations = np.linspace(0,scale,7)
			pl.xticks(tick_locations, tick_labels)
		else:
			ax.set_xticklabels([])
			xl, yl, xh, yh=np.array(ax.get_position()).ravel()
			fig = pl.gcf()
			axes = [None] * len(enemies)
			for i,ax in enumerate(axes):
				ph = len(enemies)
				img = np.asarray(Image.open('arkbotimages/' + enemy_key + '_' + enemies[i][2] + '.png'))
				#ax = fig.add_axes([1/(len(enemies)+1)*(i+0.67), 0, 0.1, 0.1])
				if beegness ==4: ax = fig.add_axes([0.4*xl+1.174*(xh-xl)/ph*(i), 0 ,2.1*(xh-xl)/ph ,2.1*(xh-xl)/ph])
				else: ax = fig.add_axes([0.1*xl+1.22*(xh-xl)/ph*(i), 0 ,2.1*(xh-xl)/ph ,2.1*(xh-xl)/ph])
				ax.axison = False
				ax.imshow(img)


		
		fig = pl.gcf()
		fig.set_size_inches(2 * beegness, beegness)
		pl.tight_layout()
		buf = io.BytesIO()
		pl.savefig(buf,format='png')
		buf.seek(0)
		file = discord.File(buf, filename='plot.png')
		pl.close()
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
				healer_message += (healer_dict[parsed_message[i]](lvl,-1, -1, 3,-1,3,buffs,boost)).skill_hps() + "\n"
				contains_data += 1
			elif parsed_message[i] in healer_dict and not (parsed_message[i+1] in modifiers):
				contains_data += 1
				healer_message += (healer_dict[parsed_message[i]](lvl,-1, -1, 3,-1,3,buffs,boost)).skill_hps() + "\n"
			elif parsed_message[i] in healer_dict and parsed_message[i+1] in modifiers:
				tmp = i
				i+=1
				skill=-1
				mastery = 3
				modlvl = 3
				pot=-1
				mod=-1
				while i < entries and parsed_message[i] in modifiers:
					if parsed_message[i] in ["s1","s2","s3"]: skill = int(parsed_message[i][1])
					elif parsed_message[i] in ["p1","p2","p3","p4","p5","p6"]: pot = int(parsed_message[i][1])
					elif parsed_message[i] in ["1","2","3"]: modlvl = int(parsed_message[i])
					elif parsed_message[i] in ["modlvl1","modlvl2","modlvl3"]: modlvl = int(parsed_message[i][-1])
					elif parsed_message[i] in ["m0","m1","m2","m3"]: mastery = int(parsed_message[i][1]) 
					elif parsed_message[i] in ["mod0","mod1","mod2","mod3"]: mod = int(parsed_message[i][3])
					elif parsed_message[i] in ["modx","x"]: mod = 1
					elif parsed_message[i] in ["x1","x2","x3"]: 
						mod = 1
						modlvl = int(parsed_message[i][1])
					elif parsed_message[i] in ["y1","y2","y3"]: 
						mod = 2
						modlvl = int(parsed_message[i][1])
					elif parsed_message[i] in ["mody","y"]: mod = 2
					elif parsed_message[i] in ["modd","d"]: mod = 3
					elif parsed_message[i] in ["d1","d2","d3"]: 
						mod = 3
						modlvl = int(parsed_message[i][1])
					elif parsed_message[i] in ["no","mod","module","nomod"]: mod = 0
					elif parsed_message[i] in ["s1m0","s1m1","s1m2","s1m3","s2m0","s2m1","s2m2","s2m3","s3m0","s3m1","s3m2","s3m3"]:
						skill = int(parsed_message[i][1])
						mastery = int(parsed_message[i][3])
					i+=1
				healer_message += (healer_dict[parsed_message[tmp]](lvl,pot, skill, mastery,mod,modlvl,buffs,boost)).skill_hps() + "\n"
				contains_data += 1
				i-=1
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
			elif parsed_message[i] in ["sp","boost","recovery"]:
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
		
		await message.channel.send(healer_message)
		
with open("token.txt") as file:
	token = file.readline()
client.run(token)


