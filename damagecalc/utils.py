import subprocess
from typing import Dict, TypeVar, Generic
import itertools
import numpy as np
import copy

from discord import DMChannel, File
import matplotlib.pyplot as plt
import nltk
import numpy as np

enemy_dict = {"13": [[800,50,"01"],[100,40,"02"],[400,50,"03"],[350,50,"04"],[1200,0,"05"],[1500,0,"06"],[900,20,"07"],[1200,20,"08"],[150,40,"09"],[3000,90,"10"],[200,20,"11"],[250,60,"12"],[300,60,"13"],[300,50,"14"]],
		"zt": [[250,50,"01"],[200,15,"02"],[250,50,"03"],[200,15,"04"],[700,60,"05"],[300,50,"06"],[150,10,"07"],[250,15,"08"],[300,50,"09"],[250,15,"10"],[600,80,"11"],[300,50,"12"],[1000,60,"13"],[600,60,"14"],[350,50,"15"],[900,60,"16"],[550,60,"17"]],
		"is": [[250,40,"01"],[200,10,"02"],[180,10,"03"],[200,10,"04"],[250,40,"05"],[900,10,"06"],[120,10,"07"],[1100,10,"08"],[800,45,"09"],[500,25,"10"],[500,25,"11"],[1000,15,"12"],[1300,15,"13"],[800,45,"14"],[1000,60,"15"]]}

T = TypeVar('T')
V = TypeVar('V')

class Registry(Generic[T, V]):

	map: Dict[T, V]
	name: str

	def __init__(self, name: str) -> None: 
		self.map = {}
		self.name = name

	def __len__(self) -> int: 
		return len(self.map)
	
	def register(self, key: T, value: V) -> None:
		if key in self.map:
			raise RuntimeWarning(f"Attempted to register duplicate key {str(key)} in registry {self.name}")

		self.map[key] = value

	def get(self, key: T) -> V:
		try:
			return self.map[key]
		except KeyError:
			return None

