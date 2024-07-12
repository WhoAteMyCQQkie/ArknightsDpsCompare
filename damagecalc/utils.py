import matplotlib.pyplot as plt
import nltk
import numpy as np
import subprocess

def plot_graph(operator, buffs=[0,0,0,0], defens=[-1], ress=[-1], graph_type=0, max_def = 3000, max_res = 120, fixval = 40, already_drawn_ops = None, shreds = [1,0,1,0], enemies = [], basebuffs = [1,0], normal_dps = True, plotnumbers = 0):
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
	if op_name in already_drawn_ops: return False
	already_drawn_ops.append(op_name)
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
		defences = np.empty(accuracy)
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
		resistances = np.empty(accuracy)
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
		for i, enemy in enumerate(enemies):
			demanded = operator.skill_dps(enemy[0],enemy[1])*(1+buffs[3])
			plt.text(i,demanded,f"{int(demanded)}",size=9, c=p[0].get_color())
	return True

def calc_message(sentence: str):
	
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
	
	
	try:
		is_valid = any(parser.parse(output))
		if is_valid:
			command = ""
			for letter in output:
				command += letter
			command = "print("+command+")"
			result = subprocess.run(['python', '-c', command], capture_output=True, text=True, timeout=1, check=False)
			if "ZeroDivisionError" in result.stderr: raise ZeroDivisionError
			if len(str(result.stdout)) < 200:
				return str(result.stdout)
			else:
				return "Result too large."
		else:
			return "Invalid syntax."
	except ValueError:
		return "Only numbers and +-x/*^() are allowed as inputs."
	except ZeroDivisionError:
		return "Congrats, you just divided by zero."
	except subprocess.TimeoutExpired:
		return "The thread did not survive trying to process this request."