class DiscordSendable:
	
	content: str
	file: File
	
	def __init__(self, content: str = None, file: File = None):
		self.content=content
		self.file=file
	
	async def send(self, channel: DMChannel):
		if self.content is None and self.file is None:
			return
		if not self.content is None and len(self.content) > 1999: #discord does not allow messages this long
			split_index = self.content.find(',', len(self.content)//2) + 1 #split behind the comma
			if split_index > 1998 or split_index == -1: split_index = len(self.content)//2
			first_part = self.content[:split_index]
			second_part = self.content[split_index:]
			await channel.send(content=first_part)
			await channel.send(content=second_part, file=self.file)
			return
		await channel.send(content=self.content, file=self.file)

class PlotParameters:
	def __init__(self,pot=-1,promotion=-1,level=-1,skill=-1,mastery=-1,module=-1,module_lvl=-1,buffs=[0,0,0,0],sp_boost=0,targets=-1,trust=100,conditionals=[True,True,True,True,True],
			  graph_type=0,fix_value=40,max_def=3000,max_res=120,res=[-1],defen=[-1],base_buffs=[1,0],shred=[1,0,1,0],normal_dps = 0,enemies=[],**kwargs):
		#Operator Parameters
		self.pot = pot
		self.promotion = promotion
		self.level = level
		self.skill = skill
		self.mastery = mastery #self.skill_lvl
		self.module = module
		self.module_lvl = module_lvl
		self.buffs = copy.deepcopy(buffs) #TODO split that into atk, aspd and fragile. for prompts thats done
		self.sp_boost = sp_boost
		self.targets = targets
		self.trust = trust
		self.conditionals = copy.deepcopy(conditionals)
		self.input_kwargs = kwargs
		

		#Plot Parameters
		self.graph_type = graph_type
		self.fix_value = fix_value
		self.max_def = max_def
		self.max_res = max_res
		self.res = res
		self.defen = defen
		self.base_buffs = base_buffs
		self.shred = copy.deepcopy(shred)
		self.normal_dps = normal_dps
		self.enemies = enemies

class PlotParametersSet(PlotParameters):
	def __init__(self):
		super().__init__()
		self.pots = {-1}
		self.promotions = {-1}
		self.levels = {-1}
		self.skills = {-1}
		self.masteries = {-1} #self.skill_lvl
		self.modules = {-1}
		self.module_lvls = {-1}

		#stuff that only the global parameters need
		self.all_conditionals = False
		self.enemy_key = ""

	def get_plot_parameters(self) -> list[PlotParameters]:
		output = []
		if not self.all_conditionals:
			for pot,promotion,level,skill,mastery,module,module_lvl in itertools.product(self.pots,self.promotions,self.levels,self.skills,self.masteries,self.modules,self.module_lvls):
				output.append(PlotParameters(pot,promotion,level,skill,mastery,module,module_lvl,self.buffs,self.sp_boost,self.targets,self.trust,self.conditionals,self.graph_type,self.fix_value,self.max_def,self.max_res,self.res,self.defen,self.base_buffs,self.shred,self.normal_dps,self.enemies,**self.input_kwargs))
		else:
			for combo in itertools.product([True,False], repeat = 5):
				for pot,promotion,level,skill,mastery,module,module_lvl in itertools.product(self.pots,self.promotions,self.levels,self.skills,self.masteries,self.modules,self.module_lvls):
					output.append(PlotParameters(pot,promotion,level,skill,mastery,module,module_lvl,self.buffs,self.sp_boost,self.targets,self.trust,list(combo),self.graph_type,self.fix_value,self.max_def,self.max_res,self.res,self.defen,self.base_buffs,self.shred,self.normal_dps,self.enemies,**self.input_kwargs))
		return output

#read in the operator specific parameters	
def parse_plot_parameters(pps: PlotParametersSet, args: list[str]):
	 #make sure to reset the parameters of the global parameter set
	previous_arg = " "
	for arg in args:
		if arg in ["s1","s2","s3"]:
			pps.skills = {-1}
		elif arg in ["e0","e1","e2"]:
			pps.promotions = {-1}
		elif arg in ["p1","p2","p3","p4","p5","p6","pot1","pot2","pot3","pot4","pot5","pot6"]:
			pps.pots = {-1}
		elif arg in ["modlvl1","modlvl2","modlvl3","modlv1","modlv2","modlv3"]:
			pps.module_lvls = {-1}
		elif arg in ["1","2","3"] and previous_arg not in ["skilllvl","skilllevel","skilllv","skillvl","skillevel","skillv","slv","slevel","slvl","lvl","level","lv","t","target","targets","trust","hit","hits","r","res","resis","resistance","d","def","defense","fixres","fixdef","fix"]:
			pps.module_lvls = {-1}
		elif arg in ["0"] and previous_arg not in ["skilllvl","skilllevel","skilllv","skillvl","skillevel","skillv","slv","slevel","slvl","lvl","level","lv","t","target","targets","trust","hit","hits","r","res","resis","resistance","d","def","defense","fixres","fixdef","fix"]:
			pps.modules = {-1}
		elif arg in ["mod0","modx","x","mody","y","modd","d","no","mod","nomod"]:
			pps.modules = {-1}
		elif arg in ["x1","x2","x3","y1","y2","y3","d1","d2","d3","modx1","modx2","modx3","mody1","mody2","mody3","modd1","modd2","modd3","mod1","mod2","mod3"]:
			pps.modules = {-1}
			pps.module_lvls = {-1}
		elif arg in ["s1m0","s1m1","s1m2","s1m3","s2m0","s2m1","s2m2","s2m3","s3m0","s3m1","s3m2","s3m3","s1l7","s2l7","s3l7"]:
			pps.skills = {-1}
			pps.masteries = {-1}
		elif arg in ["sl1","slv1","sl2","slv2","sl3","slv3","sl4","slv4","sl5","slv5","sl6","slv6","sl7","s7","slv7","l7","lv7","m0","m1","m2","m3","skilllvl","skilllevel","skilllv","skillvl","skillevel","skillv","slv","slevel","slvl"]:
			pps.masteries = {-1}
		if arg not in ["1","2","3"]:
			previous_arg = arg
	i = 0
	entries = len(args)
	unused_inputs = set()
	while i < entries:
		if args[i] in ["maxdef","limit","range","scale","maxres","reslimit","limitres","scaleres","resscale","fixdef","fixeddef","fixdefense","fixeddefense","setdef","setdefense","fixres","fixedres","fixresistance","fixedresistance","setres","resresistance"]:
			i += 1
		elif args[i] in ["s1","s2","s3"]: 
			pps.skills.add(int(args[i][1]))
			pps.skills.discard(-1)
		elif args[i] in ["e0","e1","e2"]: 
			pps.promotions.add(int(args[i][1]))
			pps.promotions.discard(-1)
		elif args[i] in ["p1","p2","p3","p4","p5","p6","pot1","pot2","pot3","pot4","pot5","pot6"]: 
			pps.pots.add(int(args[i][-1]))
			pps.pots.discard(-1)
		elif args[i] in ["1","2","3"]: 
			pps.module_lvls.add(int(args[i]))
			pps.module_lvls.discard(-1)
		elif args[i] in ["modlvl1","modlvl2","modlvl3","modlv1","modlv2","modlv3"]: 
			pps.module_lvls.add(int(args[i][-1]))
			pps.module_lvls.discard(-1)
		elif args[i] in ["m0","m1","m2","m3"]: 
			pps.masteries.add(int(args[i][1])+7)
			pps.masteries.discard(-1)
		elif args[i] in ["sl1","slv1","sl2","slv2","sl3","slv3","sl4","slv4","sl5","slv5","sl6","slv6","sl7","s7","slv7","l7","lv7"]:
			pps.masteries.add(int(args[i][-1]))
			pps.masteries.discard(-1)
		elif args[i] in ["mod1","mod2","mod3"]:
			pps.module_lvls.add(int(args[i][3]))
			pps.module_lvls.discard(-1)
		elif args[i] in ["modx","x"]:
			pps.modules.add(1)
			pps.modules.discard(-1)
		elif args[i] in ["x1","x2","x3","modx1","modx2","modx3"]: 
			pps.modules.add(1)
			pps.modules.discard(-1)
			pps.module_lvls.add(int(args[i][-1]))
			pps.module_lvls.discard(-1)
		elif args[i] in ["y1","y2","y3","mody1","mody2","mody3"]: 
			pps.modules.add(2)
			pps.modules.discard(-1)
			pps.module_lvls.add(int(args[i][-1]))
			pps.module_lvls.discard(-1)
		elif args[i] in ["mody","y"]:
			pps.modules.add(2)
			pps.modules.discard(-1)
		elif args[i] in ["modd","d","a"]:
			pps.modules.add(3)
			pps.modules.discard(-1)
		elif args[i] in ["d1","d2","d3","modd1","modd2","modd3"]: 
			pps.modules.add(3)
			pps.modules.discard(-1)
			pps.module_lvls.add(int(args[i][-1]))
			pps.module_lvls.discard(-1)
		elif args[i] in ["0","no","mod","module","nomod","nomodule","modlvl","modlv","x0","y0","mod0"]:
			pps.modules.add(0)
			pps.modules.discard(-1)
		elif args[i] in ["s1m0","s1m1","s1m2","s1m3","s2m0","s2m1","s2m2","s2m3","s3m0","s3m1","s3m2","s3m3"]:
			pps.skills.add(int(args[i][1]))
			pps.skills.discard(-1)
			pps.masteries.add(int(args[i][3])+7)
			pps.masteries.discard(-1)
		elif args[i] in ["b","buff","buffs"]:
			i+=1
			buffcount=0
			pps.buffs=[0,0,0,0]
			if args[i][-1] == "%": args[i] = args[i][:-1]
			while i < entries and buffcount < 4:
				try:
					pps.buffs[buffcount] = int(args[i])
					buffcount +=1
				except ValueError:
					break
				if buffcount == 1: pps.buffs[0] = pps.buffs[0]/100
				if buffcount == 4: pps.buffs[3] = pps.buffs[3]/100
				i+=1
			i-=1
		elif args[i] in ["atk","attack"]:
			i+=1
			pps.buffs[0] = 0
			pps.buffs[1] = 0
			while i < entries:
				if args[i][-1] == "%":
					try:
						pps.buffs[0] = float(args[i][:-1])/100
					except ValueError:
						break
				else:
					try:
						val = float(args[i])
						if val > 0 and val < 2:
							pps.buffs[0] = val
						if val >= 2:
							pps.buffs[1] = int(val)
					except ValueError:
						break
				i+=1
			i-=1

		elif args[i] in ["aspd","apsd","speed","atkspeed","attackspeed","atkspd"]:
			i+=1
			pps.buffs[2] = 0
			while i < entries:
				try:
					pps.buffs[2] = int(args[i])
				except ValueError:
					break
				i+=1
			i-=1
		elif args[i] in ["fragile","frag","dmg","healing","healingbonus","hb","bonus"]:
			i+=1
			pps.buffs[3] = 0
			if args[i][-1] == "%": args[i] = args[i][:-1]
			while i < entries:
				try:
					pps.buffs[3] = int(args[i])
				except ValueError:
					break
				i+=1
			i-=1
			pps.buffs[3] = pps.buffs[3]/100
		elif args[i] in ["sp","boost","recovery","spboost","spbuff","buffsp"]:
			i+=1
			pps.sp_boost = 0
			while i < entries:
				try:
					pps.sp_boost = float(args[i])
				except ValueError:
					break
				i+=1
			i-=1
		elif args[i] in ["t","target","targets"]:
			i+=1
			pps.targets = 1
			while i < entries:
				try:
					pps.targets = int(args[i])
				except ValueError:
					break
				i+=1
			i-=1
		elif args[i] in ["trust"]:
			pps.trust = 100
			try:
				pps.trust = int(args[i+1])
				i+=1
			except ValueError:
				pass
		elif args[i] in ["t1","t2","t3","t4","t5","t6","t7","t8","t9"]: pps.targets = int(args[i][1])
		elif args[i] in ["r","res","resis","resistance"]:
			i+=1
			pps.res = [-10]
			while i < entries:
				try:
					pps.res.append(min(pps.max_res,int(args[i])))
				except ValueError:
					break
				i+=1
			i-=1
		elif args[i] in ["d","def","defense"]:
			i+=1

			pps.defen = [-10]
			while i < entries:
				try:
					pps.defen.append(min(pps.max_def,int(args[i])))
				except ValueError:
					break
				i+=1
			i-=1
		elif args[i] in ["numbers","dmgnumbers","damage","damagenumbers"]:
			if pps.graph_type == 1:
				pps.res = np.linspace(0,pps.max_res,9)
				pps.defen = np.linspace(0,pps.max_def,9)[:-1]
			elif pps.graph_type == 2:
				pps.res = np.linspace(0,pps.max_res,9)[:-1]
				pps.defen = np.linspace(0,pps.max_def,9)
			elif pps.graph_type == 3:
				pps.res = np.linspace(0,pps.max_res,13)
			else:
				pps.defen = np.linspace(0,pps.max_def,13)
		elif args[i] in ["shred","shreds","debuff","ignore"]:
			i+=1
			pps.shred = [1,0,1,0]
			while i < entries:
				if args[i][-1] == "%":
					try:
						pps.shred[0] = max(0,(1-float(args[i][:-1])/100))
						pps.shred[2] = max(0,(1-float(args[i][:-1])/100))
					except ValueError:
						break
				else:
					try:
						val = float(args[i])
						if val > 0 and val < 1:
							pps.shred[0] = 1 - val
							pps.shred[2] = 1 - val
						if val > 2:
							pps.shred[1] = val
							pps.shred[3] = val
					except ValueError:
						break
				i+=1
			i-=1
			pps.input_kwargs["shreds"] = pps.shred
		elif args[i] in ["resshred","resdebuff","shredres","debuffres","reshred","resignore"]:
			i+=1
			pps.shred[2] = 1
			pps.shred[3] = 0
			while i < entries:
				if args[i][-1] == "%":
					try:
						pps.shred[2] = max(0,(1-float(args[i][:-1])/100))
					except ValueError:
						break
				else:
					try:
						val = float(args[i])
						if val > 0 and val < 1:
							pps.shred[2] = 1 - val
						if val > 2:
							pps.shred[3] = val
					except ValueError:
						break
				i+=1
			i-=1
			pps.input_kwargs["shreds"] = pps.shred
		elif args[i] in ["defshred","defdebuff","shreddef","debuffdef","defignore"]:
			i+=1
			pps.shred[0] = 1
			pps.shred[1] = 0
			while i < entries:
				if args[i][-1] == "%":
					try:
						pps.shred[0] = max(0,(1-float(args[i][:-1])/100))
					except ValueError:
						break
				else:
					try:
						val = float(args[i])
						if val > 0 and val < 1:
							pps.shred[0] = 1 - val
						if val > 2:
							pps.shred[1] = val
					except ValueError:
						break
				i+=1
			i-=1
			pps.input_kwargs["shreds"] = pps.shred
		elif args[i] in ["basebuff","baseatk","base","bbuff","batk"]:
			i+=1
			pps.base_buffs = [1,0]
			while i < entries:
				if args[i][-1] == "%":
					try:
						pps.base_buffs[0] = (1+float(args[i][:-1])/100)
					except ValueError:
						break
				else:
					try:
						val = float(args[i])
						if val > -1 and val < 1:
							pps.base_buffs[0] = 1 + val
						else:
							pps.base_buffs[1] = val
					except ValueError:
						break
				i+=1
			i-=1
		elif args[i] in ["lvl","level","lv"]:
			i+=1
			pps.levels = {-1}
			while i < entries:
				try:
					pps.levels.add(max(1,int(args[i])))
					pps.levels.discard(-1)
				except ValueError:
					break
				i+=1
			i-=1
		elif args[i] in ["skilllvl","skilllevel","skilllv","skillvl","skillevel","skillv","slv","slevel","slvl"]:
			i+=1
			while i < entries:
				try:
					pps.masteries.add(min(10,max(1,int(args[i]))))
					pps.masteries.discard(-1)
				except ValueError:
					break
				i+=1
			i-=1
		elif args[i] in ["iaps","bonk","received","hits","hit"]:
			i+=1
			while i < entries:
				try:
					pps.input_kwargs["hits"] = float(args[i])
				except ValueError:
					if "/" in args[i]:
						new_strings = args[i].split("/")
						try:
							pps.input_kwargs["hits"] = (float(new_strings[0]) / float(new_strings[1]))
						except ValueError:
							break
					else:
						break
				i+=1
			i-=1
		elif args[i] in ["hp","hitpoints"]:
			i+=1
			while i < entries:
				try:
					pps.input_kwargs["hp"] = int(args[i])
				except ValueError:
					break
				i+=1
			i-=1
		elif args[i] in ["total","totaldmg"]:
			pps.normal_dps = 1 if pps.normal_dps != 1 else 0
		elif args[i] in ["avg","avgdmg","average","averagedmg"]:
			pps.normal_dps = 2 if pps.normal_dps != 2 else 0
		elif args[i] in ["l","low"]:
			pps.conditionals = [False,False,False,False,False]
		elif args[i] in ["h","high"]:
			pps.conditionals = [True,True,True,True,True]
		elif args[i] in ["low1","l1","lowtrait","traitlow"]:
			pps.conditionals[0] = False
		elif args[i] in ["high1","h1","hightrait","traithigh"]:
			pps.conditionals[0] = True
		elif args[i] in ["low2","l2","lowtalent","talentlow","lowtalent1","talent1low"]:
			pps.conditionals[1] = False
		elif args[i] in ["high2","h2","hightalent","talenthigh","hightalent1","talent1high"]:
			pps.conditionals[1] = True
		elif args[i] in ["low3","l3","talentlow","lowtalent2","talent2low"]:
			pps.conditionals[2] = False
		elif args[i] in ["high3","h3","talenthigh","hightalent2","talent2high"]:
			pps.conditionals[2] = True
		elif args[i] in ["low4","l4","lows","slow","lowskill","skilllow"]:
			pps.conditionals[3] = False
		elif args[i] in ["high4","h4","highs","shigh","highskill","skillhigh"]:
			pps.conditionals[3] = True
		elif args[i] in ["low5","l5","lowm","mlow","lowmod","modlow","lowmodule","modulelow"]:
			pps.conditionals[4] = False
		elif args[i] in ["high5","h5","highm","mhigh","highmod","modhigh","highmodule","modulehigh"]:
			pps.conditionals[4] = True
		elif args[i] == "lowtalents":
			pps.conditionals[1] = False
			pps.conditionals[2] = False
		elif args[i] == "hightalents":
			pps.conditionals[1] = True
			pps.conditionals[2] = True
		elif args[i] in ["conditionals", "conditional","variation","variations","all"]:
			pps.all_conditionals = True
		elif args[i][0] == "c" and len(args[i]) < 4 and len(args[i]) > 1:
			if args[i][1:].isnumeric():
				pps.conditionals = int_to_bools(min(31,int(args[i][1:])))
		elif args[i].isnumeric():
			x = int(args[i])
			try:
				essential_prompt = args[i-1] in ["maxdef","limit","range","scale","maxres","reslimit","limitres","scaleres","resscale","fixdef","fixeddef","fixdefense",
									 "fixeddefense","setdef","setdefense","fixres","fixedres","fixresistance","fixedresistance","setres","resresistance",
									 "set","fix","fixed","chapter","chapter2","enemy","enemy2"]
			except:
				essential_prompt = False
			if x > 3 and x < 90 and not essential_prompt:
				pps.levels.add(x)
				pps.levels.discard(-1)
			else:
				unused_inputs.add(i)
		else:
			unused_inputs.add(i)
			pps.input_kwargs[args[i]] = True
		if not -1 in pps.module_lvls and 0 in pps.modules and len(pps.modules) == 1:
			pps.modules.add(-1)
		i += 1
	return unused_inputs

#read the graph scalings
def parse_plot_essentials(pps: PlotParametersSet, args: list[str]):
	i = 0
	entries = len(args)
	unused_inputs = set()
	while i < entries:
		if args[i] in ["maxdef","limit","range","scale"]:
			i+=1
			pps.max_def = 3000
			try:
				pps.max_def = min(69420,max(100, int(args[i])))
			except ValueError:
				break

		elif args[i] in ["maxres","reslimit","limitres","scaleres","resscale"]:
			i+=1
			pps.max_res = 120
			try:
				pps.max_res = min(420,max(5, int(args[i])))
			except ValueError:
				break

		elif args[i] == "split":
				pps.graph_type = 1
		elif args[i] == "split2":
				pps.graph_type = 2
		elif args[i] in ["fixdef","fixeddef","fixdefense","fixeddefense","setdef","setdefense"]:
			try:
				pps.graph_type = 3
				pps.fix_value = int(args[i+1])
				pps.fix_value = max(0,min(50000,pps.fix_value))
				i+=1
			except ValueError:
				pass	
		elif args[i] in ["fixres","fixedres","fixresistance","fixedresistance","setres","resresistance"]: 
			try:
				pps.graph_type = 4
				pps.fix_value = int(args[i+1])
				pps.fix_value = max(0,min(400,pps.fix_value))
				i+=1
			except ValueError:
				pass
		elif args[i] in ["set","fix","fixed"]:
			try:
				pps.fix_value = int(args[i+1])
				pps.graph_type = 3 if pps.fix_value >= 100 else 4
				pps.fix_value = max(0,min(50000,pps.fix_value))
				i+=1
			except ValueError:
				pass
		elif args[i] in ["enemy","chapter"]:
			if args[i+1] in enemy_dict:
				pps.enemy_key = args[i+1]
				pps.graph_type = 5
				pps.enemies = enemy_dict[args[i+1]]
				pps.enemies.sort(key=lambda tup: tup[0], reverse=False)
				i += 1
		elif args[i] in ["enemy2","chapter2"]:
			if args[i+1] in enemy_dict:
				pps.enemy_key = args[i+1]
				pps.graph_type = 5
				pps.enemies = enemy_dict[args[i+1]]
				pps.enemies.sort(key=lambda tup: tup[1], reverse=False)
				i += 1
		else:
			unused_inputs.add(i)
		i += 1
	return unused_inputs

def is_float(word: str) -> bool:
		try:
			float(word)
			return True
		except ValueError:
			return False

def bools_to_int(bool_list):
    return 31 - sum((1 << i) for i, val in enumerate(reversed(bool_list)) if val)

def int_to_bools(n):
    return [bool((31-n) & (1 << i)) for i in range(4, -1, -1)]

def levenshtein(word1, word2):
	m = len(word1)
	n = len(word2)
	D = np.zeros((m, n))
	for i in range(m):
		D[i][0] = i
	for j in range(n):
		D[0][j] = j
	if word1[0] != word2[0]: D[0][0] = 1
	for j in range(1,n): #rows
		if word1[0] != word2[0]: D[0][j] = D[0][j]+1
		for i in range(1,m): #columns
			a = D[i-1][j-1] if word1[i]==word2[j] else 2000
			b = D[i-1][j] + 1
			c = D[i][j-1] + 1
			d = D[i-1][j-1] + 1
			D[i][j] = min(a,b,c,d)
	return (int(D[m-1][n-1]))

def fix_typos(word, args):
	output = ""
	errorlimit = 0
	input_length = len(word) 
	optimizer = False #True when a solution was found, but we still search for a better solution.
	optimize_error = -10
	if input_length > 3: errorlimit = 1
	if input_length > 5: errorlimit = 2
	if input_length > 8: errorlimit = 3
	if input_length < 15:
		for key in args:
			if optimizer:
				if levenshtein(key, word) < optimize_error: #dont just stop at the first fit, but rather at the best fit.
					output = key
					optimize_error = levenshtein(key, word)
			elif levenshtein(key, word) <= errorlimit:
				output = key
				optimizer = True
				optimize_error = levenshtein(key, word)
	return output

def apply_plot(operator_input, plot_parameters, already_drawn=[], plot_numbers=0, short = False):
	pp = plot_parameters
	operator = operator_input(pp, **pp.input_kwargs)
	return plot_graph(operator,pp,pp.buffs,pp.defen,pp.res,pp.graph_type,pp.max_def,pp.max_res,pp.fix_value,already_drawn,pp.shred,pp.enemies,pp.base_buffs,pp.normal_dps, plot_numbers, short)

def plot_graph(operator,pp, buffs=[0,0,0,0], defens=[-1], ress=[-1], graph_type=0, max_def = 3000, max_res = 120, fixval = 40, already_drawn_ops = None, shreds = [1,0,1,0], enemies = [], basebuffs = [1,0], normal_dps = 0, plotnumbers = 0, short = False):
	accuracy = 1 + 30 * 6
	style = '-'
	if plotnumbers > 9: style = '--'
	if plotnumbers > 19: style = ':'
	if plotnumbers > 29: style = '-.'

	#Setting the name of the operator
	op_name = ""
	if normal_dps == 1 and operator.skill_dps(100,100) != operator.total_dmg(100,100): op_name += " totalDMG" #redneck way of checking if the total dmg method is implemented
	if normal_dps == 2 and operator.skill_dps(100,100) != operator.avg_dps(100,100): op_name += " avgDMG"
	op_name = operator.get_name() + op_name
	if op_name in already_drawn_ops: return False
	already_drawn_ops.append(op_name)
	if len(op_name) > 65: #formatting issue for too long names
		space_position = op_name.find(" ", int(len(op_name)/2))
		op_name = op_name[:space_position] + "\n" + op_name[space_position+1:]
	if short:
		op_name = operator.base_name

	#op_name = f"(c{bools_to_int(pp.conditionals)})" + op_name

	defences = np.clip(np.linspace(-shreds[1]*shreds[0],(max_def-shreds[1])*shreds[0], accuracy), 0, None)
	resistances = np.clip(np.linspace(-shreds[3]*shreds[2],(max_res-shreds[3])*shreds[2], accuracy), 0, None)
	damages = np.zeros(2*accuracy) if graph_type in [1,2] else np.zeros(accuracy)
	
	############### Normal DPS graph ################################
	if graph_type == 0:
		if normal_dps == 0: damages=operator.skill_dps(defences,resistances)*(1+buffs[3])
		elif normal_dps == 2: damages = operator.avg_dps(defences,resistances)*(1+buffs[3])
		else: damages=operator.total_dmg(defences,resistances)*(1+buffs[3])
		xaxis = np.linspace(0,max_def, accuracy)
		p = plt.plot(xaxis, damages, label=op_name, linestyle=style)
		
		for defen in defens:
			if defen >= 0:
				if normal_dps == 0: demanded = operator.skill_dps(max(0,defen-shreds[1])*shreds[0],max(defen/max_def*max_res-shreds[3],0)*shreds[2])*(1+buffs[3])
				elif normal_dps == 2: demanded = operator.avg_dps(max(0,defen-shreds[1])*shreds[0],max(defen/max_def*max_res-shreds[3],0)*shreds[2])*(1+buffs[3])
				else: demanded = operator.total_dmg(max(0,defen-shreds[1])*shreds[0],max(defen/max_def*max_res-shreds[3],0)*shreds[2])*(1+buffs[3])
				plt.text(defen,demanded,f"{int(demanded)}",size=10, c=p[0].get_color())
		for res in ress:
			if res >= 0:
				if normal_dps == 0: demanded = operator.skill_dps(max(0,res/max_res*max_def-shreds[1])*shreds[0],max(res-shreds[3],0)*shreds[2])*(1+buffs[3])
				elif normal_dps == 2: demanded = operator.avg_dps(max(0,res/max_res*max_def-shreds[1])*shreds[0],max(res-shreds[3],0)*shreds[2])*(1+buffs[3])
				else: demanded = operator.total_dmg(max(0,res/max_res*max_def-shreds[1])*shreds[0],max(res-shreds[3],0)*shreds[2])*(1+buffs[3])
				plt.text(res*25/3000*max_def/max_res*120,demanded,f"{int(demanded)}",size=10, c=p[0].get_color())
	
	############### Increments defense and THEN res ################################
	elif graph_type == 1: 
		fulldef = np.full(accuracy, max(0,max_def-shreds[1])*shreds[0])
		newdefences = np.concatenate((defences,fulldef))
		newresistances = np.concatenate((np.zeros(accuracy),resistances))
		
		if normal_dps == 0: damages = operator.skill_dps(newdefences,newresistances)*(1+buffs[3])
		elif normal_dps == 2: damages = operator.avg_dps(newdefences,newresistances)*(1+buffs[3])
		else: damages = operator.total_dmg(newdefences,newresistances)*(1+buffs[3])
		xaxis = np.linspace(0,max_def, 2*accuracy)
		p = plt.plot(xaxis, damages, label=op_name, linestyle=style)
		
		for defen in defens:
			if defen >= 0:
				defen = min(max_def-1,defen)
				if normal_dps == 0: demanded = operator.skill_dps(max(0,defen-shreds[1])*shreds[0],0)*(1+buffs[3])
				elif normal_dps == 2: demanded = operator.avg_dps(max(0,defen-shreds[1])*shreds[0],0)*(1+buffs[3])
				else: demanded = operator.total_dmg(max(0,defen-shreds[1])*shreds[0],0)*(1+buffs[3])
				plt.text(defen/2,demanded,f"{int(demanded)}",size=9, c=p[0].get_color())
		for res in ress:
			if res >= 0:
				res = min(119,res)
				if normal_dps == 0: demanded = operator.skill_dps(max(0,max_def-shreds[1])*shreds[0],max(res-shreds[3],0)*shreds[2])*(1+buffs[3])
				elif normal_dps == 2: demanded = operator.avg_dps(max(0,max_def-shreds[1])*shreds[0],max(res-shreds[3],0)*shreds[2])*(1+buffs[3])
				else: demanded = operator.total_dmg(max(0,max_def-shreds[1])*shreds[0],max(res-shreds[3],0)*shreds[2])*(1+buffs[3])
				plt.text(max_def/2+res*25/6000/max_res*120*max_def,demanded,f"{int(demanded)}",size=9, c=p[0].get_color())
	
	############### Increments Res and THEN defense ################################
	elif graph_type == 2:
		fullres = np.full(accuracy, max(max_res-shreds[3],0)*shreds[2])
		newdefences = np.concatenate((np.zeros(accuracy), defences))
		newresistances = np.concatenate((resistances, fullres))
		
		if normal_dps == 0: damages=operator.skill_dps(newdefences,newresistances)*(1+buffs[3])
		elif normal_dps == 2: damages = operator.avg_dps(newdefences,newresistances)*(1+buffs[3])
		else: damages=operator.total_dmg(newdefences,newresistances)*(1+buffs[3])
		xaxis = np.linspace(0,max_def, 2*accuracy)
		p = plt.plot(xaxis, damages, label=op_name, linestyle=style)
		
		for defen in defens:
			if defen >= 0:
				defen = min(max_def-1,defen)
				if normal_dps == 0: demanded = operator.skill_dps(max(0,defen-shreds[1])*shreds[0],max(max_res-shreds[3],0)*shreds[2])*(1+buffs[3])
				elif normal_dps == 2: demanded = operator.avg_dps(max(0,defen-shreds[1])*shreds[0],max(max_res-shreds[3],0)*shreds[2])*(1+buffs[3])
				else: demanded = operator.total_dmg(max(0,defen-shreds[1])*shreds[0],max(max_res-shreds[3],0)*shreds[2])*(1+buffs[3])
				plt.text(max_def/2+defen/2,demanded,f"{int(demanded)}",size=9, c=p[0].get_color())
		for res in ress:
			if res >= 0:
				res = min(max_res-1,res)
				if normal_dps == 0: demanded = operator.skill_dps(0,max(res-shreds[3],0)*shreds[2])*(1+buffs[3])
				elif normal_dps == 2: demanded = operator.avg_dps(0,max(res-shreds[3],0)*shreds[2])*(1+buffs[3])
				else: demanded = operator.total_dmg(0,max(res-shreds[3],0)*shreds[2])*(1+buffs[3])
				plt.text(res*25/6000/max_res*120*max_def,demanded,f"{int(demanded)}",size=9, c=p[0].get_color())
	
	############### DPS graph with a fixed defense value ################################
	elif graph_type == 3:
		defences = np.empty(accuracy)
		defences.fill(max(0,fixval-shreds[1])*shreds[0])
		
		if normal_dps == 0: damages=operator.skill_dps(defences,resistances)*(1+buffs[3])
		elif normal_dps == 2: damages = operator.avg_dps(defences,resistances)*(1+buffs[3])
		else: damages=operator.total_dmg(defences,resistances)*(1+buffs[3])
		xaxis = np.linspace(0,max_def, accuracy)
		p = plt.plot(xaxis, damages, label=op_name, linestyle=style)
		
		for res in ress:
			if res >= 0:
				if normal_dps == 0: demanded = operator.skill_dps(max(0,fixval-shreds[1])*shreds[0],max(res-shreds[3],0)*shreds[2])*(1+buffs[3])
				elif normal_dps == 2: demanded = operator.avg_dps(max(0,fixval-shreds[1])*shreds[0],max(res-shreds[3],0)*shreds[2])*(1+buffs[3])
				else: demanded = operator.total_dmg(max(0,fixval-shreds[1])*shreds[0],max(res-shreds[3],0)*shreds[2])*(1+buffs[3])
				plt.text(res*25/3000*max_def/max_res*120,demanded,f"{int(demanded)}",size=10, c=p[0].get_color())
	
	############### DPS graph with a fixed res value ################################
	elif graph_type == 4:
		resistances = np.empty(accuracy)
		resistances.fill(max(fixval-shreds[3],0)*shreds[2])
		
		if normal_dps == 0: damages = operator.skill_dps(defences,resistances)*(1+buffs[3])
		elif normal_dps == 2: damages = operator.avg_dps(defences,resistances)*(1+buffs[3])
		else: damages = operator.total_dmg(defences,resistances)*(1+buffs[3])
		xaxis = np.linspace(0,max_def, accuracy)
		p = plt.plot(xaxis, damages, label=op_name, linestyle=style)
		
		for defen in defens:
			if defen >= 0:
				if normal_dps == 0: demanded = operator.skill_dps(max(0,defen-shreds[1])*shreds[0],max(fixval-shreds[3],0)*shreds[2])*(1+buffs[3])
				elif normal_dps == 2: demanded = operator.avg_dps(max(0,defen-shreds[1])*shreds[0],max(fixval-shreds[3],0)*shreds[2])*(1+buffs[3])
				else: demanded = operator.total_dmg(max(0,defen-shreds[1])*shreds[0],max(fixval-shreds[3],0)*shreds[2])*(1+buffs[3])
				plt.text(defen,demanded,f"{int(demanded)}",size=10, c=p[0].get_color())
	
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
			plt.text(i,demanded,f"{int(demanded)}",size=10, c=p[0].get_color())
	return True

def calc_message(sentence: str, return_dict):
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
			result = eval(command)
			#command = "print("+command+")"
			#computation = subprocess.run(['python', '-c', command], capture_output=True, text=True, timeout=1, check=False)
			#result = computation.stdout
			#if "ZeroDivisionError" in computation.stderr: raise ZeroDivisionError
			if len(str(result)) < 200:
				return_dict['result'] = result
			else:
				return_dict['result'] = "Result too large"
		else:
			return_dict['result'] = "Invalid syntax."
	except ValueError:
		return_dict['result'] = "Only numbers and +-x/*^() are allowed as inputs."
	except ZeroDivisionError:
		return_dict['result'] = "Congrats, you just divided by zero."
	except subprocess.TimeoutExpired:
		return_dict['result'] = "The thread did not survive trying to process this request."
	return return_dict['result']
